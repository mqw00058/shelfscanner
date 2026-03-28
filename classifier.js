// ============================================================
// Auto Category Classifier
// ============================================================
// Classifies products into categories using two sources:
//   1. Product image (via image recognition — future integration)
//   2. Product name keywords (current fallback)
//
// When the video/image analysis pipeline is integrated, it will
// call classifyByImage() with detected visual features (e.g.
// packaging type, shelf section, product shape). Until then,
// classifyByName() handles all classification via keyword rules.
// ============================================================

const categoryRules = [
    {
        category: "Electronics",
        keywords: ["tv", "television", "airpods", "headphone", "earbuds", "vacuum", "dyson", "samsung", "lg", "onn.", "roku", "qled", "uhd", "4k", "speaker", "laptop", "tablet", "ipad", "computer", "monitor", "camera", "bluetooth"],
        visualHints: ["screen", "electronic_packaging", "cable", "remote_control"]
    },
    {
        category: "Dairy",
        keywords: ["milk", "cheese", "yogurt", "butter", "cream", "mozzarella", "cheddar", "parmesan", "cottage", "sour cream", "half and half", "creamer"],
        visualHints: ["milk_carton", "cheese_block", "yogurt_cup", "refrigerated"]
    },
    {
        category: "Beverages",
        keywords: ["water", "coffee", "tea", "cola", "coca-cola", "pepsi", "juice", "soda", "sparkling", "lemonade", "drink", "gatorade", "energy drink"],
        visualHints: ["bottle", "can", "beverage_aisle", "liquid_container"]
    },
    {
        category: "Alcohol",
        keywords: ["wine", "beer", "prosecco", "champagne", "vodka", "whiskey", "bourbon", "rum", "tequila", "gin", "sake", "merlot", "cabernet", "chardonnay", "pinot", "chuck"],
        visualHints: ["wine_bottle", "beer_can", "alcohol_label"]
    },
    {
        category: "Snacks",
        keywords: ["chips", "crackers", "nuts", "mixed nuts", "almonds", "trail mix", "popcorn", "pretzels", "cookie", "chocolate", "candy", "gummy", "snaps", "peanut butter cup", "granola bar"],
        visualHints: ["snack_bag", "chip_bag", "cracker_box", "candy_wrapper"]
    },
    {
        category: "Frozen",
        keywords: ["frozen", "gnocchi", "ice cream", "gelato", "pizza frozen", "nuggets", "mac n cheese", "mac 'n cheese", "orange chicken", "burrito", "waffle", "frozen fruit"],
        visualHints: ["frozen_package", "frost_packaging", "freezer_section"]
    },
    {
        category: "Produce",
        keywords: ["banana", "apple", "orange", "strawberr", "blueberr", "grape", "tomato", "lettuce", "spinach", "avocado", "onion", "potato", "carrot", "broccoli", "cucumber", "pepper", "celery", "mushroom", "organic baby"],
        visualHints: ["fresh_fruit", "fresh_vegetable", "produce_bin", "leafy_green"]
    },
    {
        category: "Meat & Seafood",
        keywords: ["chicken breast", "ground beef", "beef", "steak", "pork", "bacon", "sausage", "salmon", "shrimp", "fish", "turkey", "lamb", "ribs"],
        visualHints: ["meat_tray", "butcher_label", "raw_meat", "seafood_counter"]
    },
    {
        category: "Deli",
        keywords: ["rotisserie", "deli", "sliced", "ham", "salami", "prosciutto"],
        visualHints: ["deli_counter", "hot_food", "rotisserie_display"]
    },
    {
        category: "Bakery",
        keywords: ["bread", "bagel", "muffin", "croissant", "cake", "donut", "roll", "baguette", "tortilla", "pita"],
        visualHints: ["bread_loaf", "bakery_display", "baked_goods"]
    },
    {
        category: "Household",
        keywords: ["paper towel", "toilet paper", "detergent", "soap", "dish soap", "trash bag", "foil", "plastic wrap", "sponge", "cleaner", "wipe", "paper plate", "laundry", "tide", "bounty", "charmin", "dawn"],
        visualHints: ["cleaning_product", "paper_product", "household_aisle"]
    },
    {
        category: "Personal Care",
        keywords: ["toothpaste", "shampoo", "conditioner", "body wash", "deodorant", "razor", "lotion", "sunscreen", "floss", "mouthwash", "crest"],
        visualHints: ["hygiene_product", "personal_care_shelf"]
    },
    {
        category: "Baby",
        keywords: ["diaper", "huggies", "pampers", "baby food", "formula", "wipes baby", "pacifier", "bottle baby"],
        visualHints: ["diaper_package", "baby_product", "infant_care"]
    },
    {
        category: "Automotive",
        keywords: ["tire", "michelin", "goodyear", "motor oil", "wiper", "car wash", "brake", "coolant", "battery car"],
        visualHints: ["tire", "automotive_part", "car_product"]
    },
    {
        category: "Furniture",
        keywords: ["mattress", "serta", "couch", "sofa", "table", "chair", "desk", "shelf", "bookcase", "bed frame"],
        visualHints: ["mattress", "furniture_display", "large_item"]
    },
    {
        category: "Meal Kit",
        keywords: ["meal kit", "home chef", "hello fresh", "blue apron"],
        visualHints: ["meal_kit_box", "recipe_card"]
    },
    {
        category: "Seasoning",
        keywords: ["seasoning", "spice", "salt", "pepper", "cumin", "paprika", "oregano", "basil", "garlic powder", "everything but the bagel"],
        visualHints: ["spice_jar", "seasoning_bottle"]
    },
    {
        category: "Grocery",
        keywords: ["egg", "oil", "olive oil", "coconut oil", "pasta sauce", "peanut butter", "almond butter", "cookie butter", "jam", "honey", "rice", "pasta", "cereal", "flour", "sugar", "canned", "sauce", "ketchup", "mustard", "mayo"],
        visualHints: ["grocery_shelf", "pantry_item", "canned_good"]
    }
];

