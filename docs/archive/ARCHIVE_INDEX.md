# Documentation Archive Index

**Purpose**: Historical reference for consolidated and deprecated documentation  
**Date**: March 21, 2026  
**Status**: All actively used documentation has been consolidated into `/docs/PROJECT_MASTER_LOG.md`

---

## Why This Archive Exists

In March 2026, the Beige AI project consolidated multiple scattered documentation files into a single source of truth: `PROJECT_MASTER_LOG.md`. This archive preserves the historical versions for reference and audit purposes.

**Benefits of consolidation**:
- ✅ Single file to search for all technical information
- ✅ No duplicate or conflicting information
- ✅ Easier to maintain and update
- ✅ Better navigation with clear section structure
- ✅ Professional technical reference format

---

## What Was Consolidated

### Order Logging & Data Pipeline Documentation (8 files)

| File | Purpose | Content Merged To |
|------|---------|-------------------|
| `ORDER_LOGGING_BEFORE_AFTER.md` | Before/after comparison of old vs new system | Section 2 (Data Pipeline) |
| `ORDER_LOGGING_IMPROVEMENTS.md` | Implementation improvements and hardening | Section 2 (Data Pipeline) |
| `ORDER_LOGGING_COMPLETE.md` | Complete implementation details | Section 2 (Data Pipeline) |
| `ORDER_LOGGING_REFERENCE.md` | Technical reference for order logging | Section 2 (Data Pipeline) |
| `ORDER_LOGGING_SUMMARY.md` | Summary of order logging system | Section 2 (Data Pipeline) |
| `CODE_CHANGES_REFERENCE.md` | Code change reference | Section 7 (Change Log) |
| `IMPLEMENTATION_COMPLETE.md` | Implementation completion notes | Section 7 (Change Log) |
| `CONSOLIDATION_SUMMARY.md` | Phase 1 consolidation summary | Section 7 (Change Log) |

**All content preserved** in Project Master Log:
- Complete code implementations
- Before/after comparisons  
- Error handling strategies
- Testing procedures
- CSV schema details
- Performance characteristics
- Production deployment checklist

### Technical Guides & Handbooks (10 files)

| File | Original Purpose | Note |
|------|-----------------|------|
| `API_DEPLOYMENT_GUIDE.md` | API deployment instructions | Historical reference |
| `BEIGE_AI_TECHNICAL_BIBLE.md` | Technical system design | Superseded by structured handbook |
| `COMPLETE_SUMMARY.md` | Project completion summary | Superseded by current status |
| `CONCIERGE_SYSTEM_PROMPT_GUIDE.md` | Concierge system documentation | Legacy feature documentation |
| `EXECUTIVE_MASTER.md` | Executive summary | Superseded by current status |
| `INFERENCE_PIPELINE_GUIDE.md` | Inference pipeline documentation | Legacy guide |
| `MODEL_COMPARISON_GUIDE.md` | Model comparison guide | Historical reference |
| `MODEL_TRAINING_REPORT.md` | Model training results | Historical training results |
| `MODEL_USAGE_GUIDE.md` | Model usage guide | Legacy guide |
| `TECHNICAL_BIBLE.md` | System technical reference | Superseded by structured handbook |
| `USER_OPERATIONS.md` | User operations guide | Historical operations guide |
| `QUICK_REFERENCE.md` | Quick reference guide | Historical reference |

### Supporting Files (2 files)

| File | Type | Note |
|------|------|------|
| `confusion_matrix_decision_tree.png` | Image | Historical model evaluation |
| `confusion_matrix_xgboost.png` | Image | Historical model evaluation |
| `pre_training_checklist.py` | Code | Historical pre-training checklist |

---

## Active Documentation Reference

**Single Source of Truth**: `/docs/PROJECT_MASTER_LOG.md`

This file contains:
- **Section 1**: System Architecture Overview
- **Section 2**: Data Pipeline & Logging System (order logging consolidated here)
- **Section 3**: Machine Learning / Model Layer
- **Section 4**: API & Backend Flow
- **Section 5**: Streamlit / UI Layer
- **Section 6**: Known Issues & Fixes
- **Section 7**: Change Log (implementation history)

