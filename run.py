#!/usr/bin/env python3
"""Entry point for Image Layouter.

Usage:
    python run.py

Run this from the project folder (the one containing images/ and
finished-images/). Works the same way on Linux and Windows.
"""

import sys
from pathlib import Path

# Make sure the project's "code" package is importable regardless of
# where this script is launched from.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from code.app import main

if __name__ == "__main__":
    main()
