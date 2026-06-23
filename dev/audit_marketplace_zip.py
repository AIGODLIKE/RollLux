"""Quick audit of marketplace zip against common review checks."""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

ZIP = Path(__file__).resolve().parents[2] / "dist" / "rolllux-5.5.5-marketplace.zip"

PATTERNS = [
    ("threading", r"threading"),
    ("exec", r"\bexec\s*\("),
    ("eval", r"\beval\s*\("),
    ("subprocess", r"subprocess"),
    ("sys.path", r"sys\.path"),
    ("if __name__", r"if __name__"),
    ("README.md", None),
    ("mcp files", None),
    ("rolllux_mcp ops", r"rolllux_mcp\."),
    ("clipboard", r"clipboard"),
    ("hardcoded scene", r'bpy\.data\.scenes\["'),
    ("print()", r"\bprint\s*\("),
]

def main() -> int:
    z = zipfile.ZipFile(ZIP)
    py_files = [n for n in z.namelist() if n.endswith(".py")]
    print(f"Zip: {ZIP.name} ({len(z.namelist())} entries, {len(py_files)} .py)\n")

    for label, pat in PATTERNS:
        if label == "README.md":
            hits = [n for n in z.namelist() if n == "README.md"]
        elif label == "mcp files":
            hits = [n for n in z.namelist() if "mcp" in n.lower()]
        elif pat is None:
            hits = []
        else:
            hits = []
            for n in py_files:
                if re.search(pat, z.read(n).decode("utf-8", errors="replace")):
                    hits.append(n)
        status = "OK" if not hits else "FOUND"
        print(f"[{status}] {label}: {hits or '-'}")

    ops = z.read("operators.py").decode()
    print("\nOperators missing bl_options:")
    for block in re.split(r"(?=class RLLX_OT_)", ops):
        if "bl_idname" not in block:
            continue
        name = re.search(r'bl_idname = "([^"]+)"', block)
        if name and "bl_options" not in block.split("def ")[0]:
            print(f"  - {name.group(1)}")

    ui = z.read("ui.py").decode()
    print(f"\nui.py references mcp: {'mcp' in ui.lower()}")
    print(f"properties mcp_port: {'mcp_port' in z.read('properties.py').decode()}")

    tr = z.read("translations.py").decode()
    for key in ("msg_pasted", "err_no_clip", "mcp_start", "language"):
        print(f"translations dead key {key!r}: {key in tr}")

    manifest = z.read("blender_manifest.toml").decode()
    for field in ("support", "website", "[permissions]", "files"):
        print(f"manifest has {field!r}: {field in manifest}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
