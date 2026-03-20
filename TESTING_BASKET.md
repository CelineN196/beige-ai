# 🧪 Basket Testing Guide

**Purpose**: Verify all basket features work correctly  
**Time**: ~10 minutes  
**Status**: Ready to test

---

## Pre-Test Checklist

- [ ] Virtual environment activated: `source .venv/bin/activate`
- [ ] Streamlit installed: `pip install streamlit`
- [ ] No syntax errors: `python -m py_compile frontend/beige_ai_app.py`
- [ ] Database initialized: `beige_retail.db` exists
- [ ] Port 8501 available (or use `--server.port 8502`)

---

## Test Environment Setup

```bash
cd "/Users/queenceline/Downloads/Beige AI"
source .venv/bin/activate

# Clear cache (optional, for clean slate)
streamlit cache clear

# Start app
streamlit run frontend/beige_ai_app.py
```

Browser will open at: `http://localhost:8501`

---

## Test Suite 1: Basket Visibility

### Test 1.1: Basket Available on Load
```
STEP: Load the app
EXPECTED: Sidebar shows "🛍️ Your Selection" with "Your basket is empty" message
ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 1.2: Basket Title Styling
```
STEP: Check sidebar basket header
EXPECTED: 
  - Large elegant "🛍️ Your Selection" title
  - Taupe border above and below
  - Clear visual separation from other content
ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 1.3: Empty State Message
```
STEP: Look at empty basket
EXPECTED: 
  - Message: "Your basket is empty"
  - Subtext: "Generate a recommendation above to get started"
  - Styled with flower emoji and centered layout
ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

---

## Test Suite 2: Adding Items

### Test 2.1: Add from Top Recommendation
```
STEP 1: Scroll to "Your Preferences" section
STEP 2: Set mood to "Happy"
STEP 3: Click "Generate Cake Recommendation"
STEP 4: Wait for recommendations to load
STEP 5: Click first "✓ Add to Basket • $X.XX" button

EXPECTED:
  - Toast notification appears: "✅ [Cake Name] added to basket!"
  - Basket section updates with item
  - Shows: "[Cake Name]  $X.XX  [✕]"
  - Item count shows "1 item in your basket"
  - Subtotal displays: "Subtotal: $X.XX"

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 2.2: Add Item from Menu
```
STEP 1: Scroll to "🔍 Browse Full Menu" section
STEP 2: Click dropdown to select a cake
STEP 3: Choose a cake different from recommendations
STEP 4: Click "➕ Add" button

EXPECTED:
  - Toast notification appears
  - Item added to basket
  - Item count now shows "2 items in your basket"
  - Subtotal recalculates (should be $X.XX + $Y.YY)

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 2.3: Add Third Item
```
STEP 1: From same menu dropdown, select another cake
STEP 2: Click "➕ Add" again

EXPECTED:
  - Toast shows new item
  - Item count shows "3 items in your basket"
  - Three items visible in basket
  - Subtotal reflects all three prices

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

---

## Test Suite 3: Basket Management

### Test 3.1: Item Display Format
```
STEP: Look at each item in basket
EXPECTED FORMAT:
  [Cake Name]
  $X.XX
  [✕]

ACTUAL FORMAT: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 3.2: Remove Item (First Item)
```
STEP 1: Click ✕ button next to first item
STEP 2: Page reloads

EXPECTED:
  - First item removed
  - Item count shows "2 items in your basket"
  - Subtotal recalculates (should be item 2 + item 3)
  - Remaining items still visible

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 3.3: Remove Item (Middle Item)
```
STEP: Click ✕ on what is now the "first" (formerly second) item

EXPECTED:
  - That item removed
  - Item count shows "1 item in your basket"
  - Only one item remains
  - Total updates correctly

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 3.4: Remove Last Item
```
STEP: Click ✕ on remaining item

EXPECTED:
  - Item removed
  - Basket returns to empty state
  - Message shows: "Your basket is empty"
  - Item count gone

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

---

## Test Suite 4: Total Calculation

### Test 4.1: Single Item Total
```
STEP: Add one item (e.g., Chocolate Truffle at $8.50)

EXPECTED: Subtotal: $8.50
ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 4.2: Multiple Item Total
```
STEP: Add 3 different cakes with prices:
  - Chocolate Truffle: $8.50
  - Matcha Cloud: $8.50
  - Berry Chantilly: $8.50

EXPECTED: Subtotal: $25.50
ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 4.3: Total Updates on Remove
```
STEP 1: Have 3 items ($25.50 total)
STEP 2: Remove one item ($8.50)

EXPECTED: Subtotal: $17.00
ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

---

## Test Suite 5: Checkout Process

### Test 5.1: Checkout Button Visible
```
STEP: Check sidebar basket area

EXPECTED: 
  - "💳 Complete Purchase" button visible
  - Primary button type (distinct color)
  - Full width of sidebar
  - "← Continue Shopping" button below it

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 5.2: Trigger Checkout (with items)
```
STEP 1: Have at least 1 item in basket
STEP 2: Click "💳 Complete Purchase"

EXPECTED:
  - Scroll to "💳 Processing Your Order" section
  - Order summary expands showing:
    • All items with checkmarks
    • Each item's price
    • Total amount
  - Two buttons visible: "✓ Confirm & Complete" and "✕ Cancel"

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 5.3: Confirm Purchase
```
STEP 1: Order summary showing (from Test 5.2)
STEP 2: Click "✓ Confirm & Complete"

