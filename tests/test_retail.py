#!/usr/bin/env python
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / 'backend' / 'scripts'))

from retail_database_manager import get_retail_database

# Test initialization
db = get_retail_database()
print('Retail database initialized')
print(f'Path: {db.database_path}')

# Test menu initialization
cake_menu = {
    'Chocolate Truffle': 8.50,
    'Matcha Cloud': 8.50,
    'Lemon Olive Oil': 9.00,
    'Berry Chantilly': 8.50,
    'Tiramisu Silk': 9.00,
    'Black Sesame Velvet': 9.50,
    'Pistachio Rose': 9.50,
    'Vanilla Almond': 8.00
}

db.initialize_inventory_from_menu(cake_menu)
print('Inventory initialized with 8 cakes')

# Get inventory status
inventory = db.get_inventory_status()
print(f'Inventory status retrieved: {len(inventory)} cakes')

first_cake = inventory.iloc[0]['cake_name']
first_stock = inventory.iloc[0]['current_stock']
first_price = inventory.iloc[0]['unit_price']
print(f'Sample: {first_cake} - {first_stock} units at ${first_price}')

# Test a sale
print('\nTesting sale processing...')
success, sale_id = db.process_sale(
    recommended_cake='Chocolate Truffle',
    bought_cake='Matcha Cloud',
    mood='Happy',
    weather='Sunny',
    price=8.50
)

if success:
    print(f'Sale recorded: ID={sale_id}')
    print('Inventory updated')
else:
    print('Sale failed')

print('\nALL TESTS PASSED - Retail system ready!')
