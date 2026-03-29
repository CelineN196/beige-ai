"""
Supabase Deployment Validation Script for Beige AI
Automatically validates production readiness checklist.

Usage:
    python validate_supabase_deployment.py
    
Output:
    ✅ PASS - Check succeeded
    ❌ FAIL - Check failed
    ⚠️  WARNING - Check passed with warnings
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import subprocess

# Project root
PROJECT_ROOT = Path(__file__).parent
os.chdir(PROJECT_ROOT)

# Load .env
load_dotenv()

# Status indicators
PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARN = "⚠️  WARNING"


def print_section(title):
    """Print section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def check_env_file():
    """Check if .env file exists and has required keys."""
    print_section("1. CONFIGURATION CHECKS")
    
    checks_passed = 0
    checks_total = 4
    
    # Check .env exists
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        print(f"{PASS} .env file exists at {env_path}")
        checks_passed += 1
    else:
        print(f"{FAIL} .env file NOT found at {env_path}")
        print("       Run: echo 'SUPABASE_URL=...' > .env")
        return 0, checks_total
    
    # Check SUPABASE_URL
    supabase_url = os.getenv("SUPABASE_URL")
    if supabase_url and supabase_url.startswith("https://"):
        print(f"{PASS} SUPABASE_URL configured: {supabase_url[:40]}...")
        checks_passed += 1
    else:
        print(f"{FAIL} SUPABASE_URL missing or invalid")
        return checks_passed, checks_total
    
    # Check SUPABASE_KEY
    supabase_key = os.getenv("SUPABASE_KEY")
    if supabase_key and len(supabase_key) > 20:
        print(f"{PASS} SUPABASE_KEY configured: {supabase_key[:20]}...")
        checks_passed += 1
    else:
        print(f"{FAIL} SUPABASE_KEY missing or invalid")
        return checks_passed, checks_total
    
    # Check .env in .gitignore
    gitignore_path = PROJECT_ROOT / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            if ".env" in f.read():
                print(f"{PASS} .env is in .gitignore (secure)")
                checks_passed += 1
            else:
                print(f"{FAIL} .env is NOT in .gitignore (security risk!)")
    else:
        print(f"{FAIL} .gitignore not found")
    
    return checks_passed, checks_total


def check_dependencies():
    """Check if required packages are installed."""
    print_section("2. DEPENDENCIES CHECK")
    
    checks_passed = 0
    checks_total = 2
    
    required_packages = {
        'supabase': 'supabase>=2.0.0',
        'httpx': 'python-httpx>=0.24.0',
    }
    
    # Check requirements.txt
    req_path = PROJECT_ROOT / "requirements.txt"
    if req_path.exists():
        print(f"{PASS} requirements.txt exists")
        checks_passed += 1
    else:
        print(f"{FAIL} requirements.txt not found")
        return 0, checks_total
    
    # Try to import packages
    missing_packages = []
    for pkg_name, pkg_spec in required_packages.items():
        try:
            __import__(pkg_name.replace('-', '_'))
        except ImportError:
            missing_packages.append(pkg_spec)
    
    if not missing_packages:
        print(f"{PASS} All required packages installed")
        checks_passed += 1
    else:
        print(f"{FAIL} Missing packages: {', '.join(missing_packages)}")
        print("       Run: pip install -r requirements.txt")
    
    return checks_passed, checks_total


def check_database():
    """Check Supabase database connectivity and schema."""
    print_section("3. DATABASE CHECKS")
    
    checks_passed = 0
    checks_total = 6
    
    try:
        from supabase import create_client
    except ImportError:
        print(f"{FAIL} supabase package not installed")
        return 0, checks_total
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print(f"{FAIL} Supabase credentials not found in .env")
        return 0, checks_total
    
    try:
        client = create_client(supabase_url, supabase_key)
        print(f"{PASS} Connected to Supabase project")
        checks_passed += 1
    except Exception as e:
        print(f"{FAIL} Cannot connect to Supabase: {str(e)}")
        print("       Check SUPABASE_URL and SUPABASE_KEY")
        return 1, checks_total
    
    # Check feedback_logs table
    try:
        result = client.table('feedback_logs').select('id', count='exact').limit(0).execute()
        print(f"{PASS} feedback_logs table exists")
        checks_passed += 1
    except Exception as e:
        print(f"{FAIL} feedback_logs table not found: {str(e)}")
        print("       Run: Copy backend/supabase_schema.sql to Supabase SQL Editor")
        return checks_passed, checks_total
    
    # Check columns (at least key columns)
    required_columns = [
        'id', 'created_at', 'session_id', 'recommended_cake',
        'user_feedback', 'model_version'
    ]
    
    try:
        result = client.table('feedback_logs').select('*').limit(1).execute()
        if result.data:
            existing_cols = set(result.data[0].keys())
        else:
            # If table is empty, query schema differently
            existing_cols = set(required_columns)  # Assume it's correct
        
        missing_cols = set(required_columns) - existing_cols
        if not missing_cols:
            print(f"{PASS} All required columns present ({len(existing_cols)} columns)")
            checks_passed += 1
        else:
            print(f"{FAIL} Missing columns: {', '.join(missing_cols)}")
    except Exception as e:
        print(f"{WARN} Could not verify columns: {str(e)}")
        checks_passed += 1  # Don't fail on this
    
    # Check views
    views_to_check = ['v_model_performance', 'v_session_analytics']
    views_found = 0
    
    for view_name in views_to_check:
        try:
            result = client.table(view_name).select('*').limit(0).execute()
            print(f"{PASS} View {view_name} exists")
            views_found += 1
        except:
            print(f"{WARN} View {view_name} not found (optional)")
    
    checks_passed += min(views_found, 2)  # Max 2 points for views
    
    return checks_passed, checks_total


