"""Runtime procedural PNG helpers for RollLux random presets and references.

Pure numpy + a tiny built-in PNG encoder (zlib + struct). Used at runtime by
``presets.randomize_preset`` and ``presets.randomize_reference``.
"""

from __future__ import annotations

import os
import struct
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(HERE, "icons")
REF_DIR = os.path.join(HERE, "references")

THUMB = 128
REF_SIZE = 256


# --------------------------------------------------------------------------- #
# Minimal PNG writer (8-bit RGB)
# --------------------------------------------------------------------------- #
def write_png(path: str, rgb: np.ndarray) -> None:
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    h, w, _ = rgb.shape
    raw = bytearray()
    stride = w * 3
    flat = rgb.reshape(h, stride)
    for y in range(h):
        raw.append(0)  # filter: none
        raw.extend(flat[y].tobytes())
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def _gamma(lin: np.ndarray) -> np.ndarray:
    return np.power(np.clip(lin, 0.0, 1.0), 1.0 / 2.2) * 255.0


# --------------------------------------------------------------------------- #
# Shaded-sphere preset thumbnails
# --------------------------------------------------------------------------- #
def shade_sphere(key_dir, key_col, fill_col, amb_col, contrast=1.0,
                 rim=0.0, bg=(0.08, 0.08, 0.09)):
    n = THUMB
    ax = np.linspace(-1.2, 1.2, n)
    gx, gy = np.meshgrid(ax, -ax)
    r2 = gx * gx + gy * gy
    mask = r2 <= 1.0
    gz = np.sqrt(np.clip(1.0 - r2, 0.0, 1.0))

    key = np.array(key_dir, dtype=np.float64)
    key /= np.linalg.norm(key)
    ndl = np.clip(gx * key[0] + gy * key[1] + gz * key[2], 0.0, 1.0)
    ndl = ndl ** (1.0 / max(0.2, 1.0 / contrast))

    # opposite-ish soft fill
    fdir = np.array([-key[0] * 0.6, key[1] * 0.2 + 0.2, 0.8])
    fdir /= np.linalg.norm(fdir)
    ndf = np.clip(gx * fdir[0] + gy * fdir[1] + gz * fdir[2], 0.0, 1.0)

    img = np.zeros((n, n, 3), dtype=np.float64)
    for c in range(3):
        shaded = (key_col[c] * ndl
                  + fill_col[c] * ndf * (0.5 / contrast)
                  + amb_col[c] * 0.35)
        img[..., c] = np.where(mask, shaded, bg[c])

    if rim > 0.0:
        edge = np.clip(1.0 - gz, 0.0, 1.0) ** 3
        rim_band = edge * (gy > -0.2) * mask
        for c in range(3):
            img[..., c] += key_col[c] * rim_band * rim

    # subtle vignette on background
    vig = np.clip(1.0 - r2 * 0.15, 0.6, 1.0)
    img[~mask] *= vig[~mask, None]
    return _gamma(img)


