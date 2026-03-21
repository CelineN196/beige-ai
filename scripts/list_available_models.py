#!/usr/bin/env python3
"""List available Gemini models"""
import google.generativeai as genai
import os
import sys

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ Error: GEMINI_API_KEY environment variable not set.")
    print("Set it with: export GEMINI_API_KEY='your-api-key'")
    sys.exit(1)

genai.configure(api_key=api_key)

print("Available Gemini Models:")
print("=" * 70)

try:
    models = genai.list_models()
    found = False
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"✓ {model.name}")
            found = True
    
    if found:
        print("\n✅ Models support generateContent")
    else:
        print("\n⚠️ No models support generateContent")
        
except Exception as e:
    print(f"Error: {e}")
