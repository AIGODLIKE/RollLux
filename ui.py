"""N-panel UI in the 3D Viewport (category: RollLux)."""

from __future__ import annotations

import bpy
from bpy.types import Panel

from . import lighting
from . import translations
from .translations import tr

_ICON_SCALE = 3.4
_SECTION_SEP = 0.12
_PANEL_I18N: str | None = None


def _ensure_panel_i18n(lang: str) -> None:
    global _PANEL_I18N
    if _PANEL_I18N == lang:
        return
    _PANEL_I18N = lang
    translations.sync_i18n(lang)


def _sep(col, factor: float = _SECTION_SEP) -> None:
    if factor > 0.0:
        col.separator(factor=factor)


def _section_head(col, lang: str, title_key: str, icon: str) -> None:
    row = col.row(align=True)
    row.scale_y = 0.95
    row.label(text=tr(lang, title_key), icon=icon)


def _props_col(parent):
    col = parent.column(align=True)
    col.use_property_split = True
    col.use_property_decorate = False
    return col


def _draw_mode_tabs(layout, settings, lang):
    row = layout.row(align=True)
    row.scale_y = 1.1
    sub = row.row(align=True)
    sub.prop_enum(settings, "ui_mode", "QUICK", text=tr(lang, "ui_mode_quick"))
    sub = row.row(align=True)
    sub.prop_enum(settings, "ui_mode", "PRO", text=tr(lang, "ui_mode_pro"))


def _compact_col(parent):
    col = parent.column(align=True)
    col.use_property_split = False
    col.use_property_decorate = False
    return col


def _draw_tuning_row(col, settings, prop, lock_prop, label_key, lang):
    row = col.row(align=True)
    row.label(text=tr(lang, label_key))
    row.prop(settings, prop, text="")
    icon = "LOCKED" if getattr(settings, lock_prop) else "UNLOCKED"
    row.prop(
        settings, lock_prop, text="",
        icon=icon, toggle=True, emboss=getattr(settings, lock_prop),
    )


def _draw_exposure_block(col, settings, lang):
    row = col.row(align=True)
    row.label(text=tr(lang, "exposure"))
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
    sub.prop(settings, "ae_ev_bias", text=tr(lang, "ae_ev_short"))


def _draw_ae_advanced(col, settings, lang):
    if not settings.auto_exposure:
        return
    apply_cm = getattr(settings, "ae_apply_to", "COLOR_MANAGEMENT") == "COLOR_MANAGEMENT"
    col.prop(settings, "ae_apply_to", text=tr(lang, "ae_apply_short"))
    col.prop(settings, "ae_center_preset", text=tr(lang, "ae_sampling_short"))
    if settings.ae_center_preset == "CUSTOM":
        col.prop(settings, "ae_center_weight", text=tr(lang, "ae_center_short"))
    col.prop(settings, "ae_speed", text=tr(lang, "ae_speed_short"))
    if apply_cm:
        col.prop(settings, "ae_gamma", text=tr(lang, "ae_gamma_short"))
    col.prop(settings, "ae_sample_jitter", text=tr(lang, "ae_jitter_short"))
    col.prop(settings, "ae_fast_converge", text=tr(lang, "ae_fast_converge_short"))
    row = col.row(align=True)
    if apply_cm:
        row.label(
            text=tr(lang, "ae_cm_exposure", exp=f"{settings.ae_value:.2f}"),
            icon="COLOR",
        )
    else:
        row.label(
            text=tr(lang, "ae_light_ev", ev=f"{settings.ae_value:.2f}"),
            icon="LIGHT",
        )
    row.operator("rolllux.bake_ae", text="", icon="FILE_TICK")


def _draw_icon_picker(parent, settings, prop, step_id, random_op, label_key, lang):
    head = parent.row(align=True)
    head.label(text=tr(lang, label_key), icon="LIGHT" if prop == "lighting_preset" else "TEXTURE")
    head.operator(random_op, text="", icon="FILE_REFRESH")
    row = parent.row(align=True)
    side = row.column(align=True)
    side.scale_y = _ICON_SCALE
    side.operator(step_id, text="", icon="TRIA_LEFT").direction = -1
    row.template_icon_view(settings, prop, show_labels=True, scale=_ICON_SCALE)
    side = row.column(align=True)
    side.scale_y = _ICON_SCALE
    side.operator(step_id, text="", icon="TRIA_RIGHT").direction = 1


