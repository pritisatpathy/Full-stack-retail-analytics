import sqlite3

print("Connecting to database...")
conn = sqlite3.connect('retail_sales_normalized.db')
cursor = conn.cursor()

cursor.execute('SELECT "Product ID", "Product Name" FROM products')
products = cursor.fetchall()

variants = {
    'milk': ['Almond Milk', 'Whole Cow Milk', 'Oat Milk', 'Skim Milk'],
    'pizza': ['Pepperoni Pizza', 'Margherita Pizza', 'BBQ Chicken Pizza', 'Veggie Supreme'],
    'burger': ['Classic Cheeseburger', 'Bacon Double Burger', 'Spicy Chicken Burger', 'Veggie Burger'],
    'washing machine': ['Front-Load Washing Machine', 'Top-Load Washing Machine', 'Compact Washing Machine'],
    'bed': ['King Size Bed', 'Queen Size Bed', 'Twin Bunk Bed'],
    'fan': ['Ceiling Fan', 'Tower Fan', 'Desk Fan'],
    'yogurt': ['Greek Yogurt', 'Strawberry Yogurt', 'Vanilla Yogurt', 'Blueberry Yogurt'],
    'tomato': ['Cherry Tomatoes', 'Roma Tomatoes', 'Heirloom Tomatoes']
}

counters = {key: 0 for key in variants.keys()}
print(f"Calculating variations for {len(products)} products...")
updates = []

for product_id, product_name in products:
    name_lower = product_name.lower()
    new_name = product_name
    
    for base_item, variant_list in variants.items():
        if base_item in name_lower:
            idx = counters[base_item] % len(variant_list)
            new_name = variant_list[idx]
            counters[base_item] += 1
            break
            
    if new_name == product_name and " - " in product_name:
        new_name = product_name.split(" - ")[0].strip()

    updates.append((new_name, product_id))

print("Applying name changes in bulk...")
cursor.executemany('UPDATE products SET "Product Name" = ? WHERE "Product ID" = ?', updates)

conn.commit()
conn.close()
print("Success! All products have realistic names.")