LIGHTING_PRESETS = {
    "random":     dict(key_dir=(0.6, 0.3, 0.7), key_col=(1.0, 0.5, 0.9),
                       fill_col=(0.3, 0.8, 0.9), amb_col=(0.1, 0.1, 0.14),
                       contrast=2.0, rim=0.8),
    "auto":       dict(key_dir=(0.5, 0.4, 0.9), key_col=(1.0, 0.97, 0.92),
                       fill_col=(0.6, 0.62, 0.7), amb_col=(0.1, 0.1, 0.12),
                       contrast=1.4, rim=0.4),
    "portrait":   dict(key_dir=(0.6, 0.5, 0.7), key_col=(1.0, 0.86, 0.66),
                       fill_col=(0.55, 0.6, 0.72), amb_col=(0.08, 0.09, 0.12),
                       contrast=1.8, rim=0.6),
    "rembrandt":  dict(key_dir=(-0.6, 0.55, 0.55), key_col=(1.0, 0.84, 0.6),
                       fill_col=(0.18, 0.2, 0.26), amb_col=(0.04, 0.04, 0.06),
                       contrast=2.6, rim=0.4),
    "butterfly":  dict(key_dir=(0.0, 0.5, 0.9), key_col=(1.0, 0.92, 0.85),
                       fill_col=(0.7, 0.72, 0.78), amb_col=(0.16, 0.16, 0.18),
                       contrast=1.3, rim=0.5),
    "loop":       dict(key_dir=(0.45, 0.4, 0.8), key_col=(1.0, 0.9, 0.78),
                       fill_col=(0.5, 0.55, 0.65), amb_col=(0.1, 0.1, 0.13),
                       contrast=1.6, rim=0.5),
    "split":      dict(key_dir=(0.95, 0.1, 0.25), key_col=(1.0, 0.95, 0.88),
                       fill_col=(0.12, 0.14, 0.2), amb_col=(0.03, 0.03, 0.05),
                       contrast=3.0, rim=0.5),
    "clamshell":  dict(key_dir=(0.0, 0.35, 1.0), key_col=(1.0, 0.96, 0.95),
                       fill_col=(0.82, 0.82, 0.86), amb_col=(0.3, 0.29, 0.3),
                       contrast=1.05, rim=0.4),
    "beauty":     dict(key_dir=(0.1, 0.25, 1.0), key_col=(1.0, 0.93, 0.9),
                       fill_col=(0.8, 0.8, 0.85), amb_col=(0.25, 0.24, 0.26),
                       contrast=1.05, rim=0.3),
    "cinematic":  dict(key_dir=(0.85, 0.15, 0.5), key_col=(1.0, 0.66, 0.33),
                       fill_col=(0.2, 0.45, 0.6), amb_col=(0.04, 0.07, 0.1),
                       contrast=3.2, rim=1.0),
    "dramatic":   dict(key_dir=(-0.9, 0.25, 0.35), key_col=(1.0, 0.95, 0.85),
                       fill_col=(0.1, 0.12, 0.16), amb_col=(0.02, 0.02, 0.03),
                       contrast=4.5, rim=0.8),
    "noir":       dict(key_dir=(-0.85, 0.35, 0.3), key_col=(0.98, 0.99, 1.0),
                       fill_col=(0.05, 0.06, 0.08), amb_col=(0.01, 0.01, 0.02),
                       contrast=5.0, rim=1.2),
    "low_key":    dict(key_dir=(0.7, 0.25, 0.4), key_col=(1.0, 0.94, 0.85),
                       fill_col=(0.08, 0.09, 0.12), amb_col=(0.02, 0.02, 0.03),
                       contrast=3.6, rim=0.6),
    "high_key":   dict(key_dir=(0.2, 0.3, 0.95), key_col=(1.0, 1.0, 1.0),
                       fill_col=(0.92, 0.92, 0.94), amb_col=(0.4, 0.4, 0.42),
                       contrast=0.7, rim=0.2),
    "studio":     dict(key_dir=(0.25, 0.45, 0.95), key_col=(1.0, 1.0, 1.0),
                       fill_col=(0.85, 0.87, 0.9), amb_col=(0.2, 0.2, 0.22),
                       contrast=1.1, rim=0.2),
    "product":    dict(key_dir=(0.2, 0.55, 0.85), key_col=(1.0, 1.0, 1.0),
                       fill_col=(0.78, 0.8, 0.84), amb_col=(0.18, 0.18, 0.2),
                       contrast=1.2, rim=0.6),
    "soft_even":  dict(key_dir=(0.1, 0.2, 1.0), key_col=(1.0, 1.0, 1.0),
                       fill_col=(0.9, 0.9, 0.92), amb_col=(0.45, 0.45, 0.47),
                       contrast=0.6, rim=0.1),
    "rim":        dict(key_dir=(0.3, 0.5, 0.7), key_col=(1.0, 0.97, 0.92),
                       fill_col=(0.3, 0.33, 0.4), amb_col=(0.05, 0.05, 0.07),
                       contrast=1.7, rim=1.6),
    "backlight":  dict(key_dir=(0.0, 0.7, 0.4), key_col=(1.0, 0.95, 0.85),
                       fill_col=(0.25, 0.28, 0.35), amb_col=(0.05, 0.06, 0.08),
                       contrast=1.9, rim=2.0),
    "outdoor":    dict(key_dir=(0.4, 0.8, 0.6), key_col=(1.0, 0.95, 0.8),
                       fill_col=(0.45, 0.6, 0.95), amb_col=(0.12, 0.16, 0.24),
                       contrast=2.0, rim=0.5),
    "sunset":     dict(key_dir=(0.7, 0.45, 0.5), key_col=(1.0, 0.6, 0.3),
                       fill_col=(0.4, 0.35, 0.5), amb_col=(0.1, 0.07, 0.12),
                       contrast=2.4, rim=0.7),
    "twilight":   dict(key_dir=(0.15, 0.6, 0.6), key_col=(0.55, 0.65, 1.0),
                       fill_col=(0.3, 0.36, 0.5), amb_col=(0.08, 0.1, 0.16),
                       contrast=1.2, rim=0.4),
    "neon":       dict(key_dir=(0.75, 0.2, 0.5), key_col=(1.0, 0.3, 0.85),
                       fill_col=(0.2, 0.7, 0.9), amb_col=(0.06, 0.04, 0.1),
                       contrast=2.0, rim=1.3),
    "candlelight": dict(key_dir=(0.25, 0.0, 0.95), key_col=(1.0, 0.62, 0.3),
                        fill_col=(0.3, 0.2, 0.18), amb_col=(0.08, 0.04, 0.03),
                        contrast=2.0, rim=0.3),
    "moonlight":  dict(key_dir=(0.25, 0.7, 0.5), key_col=(0.55, 0.7, 1.0),
                       fill_col=(0.12, 0.16, 0.28), amb_col=(0.03, 0.04, 0.08),
                       contrast=2.4, rim=0.6),
    "underlight": dict(key_dir=(0.0, -0.8, 0.6), key_col=(1.0, 0.93, 0.86),
                       fill_col=(0.1, 0.11, 0.14), amb_col=(0.02, 0.02, 0.03),
                       contrast=2.8, rim=0.4),
}


