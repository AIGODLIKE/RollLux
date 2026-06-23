"""Scene + object settings, presets wiring, live-update callbacks, language
sync, and a read-only store for the last analysis."""

import os

import bpy
from bpy.app.handlers import persistent
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

from . import translations, presets, overlay, auto_exposure

_d = translations.rna_desc

# Guards to keep update callbacks from recursing / fighting each other.
_SUSPEND = False        # while a preset seeds the sliders before a rebuild
_REFERENCE_BUSY = False # while ensure_default_reference loads a built-in image
_DEFAULT_SCHEDULED: set[str] = set()  # scene names with a pending default load
_GENERATE_SCHEDULED: set[str] = set()  # scene names with a pending custom-load generate


def _on_auto_exposure(self, context):
    if _SUSPEND:
        return
    auto_exposure.on_toggle(self, context or bpy.context)


def _on_ae_gamma(self, context):
    if _SUSPEND:
        return
    if not self.auto_exposure:
        return
    if getattr(self, "ae_apply_to", "COLOR_MANAGEMENT") != "COLOR_MANAGEMENT":
        return
    scene = getattr(context or bpy.context, "scene", None)
    if scene is not None:
        scene.view_settings.gamma = float(self.ae_gamma)


_AE_CENTER_PRESETS = {
    "FULL": (0, False),
    "BALANCED": (70, False),
    "CENTER": (100, False),
    "FRAME": (100, True),
}


def _on_ae_center_preset(self, context):
    global _SUSPEND
    if _SUSPEND:
        return
    if self.ae_center_preset == "CUSTOM":
        return
    weight, frame_only = _AE_CENTER_PRESETS[self.ae_center_preset]
    _SUSPEND = True
    try:
        self.ae_center_weight = weight
        self.ae_frame_only = frame_only
    finally:
        _SUSPEND = False


def _on_ae_center_weight(self, context):
    if _SUSPEND:
        return
    self.ae_center_preset = "CUSTOM"


def _live(self, context):
    if _SUSPEND:
        return
    from . import lighting
    lighting.live_update(context)


def _on_rebuild(self, context):
    """Re-analyze and rebuild the rig (mode / light count / similar)."""
    if _SUSPEND:
        return
    from . import lighting
    if lighting.has_rig():
        lighting.schedule_analyze_and_generate(context)
    elif context is not None:
        lighting.analyze_only(context)


def _rotate(self, context):
    from . import lighting
    lighting.set_rig_rotation(context)
    overlay.tag_redraw()


def _height(self, context):
    from . import lighting
    lighting.set_rig_height(context)
    overlay.tag_redraw()


def _light_edit(self, context):
    from . import lighting
    lighting.live_update(context)


def _on_lock_light_colors(self, context):
    if not self.lock_light_colors or context is None:
        return
    from . import lighting
    if lighting.has_rig():
        lighting.capture_colors_to_result(context.scene)


def _on_reference_image(self, context):
    """Track when the user clears or manually picks a reference image."""
    global _REFERENCE_BUSY
    if _REFERENCE_BUSY:
        return
    if self.reference_image is None:
        self.reference_user_cleared = True
        self.reference_is_custom = False
    else:
        self.reference_user_cleared = False
        self.reference_is_custom = True
        if self.reference_preset != presets.CUSTOM_REFERENCE:
            _REFERENCE_BUSY = True
            try:
                self.reference_preset = presets.CUSTOM_REFERENCE
            finally:
                _REFERENCE_BUSY = False
        if context is not None:
            schedule_generate_after_custom_load(context.scene, context)
    overlay.tag_redraw()


def _reference_missing(settings) -> bool:
    img = settings.reference_image
    return (
        settings.reference_user_cleared
        or img is None
        or img.size[0] == 0
        or img.size[1] == 0
    )


def load_random_reference(context) -> bool:
    """Generate and load a random lighting-distribution reference image."""
    global _REFERENCE_BUSY
    s = context.scene.rolllux
    path = presets.randomize_reference(s.distribution_color_mode)
    try:
        img = bpy.data.images.load(path, check_existing=False)
        img.pack()
    except (RuntimeError, OSError):
        return False
    img.name = "RollLux_Random"
    for other in list(bpy.data.images):
        if other != img and other.name.startswith("RollLux_Random"):
            try:
                bpy.data.images.remove(other)
            except (ReferenceError, RuntimeError):
                pass
    _REFERENCE_BUSY = True
    try:
        s.reference_image = img
        s.reference_user_cleared = False
        s.reference_is_custom = False
        if s.reference_preset != "random":
            try:
                s["reference_preset"] = 0
            except Exception:
                s.reference_preset = "random"
    finally:
        _REFERENCE_BUSY = False
    overlay.tag_redraw()
    return True