// Classify product by image features (future: called by vision pipeline)
// visualFeatures: array of detected labels from image recognition
function classifyByImage(visualFeatures) {
    if (!visualFeatures || visualFeatures.length === 0) return null;

    let bestMatch = null;
    let bestScore = 0;

    for (const rule of categoryRules) {
        let score = 0;
        for (const hint of rule.visualHints) {
            if (visualFeatures.some(f => f.toLowerCase().includes(hint))) {
                score++;
            }
        }
        if (score > bestScore) {
            bestScore = score;
            bestMatch = rule.category;
        }
    }

    return bestMatch;
}

// Classify product by name keywords
function classifyByName(productName) {
    if (!productName) return "Uncategorized";

    const nameLower = productName.toLowerCase();
    let bestMatch = null;
    let bestScore = 0;

    for (const rule of categoryRules) {
        let score = 0;
        for (const keyword of rule.keywords) {
            if (nameLower.includes(keyword)) {
                // Longer keyword matches are weighted higher for precision
                score += keyword.length;
            }
        }
        if (score > bestScore) {
            bestScore = score;
            bestMatch = rule.category;
        }
    }

    return bestMatch || "Uncategorized";
}

// Main classifier: tries image first, falls back to name
// product: { name, image, imageUrl, visualFeatures? }
function classifyProduct(product) {
    // Priority 1: image-based classification (when vision pipeline provides features)
    if (product.visualFeatures) {
        const imageCategory = classifyByImage(product.visualFeatures);
        if (imageCategory) {
            return { category: imageCategory, source: "image" };
        }
    }

    // Priority 2: name-based classification
    const nameCategory = classifyByName(product.name);
    return { category: nameCategory, source: "name" };
}

// Run auto-classification on all products in the store data
function classifyAllProducts() {
    for (const storeKey in products) {
        for (const product of products[storeKey]) {
            const result = classifyProduct(product);
            product.category = result.category;
            product._categorySource = result.source;
        }
    }
}
