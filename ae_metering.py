"""Pure-Python auto-exposure metering (no bpy import — testable offline)."""

from __future__ import annotations

import math

_MID_GREY = 0.18
_HIGHLIGHT_PERCENTILE = 0.85
_P60_PERCENTILE = 0.60
_TRIM_FRAC = 0.10
_LUM_FLOOR = 1e-5
_MIN_VALID_RATIO = 0.25


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    idx = int(round((len(s) - 1) * p))
    return s[max(0, min(idx, len(s) - 1))]


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2:
        return s[mid]
    return 0.5 * (s[mid - 1] + s[mid])


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _trim_mean(values: list[float], trim_frac: float = _TRIM_FRAC) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    n = len(s)
    k = max(0, int(n * trim_frac))
    if k * 2 >= n:
        return _median(s)
    trimmed = s[k:n - k]
    return sum(trimmed) / len(trimmed)


def _log_mean(values: list[float]) -> float:
    """Geometric mean via log domain — stable for HDR mixes."""
    if not values:
        return 0.0
    logs = [math.log(max(v, _LUM_FLOOR)) for v in values]
    return math.exp(sum(logs) / len(logs))


def _aggregate(values: list[float], mode: str) -> float:
    if mode == "MEDIAN":
        return _median(values)
    if mode == "HIGHLIGHT":
        return _percentile(values, _HIGHLIGHT_PERCENTILE)
    if mode == "P60":
        return _percentile(values, _P60_PERCENTILE)
    if mode == "TRIM_MEAN":
        return _trim_mean(values)
    if mode == "LOG_AVERAGE":
        return _log_mean(values)
    return _mean(values)


def prepare_samples(
    raw_lums: list[float],
    min_valid_ratio: float = _MIN_VALID_RATIO,
    lum_floor: float = _LUM_FLOOR,
) -> tuple[list[float], bool]:
    """Apply luminance floor to dark pixels; reject when too few valid samples."""
    if not raw_lums:
        return [], False
    nonzero = sum(1 for v in raw_lums if v > lum_floor)
    if nonzero / len(raw_lums) < min_valid_ratio:
        return [], False
    return [max(lum_floor, v) for v in raw_lums], True


def meter_luminance(
    all_lums: list[float],
    center_lums: list[float],
    mode: str,
    center_weight: float,
) -> float:
    if not all_lums:
        return 0.0
    weight = max(0.0, min(1.0, center_weight / 100.0))
    cen = center_lums or all_lums
    full = _aggregate(all_lums, mode)
    center = _aggregate(cen, mode)
    return _lerp(full, center, weight)


def target_luminance(settings, scene) -> float:
    if getattr(settings, "ae_mode", "AVERAGE") == "REFERENCE":
        res = getattr(scene, "rolllux_result", None)
        if res is not None and res.valid and float(res.mean_luminance) > 1e-4:
            return float(res.mean_luminance)
        cached = float(getattr(settings, "cache_mean_lum", 0.0))
        if cached > 1e-4:
            return cached
    return _MID_GREY


def compute_target_ev(avg_lum: float, target_lum: float, ev_bias: float) -> float:
    if avg_lum <= 0.0 or target_lum <= 0.0:
        return 0.0
    return -math.log2(avg_lum / target_lum) + float(ev_bias)
