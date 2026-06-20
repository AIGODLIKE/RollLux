"""Operators: load reference, analyze, generate, clear, preset nav, light add/del."""

from __future__ import annotations

import os

import bpy
from bpy.props import IntProperty, StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from . import clipboard, lighting, overlay, presets, translations
from .translations import tr


def _schedule_enum_step(context, prop_id: str, order: tuple[str, ...], direction: int) -> None:
    """Apply an enum step on the next main-loop tick (safe during icon_view draw)."""
    settings = context.scene.rolllux
    try:
        idx = order.index(getattr(settings, prop_id))
    except ValueError:
        idx = 0
    new_id = order[(idx + direction) % len(order)]
    scene_name = context.scene.name

    def _apply():
        try:
            scene = bpy.data.scenes.get(scene_name)
            if scene is None:
                return None
            current = getattr(scene.rolllux, prop_id)
            if current != new_id:
                setattr(scene.rolllux, prop_id, new_id)
        except Exception:
            pass
        return None

    if getattr(bpy.app, "background", False):
        _apply()
        return
    bpy.app.timers.register(_apply, first_interval=0.0)


class RLLX_OT_paste_image(Operator):
    """Paste a lighting reference image from the system clipboard"""
    bl_idname = "rolllux.paste_image"
    bl_label = "Paste Reference Image"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        lang = context.scene.rolllux.language
        path = clipboard.grab_clipboard_image()
        if not path:
            self.report({"ERROR"}, tr(lang, "err_no_clip"))
            return {"CANCELLED"}

        for old in list(bpy.data.images):
            if old.name.startswith("RollLux_Clipboard") and old.users == 0:
                bpy.data.images.remove(old)

        try:
            img = bpy.data.images.load(path, check_existing=False)
            img.pack()  # embed pixels so the temp file can vanish safely
        except RuntimeError as exc:
            self.report({"ERROR"}, tr(lang, "err_load", err=exc))
            return {"CANCELLED"}
        img.name = "RollLux_Clipboard"
        context.scene.rolllux.reference_image = img
        overlay.tag_redraw()
        self.report({"INFO"}, tr(lang, "msg_pasted", name=img.name))
        return {"FINISHED"}


class RLLX_OT_open_image(Operator, ImportHelper):
    """Load a lighting reference image from disk"""
    bl_idname = "rolllux.open_image"
    bl_label = "Open Reference Image"
    bl_options = {"REGISTER", "UNDO"}

    filter_glob: StringProperty(
        default="*.png;*.jpg;*.jpeg;*.exr;*.hdr;*.tif;*.tiff;*.bmp;*.tga;*.webp",
        options={"HIDDEN"},
    )

    def execute(self, context):
        lang = context.scene.rolllux.language
        if not self.filepath or not os.path.isfile(self.filepath):
            self.report({"ERROR"}, tr(lang, "err_no_file"))
            return {"CANCELLED"}
        try:
            img = bpy.data.images.load(self.filepath, check_existing=True)
        except RuntimeError as exc:
            self.report({"ERROR"}, tr(lang, "err_load", err=exc))
            return {"CANCELLED"}
        context.scene.rolllux.reference_image = img
        overlay.tag_redraw()
        self.report({"INFO"}, tr(lang, "msg_loaded", name=img.name))
        return {"FINISHED"}


class RLLX_OT_analyze(Operator):
    """Analyze the reference image without creating lights"""
    bl_idname = "rolllux.analyze"
    bl_label = "Analyze Reference"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        s = context.scene.rolllux
        if s.reference_image is not None:
            return True
        # Enable when the built-in default exists; image loads on execute/draw.
        import os
        from . import presets as _presets
        return os.path.isfile(_presets.reference_path(_presets.DEFAULT_REFERENCE))

    def execute(self, context):
        from . import properties as _props
        _props.ensure_default_reference(context.scene, context)
        lang = context.scene.rolllux.language
        profile, err = lighting.analyze_only(context)
        if err:
            key = "err_no_image" if err == "no_image" else "err_analysis"
            self.report({"ERROR"}, tr(lang, key, err=err))
            return {"CANCELLED"}
        self.report({"INFO"}, tr(lang, "msg_analyzed", mood=profile.mood,
                                 c=f"{profile.contrast_ratio:.1f}"))
        return {"FINISHED"}


class RLLX_OT_generate(Operator):
    """Analyze the reference and build a matching light rig"""
    bl_idname = "rolllux.generate"
    bl_label = "Generate Lighting"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return getattr(context, "scene", None) is not None

    def execute(self, context):
        from . import properties as _props
        s = context.scene.rolllux
        lang = s.language
        if _props._reference_missing(s):
            if not _props.load_random_reference(context):
                self.report({"ERROR"}, tr(lang, "err_load", err="random reference"))
                return {"CANCELLED"}
        summary, err = lighting.analyze_and_generate(context)
        if err:
            key = "err_no_image" if err == "no_image" else "err_analysis"
            self.report({"ERROR"}, tr(lang, key, err=err))
            return {"CANCELLED"}
        self.report({"INFO"}, tr(lang, "msg_created", n=summary["lights"]))
        return {"FINISHED"}


class RLLX_OT_clear(Operator):
    """Remove the generated light rig and restore the environment"""
    bl_idname = "rolllux.clear"
    bl_label = "Clear Lighting"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        lang = context.scene.rolllux.language
        removed = lighting.clear_previous(context)
        context.scene.rolllux_result.valid = False
        self.report({"INFO"}, tr(lang, "msg_removed", n=removed))
        return {"FINISHED"}


