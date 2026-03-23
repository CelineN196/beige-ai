#!/usr/bin/env python
"""Check which packages have wheels available."""

import subprocess
import sys

packages = [
    'streamlit',
    'pandas',
    'numpy',
    'scikit-learn',
    'xgboost',
    'joblib',
    'pillow',
    'matplotlib',
    'google-generativeai'
]

print(f"Python: {sys.version.split()[0]}")
print("=" * 60)
print("WHEEL AVAILABILITY CHECK")
print("=" * 60)

for pkg in packages:
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'download', '--dry-run', '--only-binary=:all:', pkg],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            status = "✅ HAS WHEELS"
        else:
            # Check for "no wheels" error message
            if "Could not find" in result.stderr or "No matching distribution" in result.stderr:
                status = "❌ NO WHEELS (but package exists)"
            else:
                status = "❌ WHEELS NOT FOUND"
        
        print(f"{pkg:25} {status}")
        
    except subprocess.TimeoutExpired:
        print(f"{pkg:25} ⏱️  TIMEOUT")
    except Exception as e:
        print(f"{pkg:25} ❓ ERROR: {str(e)[:40]}")

print("=" * 60)
