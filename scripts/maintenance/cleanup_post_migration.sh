#!/bin/bash

# Beige AI - Post-Supabase V2 Migration Cleanup
# Safe, idempotent cleanup script
# Reorganizes root directory and archives migration artifacts
# Safe to run multiple times - uses `mv -n` to prevent overwrites

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "🧹 Beige AI - Post-Migration Cleanup"
echo "====================================="
echo ""

# ============================================================================
# STEP 1: CREATE DIRECTORY STRUCTURE
# ============================================================================

echo "📁 Creating directory structure..."
mkdir -p docs/migration_v2 2>/dev/null
mkdir -p docs/logs 2>/dev/null
mkdir -p tests/verification 2>/dev/null
echo "   ✅ Directories created"
echo ""

# ============================================================================
# STEP 2: MOVE MIGRATION DOCUMENTATION
# ============================================================================

echo "📚 Moving migration documentation..."

# Move Supabase documentation
for file in SUPABASE_*.md; do
    if [ -f "$file" ]; then
        mv -n "$file" docs/migration_v2/ 2>/dev/null && echo "   ✅ Moved $file"
    fi
done

# Move dynamic context documentation
for file in DYNAMIC_CONTEXT_*.md; do
    if [ -f "$file" ]; then
        mv -n "$file" docs/migration_v2/ 2>/dev/null && echo "   ✅ Moved $file"
    fi
done

# Move context quick reference
for file in CONTEXT_QUICK_*.md; do
    if [ -f "$file" ]; then
        mv -n "$file" docs/migration_v2/ 2>/dev/null && echo "   ✅ Moved $file"
    fi
done

echo ""

# ============================================================================
# STEP 3: MOVE COMPLETION LOGS
# ============================================================================

echo "📋 Moving completion logs..."

if [ -f "FILE_REORGANIZATION_COMPLETE.md" ]; then
    mv -n FILE_REORGANIZATION_COMPLETE.md docs/logs/ 2>/dev/null && echo "   ✅ Moved FILE_REORGANIZATION_COMPLETE.md"
fi

if [ -f "FRONTEND_DEBUG_CLEANUP_COMPLETE.md" ]; then
    mv -n FRONTEND_DEBUG_CLEANUP_COMPLETE.md docs/logs/ 2>/dev/null && echo "   ✅ Moved FRONTEND_DEBUG_CLEANUP_COMPLETE.md"
fi

echo ""

# ============================================================================
# STEP 4: MOVE TEST VERIFICATION SCRIPTS
# ============================================================================

echo "🧪 Moving test verification scripts..."

if [ -f "test_supabase_v2_connection.py" ]; then
    mv -n test_supabase_v2_connection.py tests/verification/ 2>/dev/null && echo "   ✅ Moved test_supabase_v2_connection.py"
fi

if [ -f "verify_frontend_cleanup.py" ]; then
    mv -n verify_frontend_cleanup.py tests/verification/ 2>/dev/null && echo "   ✅ Moved verify_frontend_cleanup.py"
fi

if [ -f "verify_structure.sh" ]; then
    mv -n verify_structure.sh tests/verification/ 2>/dev/null && echo "   ✅ Moved verify_structure.sh"
fi

echo ""

# ============================================================================
# STEP 5: FINAL VERIFICATION
# ============================================================================

echo "✅ Cleanup complete!"
echo ""
echo "📂 Root directory contents:"
echo "=========================="
ls -1 | grep -v "^$"
echo ""

migration_files=$(ls -1 docs/migration_v2/ 2>/dev/null | wc -l)
logs_files=$(ls -1 docs/logs/ 2>/dev/null | wc -l)
test_files=$(ls -1 tests/verification/ 2>/dev/null | wc -l)

echo "📊 Organized files:"
echo "   📚 Migration docs: $migration_files files"
echo "   📋 Completion logs: $logs_files files"
echo "   🧪 Test scripts: $test_files files"
echo ""
echo "✨ Root directory is clean and ready for production!"
