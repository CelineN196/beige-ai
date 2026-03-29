#!/usr/bin/env python3
"""
Debug script to diagnose Supabase insert failures.

Usage:
    python debug_supabase_inserts.py

This script will:
1. Check Supabase connectivity
2. Verify RLS policies are enabled
3. Test insert with minimal payload
4. Check for silent failures
"""

import os
import sys
from pathlib import Path

# Load env vars
from dotenv import load_dotenv
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.integrations.supabase_logger import get_supabase_client, log_feedback
import logging

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_connectivity():
    """Verify Supabase connection."""
    print("\n" + "="*70)
    print("1️⃣  CHECKING SUPABASE CONNECTIVITY")
    print("="*70)
    
    try:
        client = get_supabase_client()
        if client is None:
            print("❌ FAILED: Client returned None")
            print("   Check: SUPABASE_URL and SUPABASE_KEY in .env")
            return False
        
        print("✅ Client initialized successfully")
        print(f"   URL: {os.getenv('SUPABASE_URL')[:20]}...")
        print(f"   Key: {os.getenv('SUPABASE_KEY')[:20]}...")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def check_table_exists():
    """Verify feedback_logs table exists."""
    print("\n" + "="*70)
    print("2️⃣  CHECKING FEEDBACK_LOGS TABLE")
    print("="*70)
    
    try:
        client = get_supabase_client()
        
        # Try a simple select
        response = client.table("feedback_logs").select("id").limit(1).execute()
        
        print(f"✅ Table exists and is readable")
        print(f"   Rows in table: {len(response.data) if response.data else 'querying...'}")
        return True
        
    except Exception as e:
        error_str = str(e).lower()
        if "not found" in error_str or "does not exist" in error_str:
            print(f"❌ FAILED: Table 'feedback_logs' does not exist")
        elif "policy" in error_str or "rls" in error_str:
            print(f"❌ FAILED: RLS policy prevents SELECT")
        else:
            print(f"❌ FAILED: {e}")
        return False

def check_rls_policies():
    """Check if RLS policies are configured."""
    print("\n" + "="*70)
    print("3️⃣  CHECKING RLS POLICIES")
    print("="*70)
    
    try:
        client = get_supabase_client()
        
        # Attempt minimal insert
        test_payload = {
            "session_id": "test_diagnostics",
            "user_input": {"test": True},
            "recommended_cake": "Test Cake",
            "context": {"test": True},
            "model_version": "hybrid_v1",
        }
        
        response = client.table("feedback_logs").insert(test_payload).execute()
        
        print("✅ INSERT successful - RLS policies are configured correctly")
        print(f"   Response data: {response.data}")
        return True
        
    except Exception as e:
        error_str = str(e)
        
        if "policy" in error_str.lower() or "rls" in error_str.lower():
            print(f"❌ RLS POLICY BLOCKING INSERT")
            print(f"   Error: {error_str}")
            print(f"\n   📋 SOLUTION:")
            print(f"      1. Open Supabase dashboard")
            print(f"      2. Go to: Authentication > Policies")
            print(f"      3. Check the 'feedback_logs' table")
            print(f"      4. Ensure INSERT policy allows anon/public access")
            return False
        
        elif "permission denied" in error_str.lower():
            print(f"❌ PERMISSION DENIED")
            print(f"   Error: {error_str}")
            print(f"\n   📋 SOLUTION:")
            print(f"      Check Supabase grants for anon user")
            return False
        
        else:
            print(f"❌ INSERT FAILED: {error_str}")
            return False

def test_full_payload():
    """Test with full production payload."""
    print("\n" + "="*70)
    print("4️⃣  TESTING FULL PAYLOAD")
    print("="*70)
    
    try:
        success = log_feedback(
            session_id="debug_test_full",
            user_input={
                "mood": "happy",
                "weather_condition": "sunny",
                "temperature_celsius": 25,
            },
            recommended_cake="Dark Chocolate Cake",
            context={
                "weather": "sunny",
                "mood": "happy",
                "time_of_day": "afternoon",
            },
            latency_ms=234,
            confidence_score=0.87,
            cluster_id=2,
            user_feedback=5,
            feedback_notes="Test entry from debug script",
            model_version="hybrid_v1",
        )
        
        if success:
            print("✅ Full payload inserted successfully")
            return True
        else:
            print("❌ Full payload insert failed (check logs above)")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_checkout_payload():
    """Test checkout-specific payload."""
    print("\n" + "="*70)
    print("5️⃣  TESTING CHECKOUT PAYLOAD")
    print("="*70)
    
    try:
        success = log_feedback(
            session_id="debug_test_checkout",
            user_input={
                "order_id": "order_12345",
                "items_purchased": "Chocolate Cake, Vanilla Cake",
                "match_result": "Match",
                "total_value": 45.99,
            },
            recommended_cake="Chocolate Cake",
            context={
                "checkout": True,
                "timestamp": "2026-03-29T10:30:00Z",
            },
            feedback_notes="Checkout: Match | Purchased: Chocolate Cake, Vanilla Cake",
            model_version="hybrid_v1",
        )
        
        if success:
            print("✅ Checkout payload inserted successfully")
            return True
        else:
            print("❌ Checkout payload insert failed (check logs above)")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n🔍 SUPABASE INSERT DIAGNOSTICS")
    print("="*70)
    
    results = {
        "Connectivity": check_connectivity(),
        "Table Exists": check_table_exists(),
        "RLS Policies": check_rls_policies(),
        "Full Payload": test_full_payload(),
        "Checkout Payload": test_checkout_payload(),
    }
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Supabase inserts should work!")
    else:
        print("❌ SOME CHECKS FAILED - See details above")
        print("\n📋 NEXT STEPS:")
        print("   1. Fix the failed checks (RLS policies most common)")
        print("   2. Re-run this script to verify fixes")
        print("   3. Test the app with: streamlit run frontend/beige_ai_app.py")
    
    print("="*70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
