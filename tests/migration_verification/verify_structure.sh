#!/bin/bash
###############################################################################
# Beige AI - Post-Reorganization Verification
#
# Validates that files were moved correctly and structure is clean
###############################################################################

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

ERRORS=0

echo -e "${GREEN}=====================================================================${NC}"
echo -e "${GREEN}Beige AI - Directory Structure Verification${NC}"
echo -e "${GREEN}=====================================================================${NC}"
echo ""

# ============================================================================
# CHECK 1: Directory Structure
# ============================================================================

echo -e "${YELLOW}[CHECK 1] Required directories exist...${NC}"

required_dirs=(
    "data/raw"
    "assets/images"
    "docs/internal"
    "backend"
    "frontend"
    "core"
    "services"
    "models"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}  ✓ $dir/${NC}"
    else
        echo -e "${RED}  ✗ $dir/ missing${NC}"
        ((ERRORS++))
    fi
done

echo ""

# ============================================================================
# CHECK 2: Files Moved Successfully
# ============================================================================

echo -e "${YELLOW}[CHECK 2] Files moved to correct locations...${NC}"

check_file() {
    local filepath="$1"
    local description="$2"
    
    if [ -f "$filepath" ]; then
        size=$(du -h "$filepath" | cut -f1)
        echo -e "${GREEN}  ✓ $filepath ($description, $size)${NC}"
    else
        echo -e "${RED}  ✗ $filepath ($description) missing${NC}"
        ((ERRORS++))
    fi
}

check_file "data/raw/beige_ai_cake_dataset_v2.csv" "Dataset"
check_file "assets/images/eda_analysis.png" "EDA Analysis"
check_file "docs/internal/CHANGELOG.md" "Changelog"
check_file "docs/internal/PRODUCTION_ARCHITECTURE.md" "Architecture"
check_file "docs/internal/PRODUCTION_CLEANUP_STATUS.md" "Cleanup Status"
check_file "docs/internal/GIT_COMMIT_GUIDE.sh" "Git Guide"

echo ""

# ============================================================================
# CHECK 3: Files NOT in Root (Should be moved)
# ============================================================================

echo -e "${YELLOW}[CHECK 3] Datasets/docs removed from root...${NC}"

should_not_exist=(
    "beige_ai_cake_dataset_v2.csv"
    "beige_ai_cake_dataset.csv"
    "beige_customer_clusters.csv"
    "eda_analysis.png"
    "CHANGELOG.md"
    "GIT_COMMIT_GUIDE.sh"
)

files_in_root=0
for file in "${should_not_exist[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${RED}  ✗ $file still in root${NC}"
        ((FILES_IN_ROOT++))
        ((ERRORS++))
    fi
done

if [ $files_in_root -eq 0 ]; then
    echo -e "${GREEN}  ✓ All files moved from root${NC}"
fi

echo ""

# ============================================================================
# CHECK 4: Core Files in Root (Should remain)
# ============================================================================

echo -e "${YELLOW}[CHECK 4] Core production files in root...${NC}"

root_required=(
    "README.md"
    "requirements.txt"
    "retrain_v2_final.py"
)

for file in "${root_required[@]}"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        echo -e "${GREEN}  ✓ $file ($size)${NC}"
    else
        echo -e "${RED}  ✗ $file missing from root${NC}"
        ((ERRORS++))
    fi
done

echo ""

# ============================================================================
# CHECK 5: .gitignore Updated
# ============================================================================

echo -e "${YELLOW}[CHECK 5] Git configuration...${NC}"

if [ -f ".gitignore" ]; then
    echo -e "${GREEN}  ✓ .gitignore exists${NC}"
    
    # Check for key patterns
    if grep -q "data/raw/" .gitignore 2>/dev/null; then
        echo -e "${GREEN}    ✓ data/raw/ included in .gitignore${NC}"
    else
        echo -e "${YELLOW}    ⚠ data/raw/ might need to be in .gitignore${NC}"
    fi
else
    echo -e "${YELLOW}  ⊘ .gitignore not found${NC}"
fi

if [ -d ".git" ]; then
    echo -e "${GREEN}  ✓ .git directory exists (repo ready)${NC}"
fi

echo ""

# ============================================================================
# CHECK 6: Root Directory Cleanliness
# ============================================================================

echo -e "${YELLOW}[CHECK 6] Root directory cleanliness...${NC}"

# Count files in root
root_file_count=$(find . -maxdepth 1 -type f | wc -l)
root_dir_count=$(find . -maxdepth 1 -type d | wc -l)

echo "  Root contains:"
echo "    Files: $root_file_count"
echo "    Directories: $((root_dir_count - 1))" # Subtract self (.)

if [ $root_file_count -le 10 ]; then
    echo -e "${GREEN}  ✓ Root directory is clean (<= 10 files)${NC}"
else
    echo -e "${YELLOW}  ⚠ Root directory has $root_file_count files (consider moving more)${NC}"
fi

echo ""

# ============================================================================
# CHECK 7: Dataset Integrity
# ============================================================================

echo -e "${YELLOW}[CHECK 7] Dataset files integrity...${NC}"

datasets=(
    "data/raw/beige_ai_cake_dataset_v2.csv"
    "data/raw/beige_ai_cake_dataset.csv"
)

for dataset in "${datasets[@]}"; do
    if [ -f "$dataset" ]; then
        # Check file size
        size=$(du -h "$dataset" | cut -f1)
        lines=$(wc -l < "$dataset")
        echo -e "${GREEN}  ✓ $dataset${NC}"
        echo "    Size: $size, Lines: $lines"
    fi
done

echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "${GREEN}=====================================================================${NC}"
echo -e "${GREEN}VERIFICATION SUMMARY${NC}"
echo -e "${GREEN}=====================================================================${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Directory structure is production-ready:"
    echo "  /data/raw/          - Datasets"
    echo "  /assets/images/     - Media assets"
    echo "  /docs/internal/     - Internal documentation"
    echo "  Root:               - Core production files"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Found $ERRORS issue(s)${NC}"
    echo ""
    echo "Please fix the above issues before committing."
    echo ""
    exit 1
fi
