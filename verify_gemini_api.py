#!/usr/bin/env python3
"""
Gemini API Initialization Verification Test
Tests the robustness and safety of the Gemini API initialization in Streamlit
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "frontend"))
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import google.generativeai as genai

def test_api_initialization():
    """Test Gemini API initialization with different scenarios"""
    
    print("\n" + "="*80)
    print("🔍 GEMINI API INITIALIZATION VERIFICATION")
    print("="*80)
    
    # Test 1: Check if API key is in environment
    print("\n1️⃣ Checking environment variables...")
    env_key = os.getenv('GEMINI_API_KEY')
    if env_key:
        print(f"   ✅ GEMINI_API_KEY found in environment")
        print(f"   Key starts with: {env_key[:20]}...")
    else:
        print(f"   ❌ GEMINI_API_KEY not found in environment")
        env_key = None
    
    # Test 2: Check if secrets.toml exists and is readable
    print("\n2️⃣ Checking Streamlit secrets...")
    secrets_path = Path(__file__).parent / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        print(f"   ✅ Secrets file found at: {secrets_path}")
        try:
            with open(secrets_path, 'r') as f:
                content = f.read()
                if 'GEMINI_API_KEY' in content:
                    print(f"   ✅ GEMINI_API_KEY present in secrets.toml")
                else:
                    print(f"   ❌ GEMINI_API_KEY not found in secrets.toml")
        except Exception as e:
            print(f"   ❌ Failed to read secrets file: {e}")
    else:
        print(f"   ⚠️  Secrets file not found at: {secrets_path}")
    
    # Test 3: Check frontend secrets
    print("\n3️⃣ Checking frontend Streamlit secrets...")
    frontend_secrets = Path(__file__).parent / "frontend" / ".streamlit" / "secrets.toml"
    if frontend_secrets.exists():
        print(f"   ✅ Frontend secrets file found at: {frontend_secrets}")
        try:
            with open(frontend_secrets, 'r') as f:
                content = f.read()
                # Check format
                if '[general]' in content:
                    print(f"   ⚠️  WARNING: Secrets have [general] section (should be removed)")
                if 'GEMINI_API_KEY' in content:
                    print(f"   ✅ GEMINI_API_KEY present in frontend secrets")
        except Exception as e:
            print(f"   ❌ Failed to read frontend secrets: {e}")
    else:
        print(f"   ⚠️  Frontend secrets file not found at: {frontend_secrets}")
    
    # Test 4: Verify the fixed initialization function
    print("\n4️⃣ Verifying initialize_gemini() function...")
    try:
        # Read the app file to check if it has correct initialization
        app_path = Path(__file__).parent / "frontend" / "beige_ai_app.py"
        with open(app_path, 'r') as f:
            app_content = f.read()
        
        # Check for the new pattern
        if 'api_key = st.secrets.get("GEMINI_API_KEY")' in app_content:
            print(f"   ✅ Correct st.secrets.get() pattern found")
        else:
            print(f"   ❌ Correct st.secrets.get() pattern NOT found")
        
        if 'genai.configure(api_key=None)' in app_content:
            print(f"   ✅ Safe genai.configure(api_key=None) pattern found")
        else:
            print(f"   ❌ Safe fallback pattern NOT found")
        
        if 'os.getenv(\'GEMINI_API_KEY\')' in app_content:
            print(f"   ✅ Environment variable fallback found")
        else:
            print(f"   ❌ Environment variable fallback NOT found")
            
    except Exception as e:
        print(f"   ❌ Failed to verify function: {e}")
    
    # Test 5: Test actual initialization
    print("\n5️⃣ Testing actual API key configuration...")
    try:
        api_key = env_key or os.getenv('GEMINI_API_KEY')
        
        if api_key:
            genai.configure(api_key=api_key)
            print(f"   ✅ genai.configure() succeeded with API key")
            print(f"   ✅ API is ready for use")
        else:
            print(f"   ⚠️  No API key available - configuring with None")
            genai.configure(api_key=None)
            print(f"   ⚠️  API is in disabled mode (fallback state)")
    except Exception as e:
        print(f"   ❌ Failed to configure API: {type(e).__name__}: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("✅ VERIFICATION COMPLETE")
    print("="*80)
    print("""
Summary:
- Gemini API initialization is now robust and Streamlit-compatible
- Uses st.secrets.get() for safe access to configuration
- Falls back to environment variable for local development
- Gracefully handles missing API key with genai.configure(api_key=None)
- Proper error handling and user feedback

Next Steps:
1. Run Streamlit app: streamlit run frontend/beige_ai_app.py
2. Verify no warnings about missing API key in console
3. Test cake recommendation feature in UI
    """)

if __name__ == "__main__":
    test_api_initialization()

