"""Lighting presets + reference-image library, with thumbnail previews.

Two kinds of presets:

* **Lighting presets** (``PRESET_PARAMS``) reshape the light rig that gets built
  from the analyzed reference (softness, fill ratio, key type, contrast, tint).
  Each has a shaded-sphere thumbnail in ``icons/``.
* **Reference presets** (``REFERENCE_ORDER``) are sample lighting images in
  ``references/`` the user can pick instead of loading their own photo.

Thumbnails are loaded through ``bpy.utils.previews`` and surfaced as
``template_icon_view`` grids in the UI.
"""

from __future__ import annotations

import os
import random as _random
import tempfile

import bpy
import bpy.utils.previews

from . import analysis
from .translations import tr

ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")
REF_DIR = os.path.join(os.path.dirname(__file__), "references")
RANDOM_DIR = os.path.join(tempfile.gettempdir(), "rolllux_random")

# Runtime overrides for the "random" slots: point the preview / reference loader
# at the freshly generated temp PNGs instead of the shipped defaults.
# ``preset_key`` / ``reference_key`` track the active PreviewCollection entry
# (Blender forbids loading the same key twice, so each roll uses a new key).
_random_override = {
    "preset": None, "reference": None,
    "preset_key": "random", "reference_key": "random",
}
_random_counter = [0]
# Reuse a small pool of preview keys (del+reload deferred) instead of unbounded
# random_pN keys that eventually crash template_icon_view.
_PREVIEW_POOL = 8
_preview_apply_pending: set[str] = set()
_pending_preview_path: dict[str, str | None] = {"preset": None, "reference": None}

# Lighting presets, in display order. ``defaults`` seed the tuning sliders;
# the rest reshape the rig in apply_preset().
PRESET_ORDER = (
    "random",
    "auto", "portrait", "rembrandt", "butterfly", "loop", "split", "clamshell",
    "beauty", "cinematic", "dramatic", "noir", "low_key", "high_key", "studio",
    "product", "soft_even", "rim", "backlight", "outdoor", "sunset", "twilight",
    "neon", "candlelight", "moonlight", "underlight",
)


def _p(mode, softness, rim, rim_strength, fill_ratio, key_type, tint,
       intensity=0.2, distance=2.5, color_strength=0.85, contrast_boost=1.0):
    return dict(
        mode=mode, softness=softness, rim=rim, rim_strength=rim_strength,
        fill_ratio=fill_ratio, key_type=key_type, tint=tint,
        defaults=dict(intensity=intensity, distance=distance,
                      color_strength=color_strength, contrast_boost=contrast_boost),
    )