def schedule_generate_after_custom_load(scene=None, context=None):
    """Defer ``analyze_and_generate`` after a manual reference pick (RNA-safe)."""
    sc = scene or getattr(context, "scene", None)
    if sc is None:
        return
    name = sc.name
    if name in _GENERATE_SCHEDULED:
        return
    _GENERATE_SCHEDULED.add(name)
    ctx = context

    def _run():
        _GENERATE_SCHEDULED.discard(name)
        try:
            c = ctx or bpy.context
            target = bpy.data.scenes.get(name)
            if target is None:
                return None
            s = target.rolllux
            if not s.reference_is_custom or s.reference_image is None:
                return None
            from . import lighting
            lighting.analyze_and_generate(c)
        except Exception:
            pass
        return None

    bpy.app.timers.register(_run, first_interval=0.0)


def _load_reference_image(settings, rid, context=None):
    """Load a built-in reference PNG into ``settings.reference_image``."""
    global _REFERENCE_BUSY
    path = presets.reference_path(rid)
    if not os.path.isfile(path):
        return False
    try:
        img = bpy.data.images.load(path, check_existing=True)
    except (RuntimeError, FileNotFoundError, OSError):
        return False
    _REFERENCE_BUSY = True
    try:
        settings.reference_image = img
        settings.reference_user_cleared = False
        settings.reference_is_custom = False
    finally:
        _REFERENCE_BUSY = False
    return True


def _on_reference(self, context):
    if _REFERENCE_BUSY:
        return
    if self.reference_preset == presets.CUSTOM_REFERENCE:
        self.reference_is_custom = True
        overlay.tag_redraw()
        return
    from . import lighting
    if not _load_reference_image(self, self.reference_preset, context):
        return
    if lighting.has_rig():
        lighting.schedule_analyze_and_generate(context)
    else:
        lighting.schedule_analyze_only(context)
    overlay.tag_redraw()


def _on_preset(self, context):
    global _SUSPEND
    from . import lighting
    _SUSPEND = True
    try:
        presets.apply_defaults(self, self.lighting_preset)
    finally:
        _SUSPEND = False
    if self.reference_image is not None:
        lighting.schedule_analyze_and_generate(context)


# --------------------------------------------------------------------------- #
# Per-light data (attached to each generated light object)
# --------------------------------------------------------------------------- #
class RLLM_LightInfo(PropertyGroup):
    is_rllx: BoolProperty(default=False)
    role: StringProperty(default="")
    direction: FloatVectorProperty(size=3, default=(0.0, 0.0, 1.0))
    e0: FloatProperty(default=1.0)
    size0: FloatProperty(default=1.0)
    is_sun: BoolProperty(default=False)
    base_color: FloatVectorProperty(
        name="Color", subtype="COLOR", size=3, min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0), update=_light_edit,
    )
    gain: FloatProperty(
        name="Energy", default=1.0, min=0.0, max=10.0, soft_max=4.0,
        update=_light_edit,
    )
    softness: FloatProperty(
        name="Softness", default=1.0, min=0.05, max=10.0, soft_max=4.0,
        update=_light_edit,
    )
    enabled: BoolProperty(name="On", default=True, update=_light_edit)


class RLLM_SampledColor(PropertyGroup):
    color: FloatVectorProperty(
        name="Color", subtype="COLOR", size=3, min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0),
    )


class RLLM_AnalysisResult(PropertyGroup):
    valid: BoolProperty(default=False)
    key_color: FloatVectorProperty(subtype="COLOR", size=3, min=0.0, max=1.0,
                                    default=(1.0, 1.0, 1.0))
    fill_color: FloatVectorProperty(subtype="COLOR", size=3, min=0.0, max=1.0,
                                    default=(0.5, 0.5, 0.55))
    ambient_color: FloatVectorProperty(subtype="COLOR", size=3, min=0.0, max=1.0,
                                       default=(0.05, 0.05, 0.06))
    sampled_colors: CollectionProperty(type=RLLM_SampledColor)
    mean_luminance: FloatProperty(default=0.0)
    contrast_ratio: FloatProperty(default=0.0)
    color_temperature: FloatProperty(default=5500.0)
    warmth: FloatProperty(default=0.5)
    mood: StringProperty(default="")
    resolved_mode: StringProperty(default="")
    key_pos_x: FloatProperty(default=0.0)
    key_pos_y: FloatProperty(default=0.0)
    dir_label: StringProperty(default="")
    dir_confidence: FloatProperty(default=0.0)
    backlit: BoolProperty(default=False)


