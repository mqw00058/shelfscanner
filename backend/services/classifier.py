"""Product category classifier — Python port of classifier.js."""

CATEGORY_RULES = [
    {
        "category": "Electronics",
        "keywords": ["tv", "television", "airpods", "headphone", "earbuds", "vacuum", "dyson", "samsung", "lg", "onn.", "roku", "qled", "uhd", "4k", "speaker", "laptop", "tablet", "ipad", "computer", "monitor", "camera", "bluetooth"],
    },
    {
        "category": "Dairy",
        "keywords": ["milk", "cheese", "yogurt", "butter", "cream", "mozzarella", "cheddar", "parmesan", "cottage", "sour cream", "half and half", "creamer"],
    },
    {
        "category": "Beverages",
        "keywords": ["water", "coffee", "tea", "cola", "coca-cola", "pepsi", "juice", "soda", "sparkling", "lemonade", "drink", "gatorade", "energy drink"],
    },
    {
        "category": "Alcohol",
        "keywords": ["wine", "beer", "prosecco", "champagne", "vodka", "whiskey", "bourbon", "rum", "tequila", "gin", "sake", "merlot", "cabernet", "chardonnay", "pinot", "chuck"],
    },
    {
        "category": "Snacks",
        "keywords": ["chips", "crackers", "nuts", "mixed nuts", "almonds", "trail mix", "popcorn", "pretzels", "cookie", "chocolate", "candy", "gummy", "snaps", "peanut butter cup", "granola bar"],
    },
    {
        "category": "Frozen",
        "keywords": ["frozen", "gnocchi", "ice cream", "gelato", "pizza frozen", "nuggets", "mac n cheese", "mac 'n cheese", "orange chicken", "burrito", "waffle", "frozen fruit"],
    },
    {
        "category": "Produce",
        "keywords": ["banana", "apple", "orange", "strawberr", "blueberr", "grape", "tomato", "lettuce", "spinach", "avocado", "onion", "potato", "carrot", "broccoli", "cucumber", "pepper", "celery", "mushroom", "organic baby"],
    },
    {
        "category": "Meat & Seafood",
        "keywords": ["chicken breast", "ground beef", "beef", "steak", "pork", "bacon", "sausage", "salmon", "shrimp", "fish", "turkey", "lamb", "ribs"],
    },
    {
        "category": "Deli",
        "keywords": ["rotisserie", "deli", "sliced", "ham", "salami", "prosciutto"],
    },
    {
        "category": "Bakery",
        "keywords": ["bread", "bagel", "muffin", "croissant", "cake", "donut", "roll", "baguette", "tortilla", "pita"],
    },
    {
        "category": "Household",
        "keywords": ["paper towel", "toilet paper", "detergent", "soap", "dish soap", "trash bag", "foil", "plastic wrap", "sponge", "cleaner", "wipe", "paper plate", "laundry", "tide", "bounty", "charmin", "dawn"],
    },
    {
        "category": "Personal Care",
        "keywords": ["toothpaste", "shampoo", "conditioner", "body wash", "deodorant", "razor", "lotion", "sunscreen", "floss", "mouthwash", "crest"],
    },
    {
        "category": "Baby",
        "keywords": ["diaper", "huggies", "pampers", "baby food", "formula", "wipes baby", "pacifier", "bottle baby"],
    },
    {
        "category": "Automotive",
        "keywords": ["tire", "michelin", "goodyear", "motor oil", "wiper", "car wash", "brake", "coolant", "battery car"],
    },
    {
        "category": "Furniture",
        "keywords": ["mattress", "serta", "couch", "sofa", "table", "chair", "desk", "shelf", "bookcase", "bed frame"],
    },
    {
        "category": "Meal Kit",
        "keywords": ["meal kit", "home chef", "hello fresh", "blue apron"],
    },
    {
        "category": "Seasoning",
        "keywords": ["seasoning", "spice", "salt", "pepper", "cumin", "paprika", "oregano", "basil", "garlic powder", "everything but the bagel"],
    },
    {
        "category": "Grocery",
        "keywords": ["egg", "oil", "olive oil", "coconut oil", "pasta sauce", "peanut butter", "almond butter", "cookie butter", "jam", "honey", "rice", "pasta", "cereal", "flour", "sugar", "canned", "sauce", "ketchup", "mustard", "mayo"],
    },
]


def classify_by_name(product_name: str) -> str:
    """Classify a product by name keywords. Returns category string."""
    if not product_name:
        return "Uncategorized"

    name_lower = product_name.lower()
    best_match = None
    best_score = 0

    for rule in CATEGORY_RULES:
        score = 0
        for keyword in rule["keywords"]:
            if keyword in name_lower:
                score += len(keyword)
        if score > best_score:
            best_score = score
            best_match = rule["category"]

    return best_match or "Uncategorized"


def classify_product(product: dict) -> dict:
    """Classify a single product dict. Sets 'category' field in-place."""
    product["category"] = classify_by_name(product.get("name", ""))
    return product


def classify_all_products(products_by_store: dict[str, list[dict]]) -> None:
    """Classify all products in-place."""
    for store_products in products_by_store.values():
        for p in store_products:
            if not p.get("category"):
                classify_product(p)
