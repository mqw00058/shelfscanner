import asyncio
import os
import time
import uuid
from pathlib import Path

import streamlit as st

from backend.config import CROPS_DIR, UPLOAD_DIR
from backend.services.classifier import classify_by_name, classify_all_products
from backend.services.frame_extractor import extract_key_frames
from backend.services.image_cropper import crop_products
from backend.services.image_search import search_product_image
from backend.services.product_store import add_products, load_all_products, save_all_products
from backend.services.vision_analyzer import analyze_frame

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="ShelfScanner",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Store info ───────────────────────────────────────────────
STORE_INFO = {
    "costco": {"name": "Costco", "emoji": "🏬", "color": "#e21836",
               "desc": "Products detected from Costco store shelves"},
    "sams-club": {"name": "Sam's Club", "emoji": "🏪", "color": "#0060a9",
                  "desc": "Products detected from Sam's Club store shelves"},
    "walmart": {"name": "Walmart", "emoji": "🛒", "color": "#0071dc",
                "desc": "Products detected from Walmart store shelves"},
    "traders-joe": {"name": "Trader Joe's", "emoji": "🌿", "color": "#c8102e",
                    "desc": "Products detected from Trader Joe's store shelves"},
    "kroger": {"name": "Kroger", "emoji": "🛍️", "color": "#0033a0",
               "desc": "Products detected from Kroger store shelves"},
}

