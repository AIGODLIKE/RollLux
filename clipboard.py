"""Grab an image from the OS clipboard and save it to a temp PNG.

Blender's Python API has no cross-platform clipboard-image accessor, so we shell
out to a per-OS helper that dumps the clipboard bitmap to a PNG file which is
then loaded (and packed) as a normal ``bpy.types.Image``.

Returns the temp file path on success, or ``None`` when the clipboard holds no
image (or the platform helper is unavailable).
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile


def _temp_path() -> str:
    return os.path.join(tempfile.gettempdir(), "rolllux_clipboard.png")


def _run(cmd, **kw) -> bool:
    try:
        flags = 0
        if sys.platform.startswith("win"):
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        res = subprocess.run(
            cmd, capture_output=True, timeout=20, creationflags=flags, **kw
        )
        return res.returncode == 0
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired, ValueError):
        return False


def grab_clipboard_image() -> str | None:
    """Save the current clipboard image to a temp PNG; return its path or None."""
    out = _temp_path()
    try:
        if os.path.exists(out):
            os.remove(out)
    except OSError:
        pass

    plat = sys.platform
    if plat.startswith("win"):
        safe = out.replace("'", "''")
        script = (
            "Add-Type -AssemblyName System.Windows.Forms;"
            "Add-Type -AssemblyName System.Drawing;"
            "$img=[System.Windows.Forms.Clipboard]::GetImage();"
            "if($img -ne $null){"
            "$img.Save('" + safe + "',"
            "[System.Drawing.Imaging.ImageFormat]::Png);exit 0}else{exit 3}"
        )
        _run([
            "powershell", "-NoProfile", "-NonInteractive",
            "-ExecutionPolicy", "Bypass", "-Command", script,
        ])
    elif plat == "darwin":
        # Requires `pngpaste` (brew install pngpaste).
        _run(["pngpaste", out])
    else:
        # Linux/X11: xclip (or wl-paste on Wayland) writing PNG to stdout.
        try:
            with open(out, "wb") as fh:
                ok = _run(
                    ["xclip", "-selection", "clipboard", "-t", "image/png", "-o"],
                    stdout=fh,
                )
            if not ok or os.path.getsize(out) == 0:
                with open(out, "wb") as fh:
                    _run(["wl-paste", "--type", "image/png"], stdout=fh)
        except OSError:
            pass

    if os.path.exists(out) and os.path.getsize(out) > 0:
        return out
    return None
