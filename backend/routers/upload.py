import os
import time
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from backend.config import MAX_UPLOAD_SIZE_MB, UPLOAD_DIR
from backend.models.schemas import AnalysisResponse, DetectedProduct
from backend.services.frame_extractor import extract_key_frames, is_image, is_video
from backend.services.image_cropper import crop_products
from backend.services.image_search import search_product_image
from backend.services.product_store import add_products, load_all_products
from backend.services.vision_analyzer import analyze_frame

router = APIRouter()

ALLOWED_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v",
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff",
}


@router.get("/api/products")
async def get_products():
    """Return all saved products, grouped by store."""
    return JSONResponse(content=load_all_products())


@router.post("/api/upload", response_model=AnalysisResponse)
async def upload_and_analyze(
    file: UploadFile = File(...),
    store: str = Form(default="costco"),
    price_tag_position: str = Form(default="below"),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    file_id = uuid.uuid4().hex
    save_path = UPLOAD_DIR / f"{file_id}{ext}"

    try:
        content = await file.read()
        size_mb = len(content) / (1024 * 1024)
        if size_mb > MAX_UPLOAD_SIZE_MB:
            raise HTTPException(413, f"File too large: {size_mb:.1f}MB (max {MAX_UPLOAD_SIZE_MB}MB)")

        with open(save_path, "wb") as f:
            f.write(content)

        # Validate price_tag_position
        if price_tag_position not in ("above", "below"):
            price_tag_position = "below"

        print(f"[Upload] File: {file.filename} ({size_mb:.1f}MB), Store: {store}, Price tags: {price_tag_position}")
        start_time = time.time()

        # Extract sharp frames (blurry/motion-blur frames are filtered out)
        frames = extract_key_frames(str(save_path))
        print(f"[Frames] Extracted {len(frames)} sharp frames")

        # Analyze each frame with Claude Vision
        all_products_raw: list[dict] = []
        for i, frame in enumerate(frames):
            try:
                print(f"[Analysis] Analyzing frame {i+1}/{len(frames)}...")
                detected = analyze_frame(frame, store, price_tag_position)
                print(f"[Analysis] Frame {i+1}: {len(detected)} products detected")

                # Crop products from this frame
                detected = crop_products(frame, detected, price_tag_position)
                all_products_raw.extend(detected)
            except Exception as e:
                print(f"[Error] Frame {i+1} analysis failed: {e}")
                continue

        if not all_products_raw:
            raise HTTPException(
                422, "No products detected. Try uploading a clearer image of the shelf."
            )

        # Deduplicate by product name
        deduped = _deduplicate(all_products_raw)
        print(f"[Dedup] {len(all_products_raw)} raw → {len(deduped)} unique products")

        # Web image search for products without a good crop
        for product in deduped:
            if product.get("_needs_web_image", True) and not product.get("image"):
                url = await search_product_image(product["name"])
                if url:
                    product["imageUrl"] = url

        # Build response
        result_products = []
        for p in deduped:
            # Combine unit and unit_price info
            unit = p.get("unit") or ""
            unit_price = p.get("unit_price")
            if unit_price and unit:
                unit = f"{unit} ({unit_price})"
            elif unit_price:
                unit = unit_price

            p.pop("_needs_web_image", None)
            p.pop("bbox", None)
            p.pop("unit_price", None)

            result_products.append(
                DetectedProduct(
                    name=p.get("name", "Unknown Product"),
                    price=_safe_float(p.get("price")),
                    unit=unit or None,
                    desc=p.get("desc"),
                    shelf=p.get("shelf"),
                    emoji=p.get("emoji", "📦"),
                    image=p.get("image"),
                    imageUrl=p.get("imageUrl"),
                    badge="NEW",
                )
            )

        # Persist to disk
        products_to_save = [rp.model_dump() for rp in result_products]
        added_count = add_products(store, products_to_save)
        print(f"[Persist] {added_count} new products saved to disk for {store}")

        elapsed = time.time() - start_time
        print(f"[Done] {len(result_products)} products in {elapsed:.1f}s")

        return AnalysisResponse(
            store=store,
            products=result_products,
            frames_analyzed=len(frames),
            processing_time_seconds=round(elapsed, 2),
        )

    finally:
        if save_path.exists():
            os.remove(save_path)


def _deduplicate(products: list[dict]) -> list[dict]:
    """Remove duplicate products by normalized name.

    When the same product appears in multiple frames, keep the one with:
    1. A crop image (over no image)
    2. A price (over no price)
    3. Higher confidence (longer name = more text was read)
    """
    seen: dict[str, dict] = {}

    for p in products:
        name = p.get("name", "").strip()
        if not name:
            continue

        key = _normalize_name(name)

        if key not in seen:
            seen[key] = p
        else:
            existing = seen[key]
            # Score: prefer image, price, longer name
            new_score = _product_score(p)
            old_score = _product_score(existing)
            if new_score > old_score:
                seen[key] = p

    return list(seen.values())


def _normalize_name(name: str) -> str:
    """Normalize product name for dedup comparison."""
    name = name.lower().strip()
    # Remove common noise
    for ch in "''-.,!\"":
        name = name.replace(ch, "")
    # Collapse whitespace
    name = " ".join(name.split())
    return name


def _product_score(p: dict) -> int:
    """Score a product detection for dedup preference."""
    score = 0
    if p.get("image"):
        score += 10
    if p.get("price") is not None:
        score += 5
    score += len(p.get("name", ""))
    return score


def _safe_float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
