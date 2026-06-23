"""Build / live-update a Blender light rig from an analyzed reference.

Only place that creates scene objects. Engine agnostic: plain Blender lights
light both Cycles and Eevee. Per-light data lives on ``object.rolllux_light`` so
the rig can be tuned globally (sliders) and per-light (panel) and rebuilt
deterministically.
"""

from __future__ import annotations

import math

import bpy
from mathutils import Matrix, Vector

from . import analysis, presets

COLLECTION_NAME = "RollLux"
RIG_NAME = "RollLux_Rig"
WORLD_NAME = "RollLux World"

# Energy at gain=intensity=contrast=1, brightness folded into e0.
_AREA_BASE = 150.0
_SUN_BASE = 4.0

# Distance the _AREA_BASE was tuned at. Energy is compensated by (d / this)^2 so
# sliding "distance" reframes the rig without changing brightness.
_NOMINAL_DISTANCE = 2.5

# Set while generate() seeds per-light data, so the per-light update callbacks
_BUILDING = False


# --------------------------------------------------------------------------- #
# Target & orientation
# --------------------------------------------------------------------------- #
def _is_rolllux(obj):
    return obj is not None and (obj.name == RIG_NAME or obj.name.startswith("RLLX_"))


def _real_active(context):
    obj = context.active_object
    if obj is not None and not _is_rolllux(obj):
        return obj
    for o in context.selected_objects:
        if not _is_rolllux(o):
            return o
    return None


def resolve_target(context, settings):
    if settings.target_mode == "CURSOR":
        return context.scene.cursor.location.copy(), (_selected_radius(context) or 1.0)
    if settings.target_mode == "ORIGIN":
        return Vector((0.0, 0.0, 0.0)), (_selected_radius(context) or 1.0)
    obj = _real_active(context)
    if obj is None:
        if settings.cache_radius > 0.0:
            return Vector(settings.cache_target), settings.cache_radius
        return context.scene.cursor.location.copy(), 1.0
    return _world_aabb(context, obj)


def _world_aabb(context, obj):
    """Center + radius from the object's *visible geometry*, not its origin.

    Uses the evaluated (post-modifier) geometry's world-space axis-aligned
    bounding box, so objects whose origin sits in an odd place — or that rely on
    Mirror/Array/etc. modifiers — still get aimed at correctly.
    """
    ob = obj
    try:
        ob = obj.evaluated_get(context.evaluated_depsgraph_get())
    except Exception:
        pass
    try:
        mw = ob.matrix_world
        corners = [mw @ Vector(c) for c in ob.bound_box]
    except Exception:
        corners = []
    if not corners:
        return obj.matrix_world.translation.copy(), 1.0
    xs = [c.x for c in corners]
    ys = [c.y for c in corners]
    zs = [c.z for c in corners]
    mn = Vector((min(xs), min(ys), min(zs)))
    mx = Vector((max(xs), max(ys), max(zs)))
    center = (mn + mx) * 0.5
    radius = max((mx - mn)) * 0.5
    if radius < 1e-4:
        return obj.matrix_world.translation.copy(), 1.0
    return center, radius


def _selected_radius(context):
    obj = _real_active(context)
    if obj is None:
        return None
    _, radius = _world_aabb(context, obj)
    return radius if radius > 1e-4 else None


def resolve_basis(context, settings):
    cam = context.scene.camera
    if settings.orient_mode == "CAMERA" and cam is not None:
        m = cam.matrix_world.to_3x3()
        right = (m @ Vector((1.0, 0.0, 0.0))).normalized()
        up = (m @ Vector((0.0, 1.0, 0.0))).normalized()
        back = (m @ Vector((0.0, 0.0, 1.0))).normalized()
        return right, up, back
    return Vector((1.0, 0.0, 0.0)), Vector((0.0, 0.0, 1.0)), Vector((0.0, -1.0, 0.0))


