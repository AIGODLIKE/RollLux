"""Offline tests for the analysis logic (no Blender required).

Run:  py reflight_match/test_offline.py
"""

from __future__ import annotations

import numpy as np

import analysis


def _gradient_image(h, w, bright_x, bright_y, color=(1.0, 0.85, 0.6)):
    """Build an image whose brightest spot sits at (bright_x, bright_y) in
    normalized (-1..1) coords (top-right = +,+)."""
    yy, xx = np.mgrid[0:h, 0:w]
    nx = (xx / (w - 1)) * 2 - 1
    ny = 1 - (yy / (h - 1)) * 2
    dist = np.sqrt((nx - bright_x) ** 2 + (ny - bright_y) ** 2)
    falloff = np.clip(1.0 - dist / 2.5, 0.05, 1.0)
    img = np.stack([falloff * c for c in color], axis=-1).astype(np.float32)
    return img


def _portrait_lit(from_nx: float, from_ny: float, h: int = 160, w: int = 120):
    """Synthetic frontal portrait: elliptical face + directional shading."""
    yy, xx = np.mgrid[0:h, 0:w]
    nx = (xx / max(w - 1, 1)) * 2.0 - 1.0
    ny = 1.0 - (yy / max(h - 1, 1)) * 2.0
    face = ((nx / 0.58) ** 2 + (ny / 0.72) ** 2) < 1.0
    lx, ly = float(from_nx), float(from_ny)
    lz = 0.65
    ndotl = np.clip(0.42 + 0.48 * (nx * lx + ny * ly) + 0.35 * lz, 0.0, 1.0)
    shade = np.where(face, ndotl, 0.12)
    return np.stack([shade * 0.96, shade * 0.86, shade * 0.78], axis=-1).astype(np.float32)


def test_portrait_direction_left_vs_right():
    right = analysis.analyze_rgb(_portrait_lit(0.75, 0.35))
    left = analysis.analyze_rgb(_portrait_lit(-0.75, 0.35))
    assert right.key_screen_pos[0] > 0.15, right.key_screen_pos
    assert left.key_screen_pos[0] < -0.15, left.key_screen_pos
    assert "right" in right.dir_label, right.dir_label
    assert "left" in left.dir_label, left.dir_label
    print("OK portrait direction ->", left.dir_label, right.dir_label,
          tuple(round(c, 2) for c in left.key_screen_pos),
          tuple(round(c, 2) for c in right.key_screen_pos))


def test_portrait_butterfly_top():
    top = analysis.analyze_rgb(_portrait_lit(0.05, 0.85))
    assert top.key_screen_pos[1] > 0.12, top.key_screen_pos
    assert top.dir_v in ("top", "center") or "top" in top.dir_label, top.dir_label
    print("OK portrait butterfly/top ->", top.dir_label, tuple(round(c, 2) for c in top.key_screen_pos))


def test_portrait_key_fill_opposite():
    prof = analysis.analyze_rgb(_portrait_lit(0.7, 0.25), mode="PORTRAIT")
    key = next(s for s in prof.specs if s.role == "key")
    fill = next(s for s in prof.specs if s.role == "fill")
    assert key.direction[0] > 0.1, key.direction
    assert fill.direction[0] < -0.1, fill.direction
    print("OK portrait key/fill oppose ->", key.direction[0], fill.direction[0])


def _split_portrait(split_x: float = -0.12, h: int = 160, w: int = 120):
    """Hard split-lit portrait: sharp vertical terminator on the face."""
    yy, xx = np.mgrid[0:h, 0:w]
    nx = (xx / max(w - 1, 1)) * 2.0 - 1.0
    ny = 1.0 - (yy / max(h - 1, 1)) * 2.0
    face = ((nx / 0.58) ** 2 + (ny / 0.72) ** 2) < 1.0
    lit = nx > split_x
    shade = np.where(face, np.where(lit, 0.96, 0.035), 0.015)
    return np.stack([shade * 0.96, shade * 0.86, shade * 0.78], axis=-1).astype(np.float32)


def _dual_gel_portrait(h: int = 160, w: int = 120):
    """Blue key (right) + magenta accent (left) on a frontal face."""
    yy, xx = np.mgrid[0:h, 0:w]
    nx = (xx / max(w - 1, 1)) * 2.0 - 1.0
    ny = 1.0 - (yy / max(h - 1, 1)) * 2.0
    face = ((nx / 0.58) ** 2 + (ny / 0.72) ** 2) < 1.0
    blue = np.array([0.12, 0.28, 1.0], dtype=np.float32)
    magenta = np.array([1.0, 0.08, 0.48], dtype=np.float32)
    out = np.zeros((h, w, 3), dtype=np.float32)
    for c in range(3):
        channel = np.where(
            face,
            np.where(nx > -0.05, blue[c], np.where(nx < -0.22, magenta[c], 0.02)),
            0.01,
        )
        out[..., c] = channel
    return out


