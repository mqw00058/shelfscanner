import uuid

import cv2
import numpy as np

from backend.config import CROPS_DIR, CROP_MIN_AREA

# Padding ratios: how much to expand the bbox in each direction.
# These ensure shelf rails and price tags are visible in the crop.
PAD_LEFT = 0.25      # 25% of bbox width added to the left
PAD_RIGHT = 0.25     # 25% of bbox width added to the right
PAD_TOP = 0.30       # 30% of bbox height added above (shelf rail)
PAD_BOTTOM = 0.40    # 40% of bbox height added below (price tag area)

# Extra padding for products with large price signs
LARGE_SIGN_PAD_TOP = 0.55   # 55% above to capture hanging/large sign
LARGE_SIGN_PAD_BOTTOM = 0.20


def crop_products(
    frame: np.ndarray, products: list[dict], price_tag_position: str = "below"
) -> list[dict]:
    """Crop product regions from the frame with generous padding.

    The crop includes the product, surrounding shelf structure,
    and price tag area — like a "product display zone".
    price_tag_position controls which direction gets more padding:
    - "below": more padding below for price tag (default)
    - "above": more padding above for price tag
    """
    h, w = frame.shape[:2]

    # Flip top/bottom padding based on where the price tags are
    if price_tag_position == "above":
        default_pad_top = PAD_BOTTOM   # 0.40 — more room for price tag above
        default_pad_bottom = PAD_TOP   # 0.30
    else:
        default_pad_top = PAD_TOP      # 0.30
        default_pad_bottom = PAD_BOTTOM  # 0.40 — more room for price tag below

    for product in products:
        bbox = product.get("bbox")
        if not bbox or len(bbox) != 4:
            product["_needs_web_image"] = True
            continue

        bx, by, bw, bh = [int(v) for v in bbox]

        # For large price signs, use extra top padding so sign is at top-center
        is_large_sign = product.get("price_sign_type") == "large"
        if is_large_sign:
            pad_top = LARGE_SIGN_PAD_TOP
            pad_bot = LARGE_SIGN_PAD_BOTTOM
        else:
            pad_top = default_pad_top
            pad_bot = default_pad_bottom

        # Expand bbox with padding to include shelf + price tag
        pad_l = int(bw * PAD_LEFT)
        pad_r = int(bw * PAD_RIGHT)
        pad_t = int(bh * pad_top)
        pad_b = int(bh * pad_bot)

        x1 = max(0, bx - pad_l)
        y1 = max(0, by - pad_t)
        x2 = min(w, bx + bw + pad_r)
        y2 = min(h, by + bh + pad_b)

        crop_w = x2 - x1
        crop_h = y2 - y1

        if crop_w <= 0 or crop_h <= 0:
            product["_needs_web_image"] = True
            continue

        crop = frame[y1:y2, x1:x2]
        area = crop_w * crop_h

        # Quality checks
        if area < CROP_MIN_AREA:
            product["_needs_web_image"] = True
            continue

        if _is_blurry(crop) or _is_uniform(crop):
            product["_needs_web_image"] = True
            continue

        # Enhance the crop before saving
        crop = _enhance_crop(crop)

        # Save crop
        filename = f"{uuid.uuid4().hex}.jpg"
        crop_path = CROPS_DIR / filename
        cv2.imwrite(str(crop_path), crop, [cv2.IMWRITE_JPEG_QUALITY, 92])
        product["image"] = f"/api/crops/{filename}"
        product["_needs_web_image"] = False

    return products


def _is_blurry(crop: np.ndarray) -> bool:
    """Check if crop is too blurry to be useful as a product image."""
    if crop.size == 0:
        return True
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < 30.0


def _is_uniform(crop: np.ndarray) -> bool:
    """Check if crop is too uniform (blank area, single color)."""
    if crop.size == 0:
        return True
    return np.std(crop) < 15


def _enhance_crop(crop: np.ndarray) -> np.ndarray:
    """Lightly enhance crop for display quality."""
    lab = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    gaussian = cv2.GaussianBlur(enhanced, (0, 0), 1.5)
    sharpened = cv2.addWeighted(enhanced, 1.3, gaussian, -0.3, 0)

    return sharpened