# --------------------------------------------------------------------------- #
# Collection / cleanup
# --------------------------------------------------------------------------- #
def get_collection(context):
    coll = bpy.data.collections.get(COLLECTION_NAME)
    if coll is None:
        coll = bpy.data.collections.new(COLLECTION_NAME)
        context.scene.collection.children.link(coll)
    elif coll.name not in context.scene.collection.children:
        try:
            context.scene.collection.children.link(coll)
        except RuntimeError:
            pass
    return coll


def get_controller(context, create=False, target=None):
    coll = bpy.data.collections.get(COLLECTION_NAME)
    if coll is not None:
        ctrl = coll.objects.get(RIG_NAME)
        if ctrl is not None:
            return ctrl
    if not create:
        return None
    coll = get_collection(context)
    ctrl = bpy.data.objects.new(RIG_NAME, None)
    ctrl.empty_display_type = "SPHERE"
    ctrl.location = target or Vector((0, 0, 0))
    coll.objects.link(ctrl)
    return ctrl


def has_rig():
    coll = bpy.data.collections.get(COLLECTION_NAME)
    return bool(coll and any(o.type == "LIGHT" for o in coll.objects))


def list_lights():
    coll = bpy.data.collections.get(COLLECTION_NAME)
    if coll is None:
        return []
    lights = [o for o in coll.objects if o.type == "LIGHT" and o.rolllux_light.is_rllx]
    priority = {"key": 0, "accent": 1, "fill": 1, "rim": 2, "sky": 3, "extra": 4}
    lights.sort(key=lambda o: priority.get(o.rolllux_light.role, 5))
    return lights


def capture_colors_to_result(scene):
    """Copy current rig light colors into ``rolllux_result.sampled_colors``."""
    res = scene.rolllux_result
    colors = [tuple(o.rolllux_light.base_color) for o in list_lights()]
    if not colors:
        return
    res.sampled_colors.clear()
    for color in colors:
        item = res.sampled_colors.add()
        item.color = color
    res.valid = True


def _locked_palette(scene):
    """Palette to keep when ``lock_light_colors`` is enabled."""
    s = scene.rolllux
    if not s.lock_light_colors:
        return None
    res = scene.rolllux_result
    if res.valid and res.sampled_colors:
        return [tuple(item.color) for item in res.sampled_colors]
    colors = [tuple(o.rolllux_light.base_color) for o in list_lights()]
    return colors or None


def clear_previous(context):
    restore_environment(context)
    coll = bpy.data.collections.get(COLLECTION_NAME)
    if coll is None:
        return 0
    count = 0
    for obj in list(coll.objects):
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        count += 1
        if isinstance(data, bpy.types.Light) and data.users == 0:
            bpy.data.lights.remove(data)
    return count


def _get_bg_node(world):
    if not world or not world.use_nodes:
        return None
    bg = world.node_tree.nodes.get("Background")
    if bg is not None:
        return bg
    for n in world.node_tree.nodes:
        if n.type == "BACKGROUND":
            return n
    return None


def restore_environment(context):
    scene = context.scene
    s = scene.rolllux
    if s.bk_world_touched:
        if s.bk_world_created:
            created = scene.world
            prev = bpy.data.worlds.get(s.bk_prev_world) if s.bk_prev_world else None
            scene.world = prev
            if created is not None and created is not prev and created.users == 0:
                bpy.data.worlds.remove(created)
        else:
            bg = _get_bg_node(scene.world)
            if bg is not None:
                bg.inputs[0].default_value = tuple(s.bk_bg_color)
                bg.inputs[1].default_value = s.bk_bg_strength
        s.bk_world_touched = False
        s.bk_world_created = False
        s.bk_prev_world = ""


# --------------------------------------------------------------------------- #
# Per-light apply
# --------------------------------------------------------------------------- #
_LUMA = (0.2126, 0.7152, 0.0722)
_HIGHLIGHT_ROLES = frozenset({"key", "rim", "accent"})


