"""Package the full RollLux extension zip (includes MCP bridge).

Usage:
    py build.py              # GitHub / dev release zip
    py build_marketplace.py  # Blender Extension Platform zip

Produces ``dist/rolllux-<version>.zip`` (repo sibling ``magic-world/dist/``).
"""

from __future__ import annotations

from packaging import build


def main() -> None:
    out = build(marketplace=False)
    print(f"Built {out}")


if __name__ == "__main__":
    main()
