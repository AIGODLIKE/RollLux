"""Run inside Blender: Scripting → Open → Run Script (Alt+P).

Lights the active / selected object with RollLux.
"""
from __future__ import annotations

import bpy


def main() -> None:
    if not hasattr(bpy.types.Scene, "rolllux"):
        raise RuntimeError("RollLux extension is not enabled.")

    obj = bpy.context.active_object
    if obj is None:
        sel = [
            o for o in bpy.context.selected_objects
            if o.type in {"MESH", "CURVE", "SURFACE", "META", "FONT"}
        ]
        if not sel:
            raise RuntimeError("No mesh-like object selected.")
        obj = sel[0]
        bpy.context.view_layer.objects.active = obj

    s = bpy.context.scene.rolllux
    s.target_mode = "SELECTED"
    s.lighting_preset = "auto"
    s.light_count = 3
    bpy.ops.rolllux.generate()
    print(f"RollLux: generated lighting for {obj.name}")


if __name__ == "__main__":
    main()