# --------------------------------------------------------------------------- #
# Reference lighting sample images
# --------------------------------------------------------------------------- #
def _coords(n):
    ax = np.linspace(-1, 1, n)
    gx, gy = np.meshgrid(ax, ax[::-1])  # gy: +1 top
    return gx, gy


def _blob(gx, gy, cx, cy, sharp):
    d = (gx - cx) ** 2 + (gy - cy) ** 2
    return np.exp(-d * sharp)


def make_ref(n, *, base=0.08, grad=(0.0, 0.0), tint=(1.0, 1.0, 1.0),
             blobs=(), rim=0.0, rim_color=(1.0, 1.0, 1.0), vignette=0.0,
             stripes=0.0, dapple=0, dapple_seed=0):
    """Composite a synthetic lighting reference from simple ingredients.

    * ``base``    - ambient floor brightness (tinted)
    * ``grad``    - linear brightness ramp (+x right, +y up), tinted
    * ``blobs``   - list of ``(px, py, sharp, intensity, (r, g, b))`` highlights
    * ``rim``     - bright edge ring (rim/back light)
    * ``vignette``- darken toward the corners
    * ``stripes`` - horizontal banding (window blinds), frequency in cycles
    * ``dapple``  - N random soft spots (foliage / caustics), tinted
    All values are scene-linear; the caller applies gamma once.
    """
    gx, gy = _coords(n)  # gy: +1 top
    img = np.zeros((n, n, 3), dtype=np.float64)
    for c in range(3):
        img[..., c] = base * tint[c]

    ramp = np.clip((gx * 0.5 + 0.5) * grad[0] + (gy * 0.5 + 0.5) * grad[1], 0, None)
    for c in range(3):
        img[..., c] += ramp * tint[c]

    for (px, py, sharp, inten, col) in blobs:
        m = _blob(gx, gy, px, py, sharp) * inten
        for c in range(3):
            img[..., c] += m * col[c]

    if dapple > 0:
        rng = np.random.default_rng(dapple_seed)
        for _ in range(dapple):
            px, py = rng.uniform(-1, 1), rng.uniform(-1, 1)
            m = _blob(gx, gy, px, py, rng.uniform(8, 22)) * rng.uniform(0.3, 0.8)
            for c in range(3):
                img[..., c] += m * tint[c]

    if stripes > 0:
        band = 0.45 + 0.55 * (np.sin(gy * stripes * np.pi) > 0)
        img *= band[..., None]

    if rim > 0:
        edge = np.clip((gx ** 2 + gy ** 2) ** 0.5 - 0.5, 0, 1) ** 1.4
        for c in range(3):
            img[..., c] += edge * rim * rim_color[c]

    if vignette > 0:
        v = 1.0 - np.clip(gx ** 2 + gy ** 2, 0, 1) * vignette
        img *= v[..., None]

    return np.clip(img, 0.0, 1.6)


