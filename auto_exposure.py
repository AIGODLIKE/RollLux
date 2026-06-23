"""RollLux viewport auto exposure — Color Management or light rig from 3D View sampling."""

from __future__ import annotations

import bpy
import gpu

from . import ae_metering

_SHADING_LIT = frozenset({"MATERIAL", "RENDERED"})
_PREFERRED_SHADING = "RENDERED"

_GRID = 10
_CENTER_DENSE = 5
_THRESHOLD = 0.02
_LIGHT_RIG_THRESHOLD = 0.04
_STABLE_BAND = 0.045
_RELEASE_BAND = 0.12
_SNAP_EV = 0.025
_FAST_CONVERGE_EV = 0.1
_REDRAW_TICK = 0.12
_LIGHT_MIN_INTERVAL = 0.30
_LIGHT_POST_COMMIT = 0.55
_CYCLES_LUMA_TOL = 0.075
_CYCLES_STABLE_FRAMES = 2
_LUM_EMA_ALPHA_LIGHT = 0.22
_TARGET_EMA_ALPHA_LIGHT = 0.45
_FEEDBACK_PAUSE = 10
_FEEDBACK_OSC_LIMIT = 2

_HANDLE = None
_IDLE_TIMER = False
_JITTER = 0
_FEEDBACK: dict[str, dict] = {}
_LUM_EMA: dict[str, float] = {}
_TARGET_EMA: dict[str, float] = {}
_LIGHT_LAST_ADAPT: dict[str, float] = {}
_LIGHT_COMMIT_TIME: dict[str, float] = {}
_LIGHT_SETTLE_NEED: dict[str, float] = {}


def _lerp(a: float, b: float, t: float) -> float:
    return ae_metering._lerp(a, b, t)


def _rgb_to_luminance(color) -> float:
    return 0.2126729 * color[0] + 0.7151522 * color[1] + 0.072175 * color[2]


def _read_pixel(buffer, x: int, y: int):
    pixel = buffer.read_color(x, y, 1, 1, 3, 0, "FLOAT")
    pixel.dimensions = 3
    return [float(v) for v in pixel]


def _view3d_find(context):
    for area in context.window.screen.areas:
        if area.type != "VIEW_3D":
            continue
        space = area.spaces.active
        if space is None or space.type != "VIEW_3D":
            continue
        rv3d = space.region_3d
        for region in area.regions:
            if region.type == "WINDOW":
                return region, rv3d, space
    return None, None, None


def _view3d_space(context):
    area = getattr(context, "area", None)
    if area is not None and area.type == "VIEW_3D":
        space = area.spaces.active
        if space is not None and space.type == "VIEW_3D":
            return space
    wm = getattr(context, "window_manager", None)
    if wm is None:
        return None
    for window in wm.windows:
        for area in window.screen.areas:
            if area.type != "VIEW_3D":
                continue
            space = area.spaces.active
            if space is not None and space.type == "VIEW_3D":
                return space
    return None


def _camera_border(scene, region, rv3d):
    obj = scene.camera
    if obj is None or obj.type != "CAMERA":
        return None
    cam = obj.data
    frame = cam.view_frame(scene=scene)
    frame = [obj.matrix_world @ v for v in frame]
    from bpy_extras.view3d_utils import location_3d_to_region_2d

    frame_px = [location_3d_to_region_2d(region, rv3d, v) for v in frame]
    if not all(p is not None for p in frame_px):
        return None
    return frame_px


def _sample_region(width, height, offset_x, offset_y, frame_only, rv3d, scene, region):
    """Return (width, height, offset_x, offset_y) for the metering region."""
    if frame_only:
        if rv3d.view_perspective == "CAMERA" and scene.camera and scene.camera.type == "CAMERA":
            frame_px = _camera_border(scene, region, rv3d)
            if frame_px is not None:
                border_width = int(frame_px[0][0] - frame_px[2][0])
                border_height = int(frame_px[0][1] - frame_px[2][1])
                ox = int(frame_px[2][0])
                oy = int(frame_px[2][1])
                bw = border_width if border_width < width else width
                bh = border_height if border_height < height else height
                return bw, bh, ox, oy
        # No camera frame — use center 60% of the viewport as subject area.
        margin_x = int(width * 0.2)
        margin_y = int(height * 0.2)
        return width - 2 * margin_x, height - 2 * margin_y, offset_x + margin_x, offset_y + margin_y
    return width, height, offset_x, offset_y


