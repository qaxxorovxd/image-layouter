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


def unique_path(path: Path) -> Path:
    """Return *path*, or the same name with a -2, -3 ... suffix if it is already taken."""
    path = Path(path)
    if not path.exists():
        return path
    n = 2
    while True:
        candidate = path.with_name(f"{path.stem}-{n}{path.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def cm_to_px(cm: float, dpi: int) -> int:
    return round(cm / 2.54 * dpi)