EXPECTED:
  - Processing message appears
  - Confirmation message: "The ledger has been updated."
  - Subtext: "Enjoy your moment of solace."
  - Balloons animation appears
  - Basket automatically clears
  - "Your basket is empty" message returns

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 5.4: Cancel Checkout
```
STEP 1: Have items in basket
STEP 2: Click "💳 Complete Purchase"
STEP 3: Click "✕ Cancel"

EXPECTED:
  - Return to main page
  - Order summary disappears
  - Basket still shows items (NOT cleared)
  - Items ready to checkout again

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 5.5: Checkout with Empty Basket
```
STEP 1: Remove all items from basket
STEP 2: Try to click "💳 Complete Purchase"

EXPECTED:
  - Warning message: "Your basket is empty"
  - Option to "← Back to Shopping"
  - Cannot proceed with checkout

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

---

## Test Suite 6: Styling & UX

### Test 6.1: Beige Aesthetic
```
STEP: Examine entire basket UI

EXPECTED:
  - Cream background (#F5F3F0) or similar light color
  - Taupe accents (#BDB2A7) in borders
  - No bright colors
  - Elegant, minimalist appearance
  - Readable text with good contrast

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 6.2: Toast Notifications
```
STEP: Add an item and watch for notification

EXPECTED:
  - Small notification appears (typically bottom right)
  - Shows: "✅ [Cake Name] added to basket! 💰 $X.XX"
  - Appears for ~3 seconds then fades
  - Doesn't block page content

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 6.3: Button Styling
```
STEP: Look at all basket buttons

EXPECTED:
  - "Add to Basket" buttons: Secondary style
  - "Complete Purchase" button: Primary style (prominent)
  - "Remove" (✕) buttons: Small, inline
  - Hover effects work (color changes)
  - Buttons full width in sidebar

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 6.4: Responsive Layout
```
STEP 1: Open browser dev tools (F12)
STEP 2: Toggle device toolbar
STEP 3: Test on tablet size (768px width)
STEP 4: Test on mobile size (375px width)

EXPECTED:
  - Basket still visible
  - Items readable
  - Buttons tapable
  - Total visible
  - No text overflow

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

---

## Test Suite 7: Edge Cases

### Test 7.1: Add Same Item Twice
```
STEP 1: Add "Chocolate Truffle" from recommendations
STEP 2: Add "Chocolate Truffle" from menu

EXPECTED:
  - Both items appear in basket (not combined)
  - Shows as two separate line items
  - Total reflects both: probably $17.00

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 7.2: Page Refresh (Session Persistence)
```
STEP 1: Add 2 items to basket
STEP 2: Press F5 to refresh page
STEP 3: Wait for page to load

EXPECTED:
  - Both items still in basket
  - Totals preserved
  - Basket state recovered

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test 7.3: Browser Back Button
```
STEP 1: Add items, complete checkout
STEP 2: Click browser back button
STEP 3: Navigate forward

EXPECTED:
  - Basket should be cleared (purchase completed)
  - Can add new items
  - No "double charge" issues

ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

---

## Performance Tests

### Test P1: Add Item Speed
```
STEP: Click "Add to Basket" button
MEASURE: Time until item appears in basket

EXPECTED: <1 second (instant feel)
ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

### Test P2: Total Calculation Speed  
```
STEP: Remove an item with 10+ items in basket
MEASURE: Time until total updates

EXPECTED: <500ms (appears instant)
ACTUAL: [_______________]
RESULT: ☐ PASS ☐ FAIL
```

---

## Summary Report

```
Total Tests: _____ / _____
Passed: ☐
Failed: ☐
Blocked: ☐

Overall Status: 
☐ PASS (All tests passed)
☐ PASS WITH MINOR ISSUES (Most passed, minor cosmetic issues)
☐ FAIL (Critical issues found)

Critical Issues Found:
[_______________________________________________________________]

Minor Issues:
[_______________________________________________________________]

Recommendations:
[_______________________________________________________________]

Tested By: ____________________
Date: ____________________
Time: ____________________
```

---

## Quick Reference: Expected Values

```
Cake Menu Prices:
- Chocolate Truffle: $8.50
- Matcha Cloud: $8.50
- Lemon Olive Oil: $9.00
- Berry Chantilly: $8.50
- Tiramisu Silk: $9.00
- Black Sesame Velvet: $9.50
- Pistachio Rose: $9.50
- Vanilla Almond: $8.00

Common Total Calculations:
- 1x Chocolate Truffle = $8.50
- 2x Chocolate Truffle = $17.00
- 1x Lemon Olive Oil + 1x Black Sesame Velvet = $18.50
- 1 of each = $69.50
```

---

## If Tests Fail

### Step 1: Check Syntax
```bash
python -m py_compile frontend/beige_ai_app.py
```

### Step 2: Check Database
```bash
ls -la beige_retail.db
```

### Step 3: Check Imports
```bash
cd frontend && python -c "from checkout_handler import process_checkout; print('✅ Imports work')"
```

### Step 4: Check Terminal Output
Look for error messages in the terminal where Streamlit is running.

### Step 5: Check Browser Console
Press F12, click "Console" tab, look for JavaScript errors.

---

## Getting Help

If tests fail:

1. Check [BASKET_UI_FIX.md](BASKET_UI_FIX.md) for technical details
2. Check [BASKET_USER_GUIDE.md](BASKET_USER_GUIDE.md) for user perspective
3. Review terminal output for Python errors
4. Review browser console (F12) for JavaScript errors

---

**Version**: 1.0  
**Last Updated**: March 15, 2026  
**Status**: Ready to Test ✅
