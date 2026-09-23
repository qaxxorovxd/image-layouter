"""Composing one photo onto the page: a plain crop, or the whole photo on a blurred backdrop."""

import math

from PIL import Image, ImageEnhance, ImageFilter

from . import config as cfg


def _to_rgb(img):
    """Flatten alpha onto white so pasting/blurring behaves predictably."""
    if img.mode == "RGB":
        return img
    if img.mode in ("RGBA", "LA", "P"):
        rgba = img.convert("RGBA")
        flat = Image.new("RGB", rgba.size, "white")
        flat.paste(rgba, mask=rgba.split()[-1])
        return flat
    return img.convert("RGB")


def _cover(img, size, zoom=1.0):
    """Resize *img* so it fully covers *size* (optionally zoomed past it), then centre-crop."""
    tw, th = size
    scale = max(tw / img.width, th / img.height) * zoom
    w = max(tw, int(math.ceil(img.width * scale)))
    h = max(th, int(math.ceil(img.height * scale)))
    resized = img.resize((w, h), Image.LANCZOS)
    left = (w - tw) // 2
    top = (h - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def crop_fit(img, box, target_size):
    """Classic behaviour: cut *box* (x0, y0, x1, y1) out of *img* and scale it to the page."""
    x0, y0, x1, y1 = box
    x0, y0 = max(0, int(round(x0))), max(0, int(round(y0)))
    x1 = min(img.width, int(round(x1)))
    y1 = min(img.height, int(round(y1)))
    return img.crop((x0, y0, x1, y1)).resize(target_size, Image.LANCZOS)


def blur_fit(img, target_size):
    """Fit the whole photo on the page and fill the leftover paper with a blurred backdrop.

    The backdrop is blurred at a small working size and scaled back up — visually the
    same as blurring at full resolution, but fast enough to redraw while previewing.
    """
    tw, th = target_size
    img = _to_rgb(img)

    work_scale = min(1.0, cfg.BLUR_WORK_SIDE / max(tw, th))
    ww = max(16, int(round(tw * work_scale)))
    wh = max(16, int(round(th * work_scale)))

    backdrop = _cover(img, (ww, wh), zoom=cfg.BLUR_BG_ZOOM)
    radius = max(1.0, min(ww, wh) * cfg.BLUR_RADIUS_FRACTION)
    backdrop = backdrop.filter(ImageFilter.GaussianBlur(radius))
    if cfg.BLUR_BG_BRIGHTNESS != 1.0:
        backdrop = ImageEnhance.Brightness(backdrop).enhance(cfg.BLUR_BG_BRIGHTNESS)
    page = backdrop.resize((tw, th), Image.BILINEAR)

    # The photo itself, untouched, as large as it can be without being cut.
    avail_w = tw * (1.0 - 2 * cfg.BLUR_FG_MARGIN)
    avail_h = th * (1.0 - 2 * cfg.BLUR_FG_MARGIN)
    scale = min(avail_w / img.width, avail_h / img.height)
    fw = max(1, int(round(img.width * scale)))
    fh = max(1, int(round(img.height * scale)))
    photo = img.resize((fw, fh), Image.LANCZOS)
    page.paste(photo, ((tw - fw) // 2, (th - fh) // 2))
    return page
