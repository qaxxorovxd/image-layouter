"""Small filesystem helpers: image discovery and natural sorting."""

import re
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff", ".gif"}

_num_re = re.compile(r"(\d+)")


def natural_sort_key(path: Path):
    """Sort key so '2.jpg' comes before '10.jpg' (plain alphabetic sort would not)."""
    parts = _num_re.split(path.name)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def list_images(directory: Path):
    """Return all supported image files in *directory*, naturally sorted by name."""
    directory = Path(directory)
    if not directory.exists():
        return []
    files = [p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
    files.sort(key=natural_sort_key)
    return files


def cm_to_px(cm: float, dpi: int) -> int:
    return round(cm / 2.54 * dpi)