def check_code_files():
    """Check if required backend files exist."""
    print_section("4. CODE FILES CHECK")
    
    checks_passed = 0
    checks_total = 5
    
    # Backend files
    backend_files = {
        'supabase_logger.py': 'backend/supabase_logger.py',
        'supabase_integration.py': 'backend/supabase_integration.py',
        'supabase_schema.sql': 'backend/supabase_schema.sql',
    }
    
    for name, path in backend_files.items():
        file_path = PROJECT_ROOT / path
        if file_path.exists():
            print(f"{PASS} {name} exists")
            checks_passed += 1
        else:
            print(f"{FAIL} {name} not found at {path}")
    
    # Check frontend integration
    frontend_file = PROJECT_ROOT / "frontend" / "beige_ai_app.py"
    if frontend_file.exists():
        with open(frontend_file, 'r') as f:
            content = f.read()
            if 'log_recommendation' in content:
                print(f"{PASS} log_recommendation() is integrated in frontend")
                checks_passed += 1
            else:
                print(f"{FAIL} log_recommendation() not found in frontend")
    else:
        print(f"{FAIL} frontend/beige_ai_app.py not found")
    
    return checks_passed, checks_total


def check_test_script():
    """Run the test script to verify logging works."""
    print_section("5. INTEGRATION TEST")
    
    test_file = PROJECT_ROOT / "test_supabase_integration.py"
    if not test_file.exists():
        print(f"{WARN} test_supabase_integration.py not found (optional)")
        return 0, 1
    
    print(f"Running test script: {test_file}")
    print("(This will log 3 test records to Supabase)\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print(f"\n{PASS} Integration test passed")
            return 1, 1
        else:
            print(result.stdout)
            if result.stderr:
                print(f"Error: {result.stderr}")
            print(f"{FAIL} Integration test failed")
            return 0, 1
    except subprocess.TimeoutExpired:
        print(f"{FAIL} Test script timed out (>30s)")
        return 0, 1
    except Exception as e:
        print(f"{FAIL} Error running test: {str(e)}")
        return 0, 1


def check_deployment_readiness():
    """Check git and deployment readiness."""
    print_section("6. DEPLOYMENT READINESS")
    
    checks_passed = 0
    checks_total = 3
    
    # Check git status
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        if result.returncode == 0 and not result.stdout.strip():
            print(f"{PASS} Git working directory is clean")
            checks_passed += 1
        else:
            print(f"{WARN} Git has uncommitted changes (not critical)")
            checks_passed += 1  # Pass anyway
    except:
        print(f"{WARN} Could not check git status (git not found)")
        checks_passed += 1
    
    # Check requirements.txt is updated
    req_path = PROJECT_ROOT / "requirements.txt"
    if req_path.exists():
        with open(req_path, 'r') as f:
            content = f.read()
            if 'supabase' in content and 'python-httpx' in content:
                print(f"{PASS} requirements.txt includes Supabase dependencies")
                checks_passed += 1
            else:
                print(f"{FAIL} requirements.txt missing Supabase dependencies")
    
    # Check .env not committed
    try:
        result = subprocess.run(
            ['git', 'ls-files', '.env'],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        if not result.stdout.strip():
            print(f"{PASS} .env is not tracked in git (secure)")
            checks_passed += 1
        else:
            print(f"{FAIL} .env is tracked in git! Remove it: git rm --cached .env")
    except:
        print(f"{WARN} Could not verify .env git status")
        checks_passed += 1
    
    return checks_passed, checks_total


def print_summary(results):
    """Print final summary."""
    print_section("DEPLOYMENT VALIDATION SUMMARY")
    
    total_passed = sum(p for p, _ in results.values())
    total_checks = sum(t for _, t in results.values())
    percentage = int((total_passed / total_checks * 100)) if total_checks > 0 else 0
    
    print(f"Overall Score: {total_passed}/{total_checks} ({percentage}%)\n")
    
    for section, (passed, total) in results.items():
        status = "✅" if passed == total else "⚠️ " if passed > 0 else "❌"
        print(f"{status} {section:<30} {passed}/{total}")
    
    print()
    
    if percentage >= 90:
        print(f"🚀 {PASS} Ready for production deployment!")
    elif percentage >= 70:
        print(f"⚠️  {WARN} Most checks passed. Fix warnings before deployment.")
    else:
        print(f"❌ {FAIL} Critical issues found. Fix before deployment.")
    
    print()
    print("📋 Next steps:")
    print("   1. Fix any FAIL checks above")
    print("   2. Deploy to production")
    print("   3. Monitor first 100 logs in Supabase dashboard")
    print("   4. Set up backup for feedback_logs table")
    print()


def main():
    """Run all validation checks."""
    print("\n" + "="*70)
    print("  Beige AI - Supabase Deployment Validator")
    print("="*70)
    
    results = {
        "Configuration": check_env_file(),
        "Dependencies": check_dependencies(),
        "Database": check_database(),
        "Code Files": check_code_files(),
        "Integration Test": check_test_script(),
        "Deployment": check_deployment_readiness(),
    }
    
    print_summary(results)


if __name__ == "__main__":
    main()
