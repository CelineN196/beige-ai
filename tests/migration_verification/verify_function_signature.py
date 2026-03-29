#!/usr/bin/env python3
"""
Verify log_checkout_order function signature is correct.
Run this to confirm the fix works before running Streamlit.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import inspect

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("VERIFYING FUNCTION SIGNATURE")
print("="*70)

try:
    from backend.integrations.supabase_integration import log_checkout_order
    
    print("\n✅ Function imported successfully")
    
    # Get function signature
    sig = inspect.signature(log_checkout_order)
    
    print(f"\nFunction: log_checkout_order")
    print(f"Parameters: {sig}")
    
    # Check for purchased_items parameter
    param_names = list(sig.parameters.keys())
    print(f"\nParameter list: {param_names}")
    
    if "purchased_items" in param_names:
        print("✅ 'purchased_items' parameter FOUND")
        print(f"   Type: {sig.parameters['purchased_items'].annotation}")
        print(f"   Default: {sig.parameters['purchased_items'].default}")
    else:
        print("❌ 'purchased_items' parameter NOT FOUND")
        print("   This means the module wasn't reloaded properly")
        sys.exit(1)
    
    # Test the function call signature
    print("\n" + "="*70)
    print("TESTING FUNCTION CALL")
    print("="*70)
    
    # This won't actually run the function, just verify the signature
    try:
        # Try calling with purchased_items (should not raise TypeError about parameter)
        import inspect
        bound = sig.bind_partial(
            order_id="test_123",
            items_purchased="Chocolate Cake",
            ai_recommendation="Chocolate Cake",
            match_result="Match",
            total_value=25.00,
            purchased_items=[{"name": "Chocolate Cake"}],
        )
        print("✅ Function call signature is VALID")
        print(f"   All parameters accepted correctly")
    except TypeError as e:
        print(f"❌ Function call would fail: {e}")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("✨ VERIFICATION PASSED")
    print("="*70)
    print("\nThe function signature is correct!")
    print("If you still see the TypeError:")
    print("  1. Kill the Streamlit app (Ctrl+C)")
    print("  2. Clear Python cache: find . -type d -name __pycache__ -exec rm -rf {} +")
    print("  3. Restart: streamlit run frontend/beige_ai_app.py")
    
except ImportError as e:
    print(f"❌ Failed to import: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
