"""Offline tests for the analysis logic (no Blender required).

Run:  py reflight_match/test_offline.py
"""

from __future__ import annotations

import numpy as np

import analysis
import gen_assets


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
    assert key.color[0] > key.color[2], key.color
    assert accent.color[2] > accent.color[0], accent.color
    print("OK dual gel -> key", tuple(round(c, 2) for c in key.color),
          "accent", tuple(round(c, 2) for c in accent.color))


def test_rig_colors_match_lights():
    prof = analysis.analyze_rgb(_dual_gel_portrait(), mode="PORTRAIT", palette_size=3)
    rig_cols = analysis.rig_colors_in_order(prof, 3)
    assert rig_cols[0] == prof.key_color
    assert rig_cols[1] == prof.accent_color
    assert rig_cols[2] == prof.rim_color
    key = next(s for s in prof.specs if s.role == "key")
    accent = next(s for s in prof.specs if s.role == "accent")
    rim = next(s for s in prof.specs if s.role == "rim")
    assert key.color == prof.key_color
    assert accent.color == prof.accent_color
    assert rim.color == prof.rim_color
    print("OK rig colors match lights ->", [tuple(round(c, 2) for c in c) for c in rig_cols])


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
    distinct = analysis.sample_palette(img, lum, 4, strategy="DISTINCT")
    assert len(default) == 4
    assert len(distinct) == 4
    assert vivid[0]["color"] != soft[0]["color"]
    assert _min_hue_separation([p["color"] for p in distinct]) >= 0.10
    print("OK color strategies")


def _similar_warm_reference(n=128):
    """Three close warm blobs plus one cyan patch."""
    return gen_assets.make_ref(
        n,
        base=0.05,
        tint=(0.5, 0.4, 0.3),
        blobs=[
            (-0.5, 0.2, 1.5, 1.0, (1.2, 0.82, 0.30)),
            (0.0, 0.3, 1.5, 1.0, (1.15, 0.78, 0.28)),
            (0.5, 0.2, 1.5, 1.0, (1.1, 0.75, 0.25)),
            (-0.2, -0.4, 1.8, 1.2, (0.15, 0.75, 1.35)),
        ],
    ).astype(np.float32)


def test_distinct_skips_similar_warm():
    img = _similar_warm_reference()
    lum = analysis._luminance(img)
    vivid = analysis.sample_palette(img, lum, 4, strategy="VIVID")
    distinct = analysis.sample_palette(img, lum, 4, strategy="DISTINCT")
    assert len(distinct) >= 2

    def _is_cool(c):
        return c[2] > c[0] and c[2] > c[1] - 0.05

    assert any(_is_cool(p["color"]) for p in distinct)
    rounded = [tuple(round(c, 2) for c in p["color"]) for p in distinct]
    assert len(set(rounded)) >= 2
    vivid_warm = sum(1 for p in vivid if p["color"][0] >= p["color"][2])
    distinct_warm = sum(1 for p in distinct if p["color"][0] >= p["color"][2])
    assert distinct_warm <= vivid_warm
    if len(distinct) >= 2:
        assert _min_hue_separation([p["color"] for p in distinct]) >= 0.08
    print("OK distinct skips similar warm ->", rounded)


def test_color_strategy_distinct_i18n():
    import translations
    from translations import TR

    for lang, label in (("EN", "Distinct"), ("ZH", "异色分立"), ("JA", "色相分離")):
        assert TR["color_strategy_distinct"][lang] == label
        desc = TR["color_strategy_distinct_desc"][lang]
        assert desc and not desc.startswith("color_strategy_")

    names = [name for _ident, name, _desc in translations.color_strategy_items(None, None)]
    assert "Distinct" in names
    print("OK color strategy distinct i18n")


def test_distribution_color_mode_i18n():
    import translations
    from translations import TR

    for lang, labels in (
        ("EN", ("Balanced", "Vivid", "Soft")),
        ("ZH", ("均衡", "极色彩", "柔和")),
        ("JA", ("均衡", "ビビッド", "ソフト")),
    ):
        for suffix, label in zip(("balanced", "vivid", "soft"), labels):
            key = f"distribution_color_mode_{suffix}"
            assert TR[key][lang] == label, (lang, key)

    names = [name for _ident, name, _desc in translations.distribution_color_mode_items(None, None)]
    assert names == ["Balanced", "Vivid", "Soft"], names
    print("OK distribution color mode i18n")