PRESET_PARAMS = {
    # Overwritten each time the user hits "Random"; this is just a sane seed.
    "random":     _p("PORTRAIT", 1.0, True, 1.0, 0.3, "AREA", (1.0, 0.95, 0.9),
                     contrast_boost=1.4),
    "auto":       _p(None, 1.0, None, 1.0, None, None, (1.0, 1.0, 1.0),
                     contrast_boost=1.0),
    "portrait":   _p("PORTRAIT", 1.1, True, 1.0, None, "AREA", (1.0, 0.97, 0.92),
                     distance=2.4, contrast_boost=1.2),
    "rembrandt":  _p("PORTRAIT", 0.9, True, 0.8, 0.12, "SPOT", (1.0, 0.95, 0.85),
                     distance=2.4, color_strength=0.9, contrast_boost=2.0),
    "butterfly":  _p("PORTRAIT", 1.3, True, 0.6, 0.45, "AREA", (1.0, 0.97, 0.95),
                     distance=2.3, color_strength=0.8, contrast_boost=1.3),
    "loop":       _p("PORTRAIT", 1.1, True, 0.7, 0.3, "AREA", (1.0, 0.96, 0.9),
                     distance=2.4, contrast_boost=1.5),
    "split":      _p("PORTRAIT", 0.8, True, 0.5, 0.08, "AREA", (1.0, 0.98, 0.95),
                     distance=2.4, color_strength=0.9, contrast_boost=2.4),
    "clamshell":  _p("PORTRAIT", 2.2, False, 0.0, 0.85, "AREA", (1.0, 0.97, 0.96),
                     distance=2.2, color_strength=0.7, contrast_boost=0.6),
    "beauty":     _p("PORTRAIT", 2.4, True, 0.5, 0.8, "AREA", (1.0, 0.96, 0.95),
                     distance=2.2, color_strength=0.75, contrast_boost=0.6),
    "cinematic":  _p("PORTRAIT", 0.7, True, 1.5, 0.15, "SPOT", (1.05, 0.95, 0.85),
                     intensity=0.22, distance=2.6, color_strength=1.0, contrast_boost=1.9),
    "dramatic":   _p("PORTRAIT", 0.45, True, 0.8, 0.05, "SPOT", (1.0, 0.98, 0.92),
                     intensity=0.22, distance=2.5, color_strength=0.9, contrast_boost=2.6),
    "noir":       _p("PORTRAIT", 0.4, True, 1.2, 0.03, "SPOT", (0.98, 0.99, 1.0),
                     intensity=0.22, distance=2.5, color_strength=0.95, contrast_boost=3.4),
    "low_key":    _p("PORTRAIT", 0.6, True, 0.6, 0.05, "SPOT", (1.0, 0.97, 0.92),
                     intensity=0.2, distance=2.5, color_strength=0.9, contrast_boost=3.0),
    "high_key":   _p("SCENE", 2.6, False, 0.0, 0.9, "AREA", (1.0, 1.0, 1.0),
                     distance=2.8, color_strength=0.55, contrast_boost=0.45),
    "studio":     _p("SCENE", 2.2, False, 0.0, 0.7, "AREA", (1.0, 1.0, 1.0),
                     distance=2.8, color_strength=0.6, contrast_boost=0.7),
    "product":    _p("SCENE", 2.0, True, 0.4, 0.6, "AREA", (1.0, 1.0, 1.0),
                     distance=2.7, color_strength=0.6, contrast_boost=0.9),
    "soft_even":  _p("SCENE", 3.0, False, 0.0, 0.95, "AREA", (1.0, 1.0, 1.0),
                     distance=3.0, color_strength=0.5, contrast_boost=0.4),
    "rim":        _p("PORTRAIT", 1.0, True, 2.0, 0.3, "AREA", (1.0, 0.98, 0.95),
                     distance=2.5, contrast_boost=1.6),
    "backlight":  _p("SCENE", 1.2, True, 2.2, 0.25, "AREA", (1.0, 0.97, 0.9),
                     distance=2.7, color_strength=0.9, contrast_boost=1.8),
    "outdoor":    _p("SCENE", 1.0, False, 0.0, 0.4, "SUN", (1.0, 0.97, 0.9),
                     distance=3.0, contrast_boost=1.3),
    "sunset":     _p("SCENE", 1.0, True, 0.6, 0.35, "SUN", (1.1, 0.82, 0.55),
                     distance=3.0, color_strength=1.0, contrast_boost=2.2),
    "twilight":   _p("SCENE", 1.6, False, 0.0, 0.6, "AREA", (0.7, 0.8, 1.05),
                     distance=2.9, color_strength=0.9, contrast_boost=1.0),
    "neon":       _p("PORTRAIT", 1.0, True, 1.4, 0.4, "AREA", (1.0, 0.5, 0.9),
                     intensity=0.21, distance=2.5, color_strength=1.0, contrast_boost=1.8),
    "candlelight": _p("SCENE", 1.4, False, 0.0, 0.5, "POINT", (1.12, 0.72, 0.42),
                      distance=2.4, color_strength=1.0, contrast_boost=1.8),
    "moonlight":  _p("SCENE", 1.2, True, 0.5, 0.3, "SUN", (0.6, 0.72, 1.05),
                     distance=3.0, color_strength=0.95, contrast_boost=2.2),
    "underlight": _p("PORTRAIT", 0.9, False, 0.0, 0.15, "SPOT", (1.0, 0.95, 0.9),
                     distance=2.4, color_strength=0.9, contrast_boost=2.6),
}

# Shipped default when no user image is loaded (宽光 / Broad Light).
DEFAULT_REFERENCE = "broad_light"
# Temporary icon-view slot while the user image is active (not a file on disk).
CUSTOM_REFERENCE = "custom"

REFERENCE_ORDER = (
    "random",
    # time of day / sky
    "golden_hour", "sunrise", "sunset", "blue_hour", "twilight", "midday",
    "harsh_noon", "overcast", "foggy_morn", "night_sky", "top_sky",
    # studio
    "softbox", "softbox_l", "softbox_r", "beauty_dish", "ring_light",
    "clamshell", "butterfly", "broad_light", "short_light", "high_key",
    "low_key",
    # portrait patterns
    "rembrandt", "rembrandt_r", "loop", "split", "under_light", "hair_light",
    # cinematic / color
    "noir", "teal_orange", "neon_mc", "neon_bp", "candlelight", "firelight",
    "moonlight", "moonlit_win", "horror_up",
    # environment
    "window", "window_blind", "forest", "underwater", "snow_bounce", "desert",
    "street_lamp", "stage_spot", "concert_rgb", "sci_fi",
)

