"""N-panel UI in the 3D Viewport (category: RollLux)."""

from __future__ import annotations

import bpy
from bpy.types import Panel

from . import lighting
from .translations import tr

_ICON_SCALE = 3.4
_SECTION_SEP = 0.12


def _sep(col, factor: float = _SECTION_SEP) -> None:
    if factor > 0.0:
        col.separator(factor=factor)


def _section_head(col, title_key: str, icon: str) -> None:
    row = col.row(align=True)
    row.scale_y = 0.95
    row.label(text=tr(title_key), icon=icon)


def _props_col(parent):
    col = parent.column(align=True)
    col.use_property_split = True
    col.use_property_decorate = False
    return col


def _draw_mode_tabs(layout, settings):
    row = layout.row(align=True)
    row.scale_y = 1.1
    sub = row.row(align=True)
    sub.prop_enum(settings, "ui_mode", "QUICK", text=tr("ui_mode_quick"))
    sub = row.row(align=True)
    sub.prop_enum(settings, "ui_mode", "PRO", text=tr("ui_mode_pro"))


def _compact_col(parent):
    col = parent.column(align=True)
    col.use_property_split = False
    col.use_property_decorate = False
    return col


def _draw_tuning_row(col, settings, prop, lock_prop, label_key):
    row = col.row(align=True)
    row.label(text=tr(label_key))
    row.prop(settings, prop, text="")
    icon = "LOCKED" if getattr(settings, lock_prop) else "UNLOCKED"
    row.prop(
        settings, lock_prop, text="",
        icon=icon, toggle=True, emboss=getattr(settings, lock_prop),
    )


def _draw_exposure_block(col, settings):
    row = col.row(align=True)
    row.label(text=tr("exposure"))
    exp_row = row.row(align=True)
    exp_row.enabled = not (
        settings.auto_exposure
        and getattr(settings, "ae_apply_to", "COLOR_MANAGEMENT") == "LIGHT_RIG"
    )
    exp_row.prop(settings, "exposure", text="")
    lock_icon = "LOCKED" if settings.lock_exposure else "UNLOCKED"
    row.prop(
        settings, "lock_exposure", text="",
        icon=lock_icon, toggle=True, emboss=settings.lock_exposure,
    )
    row.prop(
        settings, "auto_exposure", text="",
        icon="OUTLINER_OB_CAMERA", toggle=True, icon_only=True,
    )
    if not settings.auto_exposure:
        return
    sub = col.row(align=True)
    sub.prop(settings, "ae_mode", text="")
    sub.prop(settings, "ae_ev_bias", text=tr("ae_ev_short"))


def _draw_ae_advanced(col, settings):
    if not settings.auto_exposure:
        return
    apply_cm = getattr(settings, "ae_apply_to", "COLOR_MANAGEMENT") == "COLOR_MANAGEMENT"
    col.prop(settings, "ae_apply_to", text=tr("ae_apply_short"))
    col.prop(settings, "ae_center_preset", text=tr("ae_sampling_short"))
    if settings.ae_center_preset == "CUSTOM":
        col.prop(settings, "ae_center_weight", text=tr("ae_center_short"))
    col.prop(settings, "ae_speed", text=tr("ae_speed_short"))
    if apply_cm:
        col.prop(settings, "ae_gamma", text=tr("ae_gamma_short"))
    col.prop(settings, "ae_sample_jitter", text=tr("ae_jitter_short"))
    col.prop(settings, "ae_fast_converge", text=tr("ae_fast_converge_short"))
    row = col.row(align=True)
    if apply_cm:
        row.label(
            text=tr("ae_cm_exposure", exp=f"{settings.ae_value:.2f}"),
            icon="COLOR",
        )
    else:
        row.label(
            text=tr("ae_light_ev", ev=f"{settings.ae_value:.2f}"),
            icon="LIGHT",
        )
    row.operator("rolllux.bake_ae", text="", icon="FILE_TICK")


def _draw_icon_picker(parent, settings, prop, step_id, random_op, label_key):
    head = parent.row(align=True)
    head.label(text=tr(label_key), icon="LIGHT" if prop == "lighting_preset" else "TEXTURE")
    head.operator(random_op, text="", icon="FILE_REFRESH")
    row = parent.row(align=True)
    side = row.column(align=True)
    side.scale_y = _ICON_SCALE
    side.operator(step_id, text="", icon="TRIA_LEFT").direction = -1
    row.template_icon_view(settings, prop, show_labels=True, scale=_ICON_SCALE)
    side = row.column(align=True)
    side.scale_y = _ICON_SCALE
    side.operator(step_id, text="", icon="TRIA_RIGHT").direction = 1


