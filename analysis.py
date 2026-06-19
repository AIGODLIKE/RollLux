"""Reference image analysis (pure numpy, no external dependencies).

Everything here is engine/Blender agnostic except :func:`image_to_rgb`, which is
the only function that touches ``bpy``. All the math operates on a plain
``(H, W, 3)`` float array in scene-linear space so it can be unit-tested
headlessly.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

# Rec.709 luminance weights (linear).
_LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)

# Longest edge the analysis runs on. Reference images get strided down to this
# so a 4K frame stays well under a millisecond.
_MAX_EDGE = 256


@dataclass
class LightSpec:
    """A single light the generator should create.

    Directions are expressed in a *camera-relative* basis:
    ``right`` (image +x), ``up`` (image +y) and ``back`` (toward the camera).
    The lighting module turns these into world coordinates around the target.
    """

    role: str               # "key" | "fill" | "rim" | "ambient" | "accent"
    light_type: str         # "AREA" | "SUN" | "SPOT" | "POINT"
    direction: tuple        # (rx, uy, back) unit-ish vector in camera basis
    color: tuple            # linear RGB
    energy: float           # relative energy (scaled later by distance/mult)
    size: float             # relative softness (area radius / spot blend / sun angle)


@dataclass
class LightingProfile:
    """Result of analysing a reference image."""

    key_color: tuple = (1.0, 1.0, 1.0)
    fill_color: tuple = (0.5, 0.5, 0.55)
    ambient_color: tuple = (0.05, 0.05, 0.06)
    rim_color: tuple = (1.0, 1.0, 1.0)

    mean_luminance: float = 0.5
    contrast_ratio: float = 4.0          # key / fill
    key_screen_pos: tuple = (0.4, 0.3)   # normalized (-1..1, -1..1), top-right = bright
    color_temperature: float = 5500.0    # approximate Kelvin
    warmth: float = 0.5                  # 0 cool .. 1 warm

    mood: str = "neutral"                # "high_key" | "low_key" | "neutral"
    is_outdoor: bool = False

    # LuxPro direction read-out
    dir_h: str = "center"                # "left" | "center" | "right"
    dir_v: str = "center"                # "top" | "center" | "bottom"
    dir_label: str = "center"            # combined id, e.g. "top_right", "backlight"
    dir_confidence: float = 0.0          # 0..1
    backlit: bool = False

    # Tone / contrast read-out (drives rig hardness and slider seeding).
    hardness: float = 0.35           # 0 soft .. 1 hard (sharp terminator)
    split_score: float = 0.0         # 0 .. 1 split / side-light strength
    shadow_frac: float = 0.0         # fraction of deep-shadow pixels
    suggested_contrast_boost: float = 1.0
    suggested_tone_shadows: float = 1.0

    dual_tone: bool = False
    accent_color: tuple = (1.0, 0.2, 0.5)
    accent_pos: tuple = (-0.4, 0.2)

    # Dominant-color palette (brightest first); each entry:
    #   {"color": (r,g,b), "lum": float, "pos": (nx, ny), "weight": float}
    palette: list = field(default_factory=list)
    # Downsampled arrays kept around so the palette can be re-clustered to an
    # arbitrary light count at generation time. Excluded from repr/compare.
    rgb_small: object = field(default=None, repr=False, compare=False)
    lum_small: object = field(default=None, repr=False, compare=False)

    specs: list = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Low level helpers
# --------------------------------------------------------------------------- #
def _luminance(rgb: np.ndarray) -> np.ndarray:
    return np.tensordot(rgb, _LUMA, axes=([-1], [0]))


def _safe_mean_color(rgb_flat: np.ndarray) -> np.ndarray:
    if rgb_flat.size == 0:
        return np.array([0.5, 0.5, 0.5], dtype=np.float32)
    return np.clip(rgb_flat.mean(axis=0), 0.0, None)


# Global color-sampling strategies (applied to palette + key/fill/ambient).
COLOR_STRATEGIES = ("DEFAULT", "VIVID", "SOFT")


def _normalize_color(color: np.ndarray) -> tuple:
    """Scale a color so its brightest channel is 1.0 (hue/chroma only)."""
    color = np.asarray(color, dtype=np.float32)
    peak = float(color.max())
    if peak <= 1e-6:
        return (1.0, 1.0, 1.0)
    out = color / peak
    return (float(out[0]), float(out[1]), float(out[2]))


def apply_color_strategy(color, strategy: str = "DEFAULT") -> tuple:
    """Remap a linear RGB triple according to the global sampling strategy."""
    if strategy not in COLOR_STRATEGIES or strategy == "DEFAULT":
        return _normalize_color(np.asarray(color, dtype=np.float32))
    r, g, b = (float(color[0]), float(color[1]), float(color[2]))
    lum = float(_LUMA @ np.array([r, g, b], dtype=np.float32))
    if strategy == "VIVID":
        sat = 1.65
        out = np.array([lum + (c - lum) * sat for c in (r, g, b)], dtype=np.float32)
        return _normalize_color(np.clip(out, 0.0, None))
    # SOFT — pull saturation down and lean toward a neutral warm gray.
    sat = 0.42
    neutral = np.array([0.93, 0.91, 0.89], dtype=np.float32)
    out = np.array([lum + (c - lum) * sat for c in (r, g, b)], dtype=np.float32)
    out = out * 0.82 + neutral * 0.18
    return _normalize_color(np.clip(out, 0.0, None))


def _estimate_kelvin(color: np.ndarray) -> float:
    """Very rough correlated color temperature from a linear RGB triple.

    Uses the red/blue balance; good enough to drive a warm/cool decision and a
    display read-out, not a colorimetric measurement.
    """
    r = float(color[0]) + 1e-4
    b = float(color[2]) + 1e-4
    ratio = r / b
    # ratio ~1 -> daylight ~6500K, warm (ratio>1) -> lower K, cool -> higher K.
    kelvin = 6500.0 / (ratio ** 0.7)
    return float(max(1500.0, min(15000.0, kelvin)))


# --------------------------------------------------------------------------- #
# Core analysis
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# Light direction (LuxPro)
# --------------------------------------------------------------------------- #
def _subject_mask(h: int, w: int, margin: float = 0.12) -> np.ndarray:
    """Center crop mask — keeps the subject region, drops most background."""
    y0, y1 = int(h * margin), int(h * (1.0 - margin))
    x0, x1 = int(w * margin), int(w * (1.0 - margin))
    mask = np.zeros((h, w), dtype=bool)
    if y1 > y0 and x1 > x0:
        mask[y0:y1, x0:x1] = True
    return mask


def _screen_norm(cx: float, cy: float, w: int, h: int) -> tuple[float, float]:
    nx = (cx / max(w - 1, 1)) * 2.0 - 1.0
    ny = 1.0 - (cy / max(h - 1, 1)) * 2.0
    return float(np.clip(nx, -1, 1)), float(np.clip(ny, -1, 1))


def _unit_dir(nx: float, ny: float) -> tuple[float, float, float]:
    mag = float((nx * nx + ny * ny) ** 0.5)
    if mag < 1e-4:
        return 0.0, 0.0, 0.0
    return nx / mag, ny / mag, min(mag, 1.0)


def _asymmetry_direction(lum: np.ndarray, mask: np.ndarray) -> tuple[float, float, float]:
    """Left/right and top/bottom luminance imbalance (strong on portraits)."""
    h, w = lum.shape
    cols = np.arange(w, dtype=np.int32)
    rows = np.arange(h, dtype=np.int32)
    cx_mid, cy_mid = w * 0.5, h * 0.5

    left = mask & (cols[None, :] < cx_mid)
    right = mask & (cols[None, :] >= cx_mid)
    top = mask & (rows[:, None] < cy_mid)
    bottom = mask & (rows[:, None] >= cy_mid)

    if not left.any() or not right.any() or not top.any() or not bottom.any():
        return 0.0, 0.0, 0.0

    l_mean = float(lum[left].mean())
    r_mean = float(lum[right].mean())
    t_mean = float(lum[top].mean())
    b_mean = float(lum[bottom].mean())

    asym_x = (r_mean - l_mean) / (r_mean + l_mean + 1e-6)
    asym_y = (t_mean - b_mean) / (t_mean + b_mean + 1e-6)
    nx, ny, conf = _unit_dir(float(np.clip(asym_x, -1, 1)),
                             float(np.clip(asym_y, -1, 1)))
    return nx, ny, conf


def _shadow_highlight_direction(lum: np.ndarray, mask: np.ndarray) -> tuple[float, float, float]:
    """Vector from shadow mass to highlight mass inside the subject mask."""
    vals = lum[mask]
    if vals.size < 32:
        return 0.0, 0.0, 0.0
    p22, p78 = np.percentile(vals, [22, 78])
    h, w = lum.shape
    ys, xs = np.mgrid[0:h, 0:w]
    sh = mask & (lum <= p22)
    hi = mask & (lum >= p78)
    if not sh.any() or not hi.any():
        return 0.0, 0.0, 0.0

    dx = float(xs[hi].mean() - xs[sh].mean())
    dy = float(ys[sh].mean() - ys[hi].mean())  # screen +y = up
    nx, ny, conf = _unit_dir(dx / max(w, 1) * 2.5, dy / max(h, 1) * 2.5)
    return nx, ny, conf


def _highlight_centroid(lum: np.ndarray, mask: np.ndarray,
                        floor_pct: float = 55.0) -> tuple[float, float, float]:
    """Brightness-weighted centroid of above-median pixels."""
    vals = lum[mask]
    if vals.size == 0:
        return 0.0, 0.0, 0.0
    floor = float(np.percentile(vals, floor_pct))
    h, w = lum.shape
    ys, xs = np.mgrid[0:h, 0:w]
    active = mask & (lum >= floor)
    if not active.any():
        return 0.0, 0.0, 0.0
    weight = np.clip(lum - floor, 0.0, None)
    weight = weight * active
    total = float(weight.sum()) + 1e-6
    cx = float((weight * xs).sum() / total)
    cy = float((weight * ys).sum() / total)
    nx, ny = _screen_norm(cx, cy, w, h)
    _, _, conf = _unit_dir(nx, ny)
    return nx, ny, conf


def _gradient_direction(lum: np.ndarray, mask: np.ndarray) -> tuple[float, float, float]:
    """Dominant luminance gradient — points toward the lit side."""
    gy, gx = np.gradient(lum.astype(np.float64))
    mag = np.sqrt(gx * gx + gy * gy)
    if not mask.any():
        return 0.0, 0.0, 0.0
    thresh = float(np.percentile(mag[mask], 55))
    active = mask & (mag >= thresh)
    if not active.any():
        return 0.0, 0.0, 0.0
    h, w = lum.shape
    gxn = float(gx[active].mean()) * w
    gyn = float(-gy[active].mean()) * h
    return _unit_dir(float(np.clip(gxn, -1, 1)), float(np.clip(gyn, -1, 1)))


def _detect_backlight(lum: np.ndarray, mask: np.ndarray) -> bool:
    """Bright rim ring around a darker subject core."""
    h, w = lum.shape
    cy0, cy1 = h // 4, h - h // 4
    cx0, cx1 = w // 4, w - w // 4
    center = float(lum[cy0:cy1, cx0:cx1].mean())
    overall = float(lum.mean())
    inner = (cy1 - cy0) * (cx1 - cx0)
    border_sum = float(lum.sum()) - float(lum[cy0:cy1, cx0:cx1].sum())
    border = border_sum / max(1, lum.size - inner)

    # Edge ring inside the subject crop (hair/back rim on portraits).
    edge_mask = mask.copy()
    y0, y1 = int(h * 0.18), int(h * 0.82)
    x0, x1 = int(w * 0.18), int(w * 0.82)
    edge_mask[y0:y1, x0:x1] = False
    rim = float(lum[edge_mask].mean()) if edge_mask.any() else border

    core = float(lum[mask].mean()) if mask.any() else center
    return bool(
        (border > center * 1.35 and center <= overall * 1.08)
        or (rim > core * 1.25 and core < overall * 1.05)
    )


def _blend_directions(components: list[tuple[float, float, float]],
                      weights: list[float]) -> tuple[float, float, float]:
    """Weighted vector sum of (nx, ny, confidence) estimates."""
    sx = sy = sw = 0.0
    for (nx, ny, conf), w in zip(components, weights):
        eff = w * max(conf, 0.05)
        sx += nx * conf * eff
        sy += ny * conf * eff
        sw += eff
    if sw < 1e-6:
        return 0.0, 0.0, 0.0
    nx, ny, conf = _unit_dir(sx / sw, sy / sw)
    return nx, ny, conf


def estimate_light_direction(lum: np.ndarray, key_screen_pos=None) -> dict:
    """Estimate dominant key-light direction on the image plane.

    Fuses asymmetry, shadow→highlight vector, highlight centroid, and
    gradient cues — tuned for portrait reference images.
    """
    h, w = lum.shape
    mask = _subject_mask(h, w)
    initial = key_screen_pos or (0.0, 0.0)

    asym = _asymmetry_direction(lum, mask)
    sh_hi = _shadow_highlight_direction(lum, mask)
    centroid = _highlight_centroid(lum, mask)
    gradient = _gradient_direction(lum, mask)

    bx, by, blend_conf = _blend_directions(
        [asym, sh_hi, centroid, gradient],
        [0.42, 0.28, 0.18, 0.12],
    )
    if blend_conf < 0.04:
        bx, by = float(initial[0]), float(initial[1])
        blend_conf = _unit_dir(bx, by)[2]

    backlit = _detect_backlight(lum, mask)

    # Discrete 3×3 vote refines continuous estimate near bucket boundaries.
    ys = np.linspace(0, h, 4).astype(int)
    xs = np.linspace(0, w, 4).astype(int)
    cells = np.zeros((3, 3), dtype=np.float64)
    for r in range(3):
        for c in range(3):
            cells[r, c] = lum[ys[r]:ys[r + 1], xs[c]:xs[c + 1]].mean()
    rr, cc = np.unravel_index(int(np.argmax(cells)), cells.shape)
    cell_nx = float(cc - 1)
    cell_ny = float(1 - rr)
    bx = bx * 0.72 + cell_nx * 0.28
    by = by * 0.72 + cell_ny * 0.28
    bx = float(np.clip(bx, -1, 1))
    by = float(np.clip(by, -1, 1))

    thresh = 0.12
    h_label = "left" if bx < -thresh else ("right" if bx > thresh else "center")
    v_label = "top" if by > thresh else ("bottom" if by < -thresh else "center")

    if backlit:
        label = "backlight"
    elif v_label != "center" and h_label != "center":
        label = f"{v_label}_{h_label}"
    elif v_label != "center":
        label = v_label
    elif h_label != "center":
        label = h_label
    else:
        label = "front"

    side_strength = abs(bx) + abs(by)
    confidence = float(min(1.0, side_strength * 0.65 + blend_conf * 0.35
                          + (0.15 if backlit else 0.0)))
    return {
        "dir_h": h_label, "dir_v": v_label, "dir_label": label,
        "dir_confidence": round(confidence, 3), "backlit": backlit,
        "refined_pos": (bx, by),
        "side_strength": side_strength,
    }


def luxpro_direction(lum: np.ndarray, key_screen_pos):
    """Classify the dominant lighting direction from a luminance map."""
    return estimate_light_direction(lum, key_screen_pos)


def _analyze_tone(lum: np.ndarray) -> dict:
    """Measure dynamic range, shadow crush, and terminator sharpness."""
    h, w = lum.shape
    mask = _subject_mask(h, w)
    vals = lum[mask]
    if vals.size < 32:
        return {
            "lum_ratio": 4.0, "spread": 0.3, "shadow_frac": 0.0,
            "hardness": 0.35, "split_score": 0.0,
        }

    p5, p10, p90, p95 = np.percentile(vals, [5, 10, 90, 95])
    lum_ratio = float(p95 / max(float(p5), 0.006))
    spread = float(p90 - p10)
    shadow_frac = float((vals <= p10).mean())

    cx = w // 2
    col = lum[:, max(0, cx - 2):min(w, cx + 3)].mean(axis=1).astype(np.float64)
    grad = np.abs(np.gradient(col))
    hardness = float(np.clip(float(grad.max()) / (spread + 0.04), 0.0, 1.0))

    _, _, asym_conf = _asymmetry_direction(lum, mask)
    split_score = float(np.clip(
        asym_conf * min(spread / 0.35, 1.25) * min(lum_ratio / 6.0, 1.35),
        0.0, 1.0,
    ))
    if shadow_frac > 0.22 and spread > 0.28:
        split_score = float(min(1.0, split_score + shadow_frac * 0.45))

    return {
        "lum_ratio": lum_ratio,
        "spread": spread,
        "shadow_frac": shadow_frac,
        "hardness": hardness,
        "split_score": split_score,
    }


def _suggest_tuning(contrast_ratio: float, tone: dict, mood: str) -> tuple[float, float]:
    """Map analyzed tone to contrast_boost and tone_shadows slider defaults."""
    boost = float(np.clip(math.sqrt(max(contrast_ratio, 1.0)) * 1.15, 1.0, 12.0))
    split = tone["split_score"]
    hard = tone["hardness"]
    if split > 0.35:
        boost *= 1.0 + split * 0.55
    if hard > 0.30:
        boost *= 1.0 + hard * 0.35
    if mood == "low_key":
        boost *= 1.12
    boost = float(np.clip(boost, 1.0, 12.0))

    shadows = 1.0
    if mood == "low_key" or split > 0.32:
        shadows = float(np.clip(
            0.18 + (1.0 - split) * 0.28 + (1.0 - tone["shadow_frac"]) * 0.12,
            0.08, 1.0,
        ))
    if hard > 0.45 and split > 0.4:
        shadows = min(shadows, 0.22)
    return boost, shadows


def _chroma_of(color) -> float:
    c = np.asarray(color, dtype=np.float32)
    peak = float(c.max())
    if peak <= 1e-6:
        return 0.0
    return float((peak - c.min()) / peak)


def _rgb_hue(color) -> float:
    """Hue in 0..1 (HSV), undefined greys -> -1."""
    r, g, b = (float(color[0]), float(color[1]), float(color[2]))
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 1e-5:
        return -1.0
    d = mx - mn
    if mx == r:
        h = ((g - b) / d) % 6.0
    elif mx == g:
        h = (b - r) / d + 2.0
    else:
        h = (r - g) / d + 4.0
    return float(h / 6.0)


def _hue_distance(a: float, b: float) -> float:
    if a < 0.0 or b < 0.0:
        return 0.0
    d = abs(a - b)
    return min(d, 1.0 - d)


def _distinct_hue_entries(entries: list, min_sep: float = 0.08) -> list:
    """Keep the strongest clusters that are hue-distinct (for gel / dual-tone)."""
    ranked = sorted(entries, key=lambda e: e["weight"], reverse=True)
    kept: list = []
    for entry in ranked:
        h = _rgb_hue(entry["color"])
        if h < 0.0:
            kept.append(entry)
            continue
        if all(
            _hue_distance(h, _rgb_hue(k["color"])) >= min_sep or _rgb_hue(k["color"]) < 0.0
            for k in kept
        ):
            kept.append(entry)
    return kept or ranked


def _assign_gel_roles(palette: list, key_screen_pos: tuple | None = None) -> tuple:
    """Primary gel (key) vs secondary (accent) by cluster weight; return positions."""
    distinct = _top_distinct_palette(palette, 2)
    if len(distinct) < 2:
        c = palette[0]["color"]
        p = palette[0]["pos"]
        return c, c, p, p
    if distinct[0]["weight"] >= distinct[1]["weight"]:
        key_e, accent_e = distinct[0], distinct[1]
    else:
        key_e, accent_e = distinct[1], distinct[0]
    return key_e["color"], accent_e["color"], key_e["pos"], accent_e["pos"]


def _is_dual_tone(palette: list) -> bool:
    distinct = _top_distinct_palette(palette, 2)
    if len(distinct) < 2:
        return False
    c0, c1 = distinct[0]["color"], distinct[1]["color"]
    if _chroma_of(c0) < 0.18 or _chroma_of(c1) < 0.18:
        return False
    h0, h1 = _rgb_hue(c0), _rgb_hue(c1)
    if h0 < 0.0 or h1 < 0.0:
        return False
    return _hue_distance(h0, h1) >= 0.08


def sample_palette(rgb: np.ndarray, lum: np.ndarray, k: int,
                   iters: int = 10, strategy: str = "DEFAULT") -> list:
    """Cluster saturated image regions into ``k`` distinct light colors.

    Seeds hue wedges so a secondary gel (e.g. red on a blue key) is not lost to
    the dominant hue. Sorted by weight (area × brightness), brightest hue-first
    among distinct entries.
    """
    flat = rgb.reshape(-1, 3).astype(np.float32)
    fl = lum.reshape(-1).astype(np.float32)
    n = flat.shape[0]
    k = int(max(1, min(k, n)))
    if n == 0:
        return []

    h, w = lum.shape
    ys, xs = np.mgrid[0:h, 0:w]
    fx = xs.reshape(-1).astype(np.float32)
    fy = ys.reshape(-1).astype(np.float32)

    mask = _subject_mask(h, w).reshape(-1)
    peak = flat.max(axis=1)
    sat = (peak - flat.min(axis=1)) / (peak + 1e-6)
    p30 = float(np.percentile(fl[mask], 30)) if mask.any() else 0.08
    active = mask & (sat > 0.10) & (fl > p30)
    if int(active.sum()) < 48:
        active = mask & (fl > p30)
    if int(active.sum()) < 16:
        active = np.ones(n, dtype=bool)

    sflat = flat[active]
    sfl = fl[active]
    ssat = sat[active]
    sfx = fx[active]
    sfy = fy[active]
    sn = sflat.shape[0]
    k = int(max(1, min(k, sn)))

    score = sfl * ssat
    hues = np.array([_rgb_hue(c) for c in sflat], dtype=np.float32)
    centers = []
    wedges = np.linspace(0.0, 1.0, k + 1)
    for i in range(k):
        lo, hi = wedges[i], wedges[i + 1]
        if i < k - 1:
            in_w = (hues >= lo) & (hues < hi)
        else:
            in_w = (hues >= lo) | (hues < wedges[1] * 0.5)
        if in_w.any():
            pick = int(np.argmax(np.where(in_w, score, -1.0)))
            centers.append(sflat[pick].copy())
    if len(centers) < k:
        order = np.argsort(-score)
        for idx in order[np.linspace(0, sn - 1, k).astype(int)]:
            centers.append(sflat[idx].copy())
            if len(centers) >= k:
                break
    centers = np.asarray(centers[:k], dtype=np.float32)

    labels = np.zeros(sn, dtype=np.int64)
    for _ in range(iters):
        dist = ((sflat[:, None, :] - centers[None, :, :]) ** 2).sum(-1)
        labels = dist.argmin(1)
        moved = False
        for j in range(k):
            m = labels == j
            if m.any():
                c = sflat[m].mean(0)
                if not np.allclose(c, centers[j]):
                    centers[j] = c
                    moved = True
        if not moved:
            break

    entries = []
    for j in range(k):
        m = labels == j
        cnt = int(m.sum())
        if cnt == 0:
            continue
        lj = float(sfl[m].mean())
        cx = float(sfx[m].mean())
        cy = float(sfy[m].mean())
        nx = (cx / max(w - 1, 1)) * 2.0 - 1.0
        ny = 1.0 - (cy / max(h - 1, 1)) * 2.0
        raw = sflat[m].mean(0)
        entries.append({
            "color": apply_color_strategy(raw, strategy),
            "lum": lj,
            "pos": (float(np.clip(nx, -1, 1)), float(np.clip(ny, -1, 1))),
            "weight": cnt * lj * float(ssat[m].mean() + 0.2),
        })
    entries.sort(key=lambda e: (e["lum"], e["weight"]), reverse=True)
    if len(entries) >= k:
        return entries

    # Fallback: full-frame k-means (flat graphic / multi-patch references).
    order = np.argsort(fl)
    fcenters = flat[order[np.linspace(0, n - 1, k).astype(int)]].copy()
    flabels = np.zeros(n, dtype=np.int64)
    for _ in range(iters):
        dist = ((flat[:, None, :] - fcenters[None, :, :]) ** 2).sum(-1)
        flabels = dist.argmin(1)
        for j in range(k):
            m = flabels == j
            if m.any():
                fcenters[j] = flat[m].mean(0)
    entries = []
    for j in range(k):
        m = flabels == j
        if not m.any():
            continue
        lj = float(fl[m].mean())
        cx = float(fx[m].mean())
        cy = float(fy[m].mean())
        nx = (cx / max(w - 1, 1)) * 2.0 - 1.0
        ny = 1.0 - (cy / max(h - 1, 1)) * 2.0
        entries.append({
            "color": apply_color_strategy(flat[m].mean(0), strategy),
            "lum": lj,
            "pos": (float(np.clip(nx, -1, 1)), float(np.clip(ny, -1, 1))),
            "weight": float(m.sum()) * lj,
        })
    entries.sort(key=lambda e: (e["lum"], e["weight"]), reverse=True)
    return entries


def _top_distinct_palette(palette: list, n: int = 2) -> list:
    return _distinct_hue_entries(palette)[:n]


def analyze_rgb(rgb: np.ndarray, mode: str = "AUTO",
                luxpro: bool = True, palette_size: int = 3,
                color_strategy: str = "DEFAULT") -> LightingProfile:
    """Analyze an ``(H, W, 3)`` linear-RGB array and build a LightingProfile.

    ``mode`` is one of ``"PORTRAIT"``, ``"SCENE"`` or ``"AUTO"`` and controls
    which set of :class:`LightSpec` get attached to the profile.
    """
    rgb = np.asarray(rgb, dtype=np.float32)
    if rgb.ndim != 3 or rgb.shape[2] < 3:
        raise ValueError("analyze_rgb expects an (H, W, >=3) array")
    rgb = rgb[..., :3]
    rgb = np.clip(rgb, 0.0, None)

    h, w = rgb.shape[:2]
    lum = _luminance(rgb)
    flat_rgb = rgb.reshape(-1, 3)
    flat_lum = lum.reshape(-1)

    mean_lum = float(flat_lum.mean())

    # Percentile thresholds split the image into highlight / mid / shadow bins.
    p15, p35, p60, p85 = np.percentile(flat_lum, [15, 35, 60, 85])

    hi_mask = flat_lum >= p85
    mid_mask = (flat_lum >= p35) & (flat_lum < p60)
    lo_mask = flat_lum <= p15

    key_color_raw = _safe_mean_color(flat_rgb[hi_mask])
    fill_color_raw = _safe_mean_color(flat_rgb[mid_mask])
    ambient_color_raw = _safe_mean_color(flat_rgb[lo_mask])

    key_lum = float(_luminance(key_color_raw))
    fill_lum = float(_luminance(fill_color_raw))
    contrast = key_lum / max(fill_lum, 1e-3)

    tone = _analyze_tone(lum)
    contrast = float(max(contrast, tone["lum_ratio"] * 0.65, 1.0))
    contrast = float(min(contrast, 40.0))

    # --- Where is the light coming from? -------------------------------- #
    # Weight pixel coordinates by how much brighter than the mid-tone they are.
    weight = np.clip(lum - p60, 0.0, None)
    ys, xs = np.mgrid[0:h, 0:w]
    total_w = float(weight.sum()) + 1e-6
    cx = float((weight * xs).sum() / total_w)
    cy = float((weight * ys).sum() / total_w)
    # Normalize to (-1..1). Row 0 is the TOP of the image (caller flips), so a
    # small cy means the light is high -> map to +up.
    nx = (cx / max(w - 1, 1)) * 2.0 - 1.0
    ny = 1.0 - (cy / max(h - 1, 1)) * 2.0
    key_screen_pos = (float(np.clip(nx, -1, 1)), float(np.clip(ny, -1, 1)))

    # --- Color temperature / warmth ------------------------------------- #
    kelvin = _estimate_kelvin(key_color_raw)
    warmth = float(np.clip((6500.0 - kelvin) / 4000.0 + 0.5, 0.0, 1.0))

    # --- Mood / scene type ---------------------------------------------- #
    if mean_lum > 0.45 and contrast < 4.0:
        mood = "high_key"
    elif mean_lum < 0.22 or contrast > 8.0 or tone["split_score"] > 0.42:
        mood = "low_key"
    else:
        mood = "neutral"

    # Outdoor heuristic: bright overall, a cool-ish ambient (sky fill) and a
    # single dominant highlight high in frame.
    amb = ambient_color_raw
    cool_ambient = (amb[2] >= amb[0] * 0.95)
    is_outdoor = bool(mean_lum > 0.4 and cool_ambient and key_screen_pos[1] > -0.1)

    lux = luxpro_direction(lum, key_screen_pos)
    if luxpro:
        # LuxPro's blended estimate also drives where the key light is placed.
        key_screen_pos = lux["refined_pos"]

    boost, tone_shadows = _suggest_tuning(contrast, tone, mood)

    profile = LightingProfile(
        key_color=apply_color_strategy(key_color_raw, color_strategy),
        fill_color=apply_color_strategy(fill_color_raw, color_strategy),
        ambient_color=tuple(float(c) for c in np.clip(ambient_color_raw, 0.0, 4.0)),
        rim_color=apply_color_strategy(key_color_raw, color_strategy),
        mean_luminance=mean_lum,
        contrast_ratio=contrast,
        key_screen_pos=key_screen_pos,
        color_temperature=kelvin,
        warmth=warmth,
        mood=mood,
        is_outdoor=is_outdoor,
        dir_h=lux["dir_h"], dir_v=lux["dir_v"], dir_label=lux["dir_label"],
        dir_confidence=lux["dir_confidence"], backlit=lux["backlit"],
        hardness=tone["hardness"], split_score=tone["split_score"],
        shadow_frac=tone["shadow_frac"],
        suggested_contrast_boost=boost,
        suggested_tone_shadows=tone_shadows,
    )

    profile.rgb_small = rgb
    profile.lum_small = lum
    k = int(max(1, palette_size))
    profile.palette = sample_palette(rgb, lum, k, strategy=color_strategy)
    profile.dual_tone = _is_dual_tone(profile.palette)
    if profile.palette:
        profile.key_color = profile.palette[0]["color"]
        if profile.dual_tone and len(profile.palette) > 1:
            kc, ac, kp, ap = _assign_gel_roles(profile.palette)
            profile.key_color = kc
            profile.accent_color = ac
            profile.key_screen_pos = kp
            profile.accent_pos = ap
            profile.fill_color = ac
            profile.rim_color = profile.palette[min(2, len(profile.palette) - 1)]["color"]
        elif len(profile.palette) > 1:
            profile.fill_color = profile.palette[1]["color"]
            profile.rim_color = profile.palette[min(2, len(profile.palette) - 1)]["color"]
        profile.ambient_color = profile.palette[-1]["color"]
    profile.specs = build_specs(profile, mode)
    return profile


def _resolve_mode(profile: LightingProfile, mode: str) -> str:
    if mode in ("PORTRAIT", "SCENE"):
        return mode
    # AUTO: outdoor / bright wide scenes -> SCENE, otherwise portrait rig.
    return "SCENE" if profile.is_outdoor else "PORTRAIT"


def _camera_light_dir(nx: float, ny: float, role: str, backlit: bool = False) -> tuple:
    """Map analyzed screen-space key direction to a camera-relative 3D vector."""
    nx, ny = float(nx), float(ny)
    if role == "rim":
        if backlit:
            return (0.0, 0.42, -1.0)
        return (-nx * 0.68, 0.48 + max(ny, 0.0) * 0.22, -0.96)
    if role == "fill":
        # Opposite the lit side, slightly above and toward the camera.
        return (-nx * 0.84, ny * 0.18 - 0.06, 1.0)
    if role == "accent":
        # Second gel — from its detected screen position, near camera.
        return (nx * 0.86, max(ny, 0.06), 0.90)
    if role == "key":
        elev = max(ny, -0.15) if ny > 0.05 else max(ny * 0.5, 0.02)
        side = min(abs(nx), 1.0)
        depth = max(0.35, 0.92 - side * 0.42)
        if backlit:
            depth = min(depth, 0.58)
        return (nx * 0.90, elev, depth)
    # accent / sky / generic
    return (nx * 0.55, max(ny, 0.1), 0.65)


def build_specs(profile: LightingProfile, mode: str) -> list:
    """Turn a profile into a list of :class:`LightSpec` for the given mode."""
    resolved = _resolve_mode(profile, mode)
    nx, ny = profile.key_screen_pos
    hard = float(profile.hardness)
    split = float(profile.split_score)
    fill_ratio = float(np.clip(1.0 / profile.contrast_ratio, 0.02, 0.8))
    if split > 0.35:
        fill_ratio = min(fill_ratio, 0.12 * (1.0 - split * 0.5))
    base_soft = 1.4 if profile.mood == "high_key" else (0.6 if profile.mood == "low_key" else 1.0)

    specs: list = []

    if resolved == "PORTRAIT":
        key_dir = _camera_light_dir(nx, ny, "key", profile.backlit)
        fill_dir = _camera_light_dir(nx, ny, "fill", profile.backlit)
        rim_dir = _camera_light_dir(nx, ny, "rim", profile.backlit)
        side = min(abs(nx) + abs(ny), 1.4)
        use_spot_key = split > 0.38 or hard > 0.42
        key_soft = base_soft * (0.95 - side * 0.12)
        key_soft *= max(0.18, 1.0 - hard * 0.72 - split * 0.35)
        fill_mul = max(0.03, 0.72 - side * 0.12 - split * 0.42 - hard * 0.18)
        fill_soft = base_soft * (2.2 - split * 0.9 - hard * 0.5)
        rim_energy = float(np.clip(
            0.75 + profile.contrast_ratio * 0.08 + split * 0.35 + hard * 0.2,
            0.55, 2.4,
        ))
        specs.append(LightSpec(
            role="key", light_type="SPOT" if use_spot_key else "AREA",
            direction=key_dir,
            color=profile.key_color, energy=1.0, size=max(0.12, key_soft),
        ))
        if profile.dual_tone:
            ax, ay = profile.accent_pos
            specs.append(LightSpec(
                role="accent", light_type="SPOT",
                direction=_camera_light_dir(ax, ay, "accent", profile.backlit),
                color=profile.accent_color,
                energy=float(np.clip(0.72 + split * 0.18, 0.65, 1.05)),
                size=max(0.10, 0.16 - hard * 0.04),
            ))
        else:
            specs.append(LightSpec(
                role="fill", light_type="AREA",
                direction=fill_dir,
                color=_blend(profile.fill_color, profile.ambient_color, 0.45),
                energy=fill_ratio * fill_mul, size=max(0.35, fill_soft),
            ))
        specs.append(LightSpec(
            role="rim", light_type="SPOT",
            direction=rim_dir,
            color=profile.rim_color if not profile.dual_tone else profile.key_color,
            energy=rim_energy * (0.75 if profile.dual_tone else 1.0),
            size=max(0.18, 0.32 - hard * 0.08),
        ))
    else:  # SCENE — broad, even, environment-first (no rim).
        use_sun = profile.is_outdoor or profile.mean_luminance > 0.32
        key_dir = _camera_light_dir(nx, ny, "key", profile.backlit)
        fill_dir = _camera_light_dir(nx, ny, "fill", profile.backlit)
        if use_sun:
            specs.append(LightSpec(
                role="key", light_type="SUN",
                direction=(key_dir[0] * 0.55, max(key_dir[1], 0.25), 0.25),
                color=profile.key_color, energy=0.75,
                size=0.35 if profile.mood == "low_key" else 1.3,
            ))
        else:
            specs.append(LightSpec(
                role="key", light_type="AREA",
                direction=key_dir,
                color=profile.key_color, energy=0.8, size=base_soft * 3.0,
            ))
        specs.append(LightSpec(
            role="fill", light_type="AREA",
            direction=fill_dir,
            color=_blend(profile.fill_color, profile.ambient_color, 0.55),
            energy=max(fill_ratio, 0.55), size=base_soft * 3.5,
        ))
        specs.append(LightSpec(
            role="sky", light_type="AREA",
            direction=(0.0, 0.92, 0.4),
            color=_blend(profile.ambient_color, profile.fill_color, 0.35),
            energy=max(fill_ratio * 0.85, 0.38), size=4.0,
        ))

    return specs


def _blend(a, b, t: float) -> tuple:
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    out = a * (1.0 - t) + b * t
    return (float(out[0]), float(out[1]), float(out[2]))


# --------------------------------------------------------------------------- #
# Blender bridge (only place that imports bpy)
# --------------------------------------------------------------------------- #
def image_to_rgb(image) -> np.ndarray:
    """Read a ``bpy.types.Image`` into a downsampled ``(H, W, 3)`` linear array.

    Rows are flipped so index 0 is the TOP of the image (matching screen-space
    intuition used throughout the analysis).
    """
    w, h = image.size
    if w == 0 or h == 0:
        raise ValueError("Reference image has no pixel data")

    channels = image.channels or 4
    buf = np.empty(w * h * channels, dtype=np.float32)
    image.pixels.foreach_get(buf)
    arr = buf.reshape(h, w, channels)[..., :3]
    arr = np.flipud(arr)  # bottom-up -> top-down

    step = max(1, max(w, h) // _MAX_EDGE)
    if step > 1:
        arr = arr[::step, ::step, :]
    return np.ascontiguousarray(arr)


# --------------------------------------------------------------------------- #
# Headless self-test
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Synthetic: warm light entering from the top-right.
    H, W = 120, 160
    yy, xx = np.mgrid[0:H, 0:W]
    grad = ((xx / W) * 0.7 + (1.0 - yy / H) * 0.7)
    test = np.stack([grad * 1.0, grad * 0.8, grad * 0.55], axis=-1).astype(np.float32)

    prof = analyze_rgb(test, mode="PORTRAIT")
    print("key_color        :", tuple(round(c, 3) for c in prof.key_color))
    print("fill_color       :", tuple(round(c, 3) for c in prof.fill_color))
    print("ambient_color    :", tuple(round(c, 3) for c in prof.ambient_color))
    print("mean_luminance   :", round(prof.mean_luminance, 3))
    print("contrast_ratio   :", round(prof.contrast_ratio, 2))
    print("key_screen_pos   :", tuple(round(c, 2) for c in prof.key_screen_pos))
    print("color_temperature:", round(prof.color_temperature), "K  warmth", round(prof.warmth, 2))
    print("mood             :", prof.mood, "| outdoor:", prof.is_outdoor)
    print("specs            :", [(s.role, s.light_type) for s in prof.specs])
    assert prof.key_screen_pos[0] > 0 and prof.key_screen_pos[1] > 0, "expected top-right key"
    assert prof.warmth > 0.5, "expected warm light"
    print("\nself-test OK")
