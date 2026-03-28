import httpx

from backend.config import SERPAPI_KEY


async def search_product_image(product_name: str) -> str | None:
    """Search for a product image using SerpAPI Google Images.

    Returns an image URL or None if not found or no API key configured.
    """
    if not SERPAPI_KEY:
        return None

    params = {
        "engine": "google_images",
        "q": f"{product_name} product",
        "num": 1,
        "api_key": SERPAPI_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://serpapi.com/search.json", params=params
            )
            resp.raise_for_status()
            data = resp.json()

        results = data.get("images_results", [])
        if results:
            return results[0].get("original")
    except Exception:
        pass

    return None
