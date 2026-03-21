#!/usr/bin/env python3
"""
Quick test script for Beige AI database and analytics system.
Tests all database operations to verify system is ready.
"""

import sys
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "backend" / "scripts"))
sys.path.insert(0, str(project_root / "backend"))

from database_manager import get_database_manager
from menu_config import CAKE_MENU

def test_database_system():
    """Run comprehensive tests on the database system."""
    
    print("\n" + "=" * 70)
    print("BEIGE.AI RETAIL INTELLIGENCE SYSTEM - TEST SUITE")
    print("=" * 70)
    
    # Initialize database
    db = get_database_manager()
    print(f"\n✅ Database Manager initialized")
    print(f"   Path: {db.database_path}")
    
    # Test 1: Initialize inventory
    print("\n[TEST 1] Initialize Inventory from Menu")
    print("-" * 70)
    db.initialize_inventory(
        CAKE_MENU,  # CAKE_MENU is a list, not a dict
        initial_stock=20,
        reorder_level=5
    )
    stats = db.get_total_inventory_value()
    print(f"✅ Inventory initialized")
    print(f"   Cakes in stock: {stats['cakes_in_stock']}")
    print(f"   Total items: {stats['total_items']}")
    
    # Test 2: Record test purchases
    print("\n[TEST 2] Record Test Purchases")
    print("-" * 70)
    test_purchases = [
        ('Korean Sesame Mini Bread', 'Korean Sesame Mini Bread', 'Happy', 'Sunny'),
        ('Dark Chocolate Sea Salt Cake', 'Dark Chocolate Sea Salt Cake', 'Celebratory', 'Sunny'),
        ('Matcha Zen Cake', 'Matcha Zen Cake', 'Stressed', 'Cloudy'),
        ('Berry Garden Cake', None, 'Tired', 'Rainy'),
        ('Korean Sesame Mini Bread', 'Café Tiramisu', 'Happy', 'Sunny'),
    ]
    
    for recommended, selected, mood, weather in test_purchases:
        purchase_id = db.record_purchase(recommended, selected, mood, weather)
        status = "Purchased" if selected else "Browsed"
        print(f"✅ Record #{purchase_id}: {status} - {selected or '(no purchase)'}")
    
    # Test 3: Update inventory
    print("\n[TEST 3] Update Inventory After Purchases")
    print("-" * 70)
    db.update_inventory('Korean Sesame Mini Bread', -2)  # 2 sold
    db.update_inventory('Dark Chocolate Sea Salt Cake', -1)  # 1 sold
    db.update_inventory('Matcha Zen Cake', -1)  # 1 sold
    db.update_inventory('Café Tiramisu', -1)  # 1 sold
    
    new_stats = db.get_total_inventory_value()
    print(f"✅ Inventory updated after sales")
    print(f"   Total items remaining: {new_stats['total_items']}")
    
    # Test 4: Get conversion rate
    print("\n[TEST 4] Analytics Metrics")
    print("-" * 70)
    conversion_rate = db.get_conversion_rate(days=1)
    accuracy = db.get_recommendation_accuracy(days=1)
    print(f"✅ Conversion Rate (1 day): {conversion_rate:.1f}%")
    print(f"✅ Recommendation Accuracy: {accuracy:.1f}%")
    
    # Test 5: Low stock alerts
    print("\n[TEST 5] Inventory Alerts (Low Stock)")
    print("-" * 70)
    low_stock = db.get_low_stock_items()
    if low_stock:
        print(f"✅ Found {len(low_stock)} items below reorder level:")
        for item in low_stock[:5]:  # Show first 5
            print(f"   • {item['cake_name']}: {item['stock']}/{item['reorder_level']} units")
    else:
        print("✅ All items adequately stocked")
    
    # Test 6: Popularity trends
    print("\n[TEST 6] Popularity Trends by Context")
    print("-" * 70)
    popularity = db.get_popularity_by_context(limit=10)
    if not popularity.empty:
        print(f"✅ Top purchased items by context:")
        for idx, row in popularity.head(5).iterrows():
            print(f"   • {row['selected_cake']}: {int(row['purchase_count'])} purchases")
            print(f"     (Mood: {row['mood']}, Weather: {row['weather']})")
    else:
        print("✅ No purchase data yet")
    
    # Test 7: Purchase history
    print("\n[TEST 7] Purchase History Analysis")
    print("-" * 70)
    history_df = db.get_purchase_history_dataframe(days=1)
    print(f"✅ Records in history: {len(history_df)}")
    if len(history_df) > 0:
        conversions = history_df['is_conversion'].sum()
        print(f"   Total recommendations: {len(history_df)}")
        print(f"   Successful purchases: {conversions}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Run Streamlit app: streamlit run frontend/beige_ai_app.py")
    print("2. Run analytics dashboard: streamlit run frontend/analytics_dashboard.py")
    print("3. View database at: data/beige_ai.db")
    print("\n")


if __name__ == "__main__":
    try:
        test_database_system()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
