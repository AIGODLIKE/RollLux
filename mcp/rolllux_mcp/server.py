"""RollLux MCP server for Cursor / Claude Desktop."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import blender_client, scripts

mcp = FastMCP(
    "RollLux",
    instructions=(
        "Control RollLux lighting in Blender. When the user asks to light, relight, "
        "or match reference lighting on an object, call light_object with the object name. "
        "Use list_scene_objects first if the object name is unknown. "
        "Requires Blender with RollLux extension and RollLux MCP Bridge addon connected."
    ),
)


def _parse_stdout(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if not raw:
        return {"ok": False, "error": "Empty response from Blender"}
    # Prefer the last JSON line (execute_code may print debug lines).
    for line in reversed(raw.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return {"ok": True, "raw": raw}


def _run(script: str) -> dict[str, Any]:
    out = blender_client.execute_code(script)
    return _parse_stdout(out)


@mcp.tool()
def check_blender() -> str:
    """Verify Blender bridge connection and RollLux extension status."""
    try:
        data = _run(scripts.check_setup_script())
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def list_scene_objects(limit: int = 50) -> str:
    """List mesh-like objects in the active Blender scene (for picking a light target)."""
    try:
        data = _run(scripts.list_objects_script(limit=limit))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_object(
    object_name: str,
    reference_image: str | None = None,
    reference_preset: str | None = None,
    preset: str = "auto",
    light_count: int = 3,
    intensity: float = 0.2,
    auto_exposure: bool = True,
    clear_existing: bool = True,
) -> str:
    """Light a Blender object with RollLux (analyze reference + build light rig).

    Args:
        object_name: Exact Blender object name (e.g. Suzanne, Cube, GEO-head).
        reference_image: Optional path to a reference photo on disk.
        reference_preset: Optional built-in library id (e.g. golden_hour, broad_light).
        preset: RollLux lighting strategy (auto, portrait, cinematic, rembrandt, random, ...).
        light_count: Number of lights (1-8).
        intensity: Global intensity multiplier.
        auto_exposure: Enable viewport auto exposure after generation.
        clear_existing: Remove previous RollLux rig before generating.
    """
    object_name = object_name.strip()
    if not object_name:
        return json.dumps({"ok": False, "error": "object_name is required"}, indent=2)

    if reference_image:
        reference_image = reference_image.strip().strip('"')
    if reference_preset:
        reference_preset = reference_preset.strip()

    try:
        script = scripts.light_object_script(
            object_name,
            reference_path=reference_image,
            reference_preset=reference_preset,
            preset=preset,
            light_count=light_count,
            intensity=intensity,
            auto_exposure=auto_exposure,
            clear_existing=clear_existing,
        )
        data = _run(script)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_selection(
    reference_image: str | None = None,
    reference_preset: str | None = None,
    preset: str = "auto",
    light_count: int = 3,
    intensity: float = 0.2,
    auto_exposure: bool = True,
    clear_existing: bool = True,
) -> str:
    """Light the currently selected / active object in Blender with RollLux.

    Uses bpy.context.active_object, or the first selected mesh-like object.
    """
    try:
        script = scripts.light_selection_script(
            reference_path=reference_image.strip().strip('"') if reference_image else None,
            reference_preset=reference_preset.strip() if reference_preset else None,
            preset=preset,
            light_count=light_count,
            intensity=intensity,
            auto_exposure=auto_exposure,
            clear_existing=clear_existing,
        )
        data = _run(script)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_from_left(
    preset: str = "portrait",
    light_count: int = 3,
    intensity: float = 0.22,
) -> str:
    """Generate a left-side distribution reference map and light the selected object."""
    try:
        data = _run(scripts.light_from_left_script(
            preset=preset, light_count=light_count, intensity=intensity,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_apple_product(
    intensity: float = 0.28,
    contrast_boost: float = 1.05,
    light_count: int = 5,
    key_energy: float = 0.12,
    fill_energy: float = 0.10,
    rim_energy: float = 3.6,
    side_rim_energy: float = 3.0,
) -> str:
    """Backlight-first product lighting: strong rear rim strips, weak front/side fill."""
    try:
        data = _run(scripts.light_apple_product_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
            key_energy=key_energy,
            fill_energy=fill_energy,
            rim_energy=rim_energy,
            side_rim_energy=side_rim_energy,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_cyberpunk(
    intensity: float = 0.26,
    contrast_boost: float = 2.5,
    light_count: int = 3,
) -> str:
    """Cyberpunk neon: magenta vs orange-yellow clash, high saturation."""
    try:
        data = _run(scripts.light_cyberpunk_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_xiaomi_product(
    intensity: float = 0.28,
    contrast_boost: float = 0.78,
    light_count: int = 5,
    key_energy: float = 0.42,
    fill_energy: float = 0.26,
    rim_energy: float = 1.2,
    side_rim_energy: float = 2.0,
) -> str:
    """Xiaomi-style product: high-key white studio, soft front, crisp side edge highlights."""
    try:
        data = _run(scripts.light_xiaomi_product_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
            key_energy=key_energy,
            fill_energy=fill_energy,
            rim_energy=rim_energy,
            side_rim_energy=side_rim_energy,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_clean_tech_product(
    intensity: float = 0.26,
    contrast_boost: float = 0.70,
    light_count: int = 5,
    key_energy: float = 0.46,
    fill_energy: float = 0.24,
    rim_energy: float = 0.95,
    side_rim_energy: float = 1.35,
) -> str:
    """Clean cool tech product: high-key ice-white studio, soft front, crisp cool edge strips."""
    try:
        data = _run(scripts.light_clean_tech_product_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
            key_energy=key_energy,
            fill_energy=fill_energy,
            rim_energy=rim_energy,
            side_rim_energy=side_rim_energy,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_tang_dynasty_product(
    intensity: float = 0.24,
    contrast_boost: float = 1.28,
    light_count: int = 5,
    key_energy: float = 0.88,
    fill_energy: float = 0.30,
    accent_energy: float = 0.72,
    rim_energy: float = 1.45,
    silk_glow_energy: float = 0.55,
) -> str:
    """Tang dynasty product mood: imperial gold key, vermillion accent, warm lantern fill."""
    try:
        data = _run(scripts.light_tang_dynasty_product_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
            key_energy=key_energy,
            fill_energy=fill_energy,
            accent_energy=accent_energy,
            rim_energy=rim_energy,
            silk_glow_energy=silk_glow_energy,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_xuanniao_black_amber(
    intensity: float = 0.18,
    contrast_boost: float = 4.2,
    light_count: int = 4,
    key_energy: float = 1.35,
    accent_energy: float = 1.05,
) -> str:
    """Xuan-bird black base with sharp orange-yellow highlights and strong contrast."""
    try:
        data = _run(scripts.light_xuanniao_black_amber_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
            key_energy=key_energy,
            accent_energy=accent_energy,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_black_red_even(
    intensity: float = 0.26,
    contrast_boost: float = 0.88,
    light_count: int = 4,
    key_energy: float = 0.90,
    fill_energy: float = 0.92,
) -> str:
    """Black-red even lighting: dark base with balanced soft red wrap."""
    try:
        data = _run(scripts.light_black_red_even_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
            key_energy=key_energy,
            fill_energy=fill_energy,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_wuwei_july(
    intensity: float = 0.28,
    contrast_boost: float = 2.85,
    light_count: int = 4,
    sun_energy: float = 1.18,
    sky_fill_energy: float = 0.38,
) -> str:
    """Wuwei July: blazing Hexi Corridor midsummer sun with dry sky and loess bounce."""
    try:
        data = _run(scripts.light_wuwei_july_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
            sun_energy=sun_energy,
            sky_fill_energy=sky_fill_energy,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_russian_style(
    intensity: float = 0.24,
    contrast_boost: float = 1.38,
    light_count: int = 4,
    sun_energy: float = 0.82,
    snow_fill_energy: float = 0.68,
) -> str:
    """Russian winter light: low pale sun, icy sky, snow bounce, faint warm accent."""
    try:
        data = _run(scripts.light_russian_style_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
            sun_energy=sun_energy,
            snow_fill_energy=snow_fill_energy,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_keynote_launch(
    intensity: float = 0.25,
    contrast_boost: float = 2.0,
    light_count: int = 6,
    key_energy: float = 1.15,
    fill_energy: float = 0.10,
    accent_energy: float = 1.05,
    rim_energy: float = 2.6,
    side_beam_energy: float = 2.1,
    top_beam_energy: float = 1.85,
) -> str:
    """Dramatic launch keynote: dark stage, hero spotlight, warm/cool accents, layered rims."""
    try:
        data = _run(scripts.light_keynote_launch_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
            key_energy=key_energy,
            fill_energy=fill_energy,
            accent_energy=accent_energy,
            rim_energy=rim_energy,
            side_beam_energy=side_beam_energy,
            top_beam_energy=top_beam_energy,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_cool_beauty_portrait(
    intensity: float = 0.24,
    contrast_boost: float = 0.65,
    light_count: int = 3,
) -> str:
    """Cool high-key beauty portrait: soft butterfly key, clamshell fill, subtle cool rim."""
    try:
        data = _run(scripts.light_cool_beauty_portrait_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_ghibli_vivid(
    intensity: float = 0.27,
    contrast_boost: float = 0.82,
    light_count: int = 5,
    sun_energy: float = 0.95,
) -> str:
    """Miyazaki/Ghibli vivid pastoral: sky blue, meadow green, golden sun, pink-lavender magic."""
    try:
        data = _run(scripts.light_ghibli_vivid_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
            sun_energy=sun_energy,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_vivid_colors(
    intensity: float = 0.28,
    contrast_boost: float = 1.15,
    light_count: int = 5,
) -> str:
    """Bright high-key vivid colors (极色彩): hue-separated gels on a luminous base."""
    try:
        data = _run(scripts.light_vivid_colors_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_jinx(
    intensity: float = 0.24,
    contrast_boost: float = 2.85,
    light_count: int = 4,
    pink_energy: float = 1.32,
    cyan_energy: float = 1.28,
) -> str:
    """Arcane Jinx style: hot pink vs electric cyan neon clash on a dark base."""
    try:
        data = _run(scripts.light_jinx_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
            pink_energy=pink_energy,
            cyan_energy=cyan_energy,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_arcane(
    intensity: float = 0.22,
    contrast_boost: float = 2.15,
    light_count: int = 4,
    amber_energy: float = 1.05,
    teal_energy: float = 0.68,
) -> str:
    """Arcane (双城之战) painterly cinematic: teal haze, amber key, magenta accent, orange rim."""
    try:
        data = _run(scripts.light_arcane_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
            amber_energy=amber_energy,
            teal_energy=teal_energy,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_doraemon(
    intensity: float = 0.28,
    contrast_boost: float = 0.72,
    light_count: int = 4,
    blue_energy: float = 1.05,
    white_energy: float = 0.88,
    red_energy: float = 0.72,
    yellow_energy: float = 0.58,
) -> str:
    """Doraemon palette: cyan-blue body, white belly fill, red nose accent, yellow bell."""
    try:
        data = _run(scripts.light_doraemon_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
            blue_energy=blue_energy,
            white_energy=white_energy,
            red_energy=red_energy,
            yellow_energy=yellow_energy,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def light_vivid_rainbow(
    intensity: float = 0.28,
    contrast_boost: float = 2.2,
    light_count: int = 5,
) -> str:
    """Vivid rainbow lighting: five hue-separated gel colors on a dark vivid reference."""
    try:
        data = _run(scripts.light_vivid_rainbow_script(
            intensity=intensity,
            contrast_boost=contrast_boost,
            light_count=light_count,
        ))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def refresh_strategy_and_distribution() -> str:
    """Re-roll RollLux procedural strategy (preset) and distribution (reference library)."""
    try:
        data = _run(scripts.refresh_roll_script())
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


@mcp.tool()
def clear_rolllux_lighting() -> str:
    """Remove the RollLux light rig from the current Blender scene."""
    try:
        data = _run(scripts.clear_lighting_script())
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
