import pandas as pd
import sqlite3

print("Reading original CSV...")
df = pd.read_csv('data/processed/retail_sales_cleaned.csv')

# 1. Clean the names
df['Clean Name'] = df['Product Name'].str.split(' - ').str[0]

# 2. Assign realistic US store prices
realistic_prices = {
    'Burgers': 5.99, 'Pizzas': 14.99, 'Fries': 3.49, 'Sandwiches': 6.99,
    'Milk': 3.99, 'Yogurt': 1.49, 'Cheese': 4.99, 'Butter': 3.49,
    'Tomatoes': 2.49, 'Mangoes': 1.99, 'Carrots': 1.29, 'Apples': 2.99,
    'Washing Machines': 499.99, 'Refrigerators': 899.99, 'Microwaves': 129.99, 'Fans': 45.99,
    'Beds': 349.99, 'Sofas': 599.99, 'Tables': 149.99, 'Chairs': 59.99,
    'Mops': 12.99, 'Buckets': 8.99, 'Utensils': 24.99, 'Detergents': 14.99
}

print("Unifying products and applying realistic prices...")
# Collapse duplicates into exactly 24 master products
products = df[['Clean Name', 'Category of Goods']].drop_duplicates(subset=['Clean Name']).copy()
products['Product Name'] = products['Clean Name']
products['Product ID'] = 'PROD-' + products['Clean Name'].str.upper().str.replace(' ', '')
products['Unit Price'] = products['Clean Name'].map(realistic_prices)

final_products = products[['Product ID', 'Product Name', 'Unit Price', 'Category of Goods']]

print("Connecting to database...")
conn = sqlite3.connect('retail_sales_normalized.db')
final_products.to_sql('products', conn, if_exists='replace', index=False)

print("Mapping historical orders to the 24 master products...")
# Link the historical orders to our 24 clean products so bestsellers still work
id_mapping = dict(zip(products['Clean Name'], products['Product ID']))
df['Unified Product ID'] = df['Clean Name'].map(id_mapping)

order_items = df[['Order ID', 'Unified Product ID', 'Quantity', 'Sales', 'Profit','Discount']].copy()
order_items.rename(columns={'Unified Product ID': 'Product ID'}, inplace=True)
order_items.to_sql('order_items', conn, if_exists='replace', index=False)

print("Building customers and orders tables...")
customers = df[['Customer ID', 'Customer Name', 'State']].drop_duplicates(subset=['Customer ID'])
customers.to_sql('customers', conn, if_exists='replace', index=False)

orders = df[['Order ID', 'Customer ID', 'Order Date', 'Ship Mode']].drop_duplicates(subset=['Order ID'])
orders.to_sql('orders', conn, if_exists='replace', index=False)

conn.close()
print("Database perfectly normalized! No duplicates, realistic prices.")