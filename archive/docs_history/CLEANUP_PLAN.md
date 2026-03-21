# Beige AI — Safe Cleanup Plan

**Status**: ✅ PROPOSED (Not Executed)  
**Date**: March 21, 2026  
**Approach**: Non-destructive, fully reversible  

---

## 📋 Executive Summary

This plan organizes your project into a clean, portfolio-ready structure by archiving:
- 36 documentation artifacts (kept in git history)
- 11 test scripts (consolidated in `/tests/`)
- 8 utility/diagnostic scripts
- 1 notebook (development sandbox)

**Result**: Clean root directory, organized archive, fully functional app.

---

## 1. Files to Archive

### 1.1 Documentation Files (36 .md files)

**Category: Feature Completion Reports**
```
BASKET_COMPLETE.md                          ← Shopping cart feature
BASKET_UI_FIX.md                           ← UI bug fixes
BASKET_USER_GUIDE.md                       ← User documentation
BEFORE_AFTER.md                            ← Visual comparisons
PRODUCT_CARDS_COMPLETE.md                  ← Product grid implementation
PRODUCT_CARDS_DELIVERABLES_INDEX.md        ← Deliverables manifest
PRODUCT_CARDS_IMPLEMENTATION_SUMMARY.md    ← Implementation notes
PRODUCT_CARDS_TECHNICAL.md                 ← Technical specs
PRODUCT_CARDS_BEFORE_AFTER.md             ← Before/after comparison
PRODUCT_CARDS_IMAGES_COMPLETE.md          ← Image integration
PRODUCT_CARDS_LOCAL_IMAGES_FIX.md         ← Image path fixes
```

**Category: API & Integration**
```
CONCIERGE_COMPLETION_SUMMARY.md    ← System prompt integration
CONCIERGE_INDEX.md                 ← Concierge docs index
CONCIERGE_STATUS.md                ← Deployment status
GEMINI_API_AUDIT_COMPLETE.md       ← API audit report
GEMINI_API_FIX_COMPLETE.md         ← API migration summary
GEMINI_API_FIX_SUMMARY.md          ← Fix summary
GEMINI_API_MIGRATION_COMPLETE.md   ← Migration completion
```

**Category: Infrastructure & Deployment**
```
INFERENCE_DELIVERY_SUMMARY.md      ← Inference pipeline summary
INFERENCE_PIPELINE_README.md       ← Inference setup guide
PATH_FIX_SUMMARY.md               ← Path resolution fixes
STREAMLIT_ACCESSIBILITY_FIX.md    ← Accessibility fixes
SYSTEM_STATUS.md                  ← Overall status report
```

**Category: Project Overview & Index**
```
COMPLETE_PROJECT_FLOW.md                ← Full user journey flow
COMPLETION_SUMMARY.md                   ← Project completion summary
DELIVERY_MANIFEST.md                    ← Delivery checklist
DOCUMENTATION_INDEX.md                  ← Old docs index
DOCUMENTATION_REFACTORING_COMPLETE.md   ← Refactoring summary
GETTING_STARTED.md                      ← Getting started guide
INDEX.md                                ← Project index
PROJECT_SUMMARY.md                      ← Project summary
PROJECT_SUMMARY_FLOWCHART.md           ← Flowchart overview
QUICK_REFERENCE.md                      ← Quick reference guide
RETAIL_QUICKSTART.md                    ← Retail setup guide
TESTING_BASKET.md                       ← Testing guide
VISUAL_OVERVIEW.md                      ← Visual documentation
```

**Archive Location**: `/archive/docs_history/`

---

### 1.2 Test Scripts (11 files)

