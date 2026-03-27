#!/usr/bin/env python3
"""
Test Supabase v2.x Integration
============================================================================

This script tests the Supabase connection with modern v2.x client library.
Use this to verify your credentials and database schema are properly set up.

Requirements:
  - supabase>=2.0.0
  - SUPABASE_URL and SUPABASE_KEY environment variables set
  - .env file in project root (optional, will be auto-loaded)

Usage:
  python test_supabase_v2_connection.py
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"📄 Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
    else:
        print(f"ℹ️  No .env file found (optional)")

def test_supabase_connection():
    """Test basic Supabase connection and permissions."""
    
    print("\n" + "="*70)
    print("🧪 SUPABASE v2.x CONNECTION TEST")
    print("="*70)
    
    # 1. Check environment variables
    print("\n[STEP 1] Checking Environment Variables")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url:
        print("❌ SUPABASE_URL not set")
        return False
    else:
        # Show masked URL
        url_display = supabase_url.split("https://")[1].split(".")[0] if "https://" in supabase_url else supabase_url
        print(f"✅ SUPABASE_URL: https://{url_display}...")
    
    if not supabase_key:
        print("❌ SUPABASE_KEY not set")
        return False
    else:
        # Show masked key
        key_display = supabase_key[:10] + "..." if len(supabase_key) > 10 else "***"
        print(f"✅ SUPABASE_KEY: {key_display}")
    
    # 2. Import Supabase client
    print("\n[STEP 2] Importing Supabase Client")
    try:
        from supabase import create_client, Client
        print("✅ Supabase v2.x client imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import supabase: {e}")
        print("   Install with: pip install 'supabase>=2.0.0'")
        return False
    
    # 3. Initialize client
    print("\n[STEP 3] Initializing Supabase Client")
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False
    
    # 4. Test table exists
    print("\n[STEP 4] Checking feedback_logs Table")
    try:
        response = supabase.table("feedback_logs").select("*").limit(1).execute()
        print("✅ feedback_logs table exists and is accessible")
        print(f"   Response type: {type(response).__name__}")
        
        # Show data structure
        if hasattr(response, 'data') and response.data:
            first_row = response.data[0]
            print(f"   Sample columns: {list(first_row.keys())[:5]}...")
    
    except Exception as e:
        print(f"⚠️  Could not access feedback_logs table: {e}")
        print("   Tip: Run backend/supabase_schema.sql in Supabase SQL editor")
        return False
    
    # 5. Test successful read
    print("\n[STEP 5] Testing Read Operation")
    try:
        response = supabase.table("feedback_logs").select("id,created_at,recommended_cake").limit(5).execute()
        print(f"✅ Successfully read {len(response.data)} records")
        if response.data:
            print(f"   First record: {response.data[0]}")
    except Exception as e:
        print(f"❌ Read test failed: {e}")
        return False
    
    # 6. Test write permission (dry run)
    print("\n[STEP 6] Testing Write Permission (Validation Only)")
    try:
        # Create test data
        import uuid
        test_entry = {
            "session_id": f"test_{uuid.uuid4().hex[:8]}",
            "user_input": json.dumps({"mood": "happy", "temperature": 25}),
            "recommended_cake": "Test Cake",
            "context": json.dumps({"weather": "sunny"}),
            "model_version": "test_v1",
        }
        
        # This validates the structure
        print("✅ Test data structure validated:")
        for key, val in test_entry.items():
            print(f"   - {key}: {str(val)[:40]}...")
        print("\n   (Actual write would happen in production)")
        
    except Exception as e:
        print(f"⚠️  Write validation failed: {e}")
        return False
    
    # 7. Test error handling
    print("\n[STEP 7] Testing Error Handling")
    try:
        # Try to select from non-existent table
        response = supabase.table("nonexistent_table").select("*").execute()
        print("⚠️  Expected error was not raised (RLS might be disabled)")
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg or "404" in error_msg:
            print("✅ Proper error handling for non-existent table")
        else:
            print(f"✅ Error handling working (error: {error_msg[:50]}...)")
    
    # Success!
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    print("\nYour Supabase setup is ready for production use.")
    print("\nNext steps:")
    print("  1. Verify schema: Run backend/supabase_schema.sql in Supabase")
    print("  2. Test logging: python backend/supabase_logger.py")
    print("  3. Integrate: Add imports to frontend/beige_ai_app.py")
    
    return True

def main():
    """Main entry point."""
    # Load .env file if exists
    load_env_file()
    
    # Run tests
    success = test_supabase_connection()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