# Translations of the human-readable names live in translations.py under
# "preset_<id>" and "ref_<id>".

_preset_previews = None
_ref_previews = None
# Cache the item lists so Blender does not GC the strings (dynamic enum gotcha).
_enum_cache: dict = {}


# --------------------------------------------------------------------------- #
# Preview loading
# --------------------------------------------------------------------------- #
def _preset_icon_path(pid: str) -> str:
    if pid == "random" and _random_override["preset"]:
        return _random_override["preset"]
    return os.path.join(ICON_DIR, f"preset_{pid}.png")


def _ref_icon_path(rid: str) -> str:
    if rid == "random" and _random_override["reference"]:
        return _random_override["reference"]
    return os.path.join(REF_DIR, f"ref_{rid}.png")


def load_previews():
    global _preset_previews, _ref_previews
    if _preset_previews is None:
        _preset_previews = bpy.utils.previews.new()
        for pid in PRESET_ORDER:
            path = _preset_icon_path(pid)
            if os.path.isfile(path):
                _preset_previews.load(pid, path, "IMAGE")
    if _ref_previews is None:
        _ref_previews = bpy.utils.previews.new()
        for rid in REFERENCE_ORDER:
            path = _ref_icon_path(rid)
            if os.path.isfile(path):
                _ref_previews.load(rid, path, "IMAGE")


def free_previews():
    global _preset_previews, _ref_previews
    for coll in (_preset_previews, _ref_previews):
        if coll is not None:
            bpy.utils.previews.remove(coll)
    _preset_previews = None
    _ref_previews = None


def reference_path(rid: str) -> str:
    return _ref_icon_path(rid)


# --------------------------------------------------------------------------- #
# Random generation (dice button)
# --------------------------------------------------------------------------- #
def _random_path(prefix: str) -> str:
    os.makedirs(RANDOM_DIR, exist_ok=True)
    _random_counter[0] += 1
    return os.path.join(RANDOM_DIR, f"{prefix}_{_random_counter[0]}.png")


# Guard against re-entrant random rolls while the UI still holds preview icons.
_RANDOMIZING = False


def _safe_preview_icon(collection, key: str) -> int:
    """Return icon_id for a preview key, or 0 if the entry is missing or stale."""
    if collection is None or not key:
        return 0
    try:
        if key not in collection:
            return 0
        preview = collection[key]
        if preview is None:
            return 0
        icon = int(getattr(preview, "icon_id", 0) or 0)
        return icon if icon > 0 else 0
    except (KeyError, ReferenceError, AttributeError, RuntimeError, TypeError):
        return 0


def _image_preview_icon(img) -> int:
    """Safe icon_id for a user-loaded reference image (enum draw may race RNA updates)."""
    if img is None:
        return 0
    try:
        if img.name not in bpy.data.images:
            return 0
        if img.size[0] <= 0 or img.size[1] <= 0:
            return 0
        img.preview_ensure()
        prev = img.preview
        if prev is None:
            return 0
        icon = int(getattr(prev, "icon_id", 0) or 0)
        return icon if icon > 0 else 0
    except (ReferenceError, AttributeError, RuntimeError, TypeError):
        return 0


def _pool_key(kind: str) -> str:
    _random_counter[0] += 1
    prefix = "random_p" if kind == "preset" else "random_r"
    return f"{prefix}{_random_counter[0] % _PREVIEW_POOL}"


def _apply_random_preview(kind: str, path: str) -> None:
    """Load one random-slot thumbnail (must not run during icon_view draw)."""
    if not path or not os.path.isfile(path):
        return
    load_previews()
    coll = _preset_previews if kind == "preset" else _ref_previews
    if coll is None:
        return
    key = _pool_key(kind)
    cache_name = "preset" if kind == "preset" else "reference"
    override_key = "preset_key" if kind == "preset" else "reference_key"
    try:
        if key in coll:
            del coll[key]
        coll.load(key, path, "IMAGE")
        _random_override[override_key] = key
        _enum_cache.pop(cache_name, None)
    except (KeyError, RuntimeError, OSError):
        pass


