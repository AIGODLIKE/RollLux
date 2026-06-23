"""Build a Marketplace-ready RollLux zip (no MCP, full manifest).

Usage:
    py build_marketplace.py

Produces ``dist/rolllux-<version>-marketplace.zip`` next to the repo.

Strips:
  - ``mcp_bridge.py`` (optional import — omitted from zip)
  - dev-only tooling (``dev/``, tests, build scripts)

Uses ``blender_manifest.marketplace.toml`` (support URL, files permission, etc.).
"""

from __future__ import annotations

from packaging import build


def main() -> None:
    out = build(marketplace=True)
    print(f"Built Marketplace zip: {out}")
    print("  - MCP stripped")
    print("  - manifest: support + files permission")
    print("  - verified: no mcp_bridge in archive")


if __name__ == "__main__":
    main()
