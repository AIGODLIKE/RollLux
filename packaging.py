"""Shared RollLux extension packaging (full dev zip vs Marketplace zip)."""

from __future__ import annotations

import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIST = HERE.parent / "dist"

# Runtime files shipped in every install zip.
CORE_FILES = (
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
    "gen_assets.py",
)

# GitHub / dev release zip extras (docs + MCP bridge).
DEV_FILES = (
    "README.md",
    "mcp_bridge.py",
)

ASSET_DIRS = (
    ("icons", ".png"),
    ("references", ".png"),
)

_STRIP_BEGIN = "# MARKETPLACE_STRIP_BEGIN"
_STRIP_END = "# MARKETPLACE_STRIP_END"


def read_version(manifest: Path | None = None) -> str:
    path = manifest or (HERE / "blender_manifest.toml")
    text = path.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return match.group(1) if match else "0.0.0"


def strip_marketplace_blocks(text: str) -> str:
    """Drop lines between MARKETPLACE_STRIP_BEGIN/END markers (inclusive)."""
    out: list[str] = []
    skipping = False
    for line in text.splitlines(keepends=True):
        if _STRIP_BEGIN in line:
            skipping = True
            continue
        if _STRIP_END in line:
            skipping = False
            continue
        if not skipping:
            out.append(line)
    return "".join(out)


def _sync_manifest_version(template_text: str, version: str) -> str:
    return re.sub(
        r'^version\s*=.*$',
        f'version = "{version}"',
        template_text,
        count=1,
        flags=re.MULTILINE,
    )


def _prepare_file(src: Path, dest: Path, *, marketplace: bool) -> None:
    text = src.read_text(encoding="utf-8")
    if marketplace:
        text = strip_marketplace_blocks(text)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8", newline="\n")


def _stage_tree(staging: Path, *, marketplace: bool) -> None:
    version = read_version()
    files = CORE_FILES if marketplace else (*CORE_FILES, *DEV_FILES)

    for name in files:
        src = HERE / name
        if not src.is_file():
            raise FileNotFoundError(f"Missing packaging source: {src}")
        _prepare_file(src, staging / name, marketplace=marketplace)

    if marketplace:
        manifest_src = HERE / "blender_manifest.marketplace.toml"
        manifest_text = _sync_manifest_version(
            manifest_src.read_text(encoding="utf-8"), version,
        )
        (staging / "blender_manifest.toml").write_text(
            manifest_text, encoding="utf-8", newline="\n",
        )
    else:
        shutil.copy2(HERE / "blender_manifest.toml", staging / "blender_manifest.toml")

    for folder, ext in ASSET_DIRS:
        src_dir = HERE / folder
        if not src_dir.is_dir():
            raise FileNotFoundError(f"Missing asset directory: {src_dir}")
        for fn in sorted(src_dir.iterdir()):
            if fn.suffix.lower() == ext:
                dest = staging / folder / fn.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(fn, dest)


def _write_zip(staging: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(staging):
            root_path = Path(root)
            for fn in sorted(files):
                full = root_path / fn
                arcname = full.relative_to(staging).as_posix()
                zf.write(full, arcname=arcname)


def _verify_marketplace_zip(out_path: Path) -> list[str]:
    issues: list[str] = []
    forbidden = (
        "mcp_bridge.py",
        "mcp/",
        "README.md",
    )
    required = (
        "blender_manifest.toml",
        "__init__.py",
        "icons/",
    )
    with zipfile.ZipFile(out_path, "r") as zf:
        names = zf.namelist()
        for bad in forbidden:
            if any(n == bad or n.startswith(bad) for n in names):
                issues.append(f"forbidden path in zip: {bad}")
        for need in required:
            if not any(n == need or n.startswith(need) for n in names):
                issues.append(f"missing required path: {need}")
        manifest = zf.read("blender_manifest.toml").decode("utf-8")
        if "support" not in manifest:
            issues.append("manifest missing support URL")
        if "[permissions]" not in manifest:
            issues.append("manifest missing [permissions]")
        if "mcp" in manifest.lower():
            issues.append("manifest mentions MCP")
        if re.search(r'files\s*=.*\.', manifest):
            issues.append("files permission description ends with a period")
        if "CC0" not in manifest and "cc0" not in manifest.lower():
            issues.append("manifest missing CC0 license for bundled PNGs")
    return issues


def _verify_marketplace_staging(staging: Path) -> list[str]:
    issues: list[str] = []
    if (staging / "README.md").is_file():
        issues.append("README.md must not ship in marketplace zip")
    init = (staging / "__init__.py").read_text(encoding="utf-8")
    if "bl_info" in init:
        issues.append("__init__.py still contains bl_info")
    if "mcp_bridge" in init:
        issues.append("__init__.py still references mcp_bridge")
    if "MARKETPLACE_STRIP_BEGIN" in init:
        issues.append("__init__.py still contains strip markers")
    ga = (staging / "gen_assets.py").read_text(encoding="utf-8")
    if "pip install" in ga.lower():
        issues.append("gen_assets.py still mentions pip install")
    if "def main(" in ga:
        issues.append("gen_assets.py still contains main()")
    if re.search(r"\bprint\s*\(", ga):
        issues.append("gen_assets.py still contains print()")
    for rel in ("ui.py", "translations.py", "properties.py"):
        text = (staging / rel).read_text(encoding="utf-8")
        if "mcp_bridge" in text or "rolllux_mcp" in text:
            issues.append(f"{rel} still references MCP")
        if "MARKETPLACE_STRIP_BEGIN" in text:
            issues.append(f"{rel} still contains strip markers")
    ops = (staging / "operators.py").read_text(encoding="utf-8")
    if re.search(r'bl_idname = "rolllux\.', ops):
        issues.append("operators still use rolllux.* bl_idname")
    if "bl_idname = \"wm.rolllux_" not in ops:
        issues.append("operators missing wm.rolllux_* bl_idname")
    props = (staging / "properties.py").read_text(encoding="utf-8")
    if "load_post" in props and "ensure_runtime_hooks" not in props:
        issues.append("properties registers load_post at import/register time")
    if "mcp_port" in props:
        issues.append("properties still defines mcp_port")
    tr = (staging / "translations.py").read_text(encoding="utf-8")
    for dead in ("msg_pasted", "err_no_clip", "mcp_start", '"language"'):
        if dead in tr:
            issues.append(f"translations still contains {dead}")
    return issues


def build(*, marketplace: bool = False) -> Path:
    version = read_version()
    suffix = "-marketplace" if marketplace else ""
    out_path = DIST / f"rolllux-{version}{suffix}.zip"

    with tempfile.TemporaryDirectory(prefix="rolllux-pack-") as tmp:
        staging = Path(tmp)
        _stage_tree(staging, marketplace=marketplace)
        if marketplace:
            issues = _verify_marketplace_staging(staging)
            if issues:
                raise RuntimeError(
                    "Marketplace staging verification failed:\n  - "
                    + "\n  - ".join(issues)
                )
        _write_zip(staging, out_path)

    if marketplace:
        issues = _verify_marketplace_zip(out_path)
        if issues:
            out_path.unlink(missing_ok=True)
            raise RuntimeError(
                "Marketplace zip verification failed:\n  - "
                + "\n  - ".join(issues)
            )

    return out_path