def _queue_random_preview(kind: str) -> None:
    """Defer random thumbnail reload so template_icon_view is not mid-draw."""
    path = _preset_icon_path("random") if kind == "preset" else _ref_icon_path("random")
    _pending_preview_path[kind] = path
    if kind in _preview_apply_pending:
        return
    _preview_apply_pending.add(kind)

    def _fn():
        _preview_apply_pending.discard(kind)
        pending = _pending_preview_path.get(kind)
        _pending_preview_path[kind] = None
        try:
            if pending:
                _apply_random_preview(kind, pending)
            _tag_ui_redraw()
        except Exception:
            pass
        return None

    # Background scripts (headless tests) have no redraw loop — apply immediately.
    if getattr(bpy.app, "background", False):
        _preview_apply_pending.discard(kind)
        _pending_preview_path[kind] = None
        if pending:
            _apply_random_preview(kind, pending)
        return

    bpy.app.timers.register(_fn, first_interval=0.0)


def _reload_random_preview(kind: str):
    """Attach a new preview icon for the ``random`` slot (deferred in interactive UI)."""
    _queue_random_preview(kind)


def _tag_ui_redraw():
    wm = bpy.context.window_manager if bpy.context else None
    if wm is None:
        return
    for window in wm.windows:
        for area in window.screen.areas:
            area.tag_redraw()


def _reload_collection(kind: str):
    """Deprecated alias — kept for callers migrating to in-place reload."""
    _reload_random_preview(kind)


def randomize_preset():
    """Roll a fresh random lighting preset into the 'random' slot."""
    global _RANDOMIZING
    if _RANDOMIZING:
        return
    _RANDOMIZING = True
    try:
        _randomize_preset_impl()
    finally:
        _RANDOMIZING = False


def _randomize_preset_impl():
    from . import gen_assets

    soft = round(_random.uniform(0.4, 2.8), 2)
    has_rim = _random.random() < 0.75
    rim_str = round(_random.uniform(0.4, 2.2), 2)
    fill = None if _random.random() < 0.25 else round(_random.uniform(0.05, 0.85), 2)
    key_type = _random.choice(("AREA", "AREA", "SPOT", "SUN", "POINT"))
    mode = _random.choice(("PORTRAIT", "SCENE"))
    tint = (round(_random.uniform(0.85, 1.12), 2),
            round(_random.uniform(0.85, 1.05), 2),
            round(_random.uniform(0.8, 1.12), 2))
    contrast = round(_random.uniform(0.6, 3.0), 2)

    PRESET_PARAMS["random"] = _p(
        mode, soft, has_rim, rim_str, fill, key_type, tint,
        intensity=round(_random.uniform(0.15, 0.24), 2),
        distance=round(_random.uniform(2.2, 3.0), 2),
        color_strength=round(_random.uniform(0.55, 1.0), 2),
        contrast_boost=contrast,
    )

    kd = (round(_random.uniform(-1.0, 1.0), 2),
          round(_random.uniform(-0.3, 0.9), 2),
          round(_random.uniform(0.3, 1.0), 2))
    img = gen_assets.shade_sphere(
        key_dir=kd, key_col=tint,
        fill_col=tuple(0.5 * c for c in tint),
        amb_col=(0.08, 0.08, 0.1), contrast=max(1.05, contrast),
        rim=rim_str if has_rim else 0.0,
    )
    path = _random_path("preset_random")
    gen_assets.write_png(path, img)
    _random_override["preset"] = path
    _reload_random_preview("preset")


def randomize_reference():
    """Roll a fresh random reference image into the 'random' slot.

    Returns the path of the generated full-size PNG so the caller can load it
    as the active reference image.
    """
    global _RANDOMIZING
    if _RANDOMIZING:
        return None
    _RANDOMIZING = True
    try:
        return _randomize_reference_impl()
    finally:
        _RANDOMIZING = False


