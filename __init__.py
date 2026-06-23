"""RollLux - reference-image lighting for Blender.

Generate a light rig that matches a reference image: multi-purpose presets with
thumbnails, a built-in reference library, real-time tuning, and a floating
in-viewport reference overlay.

Blender 5.0+ extension. Pure Python, zero external dependencies (uses the
numpy bundled with Blender), works fully offline.
"""

from __future__ import annotations

if __package__:
    from . import presets, overlay, properties, operators, ui, translations
else:  # pragma: no cover - fallback when run as a loose script
    import presets
    import overlay
    import properties
    import operators
    import ui
    import translations

_modules = (presets, overlay, properties, operators, ui)

# MARKETPLACE_STRIP_BEGIN mcp
try:
    if __package__:
        from . import mcp_bridge as _mcp_bridge
    else:
        import mcp_bridge as _mcp_bridge
except ImportError:
    _mcp_bridge = None
# MARKETPLACE_STRIP_END mcp


def register():
    for mod in _modules:
        mod.register()
    # MARKETPLACE_STRIP_BEGIN mcp
    if _mcp_bridge is not None:
        _mcp_bridge.register()
    # MARKETPLACE_STRIP_END mcp
    translations.register()


def unregister():
    translations.unregister()
    # MARKETPLACE_STRIP_BEGIN mcp
    if _mcp_bridge is not None:
        _mcp_bridge.unregister()
    # MARKETPLACE_STRIP_END mcp
    for mod in reversed(_modules):
        mod.unregister()
