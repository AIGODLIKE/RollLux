"""Development helper — regenerate icon/reference PNG assets (excluded from release zip).

Usage:
    py dev/gen_assets_main.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gen_assets import main

if __name__ == "__main__":
    main()