def _grade_color(color, strength, saturation=1.0):
    """Tint toward white (strength 0..1), overshoot chroma (>1), then saturation."""
    r, g, b = (float(color[0]), float(color[1]), float(color[2]))
    blend = min(max(float(strength), 0.0), 1.0)
    tinted = (
        1.0 * (1.0 - blend) + r * blend,
        1.0 * (1.0 - blend) + g * blend,
        1.0 * (1.0 - blend) + b * blend,
    )
    overshoot = max(float(strength) - 1.0, 0.0)
    if overshoot > 0.0:
        lum = sum(_LUMA[i] * tinted[i] for i in range(3))
        boost = 1.0 + overshoot
        tinted = tuple(lum + (c - lum) * boost for c in tinted)
    sat = float(saturation)
    if abs(sat - 1.0) > 1e-4:
        lum = sum(_LUMA[i] * tinted[i] for i in range(3))
        tinted = tuple(lum + (c - lum) * sat for c in tinted)
    return tuple(max(0.0, c) for c in tinted)


def _aim(direction):
    if direction.length < 1e-6:
        direction = Vector((0.0, 0.0, -1.0))
    return direction.to_track_quat("-Z", "Y").to_euler()


def _reference_brightness(mean_lum: float) -> float:
    """Scale analyzed spec energy from reference mean luminance (conservative)."""
    return max(0.45, min(0.45 + float(mean_lum) * 0.45, 1.05))


def _world_strength(mean_lum: float, split_score: float = 0.0,
                    shadow_frac: float = 0.0) -> float:
    """Background strength before Intensity / Exposure (kept low to avoid blow-out)."""
    base = max(0.015, min(0.04 + float(mean_lum) * 0.35, 0.55))
    crush = 1.0 - float(split_score) * 0.82 - float(shadow_frac) * 0.38
    return base * max(0.04, crush)


def _exposure_factor(exp: int) -> float:
    """Signed integer exposure: 1 = neutral, >1 brighter, <0 darker (2^exp)."""
    exp = int(exp)
    if exp >= 1:
        return float(exp)
    if exp == 0:
        return 1.0
    return 2.0 ** float(exp)


def _energy_scale(settings) -> float:
    scale = float(settings.intensity) * _exposure_factor(int(settings.exposure)) * 3.0
    if settings.auto_exposure and getattr(settings, "ae_apply_to", "COLOR_MANAGEMENT") == "LIGHT_RIG":
        scale *= 2.0 ** float(settings.ae_value)
    return scale


def _apply_light(obj, settings, target, radius, basis):
    info = obj.rolllux_light
    right, up, back = basis
    dx, dy, dz = info.direction
    world_dir = (right * dx) + (up * dy) + (back * dz)
    if world_dir.length < 1e-6:
        world_dir = back.copy()
    world_dir.normalize()
    dist = settings.distance * radius
    pos = target + world_dir * dist

    # Local (basis) transform; controller rotation provides the orbit.
    obj.location = pos
    obj.rotation_euler = _aim(target - pos)

    ld = obj.data
    energy = _energy_scale(settings) * info.e0 * info.gain
    if info.is_sun and ld.type == "SUN":
        ld.energy = energy * _SUN_BASE
        ld.angle = max(0.0017, info.softness * 0.06)
    else:
        # Compensate inverse-square falloff so distance reframes without
        # changing brightness.
        dist_comp = (settings.distance / _NOMINAL_DISTANCE) ** 2
        e = energy * _AREA_BASE * dist_comp
        if info.role in _HIGHLIGHT_ROLES:
            boost = float(settings.contrast_boost)
            split = float(getattr(settings, "cache_split_score", 0.0))
            key_pow = 0.85 if split > 0.38 else 0.70
            key_pow = key_pow if info.role == "key" else 0.55
            e *= boost ** key_pow * float(settings.tone_highlights)
        else:
            e /= settings.contrast_boost
            e *= float(settings.tone_shadows)
        ld.energy = e

    if ld.type == "AREA":
        ld.shape = "SQUARE"
        ld.size = max(0.05, radius * info.softness)
    elif ld.type == "SPOT":
        tight = info.softness < 0.38
        if info.role == "key":
            ld.spot_size = math.radians(26.0 if tight else 38.0)
            ld.spot_blend = min(0.28, max(0.02, info.softness * 0.22))
        else:
            ld.spot_size = math.radians(55.0)
            ld.spot_blend = min(1.0, max(0.1, info.softness))
        ld.shadow_soft_size = max(0.005, radius * (0.08 if tight else 0.25) * info.softness)
    elif ld.type == "POINT":
        ld.shadow_soft_size = max(0.05, radius * info.softness)

    ld.color = _grade_color(
        tuple(info.base_color), settings.color_strength, settings.color_saturation,
    )[:3]
    obj.hide_viewport = not info.enabled
    obj.hide_render = not info.enabled


