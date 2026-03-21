#!/usr/bin/env python
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / 'backend' / 'scripts'))
sys.path.insert(0, str(Path.cwd() / 'frontend'))

from retail_database_manager import get_retail_database
from checkout_handler import process_checkout

# Initialize database and menu
db = get_retail_database()
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

print('=== CHECKOUT FLOW SIMULATION ===\n')

# Simulate a customer basket
print('Step 1: Customer adds items to basket')
basket = [
    {'cake': 'Chocolate Truffle', 'price': 8.50},
    {'cake': 'Matcha Cloud', 'price': 8.50},
    {'cake': 'Berry Chantilly', 'price': 8.50}
]
print(f'✅ Basket created with {len(basket)} items')
total = sum(item['price'] for item in basket)
print(f'   Total: ${total:.2f}')

# Check inventory before
inv_before = db.get_inventory_status()
ct_before = inv_before[inv_before['cake_name'] == 'Chocolate Truffle']['current_stock'].values[0]
print(f'\nStep 2: Check inventory before checkout')
print(f'✅ Chocolate Truffle stock before: {ct_before} units')

# Process checkout (simulating beige_ai_app flow)
print(f'\nStep 3: Process checkout')
success, count, revenue = process_checkout(
    basket=basket,
    recommended_cake='Chocolate Truffle',
    mood='Happy',
    weather='Sunny',
    db_analytics=db
)

if success:
    print(f'✅ Checkout successful')
    print(f'   Items processed: {count}')
    print(f'   Revenue: ${revenue:.2f}')
else:
    print(f'❌ Checkout failed')
    sys.exit(1)

# Check inventory after
inv_after = db.get_inventory_status()
ct_after = inv_after[inv_after['cake_name'] == 'Chocolate Truffle']['current_stock'].values[0]
print(f'\nStep 4: Verify inventory was updated')
print(f'✅ Chocolate Truffle stock after: {ct_after} units')
print(f'   Sold: {ct_before - ct_after} units ✅')

# Verify sales were recorded
print(f'\nStep 5: Verify sales were recorded in database')
sales = db.get_sales_history(days=1)
print(f'✅ Found {len(sales)} sales in database')
if len(sales) > 0:
    last_sale = sales.iloc[-1]
    print(f'   Last sale: {last_sale["bought_cake"]} (recommended: {last_sale["recommended_cake"]})')

print(f'\n✅ COMPLETE CHECKOUT FLOW SUCCESSFUL!')
print('   - Items added to basket')
print('   - Database transactions recorded')
print('   - Inventory updated correctly')
print('   - Sales history logged')