class RLLM_Settings(PropertyGroup):
    ui_mode: EnumProperty(
        name="UI Mode", description=_d("ui_mode"),
        items=translations.ui_mode_items,
        default=0,
    )
    mcp_port: IntProperty(
        name="MCP Port", default=9886, min=1024, max=65535,
        description=_d("mcp_port"),
    )
    mcp_auto_connect: BoolProperty(
        name="MCP Auto Connect", default=True,
        description=_d("mcp_auto_connect"),
    )
    mcp_connected: BoolProperty(
        name="MCP Connected", default=False, options={"HIDDEN"},
    )
    reference_user_cleared: BoolProperty(default=False, options={"HIDDEN"})
    reference_is_custom: BoolProperty(default=False, options={"HIDDEN"})

    reference_image: PointerProperty(
        name="Reference", type=bpy.types.Image,
        description=_d("reference_image"),
        update=_on_reference_image,
    )

    lighting_preset: EnumProperty(
        name="Lighting Preset", description="",
        items=presets.preset_items, update=_on_preset,
    )
    reference_preset: EnumProperty(
        name="Reference Library", description="",
        items=presets.reference_items,
        default=presets.REFERENCE_ORDER.index(presets.DEFAULT_REFERENCE),
        update=_on_reference,
    )

    # Enum item names/descriptions come from dynamic i18n callbacks — leave the
    # property-level description empty so tooltips do not show English prefixes.
    mode: EnumProperty(name="Mode", items=translations.mode_items,
                       description="", update=_on_rebuild)
    target_mode: EnumProperty(name="Aim At", items=translations.target_items, description="")
    orient_mode: EnumProperty(name="Orient By", items=translations.orient_items, description="")

    use_luxpro: BoolProperty(
        name="LuxPro", default=True,
        description=_d("use_luxpro"),
    )

    light_count: IntProperty(
        name="Light Count", default=3, min=1, max=8,
        description=_d("light_count"),
        update=_on_rebuild,
    )

    color_strategy: EnumProperty(
        name="Color Strategy", description="",
        items=translations.color_strategy_items,
        default=0,
        update=_on_rebuild,
    )

    distribution_color_mode: EnumProperty(
        name="Distribution Color", description="",
        items=translations.distribution_color_mode_items,
        default=0,
    )

    live: BoolProperty(name="Live", default=True, options={"HIDDEN"})

    lock_intensity: BoolProperty(
        name="Lock Intensity", default=False,
        description=_d("lock_intensity"),
    )
    lock_exposure: BoolProperty(
        name="Lock Exposure", default=False,
        description=_d("lock_exposure"),
    )
    lock_distance: BoolProperty(
        name="Lock Distance", default=False,
        description=_d("lock_distance"),
    )
    lock_rig_rotation: BoolProperty(
        name="Lock Rotation", default=False,
        description=_d("lock_rig_rotation"),
    )
    lock_rig_height: BoolProperty(
        name="Lock Height", default=False,
        description=_d("lock_rig_height"),
    )
    lock_color_strength: BoolProperty(
        name="Lock Color Strength", default=False,
        description=_d("lock_color_strength"),
    )
    lock_color_saturation: BoolProperty(
        name="Lock Saturation", default=False,
        description=_d("lock_color_saturation"),
    )
    lock_tone_shadows: BoolProperty(
        name="Lock Shadows", default=False,
        description=_d("lock_tone_shadows"),
    )
    lock_tone_highlights: BoolProperty(
        name="Lock Highlights", default=False,
        description=_d("lock_tone_highlights"),
    )
    lock_contrast_boost: BoolProperty(
        name="Lock Contrast", default=False,
        description=_d("lock_contrast_boost"),
    )
    lock_light_colors: BoolProperty(
        name="Lock Light Colors", default=False,
        description=_d("lock_light_colors"),
        update=_on_lock_light_colors,
    )

    intensity: FloatProperty(name="Intensity", default=0.2, min=0.0, max=20.0,
                             soft_max=5.0, update=_live,
                             description=_d("intensity"))
    exposure: IntProperty(
        name="Exposure", default=1, min=-20, max=20,
        update=_live,
        description=_d("exposure"),
    )
    auto_exposure: BoolProperty(
        name="Auto Exposure", default=True,
        update=_on_auto_exposure,
        description=_d("auto_exposure"),
    )
    ae_mode: EnumProperty(
        name="AE Mode", description="",
        items=translations.ae_mode_items,
        default=0,
    )
    ae_apply_to: EnumProperty(
        name="Apply To", description="",
        items=translations.ae_apply_to_items,
        default=1,
    )
    ae_center_preset: EnumProperty(
        name="Sampling", description="",
        items=translations.ae_center_preset_items,
        default=1,
        update=_on_ae_center_preset,
    )
    ae_ev_bias: FloatProperty(
        name="EV Bias", default=0.0, min=-3.0, max=3.0, soft_min=-2.0, soft_max=2.0,
        description=_d("ae_ev_bias"),
    )
    ae_speed: FloatProperty(
        name="AE Speed", default=0.5, min=0.02, max=1.0,
        description=_d("ae_speed"),
    )
    ae_center_weight: IntProperty(
        name="Center Weight", default=70, min=0, max=100,
        subtype="PERCENTAGE",
        update=_on_ae_center_weight,
        description=_d("ae_center_weight"),
    )
    ae_sample_jitter: BoolProperty(
        name="Sample Jitter", default=True,
        description=_d("ae_sample_jitter"),
    )
    ae_fast_converge: BoolProperty(
        name="Fast Converge", default=True,
        description=_d("ae_fast_converge"),
    )
    ae_gamma: FloatProperty(
        name="Parameter Correction", default=1.0, min=0.1, max=5.0, soft_max=3.0,
        update=_on_ae_gamma,
        description=_d("ae_gamma"),
    )
    ae_frame_only: BoolProperty(default=False, options={"HIDDEN"})
    distance: FloatProperty(name="Distance", default=2.5, min=0.3, max=50.0,
                            soft_max=10.0, update=_live,
                            description=_d("distance"))
    color_strength: FloatProperty(name="Color Strength", default=0.85, min=0.0,
                                  max=2.0, soft_max=1.5, update=_live,
                                  description=_d("color_strength"))
    color_saturation: FloatProperty(name="Saturation", default=1.0, min=0.0,
                                    max=3.0, soft_max=2.0, update=_live,
                                    description=_d("color_saturation"))
    tone_shadows: FloatProperty(name="Shadows", default=1.0, min=0.05, max=3.0,
                                soft_max=2.0, update=_live,
                                description=_d("tone_shadows"))
    tone_highlights: FloatProperty(name="Highlights", default=1.0, min=0.05, max=3.0,
                                   soft_max=2.0, update=_live,
                                   description=_d("tone_highlights"))
    contrast_boost: FloatProperty(name="Contrast", default=1.0, min=0.05, max=12.0,
                                  soft_max=6.0, update=_live,
                                  description=_d("contrast_boost"))
    rig_rotation: FloatProperty(
        name="Rotate", default=0.0, min=-6.2832, max=6.2832, subtype="ANGLE",
        update=_rotate, description=_d("rig_rotation"),
    )
    rig_height: FloatProperty(
        name="Height", default=0.0, soft_min=-10.0, soft_max=10.0, subtype="DISTANCE",
        update=_height, description=_d("rig_height"),
    )

    use_world: BoolProperty(name="Set World / Ambient", default=True, update=_live,
                            description=_d("use_world"))

    auto_timer: BoolProperty(default=False, options={"HIDDEN"})
    timer_interval: FloatProperty(
        name="Interval", default=0.3, min=0.05, max=5.0, subtype="TIME",
        description=_d("timer_interval"),
    )

    float_show: BoolProperty(name="Float Reference", default=False,
                             update=overlay.on_toggle,
                             description=_d("float_show"))
    float_opacity: FloatProperty(name="Opacity", default=0.9, min=0.05, max=1.0,
                                 update=overlay.on_redraw,
                                 description=_d("float_opacity"))
    float_scale: FloatProperty(name="Size", default=1.0, min=0.2, max=3.0,
                               update=overlay.on_redraw,
                               description=_d("float_scale"))
    float_corner: EnumProperty(
        name="Corner", items=translations.corner_items, update=overlay.on_redraw,
        description=_d("float_corner"),
    )

    bk_view_exposure: FloatProperty(default=0.0, options={"HIDDEN"})
    bk_view_gamma: FloatProperty(default=1.0, options={"HIDDEN"})
    ae_value: FloatProperty(default=0.0, options={"HIDDEN"})

    bk_world_touched: BoolProperty(default=False, options={"HIDDEN"})
    bk_world_created: BoolProperty(default=False, options={"HIDDEN"})
    bk_prev_world: StringProperty(default="", options={"HIDDEN"})
    bk_bg_color: FloatVectorProperty(size=4, default=(0.05, 0.05, 0.05, 1.0),
                                     options={"HIDDEN"})
    bk_bg_strength: FloatProperty(default=1.0, options={"HIDDEN"})

    cache_ambient: FloatVectorProperty(size=3, default=(0.05, 0.05, 0.06),
                                        options={"HIDDEN"})
    cache_mean_lum: FloatProperty(default=0.3, options={"HIDDEN"})
    cache_split_score: FloatProperty(default=0.0, options={"HIDDEN"})
    cache_hardness: FloatProperty(default=0.0, options={"HIDDEN"})
    cache_shadow_frac: FloatProperty(default=0.0, options={"HIDDEN"})
    cache_target: FloatVectorProperty(size=3, default=(0.0, 0.0, 0.0),
                                       options={"HIDDEN"})
    cache_radius: FloatProperty(default=0.0, options={"HIDDEN"})


