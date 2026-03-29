#!/bin/bash

# Beige AI - Safe Root Directory Organization
# Organizes .python-version and retrain_v2_final.py

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "🔍 ANALYSIS & ORGANIZATION"
echo "==========================="
echo ""

# ==============================================================================
# 1. DECISION: .python-version
# ==============================================================================

echo "📋 Evaluating .python-version..."

PYTHON_VERSION_EXISTS=false
if [ -f .python-version ]; then
    PYTHON_VERSION_EXISTS=true
    PYTHON_VERSION=$(cat .python-version)
    echo "  ✓ File exists: .python-version ($PYTHON_VERSION)"
fi

# Check for pyenv usage
PYENV_USED=false
if grep -r "pyenv" README.md scripts/ docs/ .github/ 2>/dev/null | grep -qv "^Binary"; then
    PYENV_USED=true
fi

if grep -q "\.python-version" .gitignore 2>/dev/null; then
    PYENV_USED=true
fi

if command -v pyenv &> /dev/null; then
    PYENV_USED=true
fi

# Decision
if [ "$PYTHON_VERSION_EXISTS" = true ]; then
    if [ "$PYENV_USED" = true ]; then
        echo "  → Decision: KEEP (pyenv is used)"
        DELETE_PYTHON_VERSION=false
    else
        echo "  → Decision: DELETE (pyenv not used in project)"
        DELETE_PYTHON_VERSION=true
    fi
else
    echo "  → File does not exist"
    DELETE_PYTHON_VERSION=false
fi

echo ""

# ==============================================================================
# 2. DECISION: retrain_v2_final.py
# ==============================================================================

echo "📋 Evaluating retrain_v2_final.py..."

RETRAIN_IN_ROOT=false
RETRAIN_IN_BACKEND=false

if [ -f retrain_v2_final.py ]; then
    RETRAIN_IN_ROOT=true
    echo "  ✓ File exists in root: retrain_v2_final.py"
fi

if [ -f backend/training/retrain_v2_final.py ]; then
    RETRAIN_IN_BACKEND=true
    echo "  ✓ File exists in backend/training/: retrain_v2_final.py"
fi

if [ "$RETRAIN_IN_ROOT" = true ] && [ "$RETRAIN_IN_BACKEND" = false ]; then
    echo "  → Decision: MOVE to backend/training/"
    MOVE_RETRAIN=true
elif [ "$RETRAIN_IN_ROOT" = true ] && [ "$RETRAIN_IN_BACKEND" = true ]; then
    echo "  → Decision: SKIP (already exists in backend/training/)"
    MOVE_RETRAIN=false
else
    echo "  → File not in root (already organized)"
    MOVE_RETRAIN=false
fi

echo ""

# ==============================================================================
# 3. EXECUTION
# ==============================================================================

echo "⚙️  EXECUTING CHANGES"
echo "────────────────────"

# Delete .python-version
if [ "$DELETE_PYTHON_VERSION" = true ]; then
    rm .python-version
    echo "✓ Deleted: .python-version"
fi

# Move retrain_v2_final.py
if [ "$MOVE_RETRAIN" = true ]; then
    mkdir -p backend/training
    mv retrain_v2_final.py backend/training/retrain_v2_final.py
    echo "✓ Moved: retrain_v2_final.py → backend/training/"
fi

echo ""

# ==============================================================================
# 4. VALIDATION
# ==============================================================================

echo "🔍 VALIDATION"
echo "─────────────"

echo "Final root directory structure:"
ls -la | grep -E '^\-' | awk '{print "  " $NF}' | sort

echo ""
echo "Checking for unexpected Python files in root:"
UNEXPECTED=$(find . -maxdepth 1 -type f -name "*.py" 2>/dev/null | wc -l)
if [ "$UNEXPECTED" -eq 0 ]; then
    echo "  ✓ No Python files in root"
else
    echo "  ⚠️  Found $UNEXPECTED Python file(s) in root:"
    find . -maxdepth 1 -type f -name "*.py" -exec basename {} \;
fi

echo ""

# ==============================================================================
# 5. GIT OPERATIONS
# ==============================================================================

echo "🚀 GIT OPERATIONS"
echo "─────────────────"

if git rev-parse --git-dir >/dev/null 2>&1; then
    echo "Checking git status..."
    GIT_STATUS=$(git status --porcelain | wc -l)
    
    if [ "$GIT_STATUS" -gt 0 ]; then
        echo "  Staging changes..."
        git add .
        
        echo "  Creating commit..."
        git commit -m "refactor: organize training pipeline and clean root structure" 2>/dev/null && COMMIT_SUCCESS=true || COMMIT_SUCCESS=false
        
        if [ "$COMMIT_SUCCESS" = true ]; then
            echo "  ✓ Commit created"
            
            if git remote get-url origin >/dev/null 2>&1; then
                CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
                echo "  Pushing to origin/$CURRENT_BRANCH..."
                if git push origin "$CURRENT_BRANCH" 2>/dev/null; then
                    echo "  ✓ Pushed successfully"
                else
                    echo "  ℹ️  Already up to date"
                fi
            else
                echo "  ℹ️  No remote configured"
            fi
        else
            echo "  ℹ️  No changes to commit"
        fi
    else
        echo "  ✓ No changes to commit"
    fi
else
    echo "  ⚠️  Not a git repository"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ ORGANIZATION COMPLETE"
echo "═══════════════════════════════════════════════════════════"
