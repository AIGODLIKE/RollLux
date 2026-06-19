"""N-panel UI in the 3D Viewport (category: RollLux)."""

from __future__ import annotations

import bpy
from bpy.types import Panel

from . import lighting
from .translations import tr

_ICON_SCALE = 4.0


def _draw_tuning_row(layout, settings, prop, lock_prop, label_key, lang):
    row = layout.row(align=True)
    row.prop(settings, prop, text=tr(lang, label_key))
    icon = "LOCKED" if getattr(settings, lock_prop) else "UNLOCKED"
    row.prop(
        settings, lock_prop, text="",
        icon=icon, toggle=True, emboss=getattr(settings, lock_prop),
    )


def _draw_exposure_block(col, settings, lang):
    _draw_tuning_row(col, settings, "exposure", "lock_exposure", "exposure", lang)
    row = col.row(align=True)
    row.prop(settings, "auto_exposure", text=tr(lang, "auto_exposure"))
    if settings.auto_exposure:
        sub = col.column(align=True)
        sub.use_property_split = True
        sub.prop(settings, "ae_gamma", text=tr(lang, "ae_gamma"))


def _draw_icon_picker(layout, settings, prop, step_id, random_op, label_key, lang):
    col = layout.column(align=True)
    head = col.row(align=True)
    head.label(text=tr(lang, label_key), icon="LIGHT" if prop == "lighting_preset" else "TEXTURE")
    head.operator(random_op, text="", icon="FILE_REFRESH")
    row = col.row(align=True)
    side = row.column(align=True)
    side.scale_y = _ICON_SCALE
    side.operator(step_id, text="", icon="TRIA_LEFT").direction = -1
    row.template_icon_view(settings, prop, show_labels=True, scale=_ICON_SCALE)
    side = row.column(align=True)
    side.scale_y = _ICON_SCALE
    side.operator(step_id, text="", icon="TRIA_RIGHT").direction = 1


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
        settings = context.scene.rolllux
        lang = settings.language

        col = layout.column(align=True)
        col.template_ID(settings, "reference_image", open="rolllux.open_image")
        col.operator("rolllux.paste_image", icon="PASTEDOWN", text=tr(lang, "btn_paste"))

        layout.separator(factor=0.35)

        _draw_icon_picker(
            layout, settings, "lighting_preset",
            "rolllux.preset_step", "rolllux.random_preset", "preset_section", lang,
        )
        _draw_icon_picker(
            layout, settings, "reference_preset",
            "rolllux.reference_step", "rolllux.random_reference", "ref_section", lang,
        )

        layout.separator(factor=0.35)

        row = layout.row(align=True)
        row.scale_y = 1.35
        row.operator("rolllux.generate", icon="LIGHT", text=tr(lang, "generate"))
        row = layout.row(align=True)
        row.operator("rolllux.analyze", icon="VIEWZOOM", text=tr(lang, "analyze"))
        row.operator("rolllux.clear", icon="TRASH", text=tr(lang, "clear"))
        row.operator(
            "rolllux.auto_timer", text="",
            icon="TEMP", depress=settings.auto_timer,
        )
        row.prop(settings, "timer_interval", text="")

        layout.separator(factor=0.35)

        col = layout.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False
        _draw_tuning_row(col, settings, "intensity", "lock_intensity", "intensity", lang)
        _draw_exposure_block(col, settings, lang)
        _draw_tuning_row(col, settings, "distance", "lock_distance", "distance", lang)
        _draw_tuning_row(col, settings, "rig_rotation", "lock_rig_rotation", "rotate", lang)
        _draw_tuning_row(col, settings, "rig_height", "lock_rig_height", "height", lang)
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


class RLLX_PT_advanced(Panel):
    bl_label = ""
    bl_idname = "RLLX_PT_advanced"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "RollLux"
    bl_parent_id = "RLLX_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.label(
            text=tr(context.scene.rolllux.language, "section_advanced"),
            icon="PREFERENCES",
        )

    def draw(self, context):
        layout = self.layout
        settings = context.scene.rolllux
        lang = settings.language
        res = context.scene.rolllux_result

        col = layout.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(settings, "mode", text=tr(lang, "mode"))
        col.prop(settings, "target_mode", text=tr(lang, "target"))
        col.prop(settings, "orient_mode", text=tr(lang, "orient"))
        col.prop(settings, "light_count", text=tr(lang, "light_count"))
        col.prop(settings, "color_strategy", text=tr(lang, "color_strategy"))
        col.prop(settings, "use_luxpro", text=tr(lang, "luxpro"))

        layout.separator(factor=0.4)

        row = layout.row(align=True)
        row.prop(settings, "float_show", text=tr(lang, "float_section"))
        if settings.float_show:
            sub = layout.column(align=True)
            sub.use_property_split = True
            sub.prop(settings, "float_corner", text=tr(lang, "float_corner"))
            sub.prop(settings, "float_scale", text=tr(lang, "float_scale"))
            sub.prop(settings, "float_opacity", text=tr(lang, "float_opacity"))

        lights = lighting.list_lights()
        if lights:
            layout.separator(factor=0.4)
            layout.label(
                text=f"{tr(lang, 'lights_section')} ({len(lights)})",
                icon="LIGHT_POINT",
            )
            for obj in lights:
                info = obj.rolllux_light
                row = layout.row(align=True)
                row.prop(info, "enabled", text="")
                row.label(text=tr(lang, f"role_{info.role}"))
                row.prop(info, "base_color", text="")
                row.prop(info, "gain", text=tr(lang, "light_energy"))
                row.operator("rolllux.delete_light", text="", icon="X").name = obj.name

        if res.valid:
            layout.separator(factor=0.4)
            layout.label(text=tr(lang, "detected"), icon="VIEWZOOM")
            row = layout.row(align=True)
            if res.sampled_colors:
                for item in res.sampled_colors:
                    row.prop(item, "color", text="")
            else:
                row.prop(res, "key_color", text="")
                row.prop(res, "fill_color", text="")
                row.prop(res, "ambient_color", text="")
            dir_txt = tr(lang, f"dir_{res.dir_label}") if res.dir_label else "-"
            mood_txt = tr(lang, f"mood_{res.mood}") if res.mood else "-"
            layout.label(
                text=f"{tr(lang, 'luxpro')}: {dir_txt}  ·  "
                     f"{tr(lang, 'lbl_mood')}: {mood_txt}  ·  "
                     f"~{int(res.color_temperature)} K",
                icon="LIGHT_SUN",
            )


_classes = (
    RLLX_PT_main,
    RLLX_PT_advanced,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
