"""RollLux viewport auto exposure — Color Management from 3D View sampling."""

from __future__ import annotations

import math

import bpy
import gpu

_MID_GREY = 0.18
_GRID = 10
_THRESHOLD = 0.02
_REDRAW_TICK = 0.12
_SHADING_LIT = frozenset({"MATERIAL", "RENDERED"})
_PREFERRED_SHADING = "RENDERED"

_HANDLE = None
_IDLE_TIMER = False


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


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


def _commit_exposure(scene, settings, value: float) -> None:
    settings.ae_value = value
    scene.view_settings.exposure = value
    scene.view_settings.exposure = value
    scene.view_settings.gamma = float(settings.ae_gamma)


def _adapt_view_exposure():
    context = bpy.context
    scene = getattr(context, "scene", None)
    if scene is None:
        return
    settings = getattr(scene, "rolllux", None)
    if settings is None or not settings.auto_exposure:
        return

    area = getattr(context, "area", None)
    if area is None or area.type != "VIEW_3D":
        return
    space = area.spaces.active
    if space is None or space.type != "VIEW_3D":
        return
    if space.shading.type not in _SHADING_LIT:
        return

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
    if rv3d.view_perspective == "CAMERA" and scene.camera and scene.camera.type == "CAMERA":
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

    grid = _GRID
    center_min = grid // 2 - 1
    center_max = grid // 2 + 1
    values = center = 0.0
    count = center_count = 0
    step = 1.0 / (grid + 1)

    for i in range(grid):
        for j in range(grid):
            x = int(step * (j + 1) * width + offset_x)
            y = int(step * (i + 1) * height + offset_y)
            try:
                rgb = _read_pixel(buffer, x, y)
            except Exception:
                continue
            lum = _rgb_to_luminance(rgb)
            if lum != 0:
                values += lum
                count += 1
            if center_min <= i < center_max and center_min <= j < center_max:
                if lum != 0:
                    center += lum
                    center_count += 1
            if i == grid // 2 and j == grid // 2 and lum != 0:
                center += lum
                center_count += 1

    if count == 0 or center_count == 0:
        return

    full_avg = values / count
    center_avg = center / center_count
    weight = float(settings.ae_center_weight) / 100.0
    avg = _lerp(full_avg, center_avg, weight)

    diff_lum = avg / _MID_GREY
    if diff_lum <= 0:
        return

    target = -math.log2(diff_lum)
    current = float(settings.ae_value)
    if abs(target - current) <= _THRESHOLD:
        return

    speed = float(settings.ae_speed)
    _commit_exposure(scene, settings, _lerp(current, target, speed))


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
    if settings.auto_exposure:
        settings.bk_view_exposure = float(scene.view_settings.exposure)
        settings.bk_view_gamma = float(scene.view_settings.gamma)
        settings.ae_value = 0.0
        scene.view_settings.gamma = float(settings.ae_gamma)
        _ensure_handler()
        _ensure_idle_timer()
        _request_redraws(wm)
    else:
        scene.view_settings.exposure = float(settings.bk_view_exposure)
        scene.view_settings.gamma = float(settings.bk_view_gamma)
        settings.ae_value = 0.0
        _maybe_remove_handler()
        if not _any_active():
            _stop_idle_timer()


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


def _deferred_restore():
    try:
        restore_handlers()
    except Exception:
        pass
    return None


def register():
    bpy.app.timers.register(_deferred_restore, first_interval=0.0)


def unregister():
    global _HANDLE
    _stop_idle_timer()
    if _HANDLE is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_HANDLE, "WINDOW")
        except Exception:
            pass
        _HANDLE = None