def test_dual_gel_detects_accent():
    prof = analysis.analyze_rgb(_dual_gel_portrait(), mode="PORTRAIT", palette_size=3)
    assert prof.dual_tone, "expected dual-tone gel lighting"
    roles = {s.role for s in prof.specs}
    assert "accent" in roles, roles
    accent = next(s for s in prof.specs if s.role == "accent")
    key = next(s for s in prof.specs if s.role == "key")
    gel_colors = [key.color, accent.color]
    assert any(c[2] > c[0] + 0.1 for c in gel_colors), gel_colors
    assert any(c[0] > c[2] + 0.1 for c in gel_colors), gel_colors
    assert key.color[2] > key.color[0], key.color
    assert accent.color[0] > accent.color[2], accent.color
    print("OK dual gel -> key", tuple(round(c, 2) for c in key.color),
          "accent", tuple(round(c, 2) for c in accent.color))


def test_split_portrait_hard_contrast():
    prof = analysis.analyze_rgb(_split_portrait(), mode="PORTRAIT")
    assert prof.split_score > 0.35, prof.split_score
    assert prof.contrast_ratio > 6.0, prof.contrast_ratio
    assert prof.suggested_contrast_boost > 3.0, prof.suggested_contrast_boost
    assert prof.suggested_tone_shadows < 0.45, prof.suggested_tone_shadows
    key = next(s for s in prof.specs if s.role == "key")
    fill = next(s for s in prof.specs if s.role == "fill")
    assert key.light_type == "SPOT", key.light_type
    assert key.size < 0.45, key.size
    assert fill.energy < 0.08, fill.energy
    print("OK split portrait -> boost", round(prof.suggested_contrast_boost, 2),
          "shadows", round(prof.suggested_tone_shadows, 2),
          "fill", round(fill.energy, 3))


def test_direction_left_vs_right():
    right = analysis.analyze_rgb(_gradient_image(120, 160, 0.7, 0.3))
    left = analysis.analyze_rgb(_gradient_image(120, 160, -0.7, 0.3))
    assert right.key_screen_pos[0] > 0.2, right.key_screen_pos
    assert left.key_screen_pos[0] < -0.2, left.key_screen_pos
    print("OK direction left/right ->", round(left.key_screen_pos[0], 2),
          round(right.key_screen_pos[0], 2))


def test_warm_vs_cool():
    warm = analysis.analyze_rgb(_gradient_image(80, 80, 0.0, 0.0, (1.0, 0.7, 0.4)))
    cool = analysis.analyze_rgb(_gradient_image(80, 80, 0.0, 0.0, (0.4, 0.6, 1.0)))
    assert warm.warmth > 0.6, warm.warmth
    assert cool.warmth < 0.4, cool.warmth
    print("OK warmth warm/cool ->", round(cool.warmth, 2), round(warm.warmth, 2))


def test_modes_produce_specs():
    img = _gradient_image(100, 100, 0.5, 0.4)
    portrait = analysis.analyze_rgb(img, mode="PORTRAIT")
    scene = analysis.analyze_rgb(img, mode="SCENE")
    roles_p = {s.role for s in portrait.specs}
    roles_s = {s.role for s in scene.specs}
    types_p = {s.light_type for s in portrait.specs}
    types_s = {s.light_type for s in scene.specs}
    assert {"key", "fill", "rim"} <= roles_p, roles_p
    assert "rim" not in roles_s, roles_s
    assert "sky" in roles_s, roles_s
    assert "SPOT" in types_p, types_p
    assert "AREA" in types_s and len(types_s) >= 1, types_s
    # Every spec must be a valid Blender light type.
    valid = {"AREA", "SUN", "SPOT", "POINT"}
    for s in portrait.specs + scene.specs:
        assert s.light_type in valid, s.light_type
        assert len(s.direction) == 3 and len(s.color) == 3
    print("OK modes -> portrait", sorted(roles_p), "scene", sorted(roles_s))