def set_rig_rotation(context):
    ctrl = get_controller(context)
    if ctrl is not None:
        # rig_rotation is an ANGLE property (stored in radians).
        ctrl.rotation_euler = (0.0, 0.0, context.scene.rolllux.rig_rotation)


def set_rig_height(context):
    """Slide the whole rig up/down along world Z relative to the cached target."""
    ctrl = get_controller(context)
    if ctrl is not None:
        s = context.scene.rolllux
        ctrl.location.z = s.cache_target[2] + s.rig_height


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def generate(context, profile, settings, specs=None):
    global _BUILDING
    if specs is None:
        specs = profile.specs

    prev_active = context.view_layer.objects.active
    prev_selected = list(context.selected_objects)

    target, radius = resolve_target(context, settings)
    clear_previous(context)
    settings.cache_target = target
    settings.cache_radius = radius

    basis = resolve_basis(context, settings)
    coll = get_collection(context)
    brightness = _reference_brightness(profile.mean_luminance)

    controller = bpy.data.objects.new(RIG_NAME, None)
    controller.empty_display_type = "SPHERE"
    controller.empty_display_size = radius * 0.4
    controller.location = target + Vector((0.0, 0.0, settings.rig_height))
    controller.rotation_euler = (0.0, 0.0, settings.rig_rotation)
    coll.objects.link(controller)
    inv = Matrix.Translation(-target)

    created = []
    _BUILDING = True
    try:
        for spec in specs:
            ld = bpy.data.lights.new(name=f"RLLX_{spec.role}", type=spec.light_type)
            obj = bpy.data.objects.new(f"RLLX_{spec.role}", ld)
            info = obj.rolllux_light
            info.is_rllx = True
            info.role = spec.role
            info.direction = spec.direction
            info.e0 = spec.energy * brightness
            info.softness = spec.size
            info.is_sun = spec.light_type == "SUN"
            info.base_color = spec.color
            info.gain = 1.0
            info.enabled = True

            coll.objects.link(obj)
            obj.parent = controller
            obj.matrix_parent_inverse = inv
            _apply_light(obj, settings, target, radius, basis)
            created.append(obj)
    finally:
        _BUILDING = False

    if settings.use_world:
        _apply_world_values(
            context, settings.cache_ambient, settings.cache_mean_lum, settings,
        )

    # Keep the user's original active object so the next generate just works.
    if prev_active is not None and prev_active.name in context.view_layer.objects:
        for o in context.selected_objects:
            o.select_set(False)
        for o in prev_selected:
            if o.name in context.view_layer.objects:
                o.select_set(True)
        context.view_layer.objects.active = prev_active

    return {"lights": len(created), "target": tuple(round(c, 3) for c in target),
            "radius": round(radius, 3)}


def live_update(context):
    if _BUILDING:
        return
    coll = bpy.data.collections.get(COLLECTION_NAME)
    if coll is None:
        return
    settings = context.scene.rolllux
    if settings.cache_radius > 0.0:
        target = Vector(settings.cache_target)
        radius = settings.cache_radius
    else:
        target, radius = resolve_target(context, settings)
    basis = resolve_basis(context, settings)
    for obj in coll.objects:
        if obj.type == "LIGHT" and obj.rolllux_light.is_rllx:
            _apply_light(obj, settings, target, radius, basis)
    if settings.use_world:
        _apply_world_values(
            context, settings.cache_ambient, settings.cache_mean_lum, settings,
        )
    elif settings.bk_world_touched:
        restore_environment(context)


