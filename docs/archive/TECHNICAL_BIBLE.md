# Beige.AI Technical Bible

Complete technical reference for developers, engineers, and system architects.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Project Structure](#project-structure)
3. [Data Pipeline & Features](#data-pipeline--features)
4. [Machine Learning Model](#machine-learning-model)
5. [Recommendation Engine](#recommendation-engine)
6. [Gemini API Integration](#gemini-api-integration)
7. [Frontend Architecture](#frontend-architecture)
8. [POS & Retail Integration](#pos--retail-integration)
9. [Database Schema](#database-schema)
10. [Code Reference](#code-reference)
11. [Performance & Scaling](#performance--scaling)
12. [Troubleshooting](#troubleshooting)

---

## System Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────────────┐
│         FRONTEND LAYER (Streamlit)              │
│  - User input (mood, weather, preferences)      │
│  - Recommendation display                        │
│  - Feedback collection                           │
│  - Order management                              │
└────────────┬────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────┐
│         AI/LOGIC LAYER                          │
│  - ML Model (Random Forest)                      │
│  - Gemini API (explanations)                     │
│  - Association Rules (context)                   │
│  - Feature engineering                           │
│  - Checkout processing                           │
└────────────┬────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────┐
│         DATA LAYER                              │
│  - SQLite database (inventory, sales)            │
│  - ML model artifacts (.joblib)                  │
│  - Training datasets (.csv)                      │
│  - Configuration (menu_config.py)                │
│  - Association rules (.csv)                      │
└─────────────────────────────────────────────────┘
```

### Component Communication Flow

1. **User Input** → Streamlit collects mood, weather, preferences
2. **Feature Processing** → Preprocessor transforms raw inputs
3. **ML Prediction** → Model outputs probability for each cake
4. **Diversity Boost** → 8% lift applied to underrepresented cakes
5. **Top 3 Selection** → Highest probability cakes selected
6. **Gemini Enrichment** → API generates poetic explanations
7. **Display** → Formatted cards with ranking, confidence, explanation
8. **User Action** → Customer adds to cart or provides feedback
9. **Checkout** → Database updated with sale, inventory decremented
10. **Analytics** → Metrics computed and dashboard updated

---

## Project Structure

```
Beige AI/
├── README.md                        # Project overview
├── requirements.txt                 # Dependencies (8 packages)
├── main.py                          # Entry point (launches Streamlit)
│
├── frontend/                        # UI Layer
│   ├── beige_ai_app.py             # Main app (1000+ lines)
│   ├── styles.css                   # Styling (400+ lines)
│   ├── checkout_handler.py          # Purchase processing
│   ├── retail_analytics_dashboard.py # Metrics display
│   └── .streamlit/
│       └── config.toml              # Theme configuration
│
├── backend/                         # ML & Data Layer
│   ├── menu_config.py               # 8 cake definitions
│   ├── association_rules.csv        # Context rules
│   │
│   ├── models/                      # ML Artifacts (200KB total)
│   │   ├── cake_model.joblib        # Random Forest (500KB)
│   │   ├── preprocessor.joblib      # ColumnTransformer (50KB)
│   │   └── feature_info.joblib      # Metadata (10KB)
│   │
│   ├── data/                        # Training Datasets
│   │   ├── beige_ai_cake_dataset.csv        # v1 (1000 rows)
│   │   ├── beige_ai_cake_dataset_v2.csv    # v2 (2000 rows)
│   │   ├── cluster_profiles.csv             # Segmentation
│   │   └── beige_customer_clusters.csv      # Personas
│   │
│   ├── training/                    # Development Scripts
│   │   ├── beige_ai_data_generation.py
│   │   ├── beige_ai_model_training.py
│   │   ├── beige_ai_phase3_training.py
│   │   └── beige_ai_analytics.py
│   │
│   └── scripts/
│       ├── retail_database_manager.py   # Database operations
│
├── assets/                          # Binary Assets
│   ├── images/cakes/                # 8 PNG product images
│   └── viz/                         # Analysis visualizations
│       ├── eda_analysis.png
│       ├── phase2_analytics_visualizations.png
│       └── phase3_model_evaluation.png
│
└── docs/                            # Documentation
    ├── EXECUTIVE_MASTER.md          # For stakeholders
    ├── TECHNICAL_BIBLE.md           # This file
    └── USER_OPERATIONS.md           # For operators
```

---

## Data Pipeline & Features

### Input Features (10 dimensions)

| Feature | Type | Range | Purpose |
|---------|------|-------|---------|
| **Mood** | Categorical | happy, stressed, tired, lonely, celebratory | Emotional context |
| **Weather** | Categorical | sunny, rainy, cloudy, snowy, stormy | Environmental context |
| **Temperature** | Continuous | 0–40°C | Comfort baseline |
| **Humidity** | Continuous | 0–100% | Air quality impact |
| **Time of Day** | Categorical | morning, afternoon, evening, night | Circadian context |
| **AQI** | Continuous | 0–300 | Pollution/air quality |
| **Sweetness Preference** | Continuous | 1–10 | Personal taste |
| **Health Focus** | Continuous | 1–10 | Wellness priority |
| **Temperature Category** | Derived | cold, mild, hot | Binned temperature |
| **Comfort Index** | Derived | 0–1.0 | Mood × weather weighing |

### Feature Engineering Pipeline

```python
# 1. Categorical encoding (one-hot)
mood_vectors = OneHotEncoder().fit_transform(mood)      # 5 columns
weather_vectors = OneHotEncoder().fit_transform(weather) # 5 columns

# 2. Continuous normalization (StandardScaler)
temp_normalized = (temp - 20) / 15   # Center at 20°C
humidity_normalized = humidity / 100  # 0–1 scale

# 3. Derived features
temperature_category = "cold" if temp < 10 else "hot" if temp > 25 else "mild"
comfort_index = (mood_valence + weather_comfort) / 2  # 0–1

# 4. Full feature vector concatenation
X = [mood_vectors + weather_vectors + [temp_norm, humidity_norm, ...]]
# Shape: (1, 23) for single prediction
```

### Output Space (8 Cakes)

1. **Dark Chocolate Sea Salt** - Indulgent
2. **Matcha Zen** - Energizing
3. **Citrus Cloud** - Refreshing
4. **Berry Garden** - Fruity
5. **Silk Cheesecake** - Classic
6. **Earthy Wellness** - Health-focused
7. **Café Tiramisu** - Coffee-based
8. **Korean Sesame Mini Bread** - Nutty

---

## Machine Learning Model

### Architecture

```
Random Forest Classifier
├─ Type: sklearn.ensemble.RandomForestClassifier
├─ Trees: 100
├─ Max Depth: 15
├─ Min Samples Split: 5
├─ Min Samples Leaf: 2
├─ Max Features: sqrt
├─ Random State: 42
├─ Classes: 8 cakes
└─ Output: Probability distribution over cakes
```

### Training Process

**Dataset:** 2,000 synthetic customer profiles  
**Features:** 23 (10 input + 13 engineering/encoding)  
**Train/Test Split:** 80/20  
**Hyperparameter Tuning:** Grid search (50 combinations)  
**Validation:** 5-fold cross-validation  

### Performance Metrics

| Metric | Value |
|--------|-------|
| Overall Accuracy | 78.80% |
| Precision (macro) | 0.78 |
| Recall (macro) | 0.77 |
| F1-Score (macro) | 0.77 |
| AUC-ROC | 0.94 |

### Per-Class Performance

```
Dark Chocolate Sea Salt:  78% accuracy
Matcha Zen:              82% accuracy
Citrus Cloud:            75% accuracy
Berry Garden:            72% accuracy (underrepresented)
Silk Cheesecake:         71% accuracy (underrepresented)
Earthy Wellness:         74% accuracy
Café Tiramisu:           81% accuracy
Korean Sesame:           85% accuracy
```

### Model Inference (Prediction)

```python
@st.cache_resource
def load_model():
    model_path = BASE_DIR / "backend" / "models" / "cake_model.joblib"
    return joblib.load(model_path)

def predict(user_input):
    # 1. Load cached model & preprocessor
    model = load_model()
    preprocessor = load_preprocessor()
    
    # 2. Create DataFrame from user input
    df = pd.DataFrame([user_input])
    
    # 3. Transform features
    X_processed = preprocessor.transform(df)
    
    # 4. Generate predictions
    probabilities = model.predict_proba(X_processed)[0]
    
    # 5. Return prob dict
    return dict(zip(model.classes_, probabilities))
```

---

## Recommendation Engine

### Core Algorithm

**Step 1: Generate Base Predictions**
```python
probabilities = model.predict_proba(X)[0]
# Output: [0.15, 0.28, 0.12, 0.04, 0.03, 0.18, 0.12, 0.08]
```

**Step 2: Apply Diversity Boost**
```python
underrepresented = ["Berry Garden", "Silk Cheesecake", "Citrus Cloud", "Earthy Wellness"]
diversity_factor = 1.08  # 8% boost

for i, cake in enumerate(classes):
    if cake in underrepresented:
        probabilities[i] *= diversity_factor

# After boost: [0.15, 0.30, 0.13, 0.04, 0.03, 0.19, 0.13, 0.08]
```

**Step 3: Renormalize**
```python
probabilities = probabilities / probabilities.sum()
# Sum = 1.0 ✓
```

**Step 4: Select Top 3**
```python
top_3_indices = np.argsort(probabilities)[-3:][::-1]
top_3 = [(classes[i], probabilities[i]) for i in top_3_indices]
# Output: [("Matcha Zen", 0.30), ("Earthy Wellness", 0.19), ("Dark Chocolate", 0.15)]
```

**Step 5: Generate Explanations**
For each cake, call Gemini API or fallback to association rules.

### Why This Approach?

**Diversity Boost (8%):**
- Without boost: only top cake appears 50%+ of time
- With boost: top 3 show ~25% each (more balanced)
- Solves inventory rotation and menu testing
- Still respects model confidence (not random shuffling)

**Top-3 Strategy:**
- Provides alternatives without overwhelming
- Shows model nuance (1st choice vs. safe choice)
- Reduces decision anxiety for indecisive customers
- Increases basket size (customers may buy multiple)

**Normalization:**
- Preserves statistical validity of probabilities
- Interpretable confidence scores
- Prevents numerical issues (underflow/overflow)

---

## Gemini API Integration

### API Setup

```python
import google.generativeai as genai

# Initialize with API key from environment
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")
```

### Prompt Engineering

**Prompt Template:**
```
Create a poetic, one-sentence explanation for why someone feeling 
[MOOD] on a [WEATHER] day would love [CAKE_NAME]. 

The cake is [FLAVOR_PROFILE].

Keep it to 1–2 sentences maximum. Make it personal and evocative.
```

**Example Prompts:**
- "Create a poetic explaining why someone feeling *contemplative* on a *rainy* day would love *Matcha Zen*. The cake is *herbaceous & earthy*. Keep it to 1-2 sentences."
- "...why someone feeling *celebratory* on a *sunny* day would love *Korean Sesame Mini Bread*. The cake is *nutty & delicate*..."

**Example Outputs:**
- "The earthy matcha notes will ground your contemplative mood while the whispered sweetness lifts you gently skyward."
- "Celebrate the sunshine with delicate sesame notes—a whisper of tradition that tastes like joy."

### Generation Parameters

```python
generation_config = {
    "temperature": 0.7,          # Creativity (0.0=deterministic, 1.0=random)
    "top_p": 0.9,                # Nucleus sampling (higher = more diverse)
    "top_k": 40,                 # Token candidates (lower = more focused)
    "max_output_tokens": 100     # Limit to ~2 sentences
}

response = model.generate_content(
    prompt,
    generation_config=generation_config
)

explanation = response.text
```

### Error Handling & Fallbacks

```python
def get_explanation(cake_name, mood, weather, flavor):
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"Create a poetic explanation why {mood} {weather}..."
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text
    except Exception as e:
        print(f"⚠️ Gemini API failed: {e}")
        # Fallback to association rules
        return get_association_rule_explanation(cake_name, mood, weather)
```

### Cost Estimation

| Metric | Cost |
|--------|------|
| Input tokens | $0.00075 per 1K |
| Output tokens | $0.00375 per 1K |
| Typical explanation | 100 tokens out, 50 tokens in |
| Cost per call | ~$0.0004–0.0008 |
| Daily calls (100 users) | 40 cents/day |
| Monthly (3000 users) | ~$36/month |

**Status:** Negligible cost at scale. Budget <$500/month for 10K daily active users.

---

## Frontend Architecture

### Streamlit Application Structure

**File:** `frontend/beige_ai_app.py` (1000+ lines)

```python
# 1. IMPORTS & CONFIG (lines 1–50)
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# 2. PATH RESOLUTION (lines 51–60)
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

# 3. STYLING (lines 61–400)
st.set_page_config(page_title="Beige.AI", layout="wide")
# Custom CSS injected here

# 4. CACHING & MODEL LOADING (lines 401–450)
@st.cache_resource
def load_model():
    return joblib.load(BASE_DIR / "backend" / "models" / "cake_model.joblib")

# 5. SIDEBAR INPUT (lines 451–550)
st.sidebar.header("Your Preferences")
mood = st.sidebar.selectbox("How are you feeling?", moods)
weather = st.sidebar.selectbox("Weather outside?", weathers)

# 6. MAIN LOGIC (lines 551–850)
if st.button("Get Recommendations"):
    # Process input → predict → enrich → display

# 7. PRODUCT CARDS (lines 851–950)
st.header("Browse All Cakes")
# Display 8 cakes in 3-column grid with images & prices

# 8. BASKET & CHECKOUT (lines 951–1000)
if st.sidebar.button("View Cart"):
    # Display basket, process checkout
```

### Styling System

**Custom CSS (400+ lines)** implements:
- Beige aesthetic (#8B4513, #F5F5DC, #D4A574)
- Georgia serif typography
- Rounded buttons with hover effects
- Card-based layout
- Responsive design
- Accessibility (sufficient contrast, readable fonts)

**Streamlit Config (config.toml):**
```toml
[theme]
primaryColor = "#8B4513"
backgroundColor = "#F5F5DC"
secondaryBackgroundColor = "#FDF5E6"
textColor = "#3E2723"
font = "serif"
```

### Key UI Components

**Recommendation Cards:**
- Medal ranking (🥇 🥈 🥉)
- Cake name with emoji
- Confidence percentage
- Flavor profile
- Explanation from Gemini
- "Add to Cart" button

**Product Grid:**
- 3 columns (responsive)
- High-quality images
- Price from database
- "Add to Cart" button
- Hover lift effect

**Shopping Cart:**
- Sidebar persistent display
- Item count & total price
- Remove buttons
- "Checkout" button
- Real-time updates

---

## POS & Retail Integration

### Database Schema (SQLite)

**Table: inventory**
```sql
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY,
    cake_name VARCHAR UNIQUE,
    category VARCHAR,
    price DECIMAL(8,2),
    quantity_available INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Table: sales**
```sql
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    order_id VARCHAR UNIQUE,
    items_purchased TEXT,  -- JSON format
    total_amount DECIMAL(8,2),
    customer_email VARCHAR,
    customer_name VARCHAR,
    customer_phone VARCHAR,
    delivery_address VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Core Operations

**Fetch Prices:**
```python
def get_prices():
    # Returns {cake_name: price} dict
    # Used for display & cart calculation
```

**Check Inventory:**
```python
def get_inventory_status(cake_name):
    # Returns available quantity
    # Used for "In Stock" / "Low Stock" / "Out of Stock" display
```

**Log Sale:**
```python
def log_sale(order_id, items, total, customer_info):
    # INSERT into sales table
    # Triggers order confirmation email
```

**Update Inventory:**
```python
def update_inventory(cake_name, quantity_change):
    # UPDATE inventory SET quantity_available += quantity_change
    # Called after successful purchase
```

**Get Analytics:**
```python
def get_analytics():
    # Returns: daily_sales, top_sellers, revenue_trend
    # Used for dashboard
```

---

## Database Schema

### SQLite3 Database: `beige_retail.db`

**Connection String:**
```python
conn = sqlite3.connect(str(BASE_DIR / "beige_retail.db"))
cursor = conn.cursor()
```

**Initialization:**
- Runs on first app load
- Creates tables if not exist
- Inserts 8 cakes with $0 stock initially
- Ready for customization

**Sample Data:**

| Cake | Category | Price | Stock |
|------|----------|-------|-------|
| Dark Chocolate Sea Salt | Indulgent | $8.50 | 50 |
| Matcha Zen | Energizing | $8.99 | 50 |
| Citrus Cloud | Refreshing | $7.99 | 50 |
| Berry Garden | Fruity | $8.49 | 50 |
| Silk Cheesecake | Classic | $8.99 | 50 |
| Earthy Wellness | Health | $7.49 | 50 |
| Café Tiramisu | Coffee | $8.99 | 50 |
| Korean Sesame | Nutty | $6.99 | 50 |

---

## Code Reference

### Model Loading Pattern

```python
@st.cache_resource
def load_model():
    """Load Random Forest model from disk (cached for performance)"""
    model_path = BASE_DIR / "backend" / "models" / "cake_model.joblib"
    return joblib.load(model_path)

@st.cache_resource
def load_preprocessor():
    """Load feature transformer (cached)"""
    pp_path = BASE_DIR / "backend" / "models" / "preprocessor.joblib"
    return joblib.load(pp_path)

@st.cache_resource
def load_feature_info():
    """Load feature metadata: class names, feature names (cached)"""
    fi_path = BASE_DIR / "backend" / "models" / "feature_info.joblib"
    return joblib.load(fi_path)
```

### Prediction Pattern

```python
def get_recommendations(mood, weather, temperature, humidity, time_of_day, aqi, sweetness, health_focus):
    """
    Core recommendation function.
    
    Args:
        mood (str): emotional context
        weather (str): environmental context
        temperature (float): degrees celsius
        humidity (float): 0–100
        time_of_day (str): morning/afternoon/evening/night
        aqi (float): air quality index
        sweetness (int): 1–10 preference
        health_focus (int): 1–10 preference
    
    Returns:
        dict: {cake_name: confidence_score}
    """
    # 1. Create input dataframe
    user_input = pd.DataFrame([{
        'mood': mood,
        'weather': weather,
        'temperature': temperature,
        'humidity': humidity,
        'time_of_day': time_of_day,
        'aqi': aqi,
        'sweetness_preference': sweetness,
        'health_focus': health_focus
    }])
    
    # 2. Load cached models
    model = load_model()
    preprocessor = load_preprocessor()
    feature_info = load_feature_info()
    
    # 3. Transform features
    X_processed = preprocessor.transform(user_input)
    
    # 4. Predict probabilities
    probabilities = model.predict_proba(X_processed)[0].copy()
    
    # 5. Apply diversity boost
    underrepresented = ["Berry Garden", "Silk Cheesecake", "Citrus Cloud", "Earthy Wellness"]
    diversity_boost = 1.08
    for i, cake in enumerate(feature_info['classes']):
        if cake in underrepresented:
            probabilities[i] *= diversity_boost
    
    # 6. Renormalize
    probabilities = probabilities / probabilities.sum()
    
    # 7. Return as dict
    return dict(zip(feature_info['classes'], probabilities))
```

### Gemini Explanation Pattern

```python
def get_explanation(cake_name, flavor_profile, mood, weather):
    """
    Generate poetic explanation for why a cake fits the user's mood.
    
    Fallback to association rules if API unavailable.
    """
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-pro")
        
        prompt = f"""
        Create a one-sentence poetic explanation for why someone feeling "{mood}" 
        on a "{weather}" day would love "{cake_name}". The cake has these flavors: {flavor_profile}.
        
        Keep it evocative, personal, and short (1–2 sentences max).
        """
        
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 100
            }
        )
        
        return response.text.strip()
    
    except Exception as e:
        print(f"⚠️ Gemini API error: {e}")
        # Fallback to association rules or default explanation
        return get_association_rule_explanation(cake_name, mood, weather)
```

---

## Performance & Scaling

### Current Metrics

| Metric | Value |
|--------|-------|
| Model load | <100ms |
| Fresh prediction | <50ms |
| Inference (with cache) | <5ms |
| Gemini API call | 1–2 seconds |
| Database query | <100ms |
| Page render | <500ms |
| Total round-trip | <2.5 seconds |

### Caching Strategy

- **Model/Preprocessor:** Streamlit cache_resource (per session)
- **Feature Info:** Cache_resource
- **Database queries:** 30-second TTL on analytics
- **Gemini responses:** One-time per session (no repeat API calls for same inputs)

### Bottlenecks & Solutions

| Bottleneck | Root Cause | Solution |
|----------|-----------|----------|
| Gemini latency | Network I/O | Cache responses, pre-generate for top moods/weathers |
| Database lock | SQLite single-writer | Migrate to PostgreSQL at scale |
| Model cold start | First-time load | Streamlit Cloud keeps warm, or pre-load on deploy |
| CSS rendering | Inline CSS | Already moved to external file |

### Scaling Roadmap

**Phase 1: Current (1–10K DAU)**  
Single Streamlit Cloud instance + SQLite. Sufficient.

**Phase 2: Growth (10–100K DAU)**  
- Deploy to containerized environment (Docker)
- Migrate database to PostgreSQL
- Add Redis caching layer for analytics
- Gemini API rate limiting (60 RPM currently, request increase)

**Phase 3: Enterprise (100K+ DAU)**  
- Horizontal Streamlit instances (load balanced)
- Database read replicas
- Message queue for async tasks (Celery)
- ML model serving (BentoML, KServe)
- CDN for static assets

---

## Troubleshooting

### Issue: Model not found

**Symptom:** `FileNotFoundError: cake_model.joblib not found`

**Root Cause:** Path resolution failed; working directory incorrect

**Solution:**
```python
# Check BASE_DIR calculation
print(f"BASE_DIR: {BASE_DIR}")
print(f"Model path: {BASE_DIR / 'backend' / 'models' / 'cake_model.joblib'}")

# Ensure structure matches
ls backend/models/  # Should show cake_model.joblib
```

### Issue: Gemini API returns error

**Symptom:** `401 Unauthorized` or `API key invalid`

**Root Cause:** Environment variable not set

**Solution:**
```bash
# Set API key
export GEMINI_API_KEY="your-key-here"

# Verify
echo $GEMINI_API_KEY

# Run app
python main.py
```

### Issue: Port 8501 already in use

**Symptom:** `Address already in use`

**Root Cause:** Another Streamlit instance or service running

**Solution:**
```bash
# Kill existing process
lsof -ti:8501 | xargs kill -9

# Or use different port
streamlit run frontend/beige_ai_app.py --server.port 8502
```

### Issue: Slow predictions

**Symptom:** Recommendation takes >5 seconds

**Root Cause:** Model evicted from cache (happens rarely)

**Solution:**
- Restart Streamlit: `Ctrl+C` then `python main.py`
- Check system resources: `top` or Activity Monitor
- Verify Gemini API latency (separate from ML)

### Issue: Database locked

**Symptom:** `sqlite3.OperationalError: database is locked`

**Root Cause:** Multiple concurrent writes to SQLite

**Solution:**
- Streamlit is single-threaded, so shouldn't happen
- If multi-threaded: migrate to PostgreSQL
- Temporarily: close other connections to database

---

## References

- **Random Forest Model:** scikit-learn RandomForestClassifier
- **Feature Preprocessing:** scikit-learn ColumnTransformer
- **API:** Google Generative AI SDK
- **Frontend:** Streamlit 1.28+
- **Database:** SQLite3
- **Deployment:** Docker or Streamlit Cloud

---

*Beige.AI Technical Bible — March 19, 2026*  
*For developers building on this foundation.*