def _tang_style_reference(n=128):
    """Dark base + separated warm gold left, vermillion right, amber bottom."""
    gold = (1.2, 0.82, 0.30)
    verm = (1.3, 0.08, 0.06)
    amber = (1.0, 0.58, 0.20)
    silk = (1.0, 0.86, 0.58)
    deep = (0.88, 0.52, 0.16)
    return gen_assets.make_ref(
        n,
        base=0.03,
        tint=(0.55, 0.40, 0.28),
        blobs=[
            (-0.58, 0.24, 1.55, 1.15, gold),
            (0.62, 0.18, 1.75, 1.45, verm),
            (0.0, -0.30, 1.10, 0.75, amber),
            (0.0, 0.52, 0.92, 0.55, deep),
            (-0.32, 0.42, 0.75, 0.45, silk),
        ],
        vignette=0.28,
    ).astype(np.float32)


def test_tang_palette_not_collapsed():
    img = _tang_style_reference()
    pal = analysis.sample_palette(img, analysis._luminance(img), 5, strategy="VIVID")
    assert len(pal) == 5
    assert any(
        c[0] > 0.95 and c[1] < 0.42 and c[2] < 0.22
        for c in (p["color"] for p in pal)
    ), [p["color"] for p in pal]
    rounded = [tuple(round(c, 2) for c in p["color"]) for p in pal]
    assert len(set(rounded)) >= 4, rounded
    print("OK tang palette ->", rounded)


def test_rig_colors_use_palette_per_light():
    img = _tang_style_reference()
    prof = analysis.analyze_rgb(img, mode="PORTRAIT", palette_size=5, color_strategy="VIVID")
    rig = analysis.rig_colors_in_order(prof, 5)
    pal_cols = [tuple(round(c, 2) for c in p["color"]) for p in prof.palette]
    rig_round = [tuple(round(c, 2) for c in c) for c in rig]
    assert rig_round == pal_cols[:5]
    assert len(set(rig_round)) >= 4, rig_round
    role_triple = {
        tuple(round(c, 2) for c in prof.key_color),
        tuple(round(c, 2) for c in prof.fill_color),
        tuple(round(c, 2) for c in prof.rim_color),
    }
    assert len(set(rig_round)) > len(role_triple), (rig_round, role_triple)
    print("OK rig palette per light ->", rig_round)


def _rgb_hue(rgb):
    r, g, b = (float(rgb[0]), float(rgb[1]), float(rgb[2]))
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 1e-6:
        return 0.0
    d = mx - mn
    if mx == r:
        h = (g - b) / d + (6.0 if g < b else 0.0)
    elif mx == g:
        h = (b - r) / d + 2.0
    else:
        h = (r - g) / d + 4.0
    return (h / 6.0) % 1.0


def _min_hue_separation(colors):
    hues = [_rgb_hue(c) for c in colors]
    if len(hues) < 2:
        return 1.0
    best = 1.0
    for i, h0 in enumerate(hues):
        for h1 in hues[i + 1:]:
            d = abs(h0 - h1)
            best = min(best, d, 1.0 - d)
    return best


def _color_chroma(rgb):
    r, g, b = (float(rgb[0]), float(rgb[1]), float(rgb[2]))
    return max(r, g, b) - min(r, g, b)


def test_distribution_color_modes():
    import random
    from gen_assets import build_random_reference_params, make_ref

    for seed in range(24):
        rng = random.Random(seed)
        vivid = build_random_reference_params("VIVID", rng)
        blob_cols = [b[4] for b in vivid["blobs"]]
        assert len(blob_cols) >= 3
        assert vivid["base"] <= 0.12
        assert _min_hue_separation(blob_cols) >= 0.12

    for seed in range(24):
        rng = random.Random(seed)
        soft = build_random_reference_params("SOFT", rng)
        assert soft["base"] >= 0.28
        assert len(soft["blobs"]) <= 2
        for col in [b[4] for b in soft["blobs"]] + [soft["tint"]]:
            assert _color_chroma(col) <= 0.12

    rng = random.Random(7)
    lin = make_ref(128, **build_random_reference_params("VIVID", rng))
    pal = analysis.sample_palette(lin, analysis._luminance(lin), 5, strategy="VIVID")
    rounded = [tuple(round(c, 2) for c in p["color"]) for p in pal]
    assert len(set(rounded)) >= 3, rounded
    print("OK distribution color modes ->", rounded)


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


