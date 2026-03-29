# 🎯 RECOMMENDATION MATCH TRACKING

## Overview

The checkout logging system now captures whether the user's purchase matches the AI recommendation. This field enables:
- ✅ Tracking recommendation accuracy in real checkout behavior
- ✅ A/B testing different recommendation strategies
- ✅ Analyzing which recommendation types lead to conversions
- ✅ Identifying user override patterns (when user ignores recommendations)

---

## Data Model

### New Field: `recommendation_match`

**Location:** `feedback_logs` table in Supabase

**Type:** `text` (default: `'unknown'`)

**Valid Values:**
- `"match"` - User purchased the recommended item
- `"did_not_match"` - User purchased something different
- `"unknown"` - Cannot determine (missing data)

### Example Records

#### ✅ Match Case
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "recommended_cake": "Chocolate Cake",
  "user_input": {
    "order_id": "order_12345",
    "items_purchased": "Chocolate Cake, Vanilla Cake",
    "match_result": "Match"
  },
  "recommendation_match": "match",
  "context": {
    "checkout": true
  }
}
```

#### ❌ Did Not Match Case
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "recommended_cake": "Chocolate Cake",
  "user_input": {
    "order_id": "order_67890",
    "items_purchased": "Strawberry Cake",
    "match_result": "Not Quite"
  },
  "recommendation_match": "did_not_match",
  "context": {
    "checkout": true
  }
}
```

---

## Implementation Details

### 1. Computation Logic

The `recommendation_match` is computed by comparing:
1. **Recommended cake**: Top-1 recommendation from the ML model
2. **Purchased items**: Items in the user's cart at checkout

**Algorithm:**
```python
def _compute_recommendation_match(recommended_cake, purchased_items):
    # 1. Normalize recommended cake
    if not recommended_cake or recommended_cake == "unknown":
        return "unknown"
    
    rec_normalized = str(recommended_cake).strip().lower()
    
    # 2. Handle empty purchases
    if not purchased_items:
        return "unknown"
    
    # 3. Extract cake names from purchased items
    purchased_names = [
        item.get('name', '').strip().lower()  # or str(item).lower()
        for item in purchased_items
    ]
    
    # 4. Check if recommended is in purchased
    if rec_normalized in purchased_names:
        return "match"
    else:
        return "did_not_match"
```

### 2. Where It's Computed

**File:** `backend/integrations/supabase_integration.py`

**Function:** `log_checkout_order()`

**Execution Point:**
```python
def log_checkout_order(
    order_id: str,
    items_purchased: str,
    ai_recommendation: Any,
    match_result: str,
    total_value: Optional[float] = None,
    purchased_items: Optional[list] = None,  # ← New parameter
) -> bool:
    # Convert recommendation to string
    cake_str = _safe_stringify_recommendation(ai_recommendation)
    
    # ✨ NEW: Compute recommendation_match
    recommendation_match = _compute_recommendation_match(
        recommended_cake=cake_str,
        purchased_items=purchased_items or [],
    )
    
    # Pass to Supabase
    log_feedback(
        ...,
        recommendation_match=recommendation_match,
        ...
    )
```

### 3. Frontend Integration

**File:** `frontend/beige_ai_app.py` (checkout section, line ~1540)

**Updated Call:**
```python
supabase_logged = log_checkout_order(
    order_id=order_id,
    items_purchased=items_purchased,
    ai_recommendation=st.session_state.ai_result,
    match_result=result,
    total_value=subtotal,
    purchased_items=st.session_state.cart,  # ← New: pass cart items
)
```

---

## Data Flow

```
User Checkout
  ↓
st.session_state.cart = [
  {"name": "Chocolate Cake", "price": 25.00},
  {"name": "Vanilla Cake", "price": 20.00}
]
st.session_state.ai_result = {
  "top_3_cakes": ["Chocolate Cake", ...],
  ...
}
  ↓
Frontend calls log_checkout_order(
  purchased_items=st.session_state.cart,
  ai_recommendation=st.session_state.ai_result,
)
  ↓
Backend converts:
  ai_recommendation (dict) → "Chocolate Cake"
  cart items (list of dicts) → ["chocolate cake", "vanilla cake"]
  ↓
Comparison:
  "chocolate cake" in ["chocolate cake", "vanilla cake"] → ✅ match
  ↓
recommendation_match = "match"
  ↓
Supabase INSERT:
  recommendation_match = "match"
```

---

## Test Cases

Run the test script to verify all scenarios:

```bash
python test_recommendation_match.py
```