**Current Location**: Root directory  
**Archive Location**: `Already exists: `/tests/` (move into it)**

```
test_analytics.py
test_checkout_flow.py
test_concierge_integration.py
test_gemini_1_5_flash.py
test_gemini_fix.py
test_integration.py
test_local_images.py
test_model_names.py
test_product_cards.py
test_retail.py
test_retail_system.py
```

**Action**: Move from root → `/tests/` (consolidate testing)

---

### 1.3 Utility & Diagnostic Scripts (8 files)

**Category: Validation Scripts**
```
verify_gemini_api.py               ← API verification
check_gemini_health.py             ← Health check utility
final_validation.py                ← Final validation script
```

**Category: Setup & Configuration**
```
apply_analyst_changes.py           ← Analyst mode setup
apply_analyst_mode.py              ← Analyst mode utility
fix_indentation.py                 ← Code formatting utility
generate_cake_images.py            ← Image generation utility
list_available_models.py           ← Model listing utility
```

**Archive Location**: `/archive/scripts_utility/`

---

### 1.4 Other Artifacts (2 files)

```
REFACTORING_SUMMARY.txt   → /archive/docs_history/
practice.ipynb            → /archive/notebooks/
```

---

## 2. Proposed Directory Structure

```
Beige AI/
├── main.py                         ← Application launcher (unchanged)
├── requirements.txt                ← Dependencies (unchanged)
├── README.md                       ← Main documentation (unchanged)
├── PROJECT_MASTER_LOG.md           ← Master reference document (unchanged)
├──
├── frontend/                       ← Frontend code (unchanged)
│   ├── beige_ai_app.py
│   ├── styles.css
│   └── analytics_dashboard.py
├──
├── backend/                        ← Backend logic (unchanged)
│   ├── api.py
│   ├── inference.py
│   ├── menu_config.py
│   ├── concierge_system_prompt.py
│   ├── models/
│   ├── data/
│   ├── training/
│   └── scripts/
├──
├── docs/                           ← Reference documentation (unchanged)
│   ├── EXECUTIVE_MASTER.md
│   ├── TECHNICAL_BIBLE.md
│   └── USER_OPERATIONS.md
├──
├── tests/                          ← Consolidated test suite (NEW)
│   ├── test_analytics.py           ← Moved from root
│   ├── test_checkout_flow.py       ← Moved from root
│   ├── test_concierge_integration.py
│   ├── test_gemini_1_5_flash.py
│   ├── test_gemini_fix.py
│   ├── test_integration.py
│   ├── test_local_images.py
│   ├── test_model_names.py
│   ├── test_product_cards.py
│   ├── test_retail.py
│   └── test_retail_system.py
├──
├── assets/                         ← Images & resources (unchanged)
│   ├── images/
│   └── viz/
├──
├── archive/                        ← Project history (NEW)
│   ├── docs_history/               ← Documentation artifacts
│   │   ├── BASKET_COMPLETE.md
│   │   ├── COMPLETE_PROJECT_FLOW.md
│   │   ├── CONCIERGE_*.md
│   │   ├── GEMINI_API_*.md
│   │   ├── INFERENCE_*.md
│   │   ├── PRODUCT_CARDS_*.md
│   │   ├── STREAMLIT_*.md
│   │   ├── REFACTORING_SUMMARY.txt
│   │   └── [35 more .md files...]
│   │
│   ├── scripts_utility/            ← Diagnostic & setup tools
│   │   ├── verify_gemini_api.py
│   │   ├── check_gemini_health.py
│   │   ├── final_validation.py
│   │   ├── apply_analyst_changes.py
│   │   ├── apply_analyst_mode.py
│   │   ├── fix_indentation.py
│   │   ├── generate_cake_images.py
│   │   └── list_available_models.py
│   │
│   └── notebooks/                  ← Development notebooks
│       └── practice.ipynb
├──
├── examples/                       ← Code examples (unchanged)
├── scripts/                        ← Backend utilities (unchanged)
├── data/                           ← Dataset files (unchanged)
├──
├── beige_ai.db                     ← Database (unchanged)
├── beige_retail.db                 ← Database (unchanged)
├──
├── .git/                           ← Version control (unchanged)
├── .gitignore                      ← Git config (unchanged)
├── .streamlit/                     ← Streamlit config (unchanged)
└── .venv/                          ← Virtual environment (unchanged)
```

---

## 3. Terminal Commands (Review Only)

⚠️ **DO NOT EXECUTE YET** — These are for your review.

### Step 1: Create Archive Directories

```bash
# Create archive infrastructure
mkdir -p archive/docs_history
mkdir -p archive/scripts_utility
mkdir -p archive/notebooks
```

### Step 2: Move Documentation Files

```bash
# Move documentation to archive
mv BASKET_COMPLETE.md archive/docs_history/
mv BASKET_UI_FIX.md archive/docs_history/
mv BASKET_USER_GUIDE.md archive/docs_history/
mv BEFORE_AFTER.md archive/docs_history/
mv COMPLETE_PROJECT_FLOW.md archive/docs_history/
mv COMPLETION_SUMMARY.md archive/docs_history/
mv CONCIERGE_COMPLETION_SUMMARY.md archive/docs_history/
mv CONCIERGE_INDEX.md archive/docs_history/
mv CONCIERGE_STATUS.md archive/docs_history/
mv DELIVERY_MANIFEST.md archive/docs_history/
mv DOCUMENTATION_INDEX.md archive/docs_history/
mv DOCUMENTATION_REFACTORING_COMPLETE.md archive/docs_history/
mv GEMINI_API_AUDIT_COMPLETE.md archive/docs_history/
mv GEMINI_API_FIX_COMPLETE.md archive/docs_history/
mv GEMINI_API_FIX_SUMMARY.md archive/docs_history/
mv GEMINI_API_MIGRATION_COMPLETE.md archive/docs_history/
mv GETTING_STARTED.md archive/docs_history/
mv INDEX.md archive/docs_history/
mv INFERENCE_DELIVERY_SUMMARY.md archive/docs_history/
mv INFERENCE_PIPELINE_README.md archive/docs_history/
mv PATH_FIX_SUMMARY.md archive/docs_history/
mv PRODUCT_CARDS_BEFORE_AFTER.md archive/docs_history/
mv PRODUCT_CARDS_COMPLETE.md archive/docs_history/
mv PRODUCT_CARDS_DELIVERABLES_INDEX.md archive/docs_history/
mv PRODUCT_CARDS_IMAGES_COMPLETE.md archive/docs_history/
mv PRODUCT_CARDS_IMPLEMENTATION_SUMMARY.md archive/docs_history/
mv PRODUCT_CARDS_LOCAL_IMAGES_FIX.md archive/docs_history/
mv PRODUCT_CARDS_TECHNICAL.md archive/docs_history/
mv PROJECT_SUMMARY.md archive/docs_history/
mv PROJECT_SUMMARY_FLOWCHART.md archive/docs_history/
mv QUICK_REFERENCE.md archive/docs_history/
mv RETAIL_QUICKSTART.md archive/docs_history/
mv STREAMLIT_ACCESSIBILITY_FIX.md archive/docs_history/
mv SYSTEM_STATUS.md archive/docs_history/
mv TESTING_BASKET.md archive/docs_history/
mv VISUAL_OVERVIEW.md archive/docs_history/
mv REFACTORING_SUMMARY.txt archive/docs_history/
```

### Step 3: Move Test Files

```bash
# Move test files to /tests/ directory
mv test_analytics.py tests/
mv test_checkout_flow.py tests/
mv test_concierge_integration.py tests/
mv test_gemini_1_5_flash.py tests/
mv test_gemini_fix.py tests/
mv test_integration.py tests/
mv test_local_images.py tests/
mv test_model_names.py tests/
mv test_product_cards.py tests/
mv test_retail.py tests/
mv test_retail_system.py tests/
```

### Step 4: Move Utility Scripts

```bash
# Move diagnostic and utility scripts to archive
mv verify_gemini_api.py archive/scripts_utility/
mv check_gemini_health.py archive/scripts_utility/
mv final_validation.py archive/scripts_utility/
mv apply_analyst_changes.py archive/scripts_utility/
mv apply_analyst_mode.py archive/scripts_utility/
mv fix_indentation.py archive/scripts_utility/
mv generate_cake_images.py archive/scripts_utility/
mv list_available_models.py archive/scripts_utility/
```

### Step 5: Move Notebooks

```bash
# Move development notebooks to archive
mv practice.ipynb archive/notebooks/
```

---

## 4. Validation Checklist

### Pre-Cleanup Verification

Before executing any commands:

- [ ] **Git Status Check**
  ```bash
  cd "/Users/queenceline/Downloads/Beige AI"
  git status
  # Should show clean working directory or only new files
  ```

- [ ] **App Functionality Test**
  ```bash
  python main.py
  # Verify Streamlit app launches without errors
  # Check ML model loading ✅
  # Check Gemini fallback ✅
  # Check shopping cart ✅
  ```

- [ ] **Import Tests**
  ```bash
  python -c "from backend.menu_config import CAKE_MENU; print(len(CAKE_MENU))"
  # Should print: 8
  ```

---

### Post-Cleanup Verification

After executing all commands:

- [ ] **Directory Structure Check**
  ```bash
  # Verify new structure
  ls -la archive/docs_history/     # Should have 36 .md files
  ls -la archive/scripts_utility/  # Should have 8 .py files
  ls -la archive/notebooks/        # Should have 1 .ipynb
  ls -la tests/                    # Should have 11 .py files
  ```

- [ ] **Root Directory Cleanup Verification**
  ```bash
  # Count remaining .md and .py files in root
  ls -1 *.md 2>/dev/null | wc -l  # Should be: 3 (README, PROJECT_MASTER_LOG, CLEANUP_PLAN)
  ls -1 test_*.py 2>/dev/null | wc -l  # Should be: 0
  ls -1 verify_*.py check_*.py apply_*.py 2>/dev/null | wc -l  # Should be: 0
  ```

- [ ] **Critical Files Preserved**
  ```bash
  # Verify essential files still exist
  [ -f main.py ] && echo "✅ main.py exists"
  [ -f requirements.txt ] && echo "✅ requirements.txt exists"
  [ -f README.md ] && echo "✅ README.md exists"
  [ -f PROJECT_MASTER_LOG.md ] && echo "✅ PROJECT_MASTER_LOG.md exists"
  [ -f frontend/beige_ai_app.py ] && echo "✅ frontend app exists"
  [ -f backend/inference.py ] && echo "✅ backend exists"
  ```

- [ ] **App Still Works**
  ```bash
  python main.py
  # Verify app launches
  # Test recommendation generation
  # Test shopping basket
  ```

---

## 5. Impact Analysis

### What Stays (Production Files)

✅ **Application Code**
- `main.py` — Entry point
- `frontend/beige_ai_app.py` — 1,700+ lines, fully functional
- `backend/inference.py`, `api.py`, `concierge_system_prompt.py` — ML inference
- `backend/menu_config.py` — Cake menu data

✅ **Data & Configuration**
- `requirements.txt` — Pinned dependencies
- `beige_ai.db`, `beige_retail.db` — Databases
- `backend/models/` — Trained ML artifacts
- `backend/data/` — Training dataset
- `.streamlit/` — Streamlit config

✅ **Documentation**
- `README.md` — Quick start guide
- `PROJECT_MASTER_LOG.md` — Master reference document
- `docs/` — 3 master files (Executive, Technical, Operations)

✅ **Development**
- `backend/training/` — ML training pipeline
- `examples/` — Code examples
- `assets/` — Images & visualizations

✅ **Testing** (Reorganized)
- `tests/` — All 11 test scripts, newly organized

---

### What Gets Archived (History)

📦 **Documentation** (36 .md files + 1 .txt)
- Feature reports (Basket, Product Cards, Concierge)
- API migration logs (Gemini fixes)
- Deployment guides (Inference, Path fixes)
- Project overviews (Flow, Summary, Index)

**Why Archive?**
- ✅ Preserved in git history (nothing lost)
- ✅ Still accessible if needed
- ✅ Cleans up root directory
- ✅ Establishes clear "current" vs. "historical" boundaries

📦 **Utility Scripts** (8 .py files)
- One-time setup utilities
- Diagnostic/validation tools
- Image generation helpers
- Model inspection scripts

**Why Move?**
- ✅ Not part of day-to-day workflow
- ✅ Still accessible in `/archive/scripts_utility/`
- ✅ Reduces cognitive load in root

📦 **Development** (1 .ipynb)
- Practice notebook for experimentation
- Not part of production app

**Why Move?**
- ✅ Keeps notebooks separate from main app
- ✅ Declutters root directory

---

## 6. Why This Plan is Safe

### ✅ Non-Destructive
- **No deletions** — Every file is moved to archive (fully recoverable)
- **Git tracking** — All changes will show in git history
- **Version control** — Can revert with `git reset` if needed

### ✅ Fully Reversible
```bash
# If you want to undo everything:
mv archive/docs_history/* ./
mv archive/scripts_utility/* ./
mv archive/notebooks/* ./
mv tests/test_*.py ./
```

### ✅ Zero App Impact
- **No code changes** — Only file organization
- **No import changes** — All paths remain the same
- **No dependency changes** — requirements.txt untouched
- **No database changes** — Databases left in place

### ✅ Production Ready
- App will run identically after cleanup
- All functionality preserved
- Testing still available (just organized)

---

## 7. Execution Path (Optional)

### If you want to execute:

**1. Review this plan**
```bash
# Read through CLEANUP_PLAN.md carefully
```

**2. Run verification**
```bash
cd "/Users/queenceline/Downloads/Beige AI"
python main.py  # Verify it still works before changes
```

**3. Execute cleanup** (copy-paste commands in order)
```bash
# Step 1: Create directories
mkdir -p archive/docs_history
mkdir -p archive/scripts_utility
mkdir -p archive/notebooks

# Step 2-5: Move files (see commands above)
```

**4. Verify afterward**
```bash
# Run post-cleanup verification (see checklist)
```

**5. Commit to git**
```bash
git add -A
git commit -m "refactor: organize project structure - archive docs and utilities"
```

---

## 8. Summary

| Category | Count | Result |
|----------|-------|--------|
| Documentation archived | 36 + 1 | ✅ `/archive/docs_history/` |
| Tests consolidated | 11 | ✅ `/tests/` |
| Utility scripts moved | 8 | ✅ `/archive/scripts_utility/` |
| Notebooks moved | 1 | ✅ `/archive/notebooks/` |
| Root `.md` files (after) | 3 | ✅ README, PROJECT_MASTER_LOG, CLEANUP_PLAN |
| Root `.py` files (after) | 3 | ✅ main, requirements, .py removed |
| **Total files archived** | **57** | ✅ Fully organized & preserved |

---

## Final Notes

✅ **This is a proposal only** — No files have been moved  
✅ **Fully reversible** — Git history preserved  
✅ **Zero risk to app** — Structure change only  
✅ **Portfolio ready** — Clean, professional organization  

**Next Steps:**
1. Review this plan
2. Discuss any concerns
3. Execute when ready
4. Git commit the changes

---

**Created**: March 21, 2026  
**Status**: ✅ Ready for Review
