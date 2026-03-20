#!/usr/bin/env python3
"""
Setup verification and model comparison runner script

This script:
1. Verifies all dependencies are installed
2. Checks that data files exist
3. Runs the model comparison pipeline
4. Provides helpful error messages if something fails
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_python_version():
    """Verify Python version >= 3.8"""
    print_header("1. Checking Python Version")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   ❌ ERROR: Python 3.8+ required")
        return False
    
    print("   ✅ Python version OK")
    return True

def check_dependencies():
    """Verify required packages are installed"""
    print_header("2. Checking Dependencies")
    
    required = {
        'sklearn': 'scikit-learn',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'joblib': 'joblib',
        'matplotlib': 'matplotlib',
    }
    
    missing = []
    
    for module, package_name in required.items():
        try:
            __import__(module)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} (MISSING)")
            missing.append(package_name)
    
    if missing:
        print(f"\n   To install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def check_data_files():
    """Verify dataset files exist and are readable"""
    print_header("3. Checking Data Files")
    
    # Dynamically locate dataset using pathlib
    base_dir = Path(__file__).resolve().parents[2]  # Root: Beige AI/
    dataset_file = base_dir / "backend" / "data" / "beige_ai_cake_dataset_v2.csv"
    
    print(f"   [INFO] Looking for dataset at: {dataset_file}")
    
    if not dataset_file.exists():
        print(f"   ❌ Dataset not found")
        print(f"\n   Expected location: {dataset_file}")
        print(f"   Please ensure the dataset file exists")
        return False
    
    # Verify file is readable and contains data
    try:
        import pandas as pd
        df = pd.read_csv(dataset_file)
        print(f"   ✅ Dataset found and loaded successfully")
        print(f"   [INFO] Dataset shape: {df.shape}")
        print(f"   [INFO] Columns: {len(df.columns)}")
        return True
    except Exception as e:
        print(f"   ❌ Error reading dataset: {e}")
        return False

def check_output_directories():
    """Create output directories if they don't exist"""
    print_header("4. Setting Up Output Directories")
    
    base_dir = Path(__file__).resolve().parents[2]  # Root: Beige AI/
    
    models_dir = base_dir / "backend" / "models"
    docs_dir = base_dir / "docs"
    
    models_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"   ✅ Models directory: {models_dir}")
    print(f"   ✅ Docs directory: {docs_dir}")
    
    return True

def run_model_comparison():
    """Execute the model comparison script"""
    print_header("5. Running Model Comparison Pipeline")
    
    script_dir = Path(__file__).resolve().parent
    compare_script = script_dir / "compare_models.py"
    
    if not compare_script.exists():
        print(f"   ❌ compare_models.py not found at {compare_script}")
        return False
    
    try:
        print("   Starting pipeline...")
        print(f"   (This may take 3-5 minutes depending on dataset size)\n")
        
        result = subprocess.run(
            [sys.executable, str(compare_script)],
            cwd=str(script_dir),
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print_header("✅ Pipeline Completed Successfully")
            return True
        else:
            print_header("❌ Pipeline Failed")
            print(f"   Exit code: {result.returncode}")
            return False
            
    except Exception as e:
        print_header("❌ Error Running Pipeline")
        print(f"   {str(e)}")
        return False

def print_next_steps():
    """Print next steps and usage instructions"""
    print_header("Next Steps")
    
    print("""
   1. Review the generated report:
      docs/MODEL_TRAINING_REPORT.md
   
   2. Check the confusion matrix visualization:
      docs/confusion_matrix_*.png
   
   3. Load and use the best model:
      
      import joblib
      model = joblib.load('backend/models/best_model.joblib')
      metadata = joblib.load('backend/models/feature_info.joblib')
      
      predictions = model.predict(X_new)
   
   4. For detailed information:
      Read: docs/MODEL_COMPARISON_GUIDE.md
      Read: docs/QUICK_REFERENCE.md
   
   5. Deploy to production when ready
    """)

def main():
    """Main verification and execution flow"""
    
    print("""
    
    ╔═══════════════════════════════════════════════════════════╗
    ║     BEIGE.AI MODEL COMPARISON & SELECTION PIPELINE       ║
    ║                Setup & Execution Verification            ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Data Files", check_data_files),
        ("Output Directories", check_output_directories),
    ]
    
    passed = 0
    for name, check_fn in checks:
        if check_fn():
            passed += 1
        else:
            print_header(f"⚠️  Setup Incomplete")
            print(f"   Failed at: {name}")
            print(f"   Please fix the issues above and try again")
            sys.exit(1)
    
    print_header(f"✅ All Checks Passed ({passed}/{len(checks)})")
    
    # Ask for confirmation before running
    print("\nReady to start model comparison pipeline?")
    print("(This will take approximately 3-5 minutes)")
    
    response = input("\nProceed? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("   Cancelled by user")
        sys.exit(0)
    
    # Run the pipeline
    if run_model_comparison():
        print_next_steps()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