def test_auto_exposure_metering():
    from ae_metering import meter_luminance, compute_target_ev, target_luminance, prepare_samples

    samples = [0.05, 0.1, 0.12, 0.15, 0.9, 0.95]
    center = [0.1, 0.12, 0.15]
    avg = meter_luminance(samples, center, "AVERAGE", 0.0)
    assert abs(avg - sum(samples) / len(samples)) < 1e-6
    med = meter_luminance(samples, center, "MEDIAN", 0.0)
    assert abs(med - 0.135) < 1e-6
    hi = meter_luminance(samples, center, "HIGHLIGHT", 0.0)
    assert hi >= 0.9
    p60 = meter_luminance(samples, center, "P60", 0.0)
    assert 0.12 <= p60 <= 0.95
    trim = meter_luminance(samples, center, "TRIM_MEAN", 0.0)
    assert trim < hi
    log_avg = meter_luminance(samples, center, "LOG_AVERAGE", 0.0)
    assert log_avg > 0.0

    prepared, ok = prepare_samples([0.0, 0.0, 0.0, 0.0, 0.1])
    assert not ok
    prepared, ok = prepare_samples([0.0, 0.1, 0.2, 0.3])
    assert ok and len(prepared) == 4

    ev = compute_target_ev(0.36, 0.18, 0.0)
    assert abs(ev - (-1.0)) < 1e-6
    ev_bias = compute_target_ev(0.36, 0.18, -1.0)
    assert abs(ev_bias - (-2.0)) < 1e-6

    class _Res:
        valid = True
        mean_luminance = 0.42

    class _Settings:
        ae_mode = "REFERENCE"
        cache_mean_lum = 0.3

    class _Scene:
        rolllux_result = _Res()

    assert abs(target_luminance(_Settings(), _Scene()) - 0.42) < 1e-6
    print("OK auto exposure metering")


def test_ae_enum_i18n():
    import translations
    from translations import TR

    for ident, name, desc in translations.ae_apply_to_items(None, None):
        assert not name.startswith("ae_"), name
        assert name in ("Color Management", "Light Rig"), name
    for ident, name, desc in translations.ae_center_preset_items(None, None):
        assert not name.startswith("ae_"), name
    assert TR["ae_center_balanced"]["EN"] == "Balanced"
    print("OK ae enum i18n")


def test_ui_mode_i18n():
    import translations

    names = [name for _id, name, _d in translations.ui_mode_items(None, None)]
    assert "Quick" in names and "Pro" in names
    print("OK ui mode i18n")


def test_i18n_completeness():
    import translations
    from translations import TR, _PROP_DESC, _OPERATOR_LABELS

    for key, entry in TR.items():
        assert isinstance(entry, dict), key
        for lang in ("EN", "ZH", "JA"):
            assert lang in entry and str(entry[lang]).strip(), f"{key}.{lang}"

    for prop, desc_key in _PROP_DESC.items():
        assert desc_key in TR, f"_PROP_DESC {prop} -> {desc_key}"

    ui_keys = set()
    import re, os
    root = os.path.dirname(__file__)
    for fn in ("ui.py", "operators.py"):
        text = open(os.path.join(root, fn), encoding="utf-8").read()
        ui_keys.update(re.findall(r"""tr\(\s*['\"]([a-zA-Z0-9_]+)['\"]""", text))
    for key in ui_keys:
        assert key in TR, f"missing UI key {key!r}"

    for bl_id, tr_key in _OPERATOR_LABELS.items():
        assert tr_key in TR, f"operator {bl_id} -> {tr_key}"

    for ident, name, _desc in translations.ui_mode_items(None, None):
        assert name in ("Quick", "Pro"), name
    assert TR["ui_mode_quick"]["ZH"] and TR["ui_mode_pro"]["ZH"]
    print("OK i18n completeness")


def test_blender_reg_map():
    import translations

    raw = {"Hello": "你好", "Hello.": "你好。"}
    reg = translations._blender_reg_map(raw)
    assert (None, "Hello") in reg
    assert (None, "Hello.") in reg
    assert all(isinstance(k, tuple) and len(k) == 2 for k in reg)
    print("OK blender reg map")


if __name__ == "__main__":
    test_dual_gel_detects_accent()
    test_rig_colors_match_lights()
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
    test_distinct_skips_similar_warm()
    test_color_strategy_distinct_i18n()
    test_distribution_color_mode_i18n()
    test_tang_palette_not_collapsed()
    test_rig_colors_use_palette_per_light()
    test_distribution_color_modes()
    test_palette_tracks_count()
    test_exposure_factor()
    test_auto_exposure_metering()
    test_ae_enum_i18n()
    test_ui_mode_i18n()
    test_i18n_completeness()
    test_blender_reg_map()
    print("\nAll offline tests passed.")