def _collect_samples(buffer, width, height, offset_x, offset_y, jitter: int):
    """Sparse grid + dense 5×5 center; optional index jitter reduces moiré."""
    grid = _GRID
    center_min = grid // 2 - 1
    center_max = grid // 2 + 1
    raw_all: list[float] = []
    raw_center: list[float] = []
    step = 1.0 / (grid + 1)

    for i in range(grid):
        for j in range(grid):
            ji = (i + jitter) % grid
            jj = (j + jitter) % grid
            x = int(step * (jj + 1) * width + offset_x)
            y = int(step * (ji + 1) * height + offset_y)
            try:
                rgb = _read_pixel(buffer, x, y)
            except Exception:
                continue
            lum = _rgb_to_luminance(rgb)
            raw_all.append(lum)
            in_center = center_min <= i < center_max and center_min <= j < center_max
            if in_center or (i == grid // 2 and j == grid // 2):
                raw_center.append(lum)

    dense = _CENTER_DENSE
    dense_step = 1.0 / (dense + 1)
    cx0 = offset_x + int(width * 0.25)
    cy0 = offset_y + int(height * 0.25)
    cw = int(width * 0.5)
    ch = int(height * 0.5)
    for i in range(dense):
        for j in range(dense):
            x = int(dense_step * (j + 1) * cw + cx0)
            y = int(dense_step * (i + 1) * ch + cy0)
            try:
                rgb = _read_pixel(buffer, x, y)
            except Exception:
                continue
            lum = _rgb_to_luminance(rgb)
            raw_all.append(lum)
            raw_center.append(lum)

    return raw_all, raw_center


def _feedback_paused(scene_name: str, avg_lum: float, current_ev: float, target_ev: float) -> bool:
    state = _FEEDBACK.setdefault(scene_name, {})
    pause = int(state.get("pause", 0))
    if pause > 0:
        state["pause"] = pause - 1
        return True

    last_lum = state.get("last_lum")
    last_ev = state.get("last_ev")
    last_target = state.get("target_ev")
    if last_target is not None and abs(target_ev - last_target) < 0.04 and abs(target_ev - current_ev) < 0.06:
        state["osc"] = 0
        state["last_lum"] = avg_lum
        state["last_ev"] = current_ev
        state["target_ev"] = target_ev
        return True

    if last_lum is not None and last_ev is not None:
        lum_delta = avg_lum - last_lum
        ev_delta = current_ev - last_ev
        if abs(ev_delta) > 0.01 and abs(lum_delta) > 1e-5:
            opposed = (ev_delta > 0 and lum_delta < -1e-5) or (ev_delta < 0 and lum_delta > 1e-5)
            if opposed:
                state["osc"] = int(state.get("osc", 0)) + 1
            else:
                state["osc"] = 0
            if state.get("osc", 0) >= _FEEDBACK_OSC_LIMIT:
                state["pause"] = _FEEDBACK_PAUSE
                state["osc"] = 0
                return True

    state["last_lum"] = avg_lum
    state["last_ev"] = current_ev
    state["target_ev"] = target_ev
    return False


def _engine_is_cycles(context, space) -> bool:
    if space is None or space.shading.type != "RENDERED":
        return False
    scene = getattr(context, "scene", None)
    if scene is None:
        return False
    engine = getattr(scene.render, "engine", "")
    return "CYCLES" in engine


def _light_timing(is_cycles: bool, err: float) -> tuple[float, float]:
    """Return (min_interval, post_commit) from error magnitude and render engine."""
    if not is_cycles:
        if err > 0.55:
            return 0.20, 0.32
        if err > 0.25:
            return 0.26, 0.42
        return 0.30, 0.50
    if err > 0.85:
        return 0.26, 0.40
    if err > 0.40:
        return 0.32, 0.55
    if err > 0.18:
        return 0.38, 0.68
    return 0.42, 0.82


def _luma_settled(scene_name: str, avg: float, is_cycles: bool) -> bool:
    """Wait until consecutive Cycles viewport samples agree (path trace converged)."""
    if not is_cycles:
        return True
    state = _FEEDBACK.setdefault(scene_name, {})
    prev = state.get("luma_prev")
    state["luma_prev"] = avg
    if prev is None:
        state["luma_stable"] = 0
        return False
    denom = max(prev, avg, 1e-6)
    if abs(avg - prev) / denom <= _CYCLES_LUMA_TOL:
        state["luma_stable"] = int(state.get("luma_stable", 0)) + 1
    else:
        state["luma_stable"] = 0
    return int(state.get("luma_stable", 0)) >= _CYCLES_STABLE_FRAMES


def _deadband_hold(scene_name: str, current_ev: float, target_ev: float, band: float) -> bool:
    """Hysteresis: stay put while target wiggles near a stable EV."""
    state = _FEEDBACK.setdefault(scene_name, {})
    if state.get("stable"):
        anchor = float(state.get("stable_ev", current_ev))
        if abs(target_ev - anchor) <= _RELEASE_BAND:
            return True
        state["stable"] = False
    if abs(target_ev - current_ev) <= band:
        state["stable"] = True
        state["stable_ev"] = current_ev
        return True
    return False


def _meter_for_target(avg: float, scene_name: str, apply_to: str, current_ev: float) -> float:
    """Strip current light gain from samples so target EV is absolute, not self-reinforcing."""
    if apply_to != "LIGHT_RIG":
        return avg
    base = avg / (2.0 ** current_ev) if current_ev else avg
    prev = _LUM_EMA.get(scene_name)
    alpha = _LUM_EMA_ALPHA_LIGHT
    if prev is not None:
        base = _lerp(prev, base, alpha)
    _LUM_EMA[scene_name] = base
    return base


def _light_adapt_ready(scene_name: str, min_interval: float, post_commit: float) -> bool:
    import time
    now = time.monotonic()
    last = _LIGHT_LAST_ADAPT.get(scene_name, 0.0)
    last_commit = _LIGHT_COMMIT_TIME.get(scene_name, 0.0)
    settle = _LIGHT_SETTLE_NEED.get(scene_name, post_commit)
    if last_commit and now - last_commit < settle:
        return False
    if now - last < min_interval:
        return False
    _LIGHT_LAST_ADAPT[scene_name] = now
    return True


def _smooth_target(scene_name: str, target: float, apply_to: str, err: float) -> float:
    if apply_to != "LIGHT_RIG":
        return target
    prev = _TARGET_EMA.get(scene_name)
    if prev is None:
        _TARGET_EMA[scene_name] = target
        return target
    alpha = 0.82 if err > 0.55 else _TARGET_EMA_ALPHA_LIGHT
    smoothed = _lerp(prev, target, alpha)
    _TARGET_EMA[scene_name] = smoothed
    return smoothed


def _adapt_speed(settings, apply_to: str, err: float, is_cycles: bool) -> float:
    speed = float(settings.ae_speed)
    if apply_to == "LIGHT_RIG":
        if err > 0.85:
            cap = 0.62 if is_cycles else 0.55
        elif err > 0.45:
            cap = 0.48 if is_cycles else 0.42
        elif err > 0.20:
            cap = 0.34
        else:
            cap = 0.26
        speed = min(speed, cap)
        if err > 0.85:
            speed = max(speed, 0.42)
        elif err > 0.45:
            speed = max(speed, 0.30)
        else:
            speed *= max(0.22, err / 0.35)
    elif err < 0.15:
        speed *= max(0.25, err / 0.15)
    return speed


def _fast_converge_stop(scene_name: str, settings, current: float, target: float, step: float | None = None) -> bool:
    """When enabled, treat sub-threshold error or step as converged."""
    if not getattr(settings, "ae_fast_converge", False):
        return False
    limit = _FAST_CONVERGE_EV
    err = abs(target - current)
    if err < limit:
        _deadband_hold(scene_name, current, target, limit)
        return True
    if step is not None and abs(step - current) < limit:
        _deadband_hold(scene_name, current, target, limit)
        return True
    return False


def _apply_to_cm(scene, settings, value: float) -> None:
    settings.ae_value = value
    scene.view_settings.exposure = value
    scene.view_settings.gamma = float(settings.ae_gamma)


def _apply_to_lights(context, settings, value: float, err: float = 0.0) -> None:
    import time
    settings.ae_value = value
    from . import lighting
    lighting.live_update(context)
    scene = getattr(context, "scene", None)
    if scene is None:
        return
    is_cycles = _engine_is_cycles(context, _view3d_space(context))
    _, post = _light_timing(is_cycles, err)
    _LIGHT_SETTLE_NEED[scene.name] = post
    _LIGHT_COMMIT_TIME[scene.name] = time.monotonic()
    state = _FEEDBACK.setdefault(scene.name, {})
    state["luma_stable"] = 0
    state.pop("luma_prev", None)


def _commit_exposure(context, scene, settings, value: float, err: float = 0.0) -> None:
    apply_to = getattr(settings, "ae_apply_to", "COLOR_MANAGEMENT")
    if apply_to == "LIGHT_RIG":
        _apply_to_lights(context, settings, value, err)
    else:
        _apply_to_cm(scene, settings, value)


def _adapt_view_exposure():
    global _JITTER
    context = bpy.context
    scene = getattr(context, "scene", None)
    if scene is None:
        return
    settings = getattr(scene, "rolllux", None)
    if settings is None or not settings.auto_exposure:
        return
    from . import lighting
    if lighting.rig_busy():
        return

    area = getattr(context, "area", None)
    if area is None or area.type != "VIEW_3D":
        return
    space = area.spaces.active
    if space is None or space.type != "VIEW_3D":
        return
    if space.shading.type not in _SHADING_LIT:
        return

    is_cycles = _engine_is_cycles(context, space)

    region, rv3d, _space = _view3d_find(context)
    if region is None or rv3d is None:
        return

    try:
        viewport_info = gpu.state.viewport_get()
        width = viewport_info[2]
        height = viewport_info[3]
        buffer = gpu.state.active_framebuffer_get()
        if buffer is None:
            return
    except Exception:
        return

    offset_x = 0
    offset_y = 0
    frame_only = bool(getattr(settings, "ae_frame_only", False))
    if not frame_only and rv3d.view_perspective == "CAMERA" and scene.camera and scene.camera.type == "CAMERA":
        frame_px = _camera_border(scene, region, rv3d)
        if frame_px is not None:
            border_width = int(frame_px[0][0] - frame_px[2][0])
            border_height = int(frame_px[0][1] - frame_px[2][1])
            offset_x = int(frame_px[2][0])
            offset_y = int(frame_px[2][1])
            if border_width < width:
                width = border_width
            if border_height < height:
                height = border_height

    width, height, offset_x, offset_y = _sample_region(
        width, height, offset_x, offset_y, frame_only, rv3d, scene, region,
    )

    apply_to = getattr(settings, "ae_apply_to", "COLOR_MANAGEMENT")
    jitter = 0
    if apply_to != "LIGHT_RIG" and getattr(settings, "ae_sample_jitter", True):
        jitter = _JITTER
        _JITTER = (_JITTER + 1) % 3
    raw_all, raw_center = _collect_samples(buffer, width, height, offset_x, offset_y, jitter)

    all_lums, ok = ae_metering.prepare_samples(raw_all)
    center_lums, _ = ae_metering.prepare_samples(raw_center or raw_all)
    if not ok or not all_lums:
        return

    avg = ae_metering.meter_luminance(
        all_lums, center_lums,
        getattr(settings, "ae_mode", "AVERAGE"),
        float(settings.ae_center_weight),
    )
    if avg <= 0.0:
        return

    current = float(settings.ae_value)
    meter_avg = _meter_for_target(avg, scene.name, apply_to, current)

    target = ae_metering.compute_target_ev(
        meter_avg,
        ae_metering.target_luminance(settings, scene),
        float(getattr(settings, "ae_ev_bias", 0.0)),
    )
    err = abs(target - current)
    target = _smooth_target(scene.name, target, apply_to, err)
    err = abs(target - current)
    if apply_to == "LIGHT_RIG":
        if not _luma_settled(scene.name, avg, is_cycles):
            return
        min_iv, post_iv = _light_timing(is_cycles, err)
        if not _light_adapt_ready(scene.name, min_iv, post_iv):
            return
    if _feedback_paused(scene.name, avg, current, target):
        return
    threshold = _LIGHT_RIG_THRESHOLD if apply_to == "LIGHT_RIG" else _THRESHOLD
    if _deadband_hold(scene.name, current, target, threshold):
        return

    if _fast_converge_stop(scene.name, settings, current, target):
        return

    snap = _SNAP_EV if err <= 0.35 else (0.10 if err > 0.75 else 0.06)
    if err <= snap:
        _commit_exposure(context, scene, settings, target, err)
        return

    speed = _adapt_speed(settings, apply_to, err, is_cycles)
    step = _lerp(current, target, speed)
    if _fast_converge_stop(scene.name, settings, current, target, step):
        return
    _commit_exposure(context, scene, settings, step, err)


def _request_redraws(wm) -> None:
    if wm is None:
        return
    for window in wm.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


def _idle_redraw():
    global _IDLE_TIMER
    if not _any_active():
        _IDLE_TIMER = False
        return None
    _request_redraws(getattr(bpy.context, "window_manager", None))
    return _REDRAW_TICK


def _ensure_idle_timer() -> None:
    global _IDLE_TIMER
    if not _IDLE_TIMER and _any_active():
        _IDLE_TIMER = True
        bpy.app.timers.register(_idle_redraw, first_interval=_REDRAW_TICK)


def _stop_idle_timer() -> None:
    global _IDLE_TIMER
    _IDLE_TIMER = False
    try:
        bpy.app.timers.unregister(_idle_redraw)
    except Exception:
        pass


def on_toggle(settings, context) -> None:
    ctx = context or bpy.context
    scene = getattr(ctx, "scene", None)
    if scene is None:
        return
    wm = getattr(ctx, "window_manager", None)
    apply_to = getattr(settings, "ae_apply_to", "COLOR_MANAGEMENT")
    if settings.auto_exposure:
        if apply_to == "COLOR_MANAGEMENT":
            settings.bk_view_exposure = float(scene.view_settings.exposure)
            settings.bk_view_gamma = float(scene.view_settings.gamma)
            settings.ae_value = 0.0
            scene.view_settings.gamma = float(settings.ae_gamma)
        else:
            settings.ae_value = 0.0
        _clear_ae_state(scene.name)
        _ensure_handler()
        _ensure_idle_timer()
        _request_redraws(wm)
    else:
        if apply_to == "COLOR_MANAGEMENT":
            scene.view_settings.exposure = float(settings.bk_view_exposure)
            scene.view_settings.gamma = float(settings.bk_view_gamma)
        settings.ae_value = 0.0
        _clear_ae_state(scene.name)
        if apply_to == "LIGHT_RIG":
            from . import lighting
            lighting.live_update(ctx)
        _maybe_remove_handler()
        if not _any_active():
            _stop_idle_timer()


def bake_to_render_settings(context) -> bool:
    """Apply current AE value to Color Management and disable AE."""
    from . import properties

    scene = context.scene
    settings = scene.rolllux
    if not settings.auto_exposure:
        return False
    if getattr(settings, "ae_apply_to", "COLOR_MANAGEMENT") != "COLOR_MANAGEMENT":
        return False
    ev = float(settings.ae_value)
    gamma = float(settings.ae_gamma)

    properties._SUSPEND = True
    try:
        settings.auto_exposure = False
    finally:
        properties._SUSPEND = False

    settings.ae_value = 0.0
    _clear_ae_state(scene.name)
    _maybe_remove_handler()
    if not _any_active():
        _stop_idle_timer()

    scene.view_settings.exposure = ev
    scene.view_settings.gamma = gamma
    settings.bk_view_exposure = ev
    settings.bk_view_gamma = gamma
    return True


def bake_to_light_rig(context) -> bool:
    """Bake current AE EV into light intensity and disable AE."""
    from . import properties, lighting

    scene = context.scene
    settings = scene.rolllux
    if not settings.auto_exposure:
        return False
    if getattr(settings, "ae_apply_to", "COLOR_MANAGEMENT") != "LIGHT_RIG":
        return False

    ev = float(settings.ae_value)
    properties._SUSPEND = True
    try:
        if abs(ev) > 1e-6:
            settings.intensity = min(float(settings.intensity) * (2.0 ** ev), 20.0)
        settings.auto_exposure = False
    finally:
        properties._SUSPEND = False

    settings.ae_value = 0.0
    _clear_ae_state(scene.name)
    _maybe_remove_handler()
    if not _any_active():
        _stop_idle_timer()
    lighting.live_update(context)
    return True


def _clear_ae_state(scene_name: str) -> None:
    _FEEDBACK.pop(scene_name, None)
    _TARGET_EMA.pop(scene_name, None)
    _LUM_EMA.pop(scene_name, None)
    _LIGHT_LAST_ADAPT.pop(scene_name, None)
    _LIGHT_COMMIT_TIME.pop(scene_name, None)
    _LIGHT_SETTLE_NEED.pop(scene_name, None)


def apply_auto_exposure(context) -> str | None:
    """Bake AE into render CM or light rig. Returns apply mode id or None on failure."""
    settings = context.scene.rolllux
    apply_to = getattr(settings, "ae_apply_to", "COLOR_MANAGEMENT")
    if apply_to == "LIGHT_RIG":
        return "LIGHT_RIG" if bake_to_light_rig(context) else None
    return "COLOR_MANAGEMENT" if bake_to_render_settings(context) else None


def try_set_rendered_shading(context) -> bool:
    ctx = context or bpy.context
    space = _view3d_space(ctx)
    if space is None:
        return False
    try:
        space.shading.type = _PREFERRED_SHADING
        _request_redraws(getattr(ctx, "window_manager", None))
        return True
    except Exception:
        return False


def _any_active() -> bool:
    try:
        for scene in bpy.data.scenes:
            s = getattr(scene, "rolllux", None)
            if s is not None and s.auto_exposure:
                return True
    except (AttributeError, TypeError):
        pass
    return False


def _ensure_handler() -> None:
    global _HANDLE
    if _HANDLE is not None:
        return
    _HANDLE = bpy.types.SpaceView3D.draw_handler_add(
        _adapt_view_exposure, (), "WINDOW", "PRE_VIEW",
    )


def _maybe_remove_handler() -> None:
    global _HANDLE
    if not _any_active() and _HANDLE is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_HANDLE, "WINDOW")
        _HANDLE = None


def restore_handlers() -> None:
    if _any_active():
        _ensure_handler()
        _ensure_idle_timer()


def register():
    pass


def unregister():
    global _HANDLE
    _stop_idle_timer()
    if _HANDLE is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_HANDLE, "WINDOW")
        except Exception:
            pass
        _HANDLE = None
