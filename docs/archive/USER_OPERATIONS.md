# Beige.AI User Operations Guide

For café operators, managers, and staff running the Beige.AI system.

---

## Table of Contents

1. [Setup & Installation](#setup--installation)
2. [Running the Application](#running-the-application)
3. [Daily Operations Workflow](#daily-operations-workflow)
4. [Customer Interaction Guide](#customer-interaction-guide)
5. [Admin Dashboard](#admin-dashboard)
6. [Styling & Brand Experience](#styling--brand-experience)
7. [Customization](#customization)
8. [Quick Reference](#quick-reference)

---

## Setup & Installation

### Prerequisites

- macOS, Windows, or Linux
- Python 3.9 or higher
- 500MB free disk space
- Internet connection (first-time only)

### Installation Steps

#### Step 1: Clone/Download Project

```bash
# Navigate to project directory
cd /Users/queenceline/Downloads/"Beige AI"
```

#### Step 2: Create Virtual Environment

```bash
# Create isolated Python environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate    # macOS/Linux
# OR
.venv\Scripts\activate       # Windows
```

#### Step 3: Install Dependencies

```bash
# Install required packages (8 total)
pip install -r requirements.txt
```

**Packages installed:**
- streamlit (1.28+) — Frontend framework
- pandas — Data manipulation
- numpy — Numerical computing
- scikit-learn — ML models
- joblib — Model serialization
- google-generativeai — Gemini API
- matplotlib — Charting
- python-dotenv — Environment config

#### Step 4: Set Environment Variables

```bash
# Create .env file in project root
echo "GEMINI_API_KEY=your-api-key-here" > .env

# Or set directly in terminal
export GEMINI_API_KEY="your-api-key-here"
```

**Getting your Gemini API key:**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API key"
3. Copy the key
4. Paste into `.env` or environment variable

#### Step 5: Verify Installation

```bash
# Test Python imports
python3 -c "
import streamlit
import pandas
import numpy
import sklearn
import joblib
import google.generativeai as genai
print('✅ All packages installed successfully')
"
```

---

## Running the Application

### Quick Start (Recommended)

```bash
# From project root
python main.py

# Opens automatically at http://localhost:8501
```

**What happens:**
1. Activates virtual environment
2. Loads ML model & preprocessor
3. Initializes SQLite database
4. Starts Streamlit dev server
5. Opens browser to localhost:8501

### Manual Start

```bash
# Activate venv first
source .venv/bin/activate

# Run Streamlit directly
streamlit run frontend/beige_ai_app.py

# Customize port if needed
streamlit run frontend/beige_ai_app.py --server.port 8502
```

### Stopping the Application

```bash
# Press Ctrl+C in terminal
# Or close the browser (server keeps running until Ctrl+C)
```

### Deployment Options

**Local Machine:**
```bash
# Simple, for development & testing
python main.py
```

**Streamlit Cloud (Free Tier):**
```bash
# 1. Push code to GitHub
# 2. Go to share.streamlit.io
# 3. Deploy from repo
# 4. Share public URL instantly
```

**Docker (Production):**
```bash
# Build image
docker build -t beige-ai .

# Run container
docker run -p 8501:8501 \
  -e GEMINI_API_KEY=your-key \
  beige-ai
```

---

## Daily Operations Workflow

### For Café Staff

#### Morning Startup
1. **Power on computer & open terminal**
2. **Run:** `python main.py`
3. **Wait:** ~30 seconds for model load
4. **Verify:** Blue banner "Beige.AI" appears at http://localhost:8501
5. **Test:** Try one recommendation (test all inputs)

#### Customer Interaction
1. **Invite customer:** "Let me show you something special..."
2. **Customer selects mood:** Happy, Stressed, Tired, Lonely, Celebratory
3. **Customer selects weather:** Sunny, Rainy, Cloudy, Snowy
4. **Click "Get Recommendations"**
5. **App displays top 3 cakes with confidence & explanations**
6. **Customer gives feedback:** Thumbs up, not sure, or thumbs down
7. **Customer may add to cart & checkout or browse**

#### Feedback Loop
- **Positive feedback (👍):** Note the mood/weather combination for training notes
- **Negative feedback (👎):** Update recommendations in future (model can be retrained)

#### Closing Shift
1. **View analytics dashboard:** See day's sales, top items
2. **Note inventory:** Which cakes selling well vs. slowly
3. **Export data (optional):** CSV of today's transactions
4. **Shutdown:** `Ctrl+C` in terminal
5. **Close browser**

### For Café Manager

#### Weekly Tasks
1. **Check analytics dashboard** (in app)
   - Total revenue (7-day & 30-day)
   - Top-selling cakes (adjust procurement)
   - Mood/weather patterns (adjust advertising)
   - Inventory levels (reorder if <20% stock)

2. **Review customer feedback**
   - Export feedback data
   - Identify recommendations causing dissatisfaction
   - Plan model improvements

3. **Update menu prices** (if needed)
   - Edit `backend/menu_config.py`
   - Update database via admin panel
   - Changes live immediately

#### Monthly Tasks
1. **Model retraining** (optional but recommended)
   - Collect 200+ new customer interactions
   - Run `backend/training/beige_ai_phase3_training.py`
   - Validate accuracy on test set
   - Replace `backend/models/cake_model.joblib`
   - Restart app to load new model

2. **Feature analysis**
   - Which moods → which cakes? (identify patterns)
   - Seasonal adjustments needed?
   - New input features to add (allergies, diet)?

3. **Performance review**
   - Expansion metrics: customer satisfaction, repeat rate
   - Cost tracking: API costs, infrastructure
   - Competitive positioning

---

## Customer Interaction Guide

### The Customer Journey

#### Phase 1: Welcome
**Staff says:**  
"We use AI to match you with the perfect cake based on how you're feeling. Let's find your ideal match!"

**Tech:** Streamlit loads, hero section + input form visible

#### Phase 2: Preferences
**Customer provides:**
- Current mood (select from dropdown or tell staff)
- Weather outside (auto-detected or manual)
- Optional: temperature, humidity, taste preferences

**Tips for staff:**
- If customer indecisive: "Think about your ideal moment right now"
- If mood unclear: "Energized or peaceful? Indulgent or light?"

#### Phase 3: Recommendation
**System displays:** Top 3 cakes with:
- Ranking (🥇 🥈 🥉)
- Name with emoji icon
- Confidence % (how well it matches)
- Poetic 1–2 sentence explanation
- Category (Indulgent, Energizing, etc.)

**Staff narration:**  
"The AI recommends [#1 cake] as your best match because [explanation]. The other two options are [#2] and [#3] if you want alternatives."

#### Phase 4: Feedback
**Customer reacts:**
- 👍 "Love it!" → Goes to cart automatically
- 🤔 "Not sure" → System suggests adjusting mood input
- 👎 "Not interested" → System learns for future

**Staff guidance:**  
"Your feedback helps us get better. What would you prefer instead?"

#### Phase 5: Order & Checkout
**Customer adds to cart:**
- Quantity selection
- Specify any customizations
- Choose delivery method (pickup/delivery)
- Proceed to payment

**Optional:** Share email for loyalty program / receipt

#### Phase 6: Handoff
**System generates:**
- Order confirmation with order number
- Receipt (can print or email)
- Estimated ready time
- Special instructions for kitchen

---

## Admin Dashboard

### Accessing the Dashboard

**In Beige.AI app:**
1. Click menu (≡) in top-left
2. Select "Analytics Dashboard"
3. View real-time metrics

### Dashboard Sections

#### Sales Summary
- **Today's Revenue:** Total sales amount
- **Orders Count:** Number of transactions
- **Average Order Value:** Revenue ÷ orders

#### Top Performers (7-day)
- **Best-selling cake:** Item & quantity
- **Revenue leader:** Highest revenue item
- **Customer favorite:** Highest positive feedback %

#### Trend Charts
- **Daily revenue:** 7 or 30-day trend
- **Cake popularity:** Bar chart of sales by item
- **Mood distribution:** Which moods customers selected

#### Inventory Status
- **Stock levels:** Current qty for each cake
- **Low stock alerts:** Items below 20%
- **Reorder needed:** Recommended purchases

#### Customer Insights
- **Repeat customers:** From email data
- **Satisfaction:** Thumps up/down ratio
- **Peak hours:** When customers most active

### Exporting Data

```bash
# Data is stored in SQLite database at:
# $(PROJECT_ROOT)/beige_retail.db

# To export to CSV:
sqlite3 beige_retail.db ".headers on" ".mode csv" \
  "SELECT * FROM sales" > sales_export.csv

# Then open in Excel/Sheets for analysis
```

---

## Styling & Brand Experience

### Visual Design System

#### Color Palette

```
Primary: Saddle Brown (#8B4513)
└─ Used for buttons, headlines, accents

Background: Beige (#F5F5DC)
└─ Main page background

Sidebar: Soft Cream (#FDF5E6)
└─ Sidebar background, input fields

Text: Dark Coffee (#3E2723)
└─ Body text, high contrast

Accent: Warm Beige (#D4A574)
└─ Secondary highlights

Rankings:
├─ 1st Place: Gold (#FFD700)
├─ 2nd Place: Silver (#C0C0C0)
└─ 3rd Place: Bronze (#CD7F32)
```

#### Typography

- **Headlines:** Georgia serif, 2.5–3.2em, bold
- **Body:** Georgia serif, 1em, regular
- **Buttons:** Georgia serif, 1.1em, bold
- **Labels:** Georgia serif, 0.9em, semi-bold

#### Components

**Buttons:**
- Saddle brown background
- Rounded corners (12px)
- Hover: lighter color + subtle lift effect
- Active: darker on click

**Cards:**
- White background with 1px border
- Rounded corners (15px)
- Subtle shadow on hover
- Medal emoji (🥇🥈🥉) for ranking

**Input Fields:**
- Border: light gray
- Focus: saddle brown outline
- Padding: 10px
- Font: Georgia serif

### Cake Emoji System

Each cake has a unique emoji for instant recognition:

| Cake | Emoji |
|------|-------|
| Dark Chocolate Sea Salt | 🍫 |
| Matcha Zen | 🍵 |
| Citrus Cloud | 🍋 |
| Berry Garden | 🍓 |
| Silk Cheesecake | 🧁 |
| Earthy Wellness | 🥬 |
| Café Tiramisu | ☕ |
| Korean Sesame | 🥐 |

### Brand Voice

**Tone:** Minimalist, premium, intuitive

**In copy:**
- Short sentences (max 15 words)
- Active voice
- Specific over generic
- Warm but not casual
- Example: "The earthy matcha grounds your contemplative mood while sweetness lifts you gently."

**In error messages:**
- Friendly, never technical
- Example: "The recommendation engine took a breath. Try again in 10 seconds."
- Fallback gracefully to default explanation

---

## Customization

### Adding a New Cake

#### Step 1: Update Menu Config

**File:** `backend/menu_config.py`

```python
CAKES = [
    # ... existing cakes ...
    {
        "name": "Lavender Dreams",
        "category": "Botanical",
        "flavor": "floral, subtle, delicate",
        "sweetness": 6,
        "health_score": 7,
        "emoji": "💜"
    }
]
```

#### Step 2: Update Database

```python
# In terminal from project root
python3 << EOF
import sqlite3
from pathlib import Path

db_path = Path("beige_retail.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute(
    "INSERT INTO inventory (cake_name, category, price, quantity_available) VALUES (?, ?, ?, ?)",
    ("Lavender Dreams", "Botanical", 8.99, 50)
)
conn.commit()
conn.close()
print("✅ New cake added to inventory")
EOF
```

#### Step 3: Add Product Image

Place image at: `assets/images/cakes/lavender_dreams.png` (500×400px PNG)

#### Step 4: Retrain Model (Recommended)

```bash
cd backend/training
python beige_ai_phase3_training.py
```

This includes the new cake in recommendations.

### Changing Prices

**Method 1: Via admin panel (when built)**  
Click settings → edit prices → save

**Method 2: Direct database**

```python
import sqlite3
from pathlib import Path

db_path = Path("beige_retail.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute(
    "UPDATE inventory SET price = ? WHERE cake_name = ?",
    (9.99, "Matcha Zen")
)
conn.commit()
conn.close()
print("✅ Price updated")
```

### Changing Typography

**File:** `frontend/.streamlit/config.toml`

```toml
[theme]
font = "serif"  # Change to "sans serif" if preferred
primaryFont = "Georgia"  # Change font family
```

Then restart app.

### Adjusting Diversity Boost

**File:** `frontend/beige_ai_app.py` (around line 870)

```python
diversity_boost = 1.08  # Currently 8%, change to different %
underrepresented = ["Berry Garden", "Silk Cheesecake"]  # Edit this list
```

Save & restart app.

---

## Quick Reference

### Common Commands

```bash
# Install & setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run app
python main.py

# Manual run
streamlit run frontend/beige_ai_app.py

# Check model
python3 -c "import joblib; m = joblib.load('backend/models/cake_model.joblib'); print(f'Classes: {m.classes_}')"

# View database
sqlite3 beige_retail.db "SELECT * FROM sales LIMIT 5;"

# Export sales
sqlite3 beige_retail.db ".headers on" ".mode csv" "SELECT * FROM sales" > sales.csv
```

### File Locations

| What | Where |
|------|-------|
| Main app | `frontend/beige_ai_app.py` |
| ML models | `backend/models/` |
| Database | `beige_retail.db` |
| Styling | `frontend/styles.css` |
| Menu config | `backend/menu_config.py` |
| Training scripts | `backend/training/` |
| Logo/assets | `assets/viz/` |
| Docs | `docs/` |

### Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Port 8501 in use | `lsof -ti:8501 \| xargs kill -9` |
| Model not found | Check: `ls backend/models/cake_model.joblib` |
| Gemini API error | Verify env var: `echo $GEMINI_API_KEY` |
| Slow predictions | Restart app: `Ctrl+C` then `python main.py` |
| Database locked | Restart app (single-threaded, shouldn't happen) |

### Support Resources

- **Tech Questions:** Check `TECHNICAL_BIBLE.md`
- **For Investors:** Check `EXECUTIVE_MASTER.md`
- **Code Issues:** Look in `frontend/beige_ai_app.py` comments
- **ML Questions:** See `backend/training/` scripts

---

## Staff Training Checklist

### Week 1: Basic Operation
- [ ] Can start/stop the app correctly
- [ ] Understands customer mood input process
- [ ] Can explain recommendation confidence scores
- [ ] Can guide customer through "add to cart" flow
- [ ] Knows where to find daily sales metrics

### Week 2: Advanced Features
- [ ] Can export sales data to CSV
- [ ] Understands feedback buttons (👍🤔👎)
- [ ] Can identify top-selling cakes from analytics
- [ ] Knows how to restock low-inventory items
- [ ] Can explain why recommendation happened (based on mood/weather)

### Week 3: Troubleshooting
- [ ] Can restart app if it freezes
- [ ] Knows to check GEMINI_API_KEY if AI fails
- [ ] Can verify database connectivity
- [ ] Understands model loading times on startup
- [ ] Has checklist for daily opening/closing

### Month 1: Mastery
- [ ] Trains new staff from memory
- [ ] Suggests improvements based on customer feedback
- [ ] Understand monthly retraining process
- [ ] Can customize cakes/prices as needed
- [ ] Uses analytics to drive business decisions

---

*Beige.AI User Operations — March 19, 2026*  
*For café workers creating magic.*