**Tested Scenarios:**
1. ✅ Perfect match (single item matches recommendation)
2. ✅ No match (single item doesn't match)
3. ✅ Partial match (one of multiple items matches recommendation)
4. ✅ No match in multi-item (recommendation not purchased)
5. ✅ Case insensitive comparison
6. ✅ Whitespace trimming
7. ✅ Missing recommendation → "unknown"
8. ✅ Empty purchase list → "unknown"
9. ✅ None values handling
10. ✅ List of strings (alternative format)
11. ✅ Empty string recommendation
12. ✅ None recommendation

---

## Schema Update

Added to `backend/supabase_schema.sql`:

```sql
-- User Input & Recommendation
user_input JSONB NOT NULL,
recommended_cake TEXT NOT NULL,
recommended_cakes_top_3 TEXT[] DEFAULT NULL,
recommendation_match TEXT DEFAULT 'unknown',  -- ← NEW FIELD
```

**Applied to:** `feedback_logs` table

**Migration Required:** Run this SQL in Supabase:
```sql
ALTER TABLE feedback_logs 
ADD COLUMN recommendation_match TEXT DEFAULT 'unknown';
```

---

## Analytics Enabled

With this field, you can now answer:

### 1. Recommendation Accuracy
```sql
SELECT 
    recommendation_match,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM feedback_logs WHERE feedback_logs.context->>'checkout' = 'true'), 2) as percentage
FROM feedback_logs
WHERE context->>'checkout' = 'true'
GROUP BY recommendation_match;
```

**Result Example:**
```
recommendation_match | count | percentage
match                | 152   | 68.45%
did_not_match        | 70    | 31.53%
unknown              | 0     | 0.00%
```

### 2. Model Version Performance
```sql
SELECT 
    model_version,
    recommendation_match,
    COUNT(*) as count,
    ROUND(AVG(CAST(user_feedback AS FLOAT)), 2) as avg_rating
FROM feedback_logs
WHERE context->>'checkout' = 'true'
GROUP BY model_version, recommendation_match
ORDER BY model_version, recommendation_match;
```

### 3. User Override Patterns
```sql
SELECT 
    recommendation_match,
    ROUND(AVG(CAST(user_feedback AS FLOAT)), 2) as avg_rating,
    COUNT(*) as count
FROM feedback_logs
WHERE context->>'checkout' = 'true' AND user_feedback IS NOT NULL
GROUP BY recommendation_match;
```

---

## Future Enhancements

The foundation is now in place for:

1. **Match Score (0-1)**: Similarity score between recommended and purchased
   - Exact match: 1.0
   - Partial match (substring): 0.5
   - No match: 0.0

2. **Confidence Weighting**: Weight matches by recommendation confidence
   - High confidence matches count more
   - User overrides of low confidence recommendations are expected

3. **User Override Reason**: Track why users ignored recommendations
   - "Out of stock"
   - "Preferred different flavor"
   - "Price consideration"

4. **Temporal Analysis**: Track when recommendations are most accurate
   - Time of day
   - Weather conditions
   - Mood impact

---

## Backward Compatibility

The field defaults to `'unknown'` if not provided, so:
- ✅ Old code continues to work
- ✅ Retroactive logging won't break
- ✅ No required migrations (optional enhancement)

---

## Verification Checklist

- [x] Schema updated with `recommendation_match` column
- [x] `FeedbackLog` dataclass includes field
- [x] `log_feedback()` accepts `recommendation_match` parameter
- [x] `log_checkout_order()` computes value
- [x] Frontend passes purchased items list
- [x] Test script validates logic
- [x] Default value: `"unknown"` (non-null safe)
- [x] Case-insensitive comparison
- [x] Whitespace handling
- [x] Handles all edge cases (None, empty, missing)

---

## Deployment Notes

1. **Supabase Migration**: Run the ALTER TABLE statement above
2. **Backend Deploy**: Deploy updated supabase_logger.py and supabase_integration.py
3. **Frontend Deploy**: Deploy updated beige_ai_app.py
4. **Verify**: Run test_recommendation_match.py
5. **Monitor**: Check Supabase logs for any insert failures

---

## Usage Example

In your analytics dashboard, you can now display:

```python
# Python example
from supabase import create_client

supabase = create_client(url, key)

# Get recommendation accuracy by model version
result = supabase.table("feedback_logs") \
    .select("model_version,recommendation_match") \
    .eq("context->checkout", "true") \
    .limit(1000) \
    .execute()

# Compute accuracy
data = result.data
model_stats = {}
for record in data:
    model = record["model_version"]
    match = record["recommendation_match"]
    
    if model not in model_stats:
        model_stats[model] = {"match": 0, "did_not_match": 0, "unknown": 0}
    
    model_stats[model][match] += 1

# Display
for model, stats in model_stats.items():
    total = sum(stats.values())
    accuracy = (stats["match"] / total * 100) if total > 0 else 0
    print(f"{model}: {accuracy:.1f}% match rate")
```

---

## Summary

✅ **What you have:**
- Automatic detection of recommendation matches
- Granular analytics on user behavior vs. AI recommendations
- Foundation for A/B testing different recommendation strategies
- Non-null safe implementation (always a valid string)

✅ **What you can do with it:**
- Measure recommendation accuracy in real checkout behavior
- Identify which recommendation types convert best
- Analyze user override patterns
- Improve models based on actual purchase data
- Feed back real outcomes to the ML system

✅ **What's required:**
- Database migration (one ALTER TABLE statement)
- Test verification (test_recommendation_match.py)
- Monitor first few checkouts to ensure data quality
