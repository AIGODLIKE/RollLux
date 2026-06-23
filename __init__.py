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
    "version": (5, 5, 3),
    "blender": (5, 0, 0),
    "location": "Tool Panel",
    "support": "COMMUNITY",
    "category": "Lighting",
}

if __package__:
    from . import presets, overlay, properties, operators, ui, mcp_bridge, translations
else:  # pragma: no cover - fallback when run as a loose script
    import presets
    import overlay
    import properties
    import operators
    import ui
    import mcp_bridge
    import translations

_modules = (presets, overlay, properties, operators, mcp_bridge, ui)


def register():
    for mod in _modules:
        mod.register()
    translations.register()


def unregister():
    translations.unregister()
    for mod in reversed(_modules):
        mod.unregister()