# ── Seed data ────────────────────────────────────────────────
SEED_DATA = {
    "costco": [
        {"name": "Kirkland Signature Organic Extra Virgin Olive Oil", "price": 14.99, "unit": "2L", "emoji": "🫒", "desc": "Organic extra virgin olive oil. Premium Italian quality.", "shelf": "Aisle A, Shelf 3, 2nd from left"},
        {"name": "Kirkland Signature Rotisserie Chicken", "price": 4.99, "unit": "1 whole (~3 lbs)", "emoji": "🍗", "desc": "Freshly roasted rotisserie chicken. Tender and juicy.", "shelf": "Deli counter, hot food display", "badge": "BEST"},
        {"name": "Bounty Advanced Paper Towels", "price": 28.99, "unit": "12 rolls", "emoji": "🧻", "desc": "Premium paper towels. 2-ply construction with superior absorbency.", "shelf": "Aisle C, Shelf 5, center"},
        {"name": "Tide Pods Laundry Detergent", "price": 24.99, "unit": "152 ct", "emoji": "🧴", "desc": "3-in-1 laundry detergent pods. Cleans, freshens, and brightens.", "shelf": "Aisle C, Shelf 4, right side"},
        {"name": "Kirkland Signature Organic Eggs", "price": 8.49, "unit": "24 ct", "emoji": "🥚", "desc": "Organic free-range eggs. USDA Organic certified.", "shelf": "Refrigerated Aisle B, Shelf 1"},
        {"name": "Kirkland Signature Bacon", "price": 14.99, "unit": "4 pk (17.6 oz each)", "emoji": "🥓", "desc": "Hickory smoked bacon. Thick sliced.", "shelf": "Refrigerated Aisle B, Shelf 2, left"},
        {"name": "Samsung 65\" QLED 4K TV", "price": 599.99, "unit": "1 unit", "emoji": "📺", "desc": "Samsung 65-inch QLED 4K Smart TV. Quantum Dot technology.", "shelf": "Electronics Section D, wall display", "badge": "HOT"},
        {"name": "Dyson V15 Detect Vacuum", "price": 549.99, "unit": "1 unit", "emoji": "🔌", "desc": "Dyson V15 cordless vacuum. Laser dust detection technology.", "shelf": "Electronics Section D, Display 2"},
        {"name": "Kirkland Signature Mixed Nuts", "price": 16.99, "unit": "2.5 lbs", "emoji": "🥜", "desc": "Premium mixed nuts. Cashews, almonds, pecans, macadamias.", "shelf": "Aisle A, Shelf 6, center", "badge": "SALE"},
        {"name": "Kirkland Signature Water", "price": 4.49, "unit": "40 pk (16.9 fl oz)", "emoji": "💧", "desc": "Purified water 40-pack. Clean filtration system.", "shelf": "Beverage Aisle E, floor pallet"},
        {"name": "Kirkland Signature Almond Butter", "price": 9.99, "unit": "27 oz", "emoji": "🥜", "desc": "100% almond butter. No additives.", "shelf": "Aisle A, Shelf 4, right side"},
        {"name": "Huggies Little Movers Diapers", "price": 42.99, "unit": "180 ct (Size 4)", "emoji": "👶", "desc": "Huggies diapers. Perfect fit for active babies.", "shelf": "Aisle F, Shelf 2"},
        {"name": "Starbucks French Roast Coffee", "price": 18.49, "unit": "2.5 lbs", "emoji": "☕", "desc": "Starbucks French Roast whole bean coffee. Deep dark roast flavor.", "shelf": "Aisle A, Shelf 7, left"},
        {"name": "Kirkland Signature Prosecco", "price": 6.99, "unit": "750 ml", "emoji": "🍾", "desc": "Italian DOC Prosecco. Refreshing bubbles.", "shelf": "Alcohol Section G, Shelf 3"},
        {"name": "Michelin Defender T+H Tires", "price": 159.99, "unit": "1 tire", "emoji": "🛞", "desc": "Michelin Defender T+H tire. 80,000 mile warranty.", "shelf": "Automotive Section H, tire display"},
        {"name": "Kirkland Signature Greek Yogurt", "price": 7.99, "unit": "3 lbs (2 pk)", "emoji": "🥛", "desc": "Non-fat Greek yogurt. High in protein.", "shelf": "Refrigerated Aisle B, Shelf 3, center"},
    ],
    "sams-club": [
        {"name": "Member's Mark Chicken Breast", "price": 22.98, "unit": "10 lbs", "emoji": "🍗", "desc": "Frozen chicken breast. Individually vacuum sealed.", "shelf": "Frozen Aisle A, Shelf 2"},
        {"name": "Member's Mark Purified Water", "price": 3.98, "unit": "45 pk (16.9 fl oz)", "emoji": "💧", "desc": "Purified water bulk pack.", "shelf": "Beverage Aisle B, floor pallet", "badge": "BEST"},
        {"name": "Charmin Ultra Soft Toilet Paper", "price": 32.98, "unit": "36 rolls", "emoji": "🧻", "desc": "Charmin Ultra Soft. Premium softness.", "shelf": "Aisle C, Shelf 1"},
        {"name": "Member's Mark Colombian Coffee", "price": 14.98, "unit": "2.2 lbs", "emoji": "☕", "desc": "100% Colombian beans. Medium roast.", "shelf": "Aisle A, Shelf 8, left"},
        {"name": "Serta Perfect Sleeper Mattress", "price": 399.00, "unit": "Queen", "emoji": "🛏️", "desc": "Serta Perfect Sleeper queen mattress. Gel memory foam.", "shelf": "Furniture Section E, mattress display", "badge": "HOT"},
        {"name": "Member's Mark Organic Strawberries", "price": 6.98, "unit": "2 lbs", "emoji": "🍓", "desc": "Organic frozen strawberries. Perfect for smoothies.", "shelf": "Frozen Aisle A, Shelf 4"},
        {"name": "Apple AirPods Pro 2", "price": 189.00, "unit": "1 unit", "emoji": "🎧", "desc": "Apple AirPods Pro 2. Active noise cancellation.", "shelf": "Electronics Section D, locked display"},
        {"name": "Member's Mark Laundry Detergent", "price": 15.98, "unit": "1.5 gal", "emoji": "🧴", "desc": "Concentrated liquid laundry detergent. 110 loads.", "shelf": "Aisle C, Shelf 3, center"},
        {"name": "Pampers Swaddlers Diapers", "price": 39.98, "unit": "168 ct (Size 3)", "emoji": "👶", "desc": "Pampers Swaddlers diapers. Ultra soft comfort.", "shelf": "Aisle F, Shelf 1"},
        {"name": "Member's Mark Rotisserie Chicken", "price": 5.98, "unit": "1 whole", "emoji": "🍗", "desc": "In-store roasted rotisserie chicken.", "shelf": "Deli counter, hot food display"},
        {"name": "Member's Mark Trail Mix", "price": 11.98, "unit": "3 lbs", "emoji": "🥜", "desc": "Premium trail mix. Nuts and dried fruit blend.", "shelf": "Aisle A, Shelf 5, center"},
        {"name": "LG 75\" UHD 4K Smart TV", "price": 649.00, "unit": "1 unit", "emoji": "📺", "desc": "LG 75-inch UHD 4K Smart TV. webOS built-in.", "shelf": "Electronics Section D, wall display"},
    ],
    "walmart": [
        {"name": "Great Value Whole Milk", "price": 3.36, "unit": "1 gal", "emoji": "🥛", "desc": "Great Value whole milk. Vitamin D fortified.", "shelf": "Refrigerated Aisle A, Shelf 1", "badge": "BEST"},
        {"name": "Bananas", "price": 0.27, "unit": "1 each (~4 oz)", "emoji": "🍌", "desc": "Fresh bananas. Product of Ecuador.", "shelf": "Produce section, near entrance"},
        {"name": "Great Value Peanut Butter", "price": 2.98, "unit": "2.5 lbs", "emoji": "🥜", "desc": "Creamy peanut butter. 100% peanuts.", "shelf": "Aisle A, Shelf 3, center"},
        {"name": "Coca-Cola Classic", "price": 7.48, "unit": "24 cans (12 fl oz)", "emoji": "🥤", "desc": "Coca-Cola Classic 24-pack. The original taste.", "shelf": "Beverage Aisle B, floor pallet"},
        {"name": "Lays Classic Potato Chips", "price": 4.28, "unit": "10 oz", "emoji": "🥔", "desc": "Lays Classic potato chips. Crispy original flavor.", "shelf": "Snack Aisle C, Shelf 2"},
        {"name": "Great Value Paper Plates", "price": 8.97, "unit": "200 ct", "emoji": "🍽️", "desc": "Disposable paper plates. Microwave safe.", "shelf": "Household Aisle D, Shelf 4"},
        {"name": "Tyson Chicken Nuggets", "price": 8.47, "unit": "5 lbs", "emoji": "🍗", "desc": "Tyson chicken nuggets. 100% white meat.", "shelf": "Frozen Aisle E, Shelf 3"},
        {"name": "Crest 3D White Toothpaste", "price": 5.97, "unit": "3 pk (4.8 oz each)", "emoji": "🪥", "desc": "Crest 3D White toothpaste. Whitening formula.", "shelf": "Personal Care Aisle F, Shelf 2"},
        {"name": "Great Value Eggs", "price": 3.12, "unit": "18 ct", "emoji": "🥚", "desc": "Grade A large eggs. Farm fresh.", "shelf": "Refrigerated Aisle A, Shelf 2, bottom"},
        {"name": "Folgers Classic Roast Coffee", "price": 9.98, "unit": "3 lbs", "emoji": "☕", "desc": "Folgers Classic Roast. America's #1 coffee brand.", "shelf": "Aisle A, Shelf 6, center"},
        {"name": "Onn. 50\" 4K Roku TV", "price": 198.00, "unit": "1 unit", "emoji": "📺", "desc": "Onn 50-inch 4K Roku TV. Best value smart TV.", "shelf": "Electronics Section G, wall display", "badge": "SALE"},
        {"name": "Great Value Spring Water", "price": 3.48, "unit": "40 pk (16.9 fl oz)", "emoji": "💧", "desc": "Natural spring water 40-pack. Clean daily hydration.", "shelf": "Beverage Aisle B, floor pallet"},
        {"name": "Dawn Dish Soap", "price": 3.97, "unit": "18 fl oz", "emoji": "🫧", "desc": "Dawn dish soap. Powerful grease removal.", "shelf": "Household Aisle D, Shelf 1"},
        {"name": "Ritz Crackers", "price": 4.48, "unit": "13.8 oz", "emoji": "🍘", "desc": "Ritz crackers. The original buttery flavor.", "shelf": "Snack Aisle C, Shelf 3, left"},
    ],
    "traders-joe": [
        {"name": "Mandarin Orange Chicken", "price": 4.99, "unit": "22 oz", "emoji": "🍊", "desc": "Mandarin orange chicken. Trader Joe's bestseller #1.", "shelf": "Frozen Aisle A, Shelf 1, center", "badge": "BEST"},
        {"name": "Everything But The Bagel Seasoning", "price": 2.49, "unit": "2.3 oz", "emoji": "🥯", "desc": "Everything But The Bagel seasoning blend. Social media sensation.", "shelf": "Seasoning Aisle B, Shelf 3"},
        {"name": "Cauliflower Gnocchi", "price": 2.99, "unit": "12 oz", "emoji": "🥟", "desc": "Cauliflower gnocchi. Gluten-free healthy option.", "shelf": "Frozen Aisle A, Shelf 2", "badge": "HOT"},
        {"name": "Dark Chocolate Peanut Butter Cups", "price": 3.99, "unit": "12 oz", "emoji": "🍫", "desc": "Dark chocolate peanut butter cups. Said to be better than Reese's.", "shelf": "Snack Aisle C, Shelf 1"},
        {"name": "Organic Free Range Eggs", "price": 4.49, "unit": "12 ct", "emoji": "🥚", "desc": "Organic free-range eggs. Cage-free.", "shelf": "Refrigerated Aisle D, Shelf 1"},
        {"name": "Joe's Diner Mac 'n Cheese", "price": 3.49, "unit": "20 oz", "emoji": "🧀", "desc": "Joe's Diner mac and cheese. Creamy cheese pasta.", "shelf": "Frozen Aisle A, Shelf 3"},
        {"name": "Unexpected Cheddar Cheese", "price": 3.99, "unit": "7 oz", "emoji": "🧀", "desc": "Unexpected Cheddar cheese. Deep Parmigiano-like flavor.", "shelf": "Refrigerated Aisle D, cheese corner"},
        {"name": "Triple Ginger Snaps", "price": 3.99, "unit": "14 oz", "emoji": "🍪", "desc": "Triple ginger snap cookies. Made with three kinds of ginger.", "shelf": "Snack Aisle C, Shelf 2"},
        {"name": "Organic Coconut Oil", "price": 4.99, "unit": "16 fl oz", "emoji": "🥥", "desc": "Organic coconut oil. Virgin extra.", "shelf": "Aisle B, Shelf 2, left"},
        {"name": "Two Buck Chuck (Charles Shaw Wine)", "price": 3.49, "unit": "750 ml", "emoji": "🍷", "desc": "Charles Shaw wine. Best value table wine.", "shelf": "Alcohol Section E, wine shelf"},
        {"name": "Speculoos Cookie Butter", "price": 3.69, "unit": "14.1 oz", "emoji": "🍪", "desc": "Speculoos cookie butter. Belgian cookie spread.", "shelf": "Aisle B, Shelf 4, center", "badge": "HOT"},
        {"name": "Organic Baby Spinach", "price": 2.49, "unit": "6 oz", "emoji": "🥬", "desc": "Organic baby spinach. Perfect for salads.", "shelf": "Produce, entrance refrigerated display"},
    ],
    "kroger": [
        {"name": "Kroger Whole Milk", "price": 3.19, "unit": "1 gal", "emoji": "🥛", "desc": "Kroger whole milk. Fresh dairy.", "shelf": "Refrigerated Aisle A, Shelf 1"},
        {"name": "Simple Truth Organic Chicken Breast", "price": 9.99, "unit": "1 lb", "emoji": "🍗", "desc": "Simple Truth organic chicken breast. No antibiotics.", "shelf": "Meat Section B", "badge": "BEST"},
        {"name": "Kroger Purified Drinking Water", "price": 2.99, "unit": "24 pk (16.9 fl oz)", "emoji": "💧", "desc": "Kroger purified water 24-pack.", "shelf": "Beverage Aisle C, floor pallet"},
        {"name": "Simple Truth Natural Almonds", "price": 7.49, "unit": "1 lb", "emoji": "🥜", "desc": "Simple Truth natural almonds. Unsalted roasted.", "shelf": "Snack Aisle D, Shelf 3"},
        {"name": "Kroger Shredded Mozzarella", "price": 3.49, "unit": "1 lb", "emoji": "🧀", "desc": "Kroger shredded mozzarella cheese. Perfect for pizza.", "shelf": "Refrigerated Aisle A, cheese corner"},
        {"name": "Kroger Ground Beef 80/20", "price": 5.99, "unit": "1 lb", "emoji": "🥩", "desc": "Kroger ground beef. 80% lean, 20% fat balance.", "shelf": "Meat Section B, center"},
        {"name": "Private Selection Gelato", "price": 4.99, "unit": "16 fl oz", "emoji": "🍨", "desc": "Private Selection gelato. Italian-style.", "shelf": "Frozen Aisle E, ice cream section", "badge": "HOT"},
        {"name": "Kroger Vitamin D Whole Eggs", "price": 2.79, "unit": "12 ct", "emoji": "🥚", "desc": "Vitamin D enriched eggs. Grade A large.", "shelf": "Refrigerated Aisle A, Shelf 2"},
        {"name": "Simple Truth Organic Pasta Sauce", "price": 3.29, "unit": "24 oz", "emoji": "🍝", "desc": "Simple Truth organic pasta sauce. Marinara.", "shelf": "Aisle A, Shelf 5, center"},
        {"name": "Kroger Sparkling Water", "price": 3.29, "unit": "12 cans (12 fl oz)", "emoji": "🫧", "desc": "Kroger sparkling water. Lime flavor.", "shelf": "Beverage Aisle C, Shelf 2"},
        {"name": "Home Chef Meal Kit", "price": 19.99, "unit": "Serves 2", "emoji": "👨\u200d🍳", "desc": "Home Chef meal kit. Fresh ingredients and recipe included.", "shelf": "Refrigerated, entrance meal kit display", "badge": "NEW"},
        {"name": "Kroger Honey Wheat Bread", "price": 2.49, "unit": "20 oz", "emoji": "🍞", "desc": "Honey wheat bread. Soft texture.", "shelf": "Bakery Section F, Shelf 1"},
    ],
}


# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .product-emoji {
        font-size: 48px;
        text-align: center;
        padding: 20px 0;
        background: #f8f8f8;
        border-radius: 8px;
    }
    .product-price {
        font-size: 20px;
        font-weight: 700;
        color: #e21836;
    }
    .product-unit {
        font-size: 12px;
        color: #888;
    }
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        color: white;
        margin-left: 6px;
    }
    .badge-NEW { background: #4caf50; }
    .badge-BEST { background: #ff9800; }
    .badge-HOT { background: #f44336; }
    .badge-SALE { background: #9c27b0; }
    .store-banner {
        padding: 24px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
    }
    .store-banner h2 { margin: 0 0 4px 0; font-size: 28px; }
    .store-banner p { margin: 0; opacity: 0.9; font-size: 14px; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Session state init ───────────────────────────────────────
if "current_store" not in st.session_state:
    st.session_state.current_store = "costco"
if "current_category" not in st.session_state:
    st.session_state.current_category = "All"


# ── Helpers ──────────────────────────────────────────────────
def _ensure_seed_data():
    """Load seed data into products.json if empty."""
    existing = load_all_products()
    if existing:
        return
    import copy
    seed = copy.deepcopy(SEED_DATA)
    for store_key, items in seed.items():
        for i, p in enumerate(items):
            p["id"] = i + 1
            p["category"] = classify_by_name(p["name"])
            p.setdefault("image", None)
            p.setdefault("imageUrl", None)
    save_all_products(seed)


@st.cache_data(ttl=60)
def _read_crop_file(filename: str) -> bytes | None:
    crop_file = CROPS_DIR / filename
    if crop_file.exists():
        return crop_file.read_bytes()
    return None


def _get_product_image(product: dict):
    """Return image bytes, URL string, or None."""
    img_path = product.get("image")
    if img_path and img_path.startswith("/api/crops/"):
        filename = img_path.split("/")[-1]
        return _read_crop_file(filename)
    img_url = product.get("imageUrl")
    if img_url:
        return img_url
    return None


def _normalize_name(name: str) -> str:
    name = name.lower().strip()
    for ch in "''-.,!\"":
        name = name.replace(ch, "")
    return " ".join(name.split())


def _product_score(p: dict) -> int:
    score = 0
    if p.get("image"):
        score += 10
    if p.get("price") is not None:
        score += 5
    score += len(p.get("name", ""))
    return score


def _deduplicate(products: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for p in products:
        name = p.get("name", "").strip()
        if not name:
            continue
        key = _normalize_name(name)
        if key not in seen:
            seen[key] = p
        else:
            if _product_score(p) > _product_score(seen[key]):
                seen[key] = p
    return list(seen.values())


# ── Analysis pipeline ────────────────────────────────────────
def run_analysis(uploaded_file, store: str, price_tag_position: str):
    """Run the full analysis pipeline. Returns (added_count, frames_count)."""
    ext = Path(uploaded_file.name).suffix.lower()
    file_id = uuid.uuid4().hex
    save_path = UPLOAD_DIR / f"{file_id}{ext}"

    try:
        content = uploaded_file.read()
        with open(save_path, "wb") as f:
            f.write(content)

        with st.status("Analyzing shelf...", expanded=True) as status:
            st.write("Extracting sharp frames...")
            frames = extract_key_frames(str(save_path))
            st.write(f"Found **{len(frames)}** sharp frame(s)")

            all_products_raw: list[dict] = []
            for i, frame in enumerate(frames):
                try:
                    st.write(f"Analyzing frame {i+1}/{len(frames)} with AI...")
                    detected = analyze_frame(frame, store, price_tag_position)
                    st.write(f"Frame {i+1}: **{len(detected)}** products detected")
                    detected = crop_products(frame, detected, price_tag_position)
                    all_products_raw.extend(detected)
                except Exception as e:
                    st.write(f"Frame {i+1} failed: {e}")

            if not all_products_raw:
                status.update(label="No products detected", state="error")
                return 0, len(frames)

            deduped = _deduplicate(all_products_raw)
            st.write(f"{len(all_products_raw)} raw -> **{len(deduped)}** unique products")

            st.write("Searching for product images...")
            for p in deduped:
                if p.get("_needs_web_image", True) and not p.get("image"):
                    try:
                        url = asyncio.run(search_product_image(p["name"]))
                        if url:
                            p["imageUrl"] = url
                    except Exception:
                        pass

            for p in deduped:
                p["category"] = classify_by_name(p.get("name", ""))
                p["emoji"] = p.get("emoji", "📦")
                unit = p.get("unit") or ""
                unit_price = p.get("unit_price")
                if unit_price and unit:
                    p["unit"] = f"{unit} ({unit_price})"
                elif unit_price:
                    p["unit"] = unit_price
                p.pop("_needs_web_image", None)
                p.pop("bbox", None)
                p.pop("unit_price", None)
                p.pop("price_sign_type", None)
                p["badge"] = "NEW"

            added = add_products(store, deduped)
            status.update(label=f"Done! {added} new products added", state="complete")
            return added, len(frames)

    finally:
        if save_path.exists():
            os.remove(save_path)


# ── Product detail dialog ────────────────────────────────────
@st.dialog("Product Details", width="large")
def show_product_detail(product: dict):
    col_img, col_info = st.columns([1, 1])
    with col_img:
        img = _get_product_image(product)
        if img and isinstance(img, bytes):
            st.image(img, use_container_width=True)
        elif img and isinstance(img, str):
            st.image(img, use_container_width=True)
        else:
            st.markdown(
                f"<div style='font-size:80px;text-align:center;padding:40px 0'>"
                f"{product.get('emoji', '📦')}</div>",
                unsafe_allow_html=True,
            )

    with col_info:
        badge = product.get("badge")
        if badge:
            st.markdown(
                f"<span class='badge badge-{badge}'>{badge}</span>",
                unsafe_allow_html=True,
            )
        st.subheader(product.get("name", "Unknown"))
        price = product.get("price") or 0
        st.markdown(
            f"<span style='font-size:32px;font-weight:700;color:#e21836'>${price:.2f}</span>",
            unsafe_allow_html=True,
        )
        unit = product.get("unit", "")
        if unit:
            st.caption(f"Size: {unit}")
        st.write(product.get("desc", ""))
        st.caption(f"Category: {product.get('category', 'Uncategorized')}")
        st.caption(f"Shelf: {product.get('shelf', 'N/A')}")
        if product.get("image"):
            st.caption("Image: Captured from video")
        elif product.get("imageUrl"):
            st.caption("Image: Retrieved from web search")
        else:
            st.caption("Image: Emoji placeholder")


# ── Initialize ───────────────────────────────────────────────
_ensure_seed_data()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Select Store")

    store_options = list(STORE_INFO.keys())

    chosen = st.radio(
        "Store",
        store_options,
        index=store_options.index(st.session_state.current_store),
        format_func=lambda k: f"{STORE_INFO[k]['emoji']} {STORE_INFO[k]['name']}",
        label_visibility="collapsed",
    )
    st.session_state.current_store = chosen

    st.divider()
    st.markdown("### Upload Shelf")

    uploaded_file = st.file_uploader(
        "Upload photo or video",
        type=["jpg", "jpeg", "png", "webp", "bmp", "tiff",
              "mp4", "mov", "avi", "mkv", "webm", "m4v"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        upload_store = st.selectbox(
            "Target store",
            store_options,
            index=store_options.index(st.session_state.current_store),
            format_func=lambda k: f"{STORE_INFO[k]['emoji']} {STORE_INFO[k]['name']}",
        )

        price_pos = st.radio(
            "Where are price tags?",
            ["below", "above"],
            format_func=lambda x: "Below product" if x == "below" else "Above product",
            horizontal=True,
        )

        if st.button("Analyze Shelf", type="primary", use_container_width=True):
            start = time.time()
            added, frames = run_analysis(uploaded_file, upload_store, price_pos)
            elapsed = time.time() - start
            if added > 0:
                st.session_state.current_store = upload_store
                st.session_state.current_category = "All"
                st.success(f"{added} new products added ({frames} frames, {elapsed:.1f}s)")
                st.rerun()
            elif frames > 0:
                st.warning("No new products detected. Try a clearer image.")

# ── Main area ────────────────────────────────────────────────
store_key = st.session_state.current_store
info = STORE_INFO[store_key]

# Store banner
st.markdown(
    f'<div class="store-banner" style="background:linear-gradient(135deg,{info["color"]},{info["color"]}dd)">'
    f'<h2>{info["emoji"]} {info["name"]}</h2>'
    f'<p>{info["desc"]}</p></div>',
    unsafe_allow_html=True,
)

# Load products
all_products = load_all_products()
classify_all_products(all_products)
store_products = list(all_products.get(store_key, []))

# Categories
categories = ["All"] + sorted(set(p.get("category", "Uncategorized") for p in store_products))
selected_cat = st.pills("Category", categories, default="All", key="cat_pills")
if selected_cat:
    st.session_state.current_category = selected_cat

# Search and sort
col_search, col_sort = st.columns([3, 1])
with col_search:
    search = st.text_input("Search", placeholder="Search products...", label_visibility="collapsed")
with col_sort:
    sort_by = st.selectbox("Sort", ["Name", "Price: Low to High", "Price: High to Low"], label_visibility="collapsed")

# Filter
items = store_products
if st.session_state.current_category and st.session_state.current_category != "All":
    items = [p for p in items if p.get("category") == st.session_state.current_category]

if search:
    q = search.lower()
    items = [p for p in items if
             q in p.get("name", "").lower() or
             q in p.get("desc", "").lower() or
             q in p.get("category", "").lower()]

# Sort
if sort_by == "Price: Low to High":
    items.sort(key=lambda p: p.get("price") or 0)
elif sort_by == "Price: High to Low":
    items.sort(key=lambda p: p.get("price") or 0, reverse=True)
else:
    items.sort(key=lambda p: p.get("name", ""))

st.caption(f"{len(items)} products")

# Product grid
COLS = 4
if not items:
    st.info("No products found. Upload a shelf photo or video to get started!")
else:
    for row_start in range(0, len(items), COLS):
        row_items = items[row_start:row_start + COLS]
        cols = st.columns(COLS)
        for idx, (col, product) in enumerate(zip(cols, row_items)):
            with col:
                img = _get_product_image(product)
                if img and isinstance(img, bytes):
                    st.image(img, use_container_width=True)
                elif img and isinstance(img, str):
                    st.image(img, use_container_width=True)
                else:
                    st.markdown(
                        f"<div style='font-size:48px;text-align:center;padding:16px 0;"
                        f"background:#f8f8f8;border-radius:8px'>"
                        f"{product.get('emoji', '📦')}</div>",
                        unsafe_allow_html=True,
                    )

                badge = product.get("badge")
                badge_html = f" <span class='badge badge-{badge}'>{badge}</span>" if badge else ""
                price = product.get("price") or 0

                st.markdown(f"**{product.get('name', 'Unknown')}**{badge_html}", unsafe_allow_html=True)
                st.markdown(f"<span class='product-unit'>{product.get('unit', '')}</span>", unsafe_allow_html=True)
                st.markdown(f"<span class='product-price'>${price:.2f}</span>", unsafe_allow_html=True)

                btn_key = f"d_{store_key}_{product.get('id', 0)}_{row_start}_{idx}"
                if st.button("View Details", key=btn_key, use_container_width=True):
                    show_product_detail(product)