def _randomize_reference_impl():
    from . import gen_assets

    palette = [(1.0, 0.78, 0.5), (1.0, 0.58, 0.28), (1.0, 1.0, 1.0),
               (0.6, 0.72, 1.0), (1.0, 0.3, 0.85), (0.2, 0.85, 0.95),
               (1.0, 0.45, 0.7), (0.3, 0.5, 1.0), (0.45, 0.95, 0.5),
               (1.0, 0.5, 0.2)]
    n_blobs = _random.randint(1, 3)
    blobs = []
    for _ in range(n_blobs):
        blobs.append((
            round(_random.uniform(-0.8, 0.8), 2),
            round(_random.uniform(-0.7, 0.85), 2),
            round(_random.uniform(0.7, 2.4), 2),
            round(_random.uniform(0.5, 1.1), 2),
            _random.choice(palette),
        ))
    params = dict(
        base=round(_random.uniform(0.03, 0.5), 2),
        grad=(round(_random.uniform(0.0, 0.6), 2), round(_random.uniform(0.0, 0.6), 2)),
        tint=_random.choice(palette),
        blobs=blobs,
        rim=round(_random.uniform(0.0, 1.2), 2) if _random.random() < 0.4 else 0.0,
        vignette=round(_random.uniform(0.0, 0.5), 2) if _random.random() < 0.5 else 0.0,
        stripes=_random.choice((0.0, 0.0, 0.0, 5.0, 7.0)),
        dapple=_random.choice((0, 0, 0, 12)),
        dapple_seed=_random.randint(0, 9999),
    )
    lin = gen_assets.make_ref(gen_assets.REF_SIZE, **params)
    rgb = gen_assets._gamma(lin)

    old = _random_override["reference"]
    path = _random_path("ref_random")
    gen_assets.write_png(path, rgb)
    _random_override["reference"] = path
    _reload_random_preview("reference")
    if old and os.path.isfile(old):
        try:
            os.remove(old)
        except OSError:
            pass
    return path


# --------------------------------------------------------------------------- #
# EnumProperty item callbacks (icon views)
# --------------------------------------------------------------------------- #
def preset_items(self, context):
    load_previews()
    lang = getattr(self, "language", "EN")
    items = []
    for i, pid in enumerate(PRESET_ORDER):
        pkey = _random_override["preset_key"] if pid == "random" else pid
        icon = _safe_preview_icon(_preset_previews, pkey)
        items.append((pid, tr(lang, f"preset_{pid}"), tr(lang, f"preset_{pid}_desc"), icon, i))
    _enum_cache["preset"] = items
    return items


def reference_order(settings) -> tuple[str, ...]:
    """Built-in reference ids, plus a temporary ``custom`` slot when needed."""
    if getattr(settings, "reference_is_custom", False) and settings.reference_image:
        return (REFERENCE_ORDER[0], CUSTOM_REFERENCE, *REFERENCE_ORDER[1:])
    return REFERENCE_ORDER


def reference_items(self, context):
    load_previews()
    lang = getattr(self, "language", "EN")
    items = []
    for i, rid in enumerate(REFERENCE_ORDER):
        rkey = _random_override["reference_key"] if rid == "random" else rid
        icon = _safe_preview_icon(_ref_previews, rkey)
        items.append((rid, tr(lang, f"ref_{rid}"), tr(lang, f"ref_{rid}_desc"), icon, i))
    if getattr(self, "reference_is_custom", False) and self.reference_image:
        icon = _image_preview_icon(self.reference_image)
        items.insert(1, (
            CUSTOM_REFERENCE,
            tr(lang, "ref_custom"),
            tr(lang, "ref_custom_desc"),
            icon,
            1,
        ))
        for j, it in enumerate(items):
            items[j] = (it[0], it[1], it[2], it[3], j)
    _enum_cache["reference"] = items
    return items


# --------------------------------------------------------------------------- #
# Applying a lighting preset to an analyzed profile
# --------------------------------------------------------------------------- #
def _tint(color, t):
    return tuple(max(0.0, c * k) for c, k in zip(color, t))


def apply_preset(profile, preset_id: str, user_mode: str = "AUTO"):
    """Return a list of LightSpec for ``preset_id`` given an analyzed profile."""
    params = PRESET_PARAMS.get(preset_id)
    if params is None or preset_id == "auto":
        return list(profile.specs)

    if user_mode in ("PORTRAIT", "SCENE"):
        mode = user_mode
    elif params["mode"]:
        mode = params["mode"]
    else:
        mode = analysis._resolve_mode(profile, user_mode)

    specs = analysis.build_specs(profile, mode)

    out = []
    for spec in specs:
        if spec.role == "rim" and params["rim"] is False:
            continue
        size = spec.size * params["softness"]
        energy = spec.energy
        if spec.role == "rim" and params["rim"]:
            energy *= params["rim_strength"]
        if params["fill_ratio"] is not None:
            if spec.role == "fill":
                energy = params["fill_ratio"]
            elif spec.role in ("accent", "sky"):
                energy = params["fill_ratio"] * (0.85 if spec.role == "sky" else 0.6)
        light_type = spec.light_type
        if spec.role == "key" and params["key_type"]:
            light_type = params["key_type"]
        color = _tint(spec.color, params["tint"])

        out.append(analysis.LightSpec(
            role=spec.role, light_type=light_type, direction=spec.direction,
            color=color, energy=energy, size=size,
        ))
    return out