# Reusable colors (scene-linear-ish).
_W = (1.0, 0.78, 0.5)      # warm
_W2 = (1.0, 0.58, 0.28)    # deep warm / sunset
_N = (1.0, 1.0, 1.0)       # neutral
_C = (0.6, 0.72, 1.0)      # cool
_SKY = (0.5, 0.68, 1.0)
_MAG = (1.0, 0.3, 0.85)
_CYAN = (0.2, 0.85, 0.95)
_PINK = (1.0, 0.45, 0.7)
_BLU = (0.3, 0.5, 1.0)
_GRN = (0.45, 0.95, 0.5)
_FIRE = (1.0, 0.5, 0.2)
_TEAL = (0.2, 0.72, 0.72)

DISTRIBUTION_COLOR_MODES = ("BALANCED", "VIVID", "SOFT")

_BALANCED_GEL = [
    _W, _W2, _N, _C, _MAG, _CYAN, _PINK, _BLU, _GRN, _FIRE,
]

_VIVID_GEL = [
    (1.4, 0.12, 0.85),
    (0.15, 0.75, 1.35),
    (1.35, 0.55, 0.05),
    (0.25, 1.05, 0.35),
    (0.75, 0.25, 1.35),
]
_VIVID_SLOTS = [
    (-0.62, 0.18),
    (0.62, 0.18),
    (0.0, 0.58),
    (-0.38, -0.42),
    (0.38, -0.42),
]

_SOFT_GEL = [
    (1.0, 0.96, 0.92),
    (0.94, 0.96, 1.0),
    (0.98, 0.95, 0.90),
]
_SOFT_TINTS = [
    (0.97, 0.95, 0.92),
    (0.93, 0.95, 0.98),
]


