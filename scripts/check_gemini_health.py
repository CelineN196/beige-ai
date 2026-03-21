#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import google.generativeai as genai

def check_gemini_health():
    """
    Health check for Gemini API integration.
    
    Returns:
        dict: {
            'status': 'success' | 'api_key_error' | 'auth_error' | 'runtime_error',
            'message': str,
            'api_available': bool
        }
    """
    result = {
        'status': None,
        'message': None,
        'api_available': False
    }
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        result['status'] = 'api_key_error'
        result['message'] = 'GEMINI_API_KEY environment variable not set'
        print(f"❌ {result['message']}")
        return result
    
    # Try to configure API
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        result['status'] = 'auth_error'
        result['message'] = f'Failed to configure Gemini API: {str(e)}'
        print(f"❌ {result['message']}")
        return result
    
    # Test API with simple prompt
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(
            'Say hello in one sentence',
            generation_config={'max_output_tokens': 20}
        )
        
        if response and response.text:
            result['status'] = 'success'
            result['message'] = 'Gemini API is healthy and responding'
            result['api_available'] = True
            print(f"✅ {result['message']}")
            return result
        else:
            result['status'] = 'runtime_error'
            result['message'] = 'API returned empty response'
            print(f"❌ {result['message']}")
            return result
            
    except Exception as e:
        error_type = type(e).__name__
        result['status'] = 'runtime_error'
        result['message'] = f'{error_type}: {str(e)}'
        print(f"❌ {result['message']}")
        return result

if __name__ == '__main__':
    print('=' * 70)
    print('Gemini API Health Check')
    print('=' * 70)
    result = check_gemini_health()
    print('=' * 70)
    sys.exit(0 if result['api_available'] else 1)