def _iter_scenes():
    """Safe scene iterator — bpy.data may be restricted during add-on register."""
    try:
        return list(bpy.data.scenes)
    except (AttributeError, TypeError):
        return []


def needs_default_reference(scene) -> bool:
    """Read-only check: should we load the built-in default reference?"""
    s = getattr(scene, "rolllux", None)
    if s is None or s.reference_user_cleared:
        return False
    img = s.reference_image
    return img is None or img.size[0] == 0 or img.size[1] == 0


def schedule_default_reference(scene=None, context=None):
    """Queue ``ensure_default_reference`` outside UI draw (RNA writes forbidden there)."""
    scenes = [scene] if scene is not None else _iter_scenes()
    pending = [sc for sc in scenes if needs_default_reference(sc)]
    new = [sc for sc in pending if sc.name not in _DEFAULT_SCHEDULED]
    if not new:
        return

    for sc in new:
        _DEFAULT_SCHEDULED.add(sc.name)
    ctx = context
    names = tuple(sc.name for sc in new)

    def _run():
        for name in names:
            _DEFAULT_SCHEDULED.discard(name)
        try:
            c = ctx or bpy.context
            for sc in _iter_scenes():
                if sc.name in names and needs_default_reference(sc):
                    ensure_default_reference(sc, c)
        except Exception:
            pass
        return None

    bpy.app.timers.register(_run, first_interval=0.0)


