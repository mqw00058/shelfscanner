const storeInfo = {
    costco: {
        name: "Costco",
        desc: "Products detected from Costco store shelves",
        color: "#e21836"
    },
    "sams-club": {
        name: "Sam's Club",
        desc: "Products detected from Sam's Club store shelves",
        color: "#0060a9"
    },
    walmart: {
        name: "Walmart",
        desc: "Products detected from Walmart store shelves",
        color: "#0071dc"
    },
    "traders-joe": {
        name: "Trader Joe's",
        desc: "Products detected from Trader Joe's store shelves",
        color: "#c8102e"
    },
    kroger: {
        name: "Kroger",
        desc: "Products detected from Kroger store shelves",
        color: "#0033a0"
    }
};

// Image source priority:
//   1. "image"    — captured from uploaded video/photo (local path)
//   2. "imageUrl" — fetched from web search by product name
//   3. "emoji"    — fallback when no image is available
//
// Category is NOT hardcoded. It is auto-classified at runtime by
// classifier.js using product name keywords + image visual features.
// The "category" field below is left empty and populated on page load.

const products = {
    costco: [
        { id: 1, name: "Kirkland Signature Organic Extra Virgin Olive Oil", price: 14.99, unit: "2L", emoji: "🫒", image: null, imageUrl: null, desc: "Organic extra virgin olive oil. Premium Italian quality.", shelf: "Aisle A, Shelf 3, 2nd from left" },
        { id: 2, name: "Kirkland Signature Rotisserie Chicken", price: 4.99, unit: "1 whole (~3 lbs)", emoji: "🍗", image: null, imageUrl: null, desc: "Freshly roasted rotisserie chicken. Tender and juicy.", shelf: "Deli counter, hot food display", badge: "BEST" },
        { id: 3, name: "Bounty Advanced Paper Towels", price: 28.99, unit: "12 rolls", emoji: "🧻", image: null, imageUrl: null, desc: "Premium paper towels. 2-ply construction with superior absorbency.", shelf: "Aisle C, Shelf 5, center" },
        { id: 4, name: "Tide Pods Laundry Detergent", price: 24.99, unit: "152 ct", emoji: "🧴", image: null, imageUrl: null, desc: "3-in-1 laundry detergent pods. Cleans, freshens, and brightens.", shelf: "Aisle C, Shelf 4, right side" },
        { id: 5, name: "Kirkland Signature Organic Eggs", price: 8.49, unit: "24 ct", emoji: "🥚", image: null, imageUrl: null, desc: "Organic free-range eggs. USDA Organic certified.", shelf: "Refrigerated Aisle B, Shelf 1" },
        { id: 6, name: "Kirkland Signature Bacon", price: 14.99, unit: "4 pk (17.6 oz each)", emoji: "🥓", image: null, imageUrl: null, desc: "Hickory smoked bacon. Thick sliced.", shelf: "Refrigerated Aisle B, Shelf 2, left" },
        { id: 7, name: "Samsung 65\" QLED 4K TV", price: 599.99, unit: "1 unit", emoji: "📺", image: null, imageUrl: null, desc: "Samsung 65-inch QLED 4K Smart TV. Quantum Dot technology.", shelf: "Electronics Section D, wall display", badge: "HOT" },
        { id: 8, name: "Dyson V15 Detect Vacuum", price: 549.99, unit: "1 unit", emoji: "🔌", image: null, imageUrl: null, desc: "Dyson V15 cordless vacuum. Laser dust detection technology.", shelf: "Electronics Section D, Display 2" },
        { id: 9, name: "Kirkland Signature Mixed Nuts", price: 16.99, unit: "2.5 lbs", emoji: "🥜", image: null, imageUrl: null, desc: "Premium mixed nuts. Cashews, almonds, pecans, macadamias.", shelf: "Aisle A, Shelf 6, center", badge: "SALE" },
        { id: 10, name: "Kirkland Signature Water", price: 4.49, unit: "40 pk (16.9 fl oz)", emoji: "💧", image: null, imageUrl: null, desc: "Purified water 40-pack. Clean filtration system.", shelf: "Beverage Aisle E, floor pallet" },
        { id: 11, name: "Kirkland Signature Almond Butter", price: 9.99, unit: "27 oz", emoji: "🥜", image: null, imageUrl: null, desc: "100% almond butter. No additives.", shelf: "Aisle A, Shelf 4, right side" },
        { id: 12, name: "Huggies Little Movers Diapers", price: 42.99, unit: "180 ct (Size 4)", emoji: "👶", image: null, imageUrl: null, desc: "Huggies diapers. Perfect fit for active babies.", shelf: "Aisle F, Shelf 2" },
        { id: 13, name: "Starbucks French Roast Coffee", price: 18.49, unit: "2.5 lbs", emoji: "☕", image: null, imageUrl: null, desc: "Starbucks French Roast whole bean coffee. Deep dark roast flavor.", shelf: "Aisle A, Shelf 7, left" },
        { id: 14, name: "Kirkland Signature Prosecco", price: 6.99, unit: "750 ml", emoji: "🍾", image: null, imageUrl: null, desc: "Italian DOC Prosecco. Refreshing bubbles.", shelf: "Alcohol Section G, Shelf 3" },
        { id: 15, name: "Michelin Defender T+H Tires", price: 159.99, unit: "1 tire", emoji: "🛞", image: null, imageUrl: null, desc: "Michelin Defender T+H tire. 80,000 mile warranty.", shelf: "Automotive Section H, tire display" },
        { id: 16, name: "Kirkland Signature Greek Yogurt", price: 7.99, unit: "3 lbs (2 pk)", emoji: "🥛", image: null, imageUrl: null, desc: "Non-fat Greek yogurt. High in protein.", shelf: "Refrigerated Aisle B, Shelf 3, center" },
    ],
    "sams-club": [
        { id: 1, name: "Member's Mark Chicken Breast", price: 22.98, unit: "10 lbs", emoji: "🍗", image: null, imageUrl: null, desc: "Frozen chicken breast. Individually vacuum sealed.", shelf: "Frozen Aisle A, Shelf 2" },
        { id: 2, name: "Member's Mark Purified Water", price: 3.98, unit: "45 pk (16.9 fl oz)", emoji: "💧", image: null, imageUrl: null, desc: "Purified water bulk pack.", shelf: "Beverage Aisle B, floor pallet", badge: "BEST" },
        { id: 3, name: "Charmin Ultra Soft Toilet Paper", price: 32.98, unit: "36 rolls", emoji: "🧻", image: null, imageUrl: null, desc: "Charmin Ultra Soft. Premium softness.", shelf: "Aisle C, Shelf 1" },
        { id: 4, name: "Member's Mark Colombian Coffee", price: 14.98, unit: "2.2 lbs", emoji: "☕", image: null, imageUrl: null, desc: "100% Colombian beans. Medium roast.", shelf: "Aisle A, Shelf 8, left" },
        { id: 5, name: "Serta Perfect Sleeper Mattress", price: 399.00, unit: "Queen", emoji: "🛏️", image: null, imageUrl: null, desc: "Serta Perfect Sleeper queen mattress. Gel memory foam.", shelf: "Furniture Section E, mattress display", badge: "HOT" },
        { id: 6, name: "Member's Mark Organic Strawberries", price: 6.98, unit: "2 lbs", emoji: "🍓", image: null, imageUrl: null, desc: "Organic frozen strawberries. Perfect for smoothies.", shelf: "Frozen Aisle A, Shelf 4" },
        { id: 7, name: "Apple AirPods Pro 2", price: 189.00, unit: "1 unit", emoji: "🎧", image: null, imageUrl: null, desc: "Apple AirPods Pro 2. Active noise cancellation.", shelf: "Electronics Section D, locked display" },
        { id: 8, name: "Member's Mark Laundry Detergent", price: 15.98, unit: "1.5 gal", emoji: "🧴", image: null, imageUrl: null, desc: "Concentrated liquid laundry detergent. 110 loads.", shelf: "Aisle C, Shelf 3, center" },
        { id: 9, name: "Pampers Swaddlers Diapers", price: 39.98, unit: "168 ct (Size 3)", emoji: "👶", image: null, imageUrl: null, desc: "Pampers Swaddlers diapers. Ultra soft comfort.", shelf: "Aisle F, Shelf 1" },
        { id: 10, name: "Member's Mark Rotisserie Chicken", price: 5.98, unit: "1 whole", emoji: "🍗", image: null, imageUrl: null, desc: "In-store roasted rotisserie chicken.", shelf: "Deli counter, hot food display" },
        { id: 11, name: "Member's Mark Trail Mix", price: 11.98, unit: "3 lbs", emoji: "🥜", image: null, imageUrl: null, desc: "Premium trail mix. Nuts and dried fruit blend.", shelf: "Aisle A, Shelf 5, center" },
        { id: 12, name: "LG 75\" UHD 4K Smart TV", price: 649.00, unit: "1 unit", emoji: "📺", image: null, imageUrl: null, desc: "LG 75-inch UHD 4K Smart TV. webOS built-in.", shelf: "Electronics Section D, wall display" },
    ],
    walmart: [
        { id: 1, name: "Great Value Whole Milk", price: 3.36, unit: "1 gal", emoji: "🥛", image: null, imageUrl: null, desc: "Great Value whole milk. Vitamin D fortified.", shelf: "Refrigerated Aisle A, Shelf 1", badge: "BEST" },
        { id: 2, name: "Bananas", price: 0.27, unit: "1 each (~4 oz)", emoji: "🍌", image: null, imageUrl: null, desc: "Fresh bananas. Product of Ecuador.", shelf: "Produce section, near entrance" },
        { id: 3, name: "Great Value Peanut Butter", price: 2.98, unit: "2.5 lbs", emoji: "🥜", image: null, imageUrl: null, desc: "Creamy peanut butter. 100% peanuts.", shelf: "Aisle A, Shelf 3, center" },
        { id: 4, name: "Coca-Cola Classic", price: 7.48, unit: "24 cans (12 fl oz)", emoji: "🥤", image: null, imageUrl: null, desc: "Coca-Cola Classic 24-pack. The original taste.", shelf: "Beverage Aisle B, floor pallet" },
        { id: 5, name: "Lays Classic Potato Chips", price: 4.28, unit: "10 oz", emoji: "🥔", image: null, imageUrl: null, desc: "Lays Classic potato chips. Crispy original flavor.", shelf: "Snack Aisle C, Shelf 2" },
        { id: 6, name: "Great Value Paper Plates", price: 8.97, unit: "200 ct", emoji: "🍽️", image: null, imageUrl: null, desc: "Disposable paper plates. Microwave safe.", shelf: "Household Aisle D, Shelf 4" },
        { id: 7, name: "Tyson Chicken Nuggets", price: 8.47, unit: "5 lbs", emoji: "🍗", image: null, imageUrl: null, desc: "Tyson chicken nuggets. 100% white meat.", shelf: "Frozen Aisle E, Shelf 3" },
        { id: 8, name: "Crest 3D White Toothpaste", price: 5.97, unit: "3 pk (4.8 oz each)", emoji: "🪥", image: null, imageUrl: null, desc: "Crest 3D White toothpaste. Whitening formula.", shelf: "Personal Care Aisle F, Shelf 2" },
        { id: 9, name: "Great Value Eggs", price: 3.12, unit: "18 ct", emoji: "🥚", image: null, imageUrl: null, desc: "Grade A large eggs. Farm fresh.", shelf: "Refrigerated Aisle A, Shelf 2, bottom" },
        { id: 10, name: "Folgers Classic Roast Coffee", price: 9.98, unit: "3 lbs", emoji: "☕", image: null, imageUrl: null, desc: "Folgers Classic Roast. America's #1 coffee brand.", shelf: "Aisle A, Shelf 6, center" },
        { id: 11, name: "Onn. 50\" 4K Roku TV", price: 198.00, unit: "1 unit", emoji: "📺", image: null, imageUrl: null, desc: "Onn 50-inch 4K Roku TV. Best value smart TV.", shelf: "Electronics Section G, wall display", badge: "SALE" },
        { id: 12, name: "Great Value Spring Water", price: 3.48, unit: "40 pk (16.9 fl oz)", emoji: "💧", image: null, imageUrl: null, desc: "Natural spring water 40-pack. Clean daily hydration.", shelf: "Beverage Aisle B, floor pallet" },
        { id: 13, name: "Dawn Dish Soap", price: 3.97, unit: "18 fl oz", emoji: "🫧", image: null, imageUrl: null, desc: "Dawn dish soap. Powerful grease removal.", shelf: "Household Aisle D, Shelf 1" },
        { id: 14, name: "Ritz Crackers", price: 4.48, unit: "13.8 oz", emoji: "🍘", image: null, imageUrl: null, desc: "Ritz crackers. The original buttery flavor.", shelf: "Snack Aisle C, Shelf 3, left" },
    ],
    "traders-joe": [
        { id: 1, name: "Mandarin Orange Chicken", price: 4.99, unit: "22 oz", emoji: "🍊", image: null, imageUrl: null, desc: "Mandarin orange chicken. Trader Joe's bestseller #1.", shelf: "Frozen Aisle A, Shelf 1, center", badge: "BEST" },
        { id: 2, name: "Everything But The Bagel Seasoning", price: 2.49, unit: "2.3 oz", emoji: "🥯", image: null, imageUrl: null, desc: "Everything But The Bagel seasoning blend. Social media sensation.", shelf: "Seasoning Aisle B, Shelf 3" },
        { id: 3, name: "Cauliflower Gnocchi", price: 2.99, unit: "12 oz", emoji: "🥟", image: null, imageUrl: null, desc: "Cauliflower gnocchi. Gluten-free healthy option.", shelf: "Frozen Aisle A, Shelf 2", badge: "HOT" },
        { id: 4, name: "Dark Chocolate Peanut Butter Cups", price: 3.99, unit: "12 oz", emoji: "🍫", image: null, imageUrl: null, desc: "Dark chocolate peanut butter cups. Said to be better than Reese's.", shelf: "Snack Aisle C, Shelf 1" },
        { id: 5, name: "Organic Free Range Eggs", price: 4.49, unit: "12 ct", emoji: "🥚", image: null, imageUrl: null, desc: "Organic free-range eggs. Cage-free.", shelf: "Refrigerated Aisle D, Shelf 1" },
        { id: 6, name: "Joe's Diner Mac 'n Cheese", price: 3.49, unit: "20 oz", emoji: "🧀", image: null, imageUrl: null, desc: "Joe's Diner mac and cheese. Creamy cheese pasta.", shelf: "Frozen Aisle A, Shelf 3" },
        { id: 7, name: "Unexpected Cheddar Cheese", price: 3.99, unit: "7 oz", emoji: "🧀", image: null, imageUrl: null, desc: "Unexpected Cheddar cheese. Deep Parmigiano-like flavor.", shelf: "Refrigerated Aisle D, cheese corner" },
        { id: 8, name: "Triple Ginger Snaps", price: 3.99, unit: "14 oz", emoji: "🍪", image: null, imageUrl: null, desc: "Triple ginger snap cookies. Made with three kinds of ginger.", shelf: "Snack Aisle C, Shelf 2" },
        { id: 9, name: "Organic Coconut Oil", price: 4.99, unit: "16 fl oz", emoji: "🥥", image: null, imageUrl: null, desc: "Organic coconut oil. Virgin extra.", shelf: "Aisle B, Shelf 2, left" },
        { id: 10, name: "Two Buck Chuck (Charles Shaw Wine)", price: 3.49, unit: "750 ml", emoji: "🍷", image: null, imageUrl: null, desc: "Charles Shaw wine. Best value table wine.", shelf: "Alcohol Section E, wine shelf" },
        { id: 11, name: "Speculoos Cookie Butter", price: 3.69, unit: "14.1 oz", emoji: "🍪", image: null, imageUrl: null, desc: "Speculoos cookie butter. Belgian cookie spread.", shelf: "Aisle B, Shelf 4, center", badge: "HOT" },
        { id: 12, name: "Organic Baby Spinach", price: 2.49, unit: "6 oz", emoji: "🥬", image: null, imageUrl: null, desc: "Organic baby spinach. Perfect for salads.", shelf: "Produce, entrance refrigerated display" },
    ],
    kroger: [
        { id: 1, name: "Kroger Whole Milk", price: 3.19, unit: "1 gal", emoji: "🥛", image: null, imageUrl: null, desc: "Kroger whole milk. Fresh dairy.", shelf: "Refrigerated Aisle A, Shelf 1" },
        { id: 2, name: "Simple Truth Organic Chicken Breast", price: 9.99, unit: "1 lb", emoji: "🍗", image: null, imageUrl: null, desc: "Simple Truth organic chicken breast. No antibiotics.", shelf: "Meat Section B", badge: "BEST" },
        { id: 3, name: "Kroger Purified Drinking Water", price: 2.99, unit: "24 pk (16.9 fl oz)", emoji: "💧", image: null, imageUrl: null, desc: "Kroger purified water 24-pack.", shelf: "Beverage Aisle C, floor pallet" },
        { id: 4, name: "Simple Truth Natural Almonds", price: 7.49, unit: "1 lb", emoji: "🥜", image: null, imageUrl: null, desc: "Simple Truth natural almonds. Unsalted roasted.", shelf: "Snack Aisle D, Shelf 3" },
        { id: 5, name: "Kroger Shredded Mozzarella", price: 3.49, unit: "1 lb", emoji: "🧀", image: null, imageUrl: null, desc: "Kroger shredded mozzarella cheese. Perfect for pizza.", shelf: "Refrigerated Aisle A, cheese corner" },
        { id: 6, name: "Kroger Ground Beef 80/20", price: 5.99, unit: "1 lb", emoji: "🥩", image: null, imageUrl: null, desc: "Kroger ground beef. 80% lean, 20% fat balance.", shelf: "Meat Section B, center" },
        { id: 7, name: "Private Selection Gelato", price: 4.99, unit: "16 fl oz", emoji: "🍨", image: null, imageUrl: null, desc: "Private Selection gelato. Italian-style.", shelf: "Frozen Aisle E, ice cream section", badge: "HOT" },
        { id: 8, name: "Kroger Vitamin D Whole Eggs", price: 2.79, unit: "12 ct", emoji: "🥚", image: null, imageUrl: null, desc: "Vitamin D enriched eggs. Grade A large.", shelf: "Refrigerated Aisle A, Shelf 2" },
        { id: 9, name: "Simple Truth Organic Pasta Sauce", price: 3.29, unit: "24 oz", emoji: "🍝", image: null, imageUrl: null, desc: "Simple Truth organic pasta sauce. Marinara.", shelf: "Aisle A, Shelf 5, center" },
        { id: 10, name: "Kroger Sparkling Water", price: 3.29, unit: "12 cans (12 fl oz)", emoji: "🫧", image: null, imageUrl: null, desc: "Kroger sparkling water. Lime flavor.", shelf: "Beverage Aisle C, Shelf 2" },
        { id: 11, name: "Home Chef Meal Kit", price: 19.99, unit: "Serves 2", emoji: "👨‍🍳", image: null, imageUrl: null, desc: "Home Chef meal kit. Fresh ingredients and recipe included.", shelf: "Refrigerated, entrance meal kit display", badge: "NEW" },
        { id: 12, name: "Kroger Honey Wheat Bread", price: 2.49, unit: "20 oz", emoji: "🍞", image: null, imageUrl: null, desc: "Honey wheat bread. Soft texture.", shelf: "Bakery Section F, Shelf 1" },
    ]
};
