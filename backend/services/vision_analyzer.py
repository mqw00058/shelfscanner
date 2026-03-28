import base64
import json
import re

import anthropic
import cv2
import numpy as np

from backend.config import ANTHROPIC_API_KEY, VISION_MODEL

SYSTEM_PROMPT = """You are an expert retail shelf and price tag analyzer with exceptional OCR ability.
Your job is to meticulously examine store shelf images and extract every product with precise pricing.

You MUST respond with ONLY a valid JSON array. No markdown, no explanation, no code fences.

Each object in the array MUST have these fields:
- "name": the FULL official product name exactly as printed on the price tag or product label.
  IMPORTANT: Price tags in US stores typically show the product name in SMALL TEXT on the tag itself
  (often above or below the price). Read this text carefully. Include brand name + product name + variant.
  Example: "Kirkland Signature Organic Extra Virgin Olive Oil" not just "Olive Oil".
- "price": the displayed retail price as a number (float). Read the LARGE numbers on the price tag.
  Be precise: $4.99 → 4.99, $12.49 → 12.49. Return null ONLY if truly unreadable.
- "unit": size/weight/quantity as shown on the tag or product (e.g. "2L", "24 ct", "1.5 lbs"), or null
- "unit_price": per-unit price if shown on the tag (e.g. "$0.42/oz", "4.2¢/fl oz"), or null
- "desc": one-sentence description of the product
- "shelf": position description (e.g. "Top shelf, 3rd from left", "Bottom shelf, center")
- "emoji": single emoji representing the product
- "bbox": bounding box [x, y, width, height] in pixel coordinates.
  IMPORTANT: The bbox must be WIDE and TALL — it should include:
  (a) the product itself on the shelf,
  (b) the shelf edge/rail visible above or below the product,
  (c) the price tag attached to the shelf edge for this product.
  Think of it as a "product display zone" — the full area a shopper would see
  when looking at that product on the shelf, NOT a tight crop around just the item.

CRITICAL RULES:
1. PRICE TAGS: Examine every price tag on every shelf edge. US store price tags show:
   - LARGE bold price (e.g. "4.99" or "$4.99")
   - Small product description text (this IS the product name — read it!)
   - Sometimes a unit price in smaller text
   - Sometimes a barcode
2. PRODUCT LABELS: Also read text directly on product packaging/bottles/boxes
3. Match each price tag to the product it belongs to (usually directly above the tag)
4. LARGE PRICE SIGNS: Some products have large promotional price signs, placards,
   or hanging tags (not just small shelf-edge tags). These big signs often show the price
   in very large text and the product name/description. Detect these products too!
   For large signs, set "price_sign_type": "large" in the product object.
   For regular shelf-edge tags, set "price_sign_type": "shelf_tag" or omit it.
5. Do NOT skip products just because the image is slightly blurry — try your best
6. Do NOT invent prices — only report what you can actually read
7. If you can read the product name but not the price, still include it with price: null
8. Be thorough — scan left to right, top shelf to bottom shelf, miss nothing"""


def analyze_frame(frame: np.ndarray, store_name: str, price_tag_position: str = "below") -> list[dict]:
    """Send a frame to Claude Vision API and get detected products."""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set. Add it to your .env file.")

    # Send both the original and an enhanced crop for price tag reading
    frame_resized = _resize_for_api(frame)

    # Encode original frame
    _, buffer = cv2.imencode(".jpg", frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 92])
    image_b64 = base64.b64encode(buffer).decode("utf-8")

    # Create a contrast-enhanced version for better text readability
    enhanced = _enhance_for_ocr(frame_resized)
    _, buffer_enh = cv2.imencode(".jpg", enhanced, [cv2.IMWRITE_JPEG_QUALITY, 92])
    enhanced_b64 = base64.b64encode(buffer_enh).decode("utf-8")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    if price_tag_position == "above":
        tag_location_hint = (
            "NOTE: In this store, price tags are located ABOVE the products on the shelf. "
            "Look at the shelf edge ABOVE each product to find its price tag. "
            "The bbox should extend upward to include the price tag area above the product."
        )
    else:
        tag_location_hint = (
            "NOTE: In this store, price tags are located BELOW the products on the shelf. "
            "Look at the shelf edge BELOW each product to find its price tag. "
            "The bbox should extend downward to include the price tag area below the product."
        )

    user_prompt = (
        f"This is a store shelf image from {store_name}. "
        f"Image 1 is the original photo. Image 2 is an enhanced version for better text readability. "
        f"Use BOTH images to detect products and read price tags accurately.\n\n"
        f"The image is {frame_resized.shape[1]}x{frame_resized.shape[0]} pixels — "
        f"use these dimensions for bbox coordinates.\n\n"
        f"{tag_location_hint}\n\n"
        f"IMPORTANT: Look carefully at every price tag on the shelf edges. "
        f"The small text on price tags contains the product name — read it precisely. "
        f"The large numbers are the price — read every digit carefully.\n\n"
        f"Return ONLY a JSON array."
    )

    response = client.messages.create(
        model=VISION_MODEL,
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": enhanced_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": user_prompt,
                    },
                ],
            }
        ],
    )

    raw_text = response.content[0].text.strip()
    products = _parse_products_json(raw_text)

    # Post-process: validate prices
    for p in products:
        price = p.get("price")
        if price is not None:
            try:
                price = float(price)
                # Sanity check: typical grocery price range
                if price < 0 or price > 9999:
                    p["price"] = None
                else:
                    p["price"] = round(price, 2)
            except (ValueError, TypeError):
                p["price"] = None

    return products


def _resize_for_api(frame: np.ndarray, max_dim: int = 1568) -> np.ndarray:
    """Resize frame so the longest side is at most max_dim pixels."""
    h, w = frame.shape[:2]
    if max(h, w) <= max_dim:
        return frame
    scale = max_dim / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)


def _enhance_for_ocr(frame: np.ndarray) -> np.ndarray:
    """Create an enhanced version optimized for reading small text on price tags."""
    # Convert to LAB and boost contrast on L channel
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Aggressive CLAHE for text visibility
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))
    l = clahe.apply(l)

    lab = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # Strong unsharp mask
    gaussian = cv2.GaussianBlur(enhanced, (0, 0), 2)
    sharpened = cv2.addWeighted(enhanced, 2.0, gaussian, -1.0, 0)

    return sharpened


def _parse_products_json(text: str) -> list[dict]:
    """Parse Claude's response into a list of product dicts."""
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Try to find a JSON array in the text
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                return []
        else:
            return []

    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "products" in data:
        return data["products"]
    return []