def build_random_reference_params(mode: str = "BALANCED", rng=None) -> dict:
    """Build ``make_ref`` kwargs for a procedural lighting-distribution image.

    * ``BALANCED`` — mixed warm/cool blobs (legacy random reference).
    * ``VIVID``    — dark base, hue-separated saturated blobs in fixed slots.
    * ``SOFT``     — bright neutral base, low-saturation gentle blobs.
    """
    import random

    rng = rng or random
    mode = mode if mode in DISTRIBUTION_COLOR_MODES else "BALANCED"

    if mode == "VIVID":
        n = rng.randint(3, len(_VIVID_GEL))
        spread_sets = {
            3: [(0, 1, 3), (0, 1, 4), (0, 2, 4), (1, 2, 4)],
            4: [(0, 1, 2, 3), (0, 1, 3, 4), (0, 2, 3, 4)],
            5: [tuple(range(len(_VIVID_GEL)))],
        }
        pick = list(rng.choice(spread_sets[n]))
        blobs = []
        for i in pick:
            cx, cy = _VIVID_SLOTS[i]
            blobs.append((
                round(cx + rng.uniform(-0.08, 0.08), 2),
                round(cy + rng.uniform(-0.08, 0.08), 2),
                round(rng.uniform(1.3, 2.1), 2),
                round(rng.uniform(0.85, 1.45), 2),
                _VIVID_GEL[i],
            ))
        return dict(
            base=round(rng.uniform(0.03, 0.10), 2),
            grad=(round(rng.uniform(0.0, 0.15), 2), round(rng.uniform(0.0, 0.15), 2)),
            tint=(0.42, 0.46, 0.52),
            blobs=blobs,
            rim=round(rng.uniform(0.0, 0.5), 2) if rng.random() < 0.25 else 0.0,
            vignette=round(rng.uniform(0.15, 0.45), 2),
            stripes=0.0,
            dapple=0,
            dapple_seed=rng.randint(0, 9999),
        )

    if mode == "SOFT":
        n_blobs = rng.randint(1, 2)
        blobs = []
        for _ in range(n_blobs):
            blobs.append((
                round(rng.uniform(-0.45, 0.45), 2),
                round(rng.uniform(-0.35, 0.55), 2),
                round(rng.uniform(0.55, 1.0), 2),
                round(rng.uniform(0.35, 0.65), 2),
                rng.choice(_SOFT_GEL),
            ))
        return dict(
            base=round(rng.uniform(0.32, 0.55), 2),
            grad=(round(rng.uniform(0.0, 0.25), 2), round(rng.uniform(0.0, 0.25), 2)),
            tint=rng.choice(_SOFT_TINTS),
            blobs=blobs,
            rim=0.0,
            vignette=round(rng.uniform(0.0, 0.2), 2) if rng.random() < 0.3 else 0.0,
            stripes=0.0,
            dapple=0,
            dapple_seed=rng.randint(0, 9999),
        )

    n_blobs = rng.randint(1, 3)
    blobs = []
    for _ in range(n_blobs):
        blobs.append((
            round(rng.uniform(-0.8, 0.8), 2),
            round(rng.uniform(-0.7, 0.85), 2),
            round(rng.uniform(0.7, 2.4), 2),
            round(rng.uniform(0.5, 1.1), 2),
            rng.choice(_BALANCED_GEL),
        ))
    return dict(
        base=round(rng.uniform(0.03, 0.5), 2),
        grad=(round(rng.uniform(0.0, 0.6), 2), round(rng.uniform(0.0, 0.6), 2)),
        tint=rng.choice(_BALANCED_GEL),
        blobs=blobs,
        rim=round(rng.uniform(0.0, 1.2), 2) if rng.random() < 0.4 else 0.0,
        vignette=round(rng.uniform(0.0, 0.5), 2) if rng.random() < 0.5 else 0.0,
        stripes=rng.choice((0.0, 0.0, 0.0, 5.0, 7.0)),
        dapple=rng.choice((0, 0, 0, 12)),
        dapple_seed=rng.randint(0, 9999),
    )