**Quick Navigation**: Use the table of contents at the top of `PROJECT_MASTER_LOG.md` to jump to relevant sections.

---

## Directory Structure

```
/docs/
├── PROJECT_MASTER_LOG.md    ← ACTIVE: Complete technical reference
├── README.md                ← ACTIVE: Documentation overview
└── archive/                 ← HISTORICAL: Old documentation
    ├── ORDER_LOGGING_*.md   (consolidated)
    ├── *_GUIDE.md           (legacy guides)
    ├── *_SUMMARY.md         (legacy summaries)
    ├── *.png                (historical images)
    └── ARCHIVE_INDEX.md     ← YOU ARE HERE
```

---

## How to Use This Archive

### For Developers
1. **All current information**: Read `/docs/PROJECT_MASTER_LOG.md`
2. **Historical context**: Browse this archive if you need to understand past decisions
3. **Git history**: Use `git log` to see when files were archived and why

### For Git History Review
```bash
# See what was consolidated
git log --oneline -- docs/archive/

# View specific archived file at a point in time
git show HEAD~N:docs/archive/ORDER_LOGGING_BEFORE_AFTER.md
```

### For Team Onboarding
1. Start with `/docs/PROJECT_MASTER_LOG.md` — it has everything needed
2. Skip the archive unless troubleshooting historical issues
3. Use "Quick Navigation" in the master file to find relevant sections

---

## Future Maintenance

### When Adding New Documentation
1. **DO**: Add to `/docs/PROJECT_MASTER_LOG.md`
2. **DON'T**: Create new .md files in docs/
3. **ARCHIVE**: If a file becomes obsolete, move it to `/docs/archive/`

### Archive Policy
- Files in archive are **read-only historical references**
- No updates to archived files (improves git history clarity)
- New information belongs in `PROJECT_MASTER_LOG.md`

### When to Archive
- Implementation section is complete and documented in master file
- Technical guide is superseded by structured handbook
- Summary document becomes redundant
- Historical reference no longer needed for daily work

---

## Consolidation Timeline

**Phase 1: Consolidation (March 21, 2026)**
- Read all order logging documentation (8 files)
- Merged into PROJECT_MASTER_LOG.md
- Added deprecation notices to old files

**Phase 2: Structure & Deduplication (March 21, 2026)**
- Removed duplicate explanations
- Improved document structure (7 sections)
- Standardized terminology
- Consolidated before/after comparisons

**Phase 3: Archive & Final Cleanup (March 21, 2026)**
- Created `/docs/archive/` directory
- Moved 23 files to archive
- Established single source of truth
- Cleaned up repository structure

---

## Reference Information

| Detail | Value |
|--------|-------|
| **Consolidation Date** | March 21, 2026 |
| **Files Archived** | 24 (docs + images + scripts) |
| **Active Documentation Files** | 2 (PROJECT_MASTER_LOG.md + README.md) |
| **Consolidation Method** | Full content merge + deduplication |
| **Archive Location** | `/docs/archive/` |
| **Archive Safety** | All files preserved (no deletions) |
| **Search Location** | `/docs/PROJECT_MASTER_LOG.md` (Ctrl+F) |

---

## Questions?

If you're looking for information about:
- **Order logging**: See Section 2 in `/docs/PROJECT_MASTER_LOG.md`
- **Error handling**: See Section 6 in `/docs/PROJECT_MASTER_LOG.md`
- **System architecture**: See Section 1 in `/docs/PROJECT_MASTER_LOG.md`
- **Historical notes**: Check this archive or git history
- **Implementation details**: See Section 2 in `/docs/PROJECT_MASTER_LOG.md`

**Start with the master file.** The archive is here for historical reference only.

---

**Archive Created**: March 21, 2026  
**Archive Status**: Complete and stable  
**Last Updated**: March 21, 2026
