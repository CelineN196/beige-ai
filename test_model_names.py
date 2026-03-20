#!/usr/bin/env python3
"""Debug script to test which models work with the API key"""
import google.generativeai as genai
import os

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    api_key = 'AIzaSyBb_2ZouURAbi-fBR8jL_uwEGthGSlBu2E'
    print(f"Using configured API key")

genai.configure(api_key=api_key)

# Test different model names
test_models = [
    'gemini-2.0-flash-exp',
    'gemini-2.0-flash', 
    'gemini-2.0-pro-exp',
    'gemini-1.5-pro',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash-001',
    'gemini-pro',
]

print("Testing model availability:")
print("=" * 60)

for model_name in test_models:
    try:
        model = genai.GenerativeModel(model_name)
        # Try a simple generate_content call
        response = model.generate_content("Hi", generation_config={'max_output_tokens': 10})
        if response and response.text:
            print(f"✅ {model_name:30} WORKS")
        else:
            print(f"⚠️  {model_name:30} Empty response")
    except Exception as e:
        error_str = str(e)
        if '404' in error_str:
            print(f"❌ {model_name:30} 404 Not Found")
        elif 'permission' in error_str.lower() or 'api_key' in error_str.lower():
            print(f"❌ {model_name:30} Permission/Auth error")
        else:
            print(f"❌ {model_name:30} {error_str[:40]}")

print("=" * 60)