def _draw_reference(col, settings, lang):
    _section_head(col, lang, "section_reference", "IMAGE_DATA")
    col.template_ID(settings, "reference_image", open="rolllux.open_image")
    col.operator("rolllux.paste_image", icon="PASTEDOWN", text=tr(lang, "btn_paste"))


def _draw_presets(col, settings, lang):
    _draw_icon_picker(
        col, settings, "lighting_preset",
        "rolllux.preset_step", "rolllux.random_preset", "preset_section", lang,
    )
    _sep(col, 0.05)
    _draw_icon_picker(
        col, settings, "reference_preset",
        "rolllux.reference_step", "rolllux.random_reference", "ref_section", lang,
    )


def _draw_ae_toggle(col, settings, lang):
    row = col.row(align=True)
    row.prop(
        settings, "auto_exposure", text="",
        icon="OUTLINER_OB_CAMERA", toggle=True, icon_only=True,
    )
    if settings.auto_exposure:
        row.prop(settings, "ae_ev_bias", text=tr(lang, "ae_ev_short"))
        row.operator("rolllux.bake_ae", text="", icon="FILE_TICK")
    else:
        row.label(text=tr(lang, "auto_exposure"))


def _draw_actions_pro(col, settings, lang):
    _section_head(col, lang, "section_actions", "PLAY")
    row = col.row(align=True)
    row.operator("rolllux.generate", icon="LIGHT", text=tr(lang, "generate"))
    row = col.row(align=True)
    row.operator("rolllux.analyze", icon="VIEWZOOM", text=tr(lang, "analyze"))
    row.operator("rolllux.clear", icon="TRASH", text=tr(lang, "clear"))
    row.operator(
        "rolllux.auto_timer", text="",
        icon="TEMP", depress=settings.auto_timer,
    )
    row.prop(settings, "timer_interval", text="")


def _draw_actions_quick(col, settings, lang):
    _section_head(col, lang, "section_actions", "PLAY")
    row = col.row(align=True)
    row.scale_y = 1.2
    row.operator("rolllux.generate", icon="LIGHT", text=tr(lang, "generate"))
    row = col.row(align=True)
    row.operator("rolllux.clear", icon="TRASH", text=tr(lang, "clear"))
    row.operator(
        "rolllux.auto_timer", text="",
        icon="TEMP", depress=settings.auto_timer,
    )
    row.prop(settings, "timer_interval", text="")


def _draw_quick(layout, settings, lang):
    box = layout.box()
    col = _props_col(box)
    _draw_reference(col, settings, lang)
    _sep(col)
    _draw_presets(col, settings, lang)
    _sep(col)
    _draw_ae_toggle(col, settings, lang)
    _sep(col)
    _draw_actions_quick(col, settings, lang)


def _draw_setup(col, settings, lang):
    _section_head(col, lang, "section_setup", "LIGHT_DATA")
    col.prop(settings, "mode", text=tr(lang, "mode"))
    col.prop(settings, "target_mode", text=tr(lang, "target"))
    col.prop(settings, "orient_mode", text=tr(lang, "orient"))
    col.prop(settings, "light_count", text=tr(lang, "light_count"))
    col.prop(settings, "color_strategy", text=tr(lang, "color_strategy"))
    col.prop(settings, "use_luxpro", text=tr(lang, "luxpro"))


def _draw_energy(col, settings, lang):
    _section_head(col, lang, "section_energy", "OUTLINER_OB_LIGHT")
    _draw_tuning_row(col, settings, "intensity", "lock_intensity", "intensity", lang)
    _draw_exposure_block(col, settings, lang)


def _draw_placement(col, settings, lang):
    _section_head(col, lang, "section_rig", "ORIENTATION_GIMBAL")
    _draw_tuning_row(col, settings, "distance", "lock_distance", "distance", lang)
    _draw_tuning_row(col, settings, "rig_rotation", "lock_rig_rotation", "rotate", lang)
    _draw_tuning_row(col, settings, "rig_height", "lock_rig_height", "height", lang)


def _draw_color_world(col, settings, lang):
    _section_head(col, lang, "section_color", "COLOR")
    _draw_tuning_row(
        col, settings, "color_strength", "lock_color_strength", "color_strength", lang,
    )
    _draw_tuning_row(
        col, settings, "color_saturation", "lock_color_saturation", "saturation", lang,
    )
    _draw_tuning_row(
        col, settings, "tone_shadows", "lock_tone_shadows", "shadows", lang,
    )
    _draw_tuning_row(
        col, settings, "tone_highlights", "lock_tone_highlights", "highlights", lang,
    )
    _draw_tuning_row(
        col, settings, "contrast_boost", "lock_contrast_boost", "contrast", lang,
    )
    col.prop(settings, "use_world", text=tr(lang, "use_world"))