def _draw_reference(col, settings):
    _section_head(col, "section_reference", "IMAGE_DATA")
    col.template_ID(settings, "reference_image", open="rolllux.open_image")


def _draw_presets(col, settings):
    _draw_icon_picker(
        col, settings, "lighting_preset",
        "rolllux.preset_step", "rolllux.random_preset", "preset_section",
    )
    _sep(col, 0.05)
    _draw_icon_picker(
        col, settings, "reference_preset",
        "rolllux.reference_step", "rolllux.random_reference", "ref_section",
    )
    col.prop(settings, "distribution_color_mode", text=tr("distribution_color_mode"))


def _draw_ae_toggle(col, settings):
    row = col.row(align=True)
    row.prop(
        settings, "auto_exposure", text="",
        icon="OUTLINER_OB_CAMERA", toggle=True, icon_only=True,
    )
    if settings.auto_exposure:
        row.prop(settings, "ae_ev_bias", text=tr("ae_ev_short"))
        row.operator("rolllux.bake_ae", text="", icon="FILE_TICK")
    else:
        row.label(text=tr("auto_exposure"))


def _draw_actions_pro(col, settings):
    _section_head(col, "section_actions", "PLAY")
    row = col.row(align=True)
    row.operator("rolllux.generate", icon="LIGHT", text=tr("generate"))
    row = col.row(align=True)
    row.operator("rolllux.analyze", icon="VIEWZOOM", text=tr("analyze"))
    row.operator("rolllux.clear", icon="TRASH", text=tr("clear"))
    row.operator(
        "rolllux.auto_timer", text="",
        icon="TEMP", depress=settings.auto_timer,
    )
    row.prop(settings, "timer_interval", text="")


def _draw_actions_quick(col, settings):
    _section_head(col, "section_actions", "PLAY")
    row = col.row(align=True)
    row.scale_y = 1.2
    row.operator("rolllux.generate", icon="LIGHT", text=tr("generate"))
    row = col.row(align=True)
    row.operator("rolllux.clear", icon="TRASH", text=tr("clear"))
    row.operator(
        "rolllux.auto_timer", text="",
        icon="TEMP", depress=settings.auto_timer,
    )
    row.prop(settings, "timer_interval", text="")


def _draw_quick(layout, settings):
    box = layout.box()
    col = _props_col(box)
    _draw_reference(col, settings)
    _sep(col)
    _draw_presets(col, settings)
    _sep(col)
    _draw_ae_toggle(col, settings)
    _sep(col)
    _draw_actions_quick(col, settings)


def _draw_setup(col, settings):
    _section_head(col, "section_setup", "LIGHT_DATA")
    col.prop(settings, "mode", text=tr("mode"))
    col.prop(settings, "target_mode", text=tr("target"))
    col.prop(settings, "orient_mode", text=tr("orient"))
    col.prop(settings, "light_count", text=tr("light_count"))
    col.prop(settings, "color_strategy", text=tr("color_strategy"))
    col.prop(settings, "use_luxpro", text=tr("luxpro"))


def _draw_energy(col, settings):
    _section_head(col, "section_energy", "OUTLINER_OB_LIGHT")
    _draw_tuning_row(col, settings, "intensity", "lock_intensity", "intensity")
    _draw_exposure_block(col, settings)


def _draw_placement(col, settings):
    _section_head(col, "section_rig", "ORIENTATION_GIMBAL")
    _draw_tuning_row(col, settings, "distance", "lock_distance", "distance")
    _draw_tuning_row(col, settings, "rig_rotation", "lock_rig_rotation", "rotate")
    _draw_tuning_row(col, settings, "rig_height", "lock_rig_height", "height")


def _draw_color_world(col, settings):
    _section_head(col, "section_color", "COLOR")
    _draw_tuning_row(
        col, settings, "color_strength", "lock_color_strength", "color_strength",
    )
    _draw_tuning_row(
        col, settings, "color_saturation", "lock_color_saturation", "saturation",
    )
    _draw_tuning_row(
        col, settings, "tone_shadows", "lock_tone_shadows", "shadows",
    )
    _draw_tuning_row(
        col, settings, "tone_highlights", "lock_tone_highlights", "highlights",
    )
    _draw_tuning_row(
        col, settings, "contrast_boost", "lock_contrast_boost", "contrast",
    )
    col.prop(settings, "use_world", text=tr("use_world"))


