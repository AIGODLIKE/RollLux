"""Audit RollLux UI i18n completeness (offline)."""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import translations as T
from translations import TR, _PROP_DESC, _PROP_NAME

try:
    from presets import PRESET_ORDER, REFERENCE_ORDER
except ImportError:
    PRESET_ORDER = ()
    REFERENCE_ORDER = ()

LANGS = ("EN", "ZH", "JA")
ROOT = os.path.dirname(__file__)


def main() -> int:
    issues: list[str] = []

    for key, entry in TR.items():
        if not isinstance(entry, dict):
            issues.append(f"TR[{key!r}] not a dict")
            continue
        for lang in LANGS:
            val = entry.get(lang)
            if val is None or not str(val).strip():
                issues.append(f"TR[{key!r}] missing or empty {lang}")

    for prop, desc_key in _PROP_DESC.items():
        if desc_key not in TR:
            issues.append(f"_PROP_DESC {prop} -> missing TR key {desc_key!r}")

    for prop, name_key in _PROP_NAME.items():
        if name_key not in TR:
            issues.append(f"_PROP_NAME {prop} -> missing {name_key!r}")

    ui_keys: set[str] = set()
    for fn in ("ui.py", "operators.py"):
        text = open(os.path.join(ROOT, fn), encoding="utf-8").read()
        ui_keys.update(re.findall(r"""tr\(\s*['\"]([a-zA-Z0-9_]+)['\"]""", text))
    for key in sorted(ui_keys):
        if key not in TR:
            issues.append(f"UI tr() key missing from TR: {key!r}")

    for r in ("key", "fill", "rim", "sky", "accent", "extra"):
        if f"role_{r}" not in TR:
            issues.append(f"missing role_{r}")

    if "ui_mode" not in _PROP_DESC:
        issues.append("ui_mode not in _PROP_DESC (tooltip stays English)")

    for pid in PRESET_ORDER:
        for suffix in ("", "_desc"):
            k = f"preset_{pid}{suffix}"
            if k not in TR:
                issues.append(f"missing preset translation {k}")

    for rid in REFERENCE_ORDER:
        for suffix in ("", "_desc"):
            k = f"ref_{rid}{suffix}"
            if k not in TR:
                issues.append(f"missing reference translation {k}")

    class _S:
        language = "ZH"

    s = _S()
    for fn in (
        "ui_mode_items", "ae_apply_to_items", "ae_center_preset_items",
        "ae_mode_items", "mode_items", "target_items", "orient_items",
        "color_strategy_items", "distribution_color_mode_items", "corner_items",
    ):
        for item in getattr(T, fn)(s, None):
            name = item[1]
            desc = item[2] if len(item) > 2 else ""
            if name.startswith(("ae_", "ui_mode_", "desc_", "mode_", "target_", "orient_",
                                "distribution_color_mode_", "color_strategy_")):
                issues.append(f"{fn} untranslated label: {name!r}")
            if desc and desc.startswith(("ae_", "desc_", "mode_", "target_", "orient_",
                                          "distribution_color_mode_", "color_strategy_")):
                issues.append(f"{fn} untranslated desc: {item[0]!r} -> {desc!r}")

    op_text = open(os.path.join(ROOT, "operators.py"), encoding="utf-8").read()
    if re.search(r'report\(\{[^}]+\},\s*"[^"]+"\)', op_text):
        issues.append("operator report uses hardcoded English string")

    from translations import _OPERATOR_LABELS
    for cls_name in (
        "open_image", "analyze", "generate", "clear",
        "preset_step", "random_preset", "auto_timer", "reference_step",
        "random_reference", "set_rendered", "bake_ae", "delete_light",
    ):
        bl_id = f"rolllux.{cls_name}"
        if bl_id not in _OPERATOR_LABELS:
            issues.append(f"operator missing i18n map: {bl_id}")

    print(f"Issues: {len(issues)}")
    for issue in issues:
        print(f"  - {issue}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