def _draw_overlay(col, settings, lang):
    _section_head(col, lang, "section_overlay", "IMAGE_BACKGROUND")
    col.prop(settings, "float_show", text=tr(lang, "float_section"))
    if settings.float_show:
        col.prop(settings, "float_corner", text=tr(lang, "float_corner"))
        col.prop(settings, "float_scale", text=tr(lang, "float_scale"))
        col.prop(settings, "float_opacity", text=tr(lang, "float_opacity"))


def _draw_lights(layout, settings, lang):
    lights = lighting.list_lights()
    if not lights:
        return
    box = layout.box()
    col = box.column(align=True)
    col.use_property_split = False
    col.use_property_decorate = False
    head = col.row(align=True)
    head.label(text=tr(lang, "section_lights"), icon="LIGHT_POINT")
    head.label(text=f"({len(lights)})")
    for obj in lights:
        info = obj.rolllux_light
        role = tr(lang, f"role_{info.role}")
        top = col.row(align=True)
        top.prop(info, "enabled", text="")
        top.label(text=role)
        top.operator("rolllux.delete_light", text="", icon="X").name = obj.name
        bottom = col.row(align=True)
        bottom.prop(info, "base_color", text="")
        bottom.prop(info, "gain", text=tr(lang, "light_energy"))


def _draw_analysis(box, settings, lang, res):
    if not res.valid:
        return
    col = _props_col(box)
    _section_head(col, lang, "section_analysis", "VIEWZOOM")
    row = col.row(align=True)
    if res.sampled_colors:
        for item in res.sampled_colors:
            row.prop(item, "color", text="")
    else:
        row.prop(res, "key_color", text="")
        row.prop(res, "fill_color", text="")
        row.prop(res, "ambient_color", text="")
    dir_txt = tr(lang, f"dir_{res.dir_label}") if res.dir_label else "-"
    mood_txt = tr(lang, f"mood_{res.mood}") if res.mood else "-"
    col.label(
        text=f"{tr(lang, 'luxpro')}: {dir_txt}  ·  "
             f"{tr(lang, 'lbl_mood')}: {mood_txt}  ·  "
             f"~{int(res.color_temperature)} K",
        icon="LIGHT_SUN",
    )


def _draw_pro(layout, settings, lang, res):
    # Workflow: reference + presets + actions (one panel)
    workflow = layout.box()
    wf = _props_col(workflow)
    _draw_reference(wf, settings, lang)
    _sep(wf)
    _draw_presets(wf, settings, lang)
    _sep(wf)
    _draw_actions_pro(wf, settings, lang)

    # Tuning: setup + energy + placement + color (one panel)
    tuning = layout.box()
    setup = _props_col(tuning)
    _draw_setup(setup, settings, lang)
    _sep(setup)
    tn = _compact_col(tuning)
    _draw_energy(tn, settings, lang)
    _sep(tn)
    _draw_placement(tn, settings, lang)
    _sep(tn)
    _draw_color_world(tn, settings, lang)

    if settings.auto_exposure:
        ae_box = layout.box()
        _draw_ae_advanced(_props_col(ae_box), settings, lang)

    extra = layout.box()
    ex = _props_col(extra)
    _draw_overlay(ex, settings, lang)
    _draw_lights(layout, settings, lang)
    if res.valid:
        analysis_box = layout.box()
        _draw_analysis(analysis_box, settings, lang, res)


class RLLX_PT_main(Panel):
    bl_label = "RollLux"
    bl_idname = "RLLX_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "RollLux"

    def draw_header_preset(self, context):
        row = self.layout.row(align=True)
        row.label(text="", icon="WORLD")
        row.prop(context.scene.rolllux, "language", text="")

    def draw(self, context):
        from . import properties as _props
        _props.schedule_default_reference(context.scene, context)

        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        settings = context.scene.rolllux
        lang = settings.language
        _ensure_panel_i18n(lang)
        from . import auto_exposure
        auto_exposure.restore_handlers()

        _draw_mode_tabs(layout, settings, lang)

        if settings.ui_mode == "QUICK":
            _draw_quick(layout, settings, lang)
        else:
            _draw_pro(layout, settings, lang, context.scene.rolllux_result)


_classes = (RLLX_PT_main,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
