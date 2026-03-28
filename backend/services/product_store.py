"""Persistent JSON-based product storage.

Products are saved per-store and survive server restarts.
"""
import json
import threading

from backend.config import PRODUCTS_FILE

_lock = threading.Lock()


def load_all_products() -> dict[str, list[dict]]:
    """Load all products from disk. Returns {store_key: [product, ...]}."""
    if not PRODUCTS_FILE.exists():
        return {}
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def save_all_products(data: dict[str, list[dict]]) -> None:
    """Save all products to disk."""
    with _lock:
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def add_products(store: str, new_products: list[dict]) -> int:
    """Add products to a store, deduplicating by name. Returns count added."""
    all_data = load_all_products()
    existing = all_data.get(store, [])

    existing_names = {p["name"].lower().strip() for p in existing}

    added = 0
    max_id = max((p.get("id", 0) for p in existing), default=0)

    for p in new_products:
        name_key = p.get("name", "").lower().strip()
        if not name_key or name_key in existing_names:
            continue
        max_id += 1
        p["id"] = max_id
        existing.append(p)
        existing_names.add(name_key)
        added += 1

    all_data[store] = existing
    save_all_products(all_data)
    return added


def get_store_products(store: str) -> list[dict]:
    """Get all products for a specific store."""
    return load_all_products().get(store, [])
