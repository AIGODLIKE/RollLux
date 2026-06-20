"""RollLux - reference-image lighting for Blender.

Generate a light rig that matches a reference image: multi-purpose presets with
thumbnails, a built-in reference library, real-time tuning, and a floating
in-viewport reference overlay.

Blender 5.0+ extension. Pure Python, zero external dependencies (uses the
numpy bundled with Blender), works fully offline.
"""

from __future__ import annotations

bl_info = {
    "name": "RollLux",
    "description": "Roll random lighting from reference images with one click.",
    "author": "ACGGIT",
    "version": (4, 3, 13),
    "blender": (5, 0, 0),
    "location": "Tool Panel",
    "support": "COMMUNITY",
    "category": "Lighting",
}

if __package__:
    from . import presets, overlay, properties, operators, ui
else:  # pragma: no cover - fallback when run as a loose script
    import presets
    import overlay
    import properties
    import operators
    import ui

_modules = (presets, overlay, properties, operators, ui)


def register():
    for mod in _modules:
        mod.register()


def unregister():
    for mod in reversed(_modules):
        mod.unregister()


if __name__ == "__main__":
    register()
