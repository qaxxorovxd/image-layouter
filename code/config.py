"""Default settings and tunable constants for Image Layouter."""

# Default print layout (centimeters) and export quality.
DEFAULT_LAYOUT_W_CM = 10.0
DEFAULT_LAYOUT_H_CM = 15.0
DEFAULT_DPI = 300

# Paper orientation the session starts in: "portrait" (tall) or "landscape" (wide).
# "auto" keeps whatever the startup dialog's width/height imply.
DEFAULT_ORIENTATION = "auto"

# Start every photo in blur-fit mode ("B") instead of crop mode.
DEFAULT_BLUR_FIT = False

# What "N" (skip) does with the original photo: False copies it into
# skipped-images/ and leaves images/ untouched, True moves it out of images/.
SKIP_MOVE_ORIGINAL = False

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

# --- Blur-fit mode ("B"): whole photo on the page, blurred backdrop in the gaps.
# Blur radius, as a fraction of the page's short side.
BLUR_RADIUS_FRACTION = 0.05
# The backdrop is zoomed a little past "cover" so the blur has no edge artefacts.
BLUR_BG_ZOOM = 1.14
# <1.0 darkens the backdrop so the photo stands out from it.
BLUR_BG_BRIGHTNESS = 0.82
# The backdrop is blurred at this size (px, long side) and scaled up afterwards.
BLUR_WORK_SIDE = 360
# Free paper kept on every side, as a fraction of the page (0.0 = photo touches the edges).
BLUR_FG_MARGIN = 0.0
# Page size (px, long side) used for the on-screen blur-fit preview.
BLUR_PREVIEW_SIDE = 900

# Appearance.
CANVAS_BG = "#1e1e1e"
BOX_OUTLINE_COLOR = "#ffcc00"
PAGE_OUTLINE_COLOR = "#ffcc00"
DIM_STIPPLE = "gray50"
