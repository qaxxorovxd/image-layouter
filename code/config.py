"""Default settings and tunable constants for Image Layouter."""

# Default print layout (centimeters) and export quality.
DEFAULT_LAYOUT_W_CM = 10.0
DEFAULT_LAYOUT_H_CM = 15.0
DEFAULT_DPI = 300

# How far one W/A/S/D (or arrow key) press moves the crop box,
# as a fraction of the box's current height.
PAN_STEP_FRACTION = 0.04

# How much one zoom step (key "1"/"2" or mouse wheel notch) changes
# the crop box size. >1.0, applied as a multiply/divide pair.
ZOOM_FACTOR = 1.08

# Smallest the crop box may shrink to (zoom in limit), as a fraction
# of the largest box that fits the whole image.
MIN_ZOOM_FRACTION = 0.12

# Largest side (px) used for the cached preview image. Keeps panning/
# zooming smooth even for very large source photos.
MAX_PREVIEW_SIDE = 2000

# Appearance.
CANVAS_BG = "#1e1e1e"
BOX_OUTLINE_COLOR = "#ffcc00"
DIM_STIPPLE = "gray50"