class RLLX_OT_preset_step(Operator):
    """Switch to the previous / next lighting preset"""
    bl_idname = "rolllux.preset_step"
    bl_label = "Step Preset"
    bl_options = {"REGISTER", "UNDO"}

    direction: IntProperty(default=1)

    def execute(self, context):
        _schedule_enum_step(
            context, "lighting_preset", presets.PRESET_ORDER, self.direction,
        )
        return {"FINISHED"}


class RLLX_OT_random_preset(Operator):
    """Generate a random lighting preset"""
    bl_idname = "rolllux.random_preset"
    bl_label = "Random Lighting Preset"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        from . import properties as _props
        s = context.scene.rolllux
        presets.randomize_preset()
        if s.lighting_preset == "random":
            _props._SUSPEND = True
            try:
                presets.apply_defaults(s, "random")
            finally:
                _props._SUSPEND = False
            if s.reference_image is not None:
                lighting.schedule_analyze_and_generate(context)
        else:
            s.lighting_preset = "random"  # _on_preset applies defaults + deferred regen
        self.report({"INFO"}, tr(s.language, "msg_random_preset"))
        return {"FINISHED"}


class RLLX_OT_random_reference(Operator):
    """Generate a random reference image"""
    bl_idname = "rolllux.random_reference"
    bl_label = "Random Reference Image"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        s = context.scene.rolllux
        from . import properties as _props
        if not _props.load_random_reference(context):
            self.report({"ERROR"}, tr(s.language, "err_load", err="random reference"))
            return {"CANCELLED"}
        if lighting.has_rig():
            lighting.schedule_analyze_and_generate(context)
        self.report({"INFO"}, tr(s.language, "msg_random_reference"))
        return {"FINISHED"}


class RLLX_OT_auto_timer(Operator):
    """Toggle a timer that re-generates the lighting on an interval"""
    bl_idname = "rolllux.auto_timer"
    bl_label = "Auto Generate Timer"

    _timer = None

    def execute(self, context):
        s = context.scene.rolllux
        if s.auto_timer:  # already running -> stop
            s.auto_timer = False
            return {"FINISHED"}
        wm = context.window_manager
        if context.window is None:  # headless: nothing to drive a modal loop
            self.report({"WARNING"}, tr(s.language, "err_no_window"))
            return {"CANCELLED"}
        s.auto_timer = True
        self._timer = wm.event_timer_add(s.timer_interval, window=context.window)
        wm.modal_handler_add(self)
        self.report({"INFO"}, tr(s.language, "msg_timer_on"))
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        s = context.scene.rolllux
        if not s.auto_timer:
            self.cancel(context)
            return {"CANCELLED"}
        if event.type == "TIMER":
            from . import properties as _props
            _props.ensure_default_reference(context.scene, context)
            if s.reference_image is not None and not lighting.rig_busy():
                lighting.schedule_analyze_and_generate(context)
        return {"PASS_THROUGH"}

    def cancel(self, context):
        wm = context.window_manager
        if self._timer is not None:
            wm.event_timer_remove(self._timer)
            self._timer = None
        context.scene.rolllux.auto_timer = False
        self.report({"INFO"}, tr(context.scene.rolllux.language, "msg_timer_off"))


class RLLX_OT_reference_step(Operator):
    """Switch to the previous / next reference library image"""
    bl_idname = "rolllux.reference_step"
    bl_label = "Step Reference"
    bl_options = {"REGISTER", "UNDO"}

    direction: IntProperty(default=1)

    def execute(self, context):
        s = context.scene.rolllux
        _schedule_enum_step(
            context, "reference_preset", presets.reference_order(s), self.direction,
        )
        return {"FINISHED"}


class RLLX_OT_set_rendered(Operator):
    """Switch the 3D View to Rendered shading (required for Auto Exposure)"""
    bl_idname = "rolllux.set_rendered"
    bl_label = "Set Rendered Shading"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        from . import auto_exposure
        lang = context.scene.rolllux.language
        if auto_exposure.try_set_rendered_shading(context):
            self.report({"INFO"}, tr(lang, "msg_set_rendered"))
            return {"FINISHED"}
        self.report({"WARNING"}, tr(lang, "err_no_view3d"))
        return {"CANCELLED"}


class RLLX_OT_bake_ae(Operator):
    """Apply current auto exposure to render settings or light intensity, then disable AE"""
    bl_idname = "rolllux.bake_ae"
    bl_label = "Apply Exposure"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        s = context.scene.rolllux
        return s.auto_exposure

    def execute(self, context):
        from . import auto_exposure
        lang = context.scene.rolllux.language
        mode = auto_exposure.apply_auto_exposure(context)
        if mode is None:
            return {"CANCELLED"}
        key = "msg_ae_applied_light" if mode == "LIGHT_RIG" else "msg_ae_baked"
        self.report({"INFO"}, tr(lang, key))
        return {"FINISHED"}


class RLLX_OT_delete_light(Operator):
    """Delete a light from the rig"""
    bl_idname = "rolllux.delete_light"
    bl_label = "Delete Light"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty()

    def execute(self, context):
        lang = context.scene.rolllux.language
        ok = lighting.delete_light(context, self.name)
        if not ok:
            return {"CANCELLED"}
        self.report({"INFO"}, tr(lang, "msg_light_deleted"))
        return {"FINISHED"}


_classes = (
    RLLX_OT_paste_image,
    RLLX_OT_open_image,
    RLLX_OT_analyze,
    RLLX_OT_generate,
    RLLX_OT_clear,
    RLLX_OT_preset_step,
    RLLX_OT_random_preset,
    RLLX_OT_auto_timer,
    RLLX_OT_reference_step,
    RLLX_OT_random_reference,
    RLLX_OT_set_rendered,
    RLLX_OT_bake_ae,
    RLLX_OT_delete_light,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    translations.register_operators_i18n(*_classes)
    translations.apply_operator_i18n(translations.detect_language())


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