# --------------------------------------------------------------------------- #
# Delete lights
# --------------------------------------------------------------------------- #
def delete_light(context, name):
    coll = bpy.data.collections.get(COLLECTION_NAME)
    if coll is None:
        return False
    obj = coll.objects.get(name)
    if obj is None or not obj.rolllux_light.is_rllx:
        return False
    data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if isinstance(data, bpy.types.Light) and data.users == 0:
        bpy.data.lights.remove(data)
    return True


# --------------------------------------------------------------------------- #
# Analyze helpers (image -> profile -> store / build)
# --------------------------------------------------------------------------- #
def store_result(scene, profile):
    s = scene.rolllux
    res = scene.rolllux_result
    count = max(1, int(s.light_count))
    res.valid = True
    res.key_color = profile.key_color
    res.fill_color = profile.fill_color
    res.ambient_color = tuple(min(c, 1.0) for c in profile.ambient_color)
    preserved = None
    if s.lock_light_colors and res.sampled_colors:
        preserved = [tuple(item.color) for item in res.sampled_colors]
    res.sampled_colors.clear()
    rig_colors = analysis.rig_colors_in_order(profile, count)
    if preserved:
        for i in range(count):
            item = res.sampled_colors.add()
            if i < len(preserved):
                item.color = preserved[i]
            elif preserved:
                item.color = preserved[-1]
            else:
                item.color = rig_colors[i] if i < len(rig_colors) else profile.key_color
    else:
        for i in range(count):
            item = res.sampled_colors.add()
            item.color = rig_colors[i] if i < len(rig_colors) else profile.key_color
    res.mean_luminance = profile.mean_luminance
    res.contrast_ratio = profile.contrast_ratio
    res.color_temperature = profile.color_temperature
    res.warmth = profile.warmth
    res.mood = profile.mood
    res.resolved_mode = analysis._resolve_mode(profile, s.mode)
    res.key_pos_x, res.key_pos_y = profile.key_screen_pos
    res.dir_label = profile.dir_label
    res.dir_confidence = profile.dir_confidence
    res.backlit = profile.backlit
    s.cache_ambient = tuple(min(c, 4.0) for c in profile.ambient_color)[:3]
    s.cache_mean_lum = profile.mean_luminance
    s.cache_split_score = float(profile.split_score)
    s.cache_hardness = float(profile.hardness)
    s.cache_shadow_frac = float(profile.shadow_frac)
    if not s.lock_contrast_boost:
        s.contrast_boost = float(profile.suggested_contrast_boost)
    if not s.lock_tone_shadows:
        s.tone_shadows = float(profile.suggested_tone_shadows)


def _profile_from_settings(context):
    s = context.scene.rolllux
    img = s.reference_image
    if img is None:
        return None, "no_image"
    try:
        rgb = analysis.image_to_rgb(img)
        profile = analysis.analyze_rgb(
            rgb, mode=s.mode, luxpro=s.use_luxpro,
            palette_size=s.light_count, color_strategy=s.color_strategy,
        )
    except Exception as exc:
        return None, str(exc)
    store_result(context.scene, profile)
    return profile, None


_REGEN_PENDING: set[str] = set()
_RIG_BUSY = False


def rig_busy() -> bool:
    return _RIG_BUSY


def analyze_only(context):
    global _RIG_BUSY
    if _RIG_BUSY:
        schedule_analyze_only(context)
        return None, "busy"
    _RIG_BUSY = True
    try:
        return _profile_from_settings(context)
    finally:
        _RIG_BUSY = False