_ROLE_PRIORITY = {"key": 0, "accent": 1, "fill": 1, "rim": 2, "sky": 3, "extra": 4}


def _palette_color_for_role(role, index, palette, profile, spec):
    if getattr(profile, "dual_tone", False):
        if role == "key" and palette:
            return palette[0]["color"]
        if role == "accent":
            return getattr(profile, "accent_color", spec.color)
        if role == "rim":
            if len(palette) > 2:
                return palette[2]["color"]
            return palette[0]["color"] if palette else spec.color
    role_idx = {"key": 0, "fill": 1, "accent": 1, "rim": 2, "sky": 2, "extra": index}
    idx = role_idx.get(role, index)
    if palette and idx < len(palette):
        return palette[idx]["color"]
    return spec.color


def fit_to_count(specs, count, profile, color_strategy: str = "DEFAULT"):
    """Trim or extend a spec list to exactly ``count`` lights.

    Each output light gets ``palette[i]`` so sampled colors match light count.
    """
    count = max(1, int(count))
    ordered = sorted(specs, key=lambda s: _ROLE_PRIORITY.get(s.role, 5))

    palette = list(getattr(profile, "palette", None) or [])
    rgb = getattr(profile, "rgb_small", None)
    lum = getattr(profile, "lum_small", None)
    if len(palette) < count and rgb is not None and lum is not None:
        palette = analysis.sample_palette(rgb, lum, count, strategy=color_strategy)

    if count <= len(ordered):
        out = ordered[:count]
    else:
        out = list(ordered)
        need = count - len(ordered)

        def _key(col):
            return tuple(round(float(c), 2) for c in col)

        used = {_key(s.color) for s in ordered}
        extra, seen = [], set()
        for entry in palette:
            ck = _key(entry["color"])
            if ck in used or ck in seen:
                continue
            seen.add(ck)
            extra.append(entry)
        if not extra:
            extra = palette

        fallback = tuple((b * 0.6 + a * 0.4)
                         for b, a in zip(profile.fill_color, profile.ambient_color))
        mean_lum = max(getattr(profile, "mean_luminance", 0.5), 1e-3)

        for i in range(need):
            if extra:
                entry = extra[i % len(extra)]
                nx, ny = entry["pos"]
                color = entry["color"]
                energy = float(max(0.12, min(0.85, (entry["lum"] / mean_lum) * 0.4)))
                direction = (nx, max(ny, -0.25), 0.7)
            else:
                t = (i + 1) / (need + 1)
                color = fallback
                energy = max(0.12, 0.4 * (1.0 - 0.5 * t))
                direction = (-0.9 + 1.8 * t, 0.15, 0.75)
            out.append(analysis.LightSpec(
                role="extra", light_type="AREA",
                direction=direction, color=color, energy=energy, size=2.0,
            ))

    final = []
    for i, spec in enumerate(out):
        color = _palette_color_for_role(spec.role, i, palette, profile, spec)
        final.append(analysis.LightSpec(
            role=spec.role, light_type=spec.light_type,
            direction=spec.direction, color=color,
            energy=spec.energy, size=spec.size,
        ))
    return final


def apply_defaults(settings, preset_id: str):
    """Seed the tuning sliders from a preset's defaults (no rig change).

    Properties with their lock enabled are left unchanged.
    """
    params = PRESET_PARAMS.get(preset_id)
    if not params:
        return
    d = params.get("defaults")
    if not d:
        return
    _TUNING = (
        ("intensity", "lock_intensity", "intensity"),
        ("distance", "lock_distance", "distance"),
        ("color_strength", "lock_color_strength", "color_strength"),
        ("contrast_boost", "lock_contrast_boost", "contrast_boost"),
    )
    for attr, lock, key in _TUNING:
        if not getattr(settings, lock):
            setattr(settings, attr, d[key])
    if params["mode"]:
        settings.mode = params["mode"]


def register():
    load_previews()


def unregister():
    free_previews()