REFERENCE_PRESETS = {
    "random":      dict(base=0.06, blobs=[(-0.55, 0.3, 1.2, 0.8, _MAG),
                                          (0.55, -0.1, 1.2, 0.8, _CYAN),
                                          (0.0, 0.6, 1.4, 0.6, _W)]),
    # --- time of day / sky ------------------------------------------------ #
    "golden_hour": dict(base=0.2, grad=(0.9, 0.1), tint=_W,
                        blobs=[(0.7, 0.3, 1.2, 0.7, _W)]),
    "sunrise":     dict(base=0.16, grad=(0.5, 0.2), tint=(1.0, 0.7, 0.45),
                        blobs=[(-0.6, -0.2, 1.4, 0.8, (1.0, 0.65, 0.4))]),
    "sunset":      dict(base=0.18, grad=(0.6, 0.0), tint=_W2,
                        blobs=[(0.6, -0.25, 1.3, 0.9, _W2)], vignette=0.3),
    "blue_hour":   dict(base=0.12, grad=(0.0, 0.6), tint=_C),
    "twilight":    dict(base=0.1, grad=(0.0, 0.5), tint=(0.7, 0.6, 1.0),
                        blobs=[(0.0, 0.8, 1.0, 0.4, _MAG)]),
    "midday":      dict(base=0.4, grad=(0.0, 0.5), tint=_N,
                        blobs=[(0.1, 0.8, 1.4, 0.6, _N)]),
    "harsh_noon":  dict(base=0.25, blobs=[(0.0, 0.85, 3.0, 1.1, _N)],
                        vignette=0.45),
    "overcast":    dict(base=0.55, grad=(0.0, 0.25), tint=(0.95, 0.97, 1.0)),
    "foggy_morn":  dict(base=0.5, grad=(0.0, 0.3), tint=(0.9, 0.95, 1.0),
                        vignette=0.2),
    "night_sky":   dict(base=0.04, grad=(0.0, 0.25), tint=_C,
                        blobs=[(0.4, 0.8, 6.0, 0.5, (0.8, 0.9, 1.0))]),
    "top_sky":     dict(base=0.08, grad=(0.0, 0.95), tint=(0.85, 0.92, 1.0)),
    # --- studio ----------------------------------------------------------- #
    "softbox":     dict(base=0.5, blobs=[(0.0, 0.4, 0.6, 0.5, _N)]),
    "softbox_l":   dict(base=0.18, blobs=[(-0.6, 0.35, 0.9, 0.8, _N)]),
    "softbox_r":   dict(base=0.18, blobs=[(0.6, 0.35, 0.9, 0.8, _N)]),
    "beauty_dish": dict(base=0.2, blobs=[(0.0, 0.45, 1.6, 0.9, _N)], rim=0.25),
    "ring_light":  dict(base=0.18, blobs=[(0.0, 0.0, 0.8, 0.7, _N)], rim=0.7),
    "clamshell":   dict(base=0.25, blobs=[(0.0, 0.6, 1.2, 0.7, _N),
                                          (0.0, -0.6, 1.2, 0.45, _N)]),
    "butterfly":   dict(base=0.2, blobs=[(0.0, 0.55, 1.4, 0.85, (1.0, 0.95, 0.9))]),
    "broad_light": dict(base=0.16, blobs=[(-0.45, 0.25, 1.0, 0.85, (1.0, 0.96, 0.9))]),
    "short_light": dict(base=0.12, blobs=[(0.55, 0.3, 1.3, 0.85, (1.0, 0.96, 0.9))],
                        vignette=0.2),
    "high_key":    dict(base=0.7, blobs=[(0.0, 0.5, 0.7, 0.4, _N)]),
    "low_key":     dict(base=0.03, blobs=[(0.45, 0.2, 2.2, 1.0, (1.0, 0.97, 0.92))],
                        vignette=0.5),
    # --- portrait patterns ------------------------------------------------ #
    "rembrandt":   dict(base=0.06, blobs=[(-0.5, 0.45, 1.6, 1.1, _W)]),
    "rembrandt_r": dict(base=0.06, blobs=[(0.5, 0.45, 1.6, 1.1, _W)]),
    "loop":        dict(base=0.12, blobs=[(0.35, 0.3, 1.4, 0.95, (1.0, 0.95, 0.88))]),
    "split":       dict(base=0.05, blobs=[(0.85, 0.1, 2.0, 1.1, (1.0, 0.97, 0.92))],
                        vignette=0.35),
    "under_light": dict(base=0.06, blobs=[(0.0, -0.7, 1.6, 1.0, (1.0, 0.95, 0.9))]),
    "hair_light":  dict(base=0.1, blobs=[(0.0, 0.5, 1.0, 0.5, _N)], rim=0.9),
    # --- cinematic / color ------------------------------------------------ #
    "noir":        dict(base=0.02, blobs=[(-0.8, 0.35, 2.4, 1.2, _N)],
                        stripes=6.0, vignette=0.55),
    "teal_orange": dict(base=0.08, blobs=[(0.6, 0.25, 1.2, 0.9, _W2),
                                          (-0.6, -0.1, 1.0, 0.6, _TEAL)]),
    "neon_mc":     dict(base=0.04, blobs=[(-0.55, 0.3, 1.2, 0.9, _MAG),
                                          (0.55, -0.1, 1.2, 0.9, _CYAN)]),
    "neon_bp":     dict(base=0.04, blobs=[(-0.5, 0.0, 1.2, 0.9, _BLU),
                                          (0.55, 0.3, 1.2, 0.9, _PINK)]),
    "candlelight": dict(base=0.05, blobs=[(0.0, -0.1, 1.8, 1.0, _FIRE)],
                        vignette=0.5),
    "firelight":   dict(base=0.06, grad=(0.0, -0.1), tint=_FIRE,
                        blobs=[(0.0, -0.5, 1.0, 0.9, _FIRE)], vignette=0.35),
    "moonlight":   dict(base=0.05, blobs=[(-0.4, 0.5, 1.4, 0.7, _SKY)],
                        vignette=0.3),
    "moonlit_win": dict(base=0.04, blobs=[(0.5, 0.2, 1.0, 0.8, _SKY)],
                        stripes=5.0, vignette=0.35),
    "horror_up":   dict(base=0.04, blobs=[(0.0, -0.7, 1.6, 1.0, _GRN)],
                        vignette=0.45),
    # --- environment ------------------------------------------------------ #
    "window":      dict(base=0.12, blobs=[(0.55, 0.35, 0.8, 0.85, (1.0, 0.98, 0.92))]),
    "window_blind": dict(base=0.1, blobs=[(0.5, 0.3, 0.8, 0.9, _W)], stripes=7.0),
    "forest":      dict(base=0.1, grad=(0.0, 0.3), tint=_GRN, dapple=14,
                        dapple_seed=7),
    "underwater":  dict(base=0.12, grad=(0.0, 0.4), tint=_TEAL, dapple=12,
                        dapple_seed=3),
    "snow_bounce": dict(base=0.6, grad=(0.0, 0.2), tint=(0.95, 0.98, 1.0),
                        blobs=[(0.0, -0.5, 0.8, 0.3, _N)]),
    "desert":      dict(base=0.35, grad=(0.2, 0.4), tint=(1.0, 0.85, 0.6),
                        blobs=[(0.3, 0.7, 1.4, 0.6, _W)]),
    "street_lamp": dict(base=0.03, blobs=[(0.0, 0.4, 2.0, 1.0, (1.0, 0.8, 0.5))],
                        vignette=0.6),
    "stage_spot":  dict(base=0.02, blobs=[(0.0, 0.6, 2.6, 1.2, _N)], vignette=0.6),
    "concert_rgb": dict(base=0.04, blobs=[(-0.6, 0.4, 1.4, 0.8, _BLU),
                                          (0.0, 0.5, 1.4, 0.8, _MAG),
                                          (0.6, 0.4, 1.4, 0.8, _CYAN)]),
    "sci_fi":      dict(base=0.06, blobs=[(0.5, 0.0, 1.0, 0.7, _CYAN)],
                        stripes=4.0, vignette=0.3),
}


# MARKETPLACE_STRIP_BEGIN dev_main
def main():
    os.makedirs(ICON_DIR, exist_ok=True)
    os.makedirs(REF_DIR, exist_ok=True)

    for pid, params in LIGHTING_PRESETS.items():
        img = shade_sphere(**params)
        write_png(os.path.join(ICON_DIR, f"preset_{pid}.png"), img)
        print("icon  ", pid)

    for rid, params in REFERENCE_PRESETS.items():
        lin = make_ref(REF_SIZE, **params)
        write_png(os.path.join(REF_DIR, f"ref_{rid}.png"), _gamma(lin))
        print("ref   ", rid)

    print("\nAssets written to:")
    print(" ", ICON_DIR)
    print(" ", REF_DIR)
# MARKETPLACE_STRIP_END dev_main