def analyze_and_generate(context):
    global _RIG_BUSY
    if _RIG_BUSY:
        schedule_analyze_and_generate(context)
        return None, "busy"
    _RIG_BUSY = True
    try:
        profile, err = _profile_from_settings(context)
        if err:
            return None, err
        s = context.scene.rolllux
        specs = presets.apply_preset(profile, s.lighting_preset, s.mode)
        specs = presets.fit_to_count(
            specs, s.light_count, profile, s.color_strategy,
            locked_colors=_locked_palette(context.scene),
        )
        summary = generate(context, profile, s, specs=specs)
        return summary, None
    finally:
        _RIG_BUSY = False


def schedule_analyze_and_generate(context):
    """Defer rig rebuild to the next main-loop tick (safe during UI draw / render)."""
    if context is None or getattr(context, "scene", None) is None:
        return
    name = context.scene.name
    if name in _REGEN_PENDING:
        return
    _REGEN_PENDING.add(name)

    def _fn():
        _REGEN_PENDING.discard(name)
        try:
            ctx = bpy.context
            if ctx is None or getattr(ctx, "scene", None) is None:
                return None
            if ctx.scene.name != name:
                return None
            if ctx.scene.rolllux.reference_image is None:
                return None
            if _RIG_BUSY:
                schedule_analyze_and_generate(ctx)
                return None
            analyze_and_generate(ctx)
        except Exception:
            pass
        return None

    if getattr(bpy.app, "background", False):
        _REGEN_PENDING.discard(name)
        try:
            if not _RIG_BUSY:
                analyze_and_generate(context)
            else:
                schedule_analyze_and_generate(context)
        except Exception:
            pass
        return

    bpy.app.timers.register(_fn, first_interval=0.0)


def schedule_analyze_only(context):
    """Defer reference analysis to the next main-loop tick (safe during UI draw)."""
    if context is None or getattr(context, "scene", None) is None:
        return
    name = context.scene.name
    if name in _REGEN_PENDING:
        return
    _REGEN_PENDING.add(name)

    def _fn():
        _REGEN_PENDING.discard(name)
        try:
            ctx = bpy.context
            if ctx is None or getattr(ctx, "scene", None) is None:
                return None
            if ctx.scene.name != name:
                return None
            if ctx.scene.rolllux.reference_image is None:
                return None
            if _RIG_BUSY:
                schedule_analyze_only(ctx)
                return None
            analyze_only(ctx)
        except Exception:
            pass
        return None

    if getattr(bpy.app, "background", False):
        _REGEN_PENDING.discard(name)
        try:
            if not _RIG_BUSY:
                analyze_only(context)
            else:
                schedule_analyze_only(context)
        except Exception:
            pass
        return

    bpy.app.timers.register(_fn, first_interval=0.0)


# --------------------------------------------------------------------------- #
# World
# --------------------------------------------------------------------------- #
def _apply_world_values(context, ambient, mean_lum, settings):
    scene = context.scene
    prev_world = scene.world
    created = prev_world is None
    world = prev_world
    if world is None:
        world = bpy.data.worlds.new(WORLD_NAME)
        scene.world = world
    world.use_nodes = True
    bg = _get_bg_node(world)
    if bg is None:
        return
    if not settings.bk_world_touched:
        settings.bk_world_created = created
        settings.bk_prev_world = prev_world.name if prev_world else ""
        col = bg.inputs[0].default_value
        settings.bk_bg_color = (col[0], col[1], col[2], col[3])
        settings.bk_bg_strength = bg.inputs[1].default_value
        settings.bk_world_touched = True
    amb = _grade_color(
        tuple(ambient), settings.color_strength, settings.color_saturation,
    )
    bg.inputs[0].default_value = (amb[0], amb[1], amb[2], 1.0)
    strength = _world_strength(
        mean_lum,
        getattr(settings, "cache_split_score", 0.0),
        getattr(settings, "cache_shadow_frac", 0.0),
    ) * float(settings.tone_shadows)
    bg.inputs[1].default_value = strength * _energy_scale(settings)