def _draw_overlay(col, settings):
    _section_head(col, "section_overlay", "IMAGE_BACKGROUND")
    col.prop(settings, "float_show", text=tr("float_section"))
    if settings.float_show:
        col.prop(settings, "float_corner", text=tr("float_corner"))
        col.prop(settings, "float_scale", text=tr("float_scale"))
        col.prop(settings, "float_opacity", text=tr("float_opacity"))


def _draw_lights(layout, settings):
    lights = lighting.list_lights()
    if not lights:
        return
    box = layout.box()
    col = box.column(align=True)
    col.use_property_split = False
    col.use_property_decorate = False
    head = col.row(align=True)
    head.label(text=tr("section_lights"), icon="LIGHT_POINT")
    head.label(text=f"({len(lights)})")
    icon = "LOCKED" if settings.lock_light_colors else "UNLOCKED"
    head.prop(
        settings, "lock_light_colors", text="",
        icon=icon, toggle=True, emboss=settings.lock_light_colors,
    )
    for obj in lights:
        info = obj.rolllux_light
        role = tr(f"role_{info.role}")
        top = col.row(align=True)
        top.prop(info, "enabled", text="")
        top.label(text=role)
        top.operator("rolllux.delete_light", text="", icon="X").name = obj.name
        bottom = col.row(align=True)
        bottom.prop(info, "base_color", text="")
        bottom.prop(info, "gain", text=tr("light_energy"))


def _draw_analysis(box, settings, res):
    if not res.valid:
        return
    col = _props_col(box)
    _section_head(col, "section_analysis", "VIEWZOOM")
    row = col.row(align=True)
    if res.sampled_colors:
        for item in res.sampled_colors:
            row.prop(item, "color", text="")
    else:
        row.prop(res, "key_color", text="")
        row.prop(res, "fill_color", text="")
        row.prop(res, "ambient_color", text="")
    dir_txt = tr(f"dir_{res.dir_label}") if res.dir_label else "-"
    mood_txt = tr(f"mood_{res.mood}") if res.mood else "-"
    col.label(
        text=f"{tr('luxpro')}: {dir_txt}  ·  "
             f"{tr('lbl_mood')}: {mood_txt}  ·  "
             f"~{int(res.color_temperature)} K",
        icon="LIGHT_SUN",
    )


def _draw_pro(layout, settings, res):
    workflow = layout.box()
    wf = _props_col(workflow)
    _draw_reference(wf, settings)
    _sep(wf)
    _draw_presets(wf, settings)
    _sep(wf)
    _draw_actions_pro(wf, settings)

    tuning = layout.box()
    setup = _props_col(tuning)
    _draw_setup(setup, settings)
    _sep(setup)
    tn = _compact_col(tuning)
    _draw_energy(tn, settings)
    _sep(tn)
    _draw_placement(tn, settings)
    _sep(tn)
    _draw_color_world(tn, settings)

    if settings.auto_exposure:
        ae_box = layout.box()
        _draw_ae_advanced(_props_col(ae_box), settings)

    extra = layout.box()
    ex = _props_col(extra)
    _draw_overlay(ex, settings)
    _draw_lights(layout, settings)
    if res.valid:
        analysis_box = layout.box()
        _draw_analysis(analysis_box, settings, res)


class RLLX_PT_main(Panel):
    bl_label = "RollLux"
    bl_idname = "RLLX_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "RollLux"

    def draw_header_preset(self, context):
        from . import mcp_bridge

        settings = context.scene.rolllux
        row = self.layout.row(align=True)
        running = mcp_bridge.is_connected()
        if running:
            row.operator(
                "rolllux_mcp.toggle",
                text=tr("mcp_running_short", port=settings.mcp_port),
                icon="RADIOBUT_ON",
                depress=True,
            )
        else:
            row.operator(
                "rolllux_mcp.toggle",
                text=tr("mcp_start"),
                icon="PLAY",
            )
        row.menu("RLLX_MT_mcp", text="", icon="PREFERENCES")

    def draw(self, context):
        from . import properties as _props
        _props.schedule_default_reference(context.scene, context)

        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        settings = context.scene.rolllux
        from . import auto_exposure
        auto_exposure.restore_handlers()

        _draw_mode_tabs(layout, settings)

        if settings.ui_mode == "QUICK":
            _draw_quick(layout, settings)
        else:
            _draw_pro(layout, settings, context.scene.rolllux_result)


_classes = (RLLX_PT_main,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
