"""Package the add-on into an installable Blender extension zip.

Usage:
    py build.py

Produces ``dist/rolllux-<version>.zip`` (repo sibling ``magic-world/dist/``).
"""

from __future__ import annotations

import os
import re
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(os.path.dirname(HERE), "dist")

INCLUDE = (
    "blender_manifest.toml",
    "__init__.py",
    "properties.py",
    "operators.py",
    "lighting.py",
    "ae_metering.py",
    "auto_exposure.py",
    "analysis.py",
    "ui.py",
    "translations.py",
    "presets.py",
    "overlay.py",
    "clipboard.py",
    "gen_assets.py",
    "README.md",
)

INCLUDE_DIRS = (
    ("icons", ".png"),
    ("references", ".png"),
)


def _version() -> str:
    manifest = os.path.join(HERE, "blender_manifest.toml")
    with open(manifest, "r", encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return m.group(1) if m else "0.0.0"


def main() -> None:
    version = _version()
    os.makedirs(DIST, exist_ok=True)
    out = os.path.join(DIST, f"rolllux-{version}.zip")

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in INCLUDE:
            path = os.path.join(HERE, name)
            if os.path.isfile(path):
                zf.write(path, arcname=name)
            else:
                print(f"  (skip missing) {name}")
        for folder, ext in INCLUDE_DIRS:
            d = os.path.join(HERE, folder)
            if not os.path.isdir(d):
                print(f"  (skip missing dir) {folder}")
                continue
            for fn in sorted(os.listdir(d)):
                if fn.lower().endswith(ext):
                    zf.write(os.path.join(d, fn), arcname=f"{folder}/{fn}")
    print(f"Built {out}")


if __name__ == "__main__":
    main()