def ensure_default_reference(scene=None, context=None):
    """Load the default ``broad_light`` reference when none is set."""
    global _REFERENCE_BUSY
    scenes = [scene] if scene is not None else _iter_scenes()
    ctx = context or getattr(bpy.context, "scene", None) and bpy.context or None
    rid = presets.DEFAULT_REFERENCE
    for sc in scenes:
        s = getattr(sc, "rolllux", None)
        if s is None or s.reference_user_cleared:
            continue
        img = s.reference_image
        if img is not None and img.size[0] > 0 and img.size[1] > 0:
            continue
        _REFERENCE_BUSY = True
        try:
            if s.reference_preset != rid:
                s.reference_preset = rid
            if s.reference_image is None or s.reference_image.size[0] == 0:
                if not _load_reference_image(s, rid, ctx):
                    continue
                from . import lighting
                lighting.schedule_analyze_only(ctx)
        finally:
            _REFERENCE_BUSY = False
        overlay.tag_redraw()


def _deferred_init():
    try:
        ensure_default_reference()
    except Exception:
        pass
    return None


@persistent
def _on_load(_dummy):
    try:
        ensure_default_reference()
    except Exception:
        pass

    try:
        auto_exposure.restore_handlers()
    except Exception:
        pass


_classes = (RLLM_LightInfo, RLLM_SampledColor, RLLM_AnalysisResult, RLLM_Settings)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rolllux = PointerProperty(type=RLLM_Settings)
    bpy.types.Scene.rolllux_result = PointerProperty(type=RLLM_AnalysisResult)
    bpy.types.Object.rolllux_light = PointerProperty(type=RLLM_LightInfo)
    if _on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load)
    bpy.app.timers.register(_deferred_init, first_interval=0.0)
    auto_exposure.register()


def unregister():
    auto_exposure.unregister()
    if _on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load)
    del bpy.types.Object.rolllux_light
    del bpy.types.Scene.rolllux_result
    del bpy.types.Scene.rolllux
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
