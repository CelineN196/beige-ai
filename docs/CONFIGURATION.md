# Beige.AI Menu Configuration Guide

## Overview

The Beige.AI project uses a **centralized menu configuration system** to manage the cake menu across all modules. This allows you to update the product catalog in one place without modifying multiple scripts.

---

## File Structure

### `menu_config.py` - Configuration Module

This is the **single source of truth** for the cake menu. Located in the project root directory.

#### Key Components:

1. **`CAKE_MENU`** - List of all available cake categories
   ```python
   CAKE_MENU = [
       "Dark Chocolate Sea Salt Cake",
       "Matcha Zen Cake",
       "Citrus Cloud Cake",
       "Berry Garden Cake",
       "Silk Cheesecake",
       "Earthy Wellness Cake",
       "Café Tiramisu",
       "Korean Sesame Mini Bread"
   ]
   ```

2. **`CAKE_CATEGORIES`** - Detailed properties for each cake (optional, for Phase 3+)
   ```python
   CAKE_CATEGORIES = {
       "Dark Chocolate Sea Salt Cake": {
           "category": "Indulgent",
           "flavor_profile": "Rich & Savory",
           "sweetness_level": 8,
           "health_score": 2
       },
       # ... more cakes
   }
   ```

3. **Helper Functions**:
   - `get_cake_menu()` - Returns the list of cakes
   - `get_cake_count()` - Returns total number of cakes
   - `is_valid_cake(cake_name)` - Validates if a cake exists in menu
   - `get_cake_properties(cake_name)` - Retrieves cake properties
   - `validate_menu()` - Ensures all cakes have properties defined

---

## How Scripts Use the Configuration

### 1. Data Generation Script (`beige_ai_data_generation.py`)

**Import:**
```python
from menu_config import CAKE_MENU
```

**Usage:**
```python
# Use CAKE_MENU for rule-based labeling
cake_categories_menu = CAKE_MENU

# In assign_cake_category function:
scores = {cake: 1.0 for cake in cake_categories_menu}
scores['Matcha Zen Cake'] *= 1.6  # Rule application
```

**Impact:** Generates synthetic dataset with cake_category values from CAKE_MENU

### 2. Analytics Script (`beige_ai_analytics.py`)

**Import:**
```python
from menu_config import CAKE_MENU
```

**Usage:**
```python
# Validate that data matches configuration
unique_cakes_in_data = set(df['cake_category'].unique())
configured_cakes = set(CAKE_MENU)

if unique_cakes_in_data == configured_cakes:
    print("✓ Cake categories match configuration")
```

**Impact:** Ensures consistency between data and configuration

---

## How to Update the Menu

### Adding a New Cake

1. **Edit `menu_config.py`:**
   ```python
   CAKE_MENU = [
       # ... existing cakes ...
       "New Cake Name"  # Add here
   ]
   ```

2. **Add properties (optional, for future use):**
   ```python
   CAKE_CATEGORIES = {
       # ... existing cakes ...
       "New Cake Name": {
           "category": "Category",
           "flavor_profile": "Description",
           "sweetness_level": 7,
           "health_score": 5
       }
   }
   ```

3. **Update domain knowledge rules (if needed):**
   - Edit `assign_cake_category()` in `beige_ai_data_generation.py`
   - Add scoring logic for the new cake

4. **Regenerate dataset:**
   ```bash
   python beige_ai_data_generation.py
   ```

5. **Rerun analytics:**
   ```bash
   python beige_ai_analytics.py
   ```

---

### Removing a Cake

1. **Edit `menu_config.py`:**
   - Remove from `CAKE_MENU`
   - Remove from `CAKE_CATEGORIES`

2. **Update domain knowledge rules:**
   - Remove scoring logic from `assign_cake_category()`

3. **Regenerate dataset and analytics**

---

### Renaming a Cake

1. **Edit `menu_config.py`:**
   - Update name in `CAKE_MENU`
   - Update key in `CAKE_CATEGORIES`

2. **Update domain knowledge rules:**
   - Find all references in `beige_ai_data_generation.py`
   - Update scoring logic

3. **Regenerate dataset and analytics**

---

## Validation & Error Handling

### Automatic Validation

When `menu_config.py` is imported, it automatically validates that all cakes in `CAKE_MENU` have properties defined in `CAKE_CATEGORIES`:

```python
_is_valid, _missing = validate_menu()
if not _is_valid:
    print(f"⚠️ Warning: Missing properties for cakes: {_missing}")
```

### Data Validation in Analytics

The analytics script checks that dataset values match the configuration:

```
✓ Cake categories match configuration (menu_config.py)
```

---

## Current Menu (8 Cakes)

| # | Cake Name | Sweetness | Health | Category |
|----|-----------|-----------|--------|----------|
| 1 | Dark Chocolate Sea Salt Cake | 8 | 2 | Indulgent |
| 2 | Matcha Zen Cake | 6 | 8 | Energizing |
| 3 | Citrus Cloud Cake | 7 | 7 | Refreshing |
| 4 | Berry Garden Cake | 7 | 8 | Fruity |
| 5 | Silk Cheesecake | 9 | 3 | Indulgent |
| 6 | Earthy Wellness Cake | 4 | 9 | Health-Conscious |
| 7 | Café Tiramisu | 7 | 5 | Energizing |
| 8 | Korean Sesame Mini Bread | 2 | 6 | Savory |

---

## File Dependencies

```
menu_config.py
├── beige_ai_data_generation.py (imports CAKE_MENU)
├── beige_ai_analytics.py (imports CAKE_MENU)
└── (Future) Phase 3: Classification & Recommendation (will import)
```

---

## Best Practices

1. **Always update `menu_config.py` first** before making changes to individual scripts
2. **Maintain consistent cake names** across the configuration
3. **Keep CAKE_MENU and CAKE_CATEGORIES in sync** to avoid validation warnings
4. **Test after changes** by running:
   ```bash
   python -c "from menu_config import validate_menu; print(validate_menu())"
   ```
5. **Regenerate the dataset** whenever the menu changes
6. **Re-run analytics** to update cluster profiles and association rules

---

## Summary

The centralized menu configuration provides:
- ✅ **Single source of truth** for cake menu
- ✅ **Easy updates** without code modification
- ✅ **Consistency validation** across modules
- ✅ **Scalability** for adding new cakes
- ✅ **Modularity** for future features

For questions or issues, refer to the inline documentation in `menu_config.py`.