def test_contrast_drives_fill():
    # High-contrast (single bright spot, dark surround) vs flat image.
    hi = analysis.analyze_rgb(_gradient_image(100, 100, 0.0, 0.0))
    flat = analysis.analyze_rgb(np.full((100, 100, 3), 0.5, dtype=np.float32))
    assert hi.contrast_ratio >= flat.contrast_ratio
    print("OK contrast hi/flat ->", round(flat.contrast_ratio, 2),
          round(hi.contrast_ratio, 2))


def test_luxpro_labels():
    right = analysis.analyze_rgb(_gradient_image(120, 160, 0.8, 0.3))
    left = analysis.analyze_rgb(_gradient_image(120, 160, -0.8, 0.3))
    top = analysis.analyze_rgb(_gradient_image(120, 160, 0.0, 0.9))
    assert "right" in right.dir_label, right.dir_label
    assert "left" in left.dir_label, left.dir_label
    assert top.dir_v == "top", top.dir_label
    assert 0.0 <= right.dir_confidence <= 1.0
    print("OK luxpro ->", left.dir_label, top.dir_label, right.dir_label)


def test_luxpro_backlight():
    n = 120
    yy, xx = np.mgrid[0:n, 0:n]
    nx = (xx / (n - 1)) * 2 - 1
    ny = 1 - (yy / (n - 1)) * 2
    edge = np.clip((nx ** 2 + ny ** 2) ** 0.5 - 0.3, 0, 1)
    b = np.clip(0.05 + edge * 1.0, 0, 1.2)
    img = np.stack([b, b, b], -1).astype(np.float32)
    prof = analysis.analyze_rgb(img)
    assert prof.backlit, f"expected backlit, got {prof.dir_label}"
    print("OK luxpro backlight ->", prof.dir_label)


def _multicolor_image(n=128):
    """Four colored quadrants so a palette should recover distinct hues."""
    img = np.zeros((n, n, 3), dtype=np.float32)
    h = n // 2
    img[:h, :h] = (1.0, 0.2, 0.2)   # top-left red
    img[:h, h:] = (0.2, 1.0, 0.2)   # top-right green
    img[h:, :h] = (0.2, 0.2, 1.0)   # bottom-left blue
    img[h:, h:] = (1.0, 1.0, 0.2)   # bottom-right yellow
    return img


def _dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def test_palette_distinct_colors():
    img = _multicolor_image()
    pal = analysis.sample_palette(img, analysis._luminance(img), 4)
    assert len(pal) == 4, len(pal)
    cols = [p["color"] for p in pal]
    # Every pair should be meaningfully different (distinct sampling).
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            assert _dist(cols[i], cols[j]) > 0.3, (cols[i], cols[j])
    print("OK palette distinct ->", [tuple(round(c, 2) for c in p["color"]) for p in pal])


def test_color_strategies():
    img = _multicolor_image()
    lum = analysis._luminance(img)
    default = analysis.sample_palette(img, lum, 4, strategy="DEFAULT")
    vivid = analysis.sample_palette(img, lum, 4, strategy="VIVID")
    soft = analysis.sample_palette(img, lum, 4, strategy="SOFT")
    assert len(default) == 4
    assert vivid[0]["color"] != soft[0]["color"]
    print("OK color strategies")


def test_palette_tracks_count():
    img = _multicolor_image()
    prof = analysis.analyze_rgb(img, mode="PORTRAIT", palette_size=4)
    assert len(prof.palette) == 4
    print("OK palette size tracks count ->", len(prof.palette))


def test_exposure_factor():
    def _exposure_factor(exp: int) -> float:
        exp = int(exp)
        if exp >= 1:
            return float(exp)
        if exp == 0:
            return 1.0
        return 2.0 ** float(exp)

    assert abs(_exposure_factor(1) - 1.0) < 1e-6
    assert abs(_exposure_factor(3) - 3.0) < 1e-6
    assert abs(_exposure_factor(-1) - 0.5) < 1e-6
    assert abs(_exposure_factor(-2) - 0.25) < 1e-6
    print("OK exposure factor")


if __name__ == "__main__":
    test_dual_gel_detects_accent()
    test_split_portrait_hard_contrast()
    test_direction_left_vs_right()
    test_portrait_direction_left_vs_right()
    test_portrait_butterfly_top()
    test_portrait_key_fill_opposite()
    test_warm_vs_cool()
    test_modes_produce_specs()
    test_contrast_drives_fill()
    test_luxpro_labels()
    test_luxpro_backlight()
    test_palette_distinct_colors()
    test_color_strategies()
    test_palette_tracks_count()
    test_exposure_factor()
    print("\nAll offline tests passed.")
