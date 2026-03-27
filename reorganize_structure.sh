#!/bin/bash
###############################################################################
# Beige AI - Production File Structure Reorganization
#
# Safe, idempotent reorganization script for:
# - Datasets → /data/raw/
# - Images → /assets/images/
# - Internal docs → /docs/internal/
#
# Features:
# - mkdir -p (safe if folders exist)
# - mv -n (no overwrite, skip if exists)
# - Error handling with return codes
# - Validation and summary
###############################################################################

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Counters
MOVED=0
SKIPPED=0
FAILED=0

# Get script directory (project root)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${GREEN}=====================================================================${NC}"
echo -e "${GREEN}Beige AI - Production Directory Reorganization${NC}"
echo -e "${GREEN}=====================================================================${NC}"
echo ""
echo "Project Root: $PROJECT_ROOT"
echo ""

# ============================================================================
# STEP 1: Create Directory Structure
# ============================================================================

echo -e "${YELLOW}[STEP 1] Creating directory structure...${NC}"

mkdir -p data/raw
mkdir -p assets/images
mkdir -p docs/internal

echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# ============================================================================
# STEP 2: Move Datasets
# ============================================================================

echo -e "${YELLOW}[STEP 2] Moving datasets to /data/raw/...${NC}"

# Array of dataset files to move
datasets=(
    "beige_ai_cake_dataset_v2.csv"
    "beige_ai_cake_dataset.csv"
    "beige_customer_clusters.csv"
)

for file in "${datasets[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo "  Moving: $file"
        if mv -n "$PROJECT_ROOT/$file" "$PROJECT_ROOT/data/raw/$file" 2>/dev/null; then
            echo -e "${GREEN}    ✓ Moved${NC}"
            ((MOVED++))
        else
            # File might already exist in destination
            if [ -f "$PROJECT_ROOT/data/raw/$file" ]; then
                echo -e "${YELLOW}    ⊘ Already in data/raw/, skipping${NC}"
                ((SKIPPED++))
                # Remove duplicate from root if it exists
                rm -f "$PROJECT_ROOT/$file" 2>/dev/null && echo -e "${GREEN}    ✓ Removed duplicate from root${NC}"
            else
                echo -e "${RED}    ✗ Failed to move${NC}"
                ((FAILED++))
            fi
        fi
    else
        echo -e "${YELLOW}  ⊘ $file not found, skipping${NC}"
    fi
done

echo ""

# ============================================================================
# STEP 3: Move Images
# ============================================================================

echo -e "${YELLOW}[STEP 3] Moving media files to /assets/images/...${NC}"

# Array of image files to move
images=(
    "eda_analysis.png"
)

for file in "${images[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo "  Moving: $file"
        if mv -n "$PROJECT_ROOT/$file" "$PROJECT_ROOT/assets/images/$file" 2>/dev/null; then
            echo -e "${GREEN}    ✓ Moved${NC}"
            ((MOVED++))
        else
            if [ -f "$PROJECT_ROOT/assets/images/$file" ]; then
                echo -e "${YELLOW}    ⊘ Already in assets/images/, skipping${NC}"
                ((SKIPPED++))
                rm -f "$PROJECT_ROOT/$file" 2>/dev/null
            else
                echo -e "${RED}    ✗ Failed to move${NC}"
                ((FAILED++))
            fi
        fi
    else
        echo -e "${YELLOW}  ⊘ $file not found, skipping${NC}"
    fi
done

echo ""

# ============================================================================
# STEP 4: Move Internal Documentation
# ============================================================================

echo -e "${YELLOW}[STEP 4] Moving internal docs to /docs/internal/...${NC}"

# Array of documentation files to move
docs=(
    "CHANGELOG.md"
    "GIT_COMMIT_GUIDE.sh"
    "PRODUCTION_ARCHITECTURE.md"
    "PRODUCTION_CLEANUP_STATUS.md"
)

for file in "${docs[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo "  Moving: $file"
        if mv -n "$PROJECT_ROOT/$file" "$PROJECT_ROOT/docs/internal/$file" 2>/dev/null; then
            echo -e "${GREEN}    ✓ Moved${NC}"
            ((MOVED++))
        else
            if [ -f "$PROJECT_ROOT/docs/internal/$file" ]; then
                echo -e "${YELLOW}    ⊘ Already in docs/internal/, skipping${NC}"
                ((SKIPPED++))
                rm -f "$PROJECT_ROOT/$file" 2>/dev/null
            else
                echo -e "${RED}    ✗ Failed to move${NC}"
                ((FAILED++))
            fi
        fi
    else
        echo -e "${YELLOW}  ⊘ $file not found, skipping${NC}"
    fi
done

echo ""

# ============================================================================
# STEP 5: Verify Root Directory
# ============================================================================

echo -e "${YELLOW}[STEP 5] Verifying root directory structure...${NC}"
echo ""

KEEP_IN_ROOT=(
    "retrain_v2_final.py"
    "README.md"
    "requirements.txt"
    ".gitignore"
    ".python-version"
    ".git"
)

echo "✓ Core directories (should exist):"
for dir in backend core frontend services models scripts tests analysis archive examples assets data docs; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir/"
    fi
done

echo ""
echo "✓ Root files (should exist):"
for file in "${KEEP_IN_ROOT[@]}"; do
    if [ -f "$file" ] || [ -d "$file" ]; then
        # Get file type
        if [ -d "$file" ]; then
            echo "  ✓ $file/ (directory)"
        else
            SIZE=$(du -h "$file" | cut -f1)
            echo "  ✓ $file ($SIZE)"
        fi
    fi
done

echo ""

# ============================================================================
# STEP 6: Summary
# ============================================================================

echo -e "${GREEN}=====================================================================${NC}"
echo -e "${GREEN}REORGANIZATION SUMMARY${NC}"
echo -e "${GREEN}=====================================================================${NC}"

echo ""
echo "Files moved:     ${MOVED}"
echo "Files skipped:   ${SKIPPED}"
echo "Files failed:    ${FAILED}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Reorganization completed successfully!${NC}"
else
    echo -e "${RED}⚠ Some operations failed. Please review above.${NC}"
    exit 1
fi

echo ""
echo "Next steps:"
echo "  1. Review python code paths (updated separately)"
echo "  2. Run: ./verify_structure.sh"
echo "  3. Test: streamlit run frontend/beige_ai_app.py"
echo "  4. Commit: git add . && git commit -m 'refactor: reorganize file structure'"
echo ""
