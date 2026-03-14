# 🍰 Beige.AI Streamlit App - Quick Start

## 30-Second Setup

### 1. Install Streamlit
```bash
pip install streamlit
```

### 2. Run the App
```bash
cd /Users/queenceline/Downloads/Beige\ AI
streamlit run beige_ai_app.py
```

### 3. Open Browser
- Auto-opens at `http://localhost:8501`
- If not: open browser and go to URL above

## Using the App

### Step 1: Answer Questions in Sidebar
- **Mood**: How you're feeling (Happy, Stressed, etc.)
- **Weather**: Current weather (Sunny, Rainy, etc.)
- **Temperature**: In Celsius (0-40°C slider)
- **Humidity**: Percentage (0-100% slider)
- **Time**: Morning/Afternoon/Evening/Night
- **AQI**: Air Quality Index (0-300 slider)
- **Sweetness**: 1-10 scale
- **Health**: 1-10 scale

### Step 2: Click "Generate Recommendation"

The app will:
1. Process your inputs
2. Calculate additional features
3. Run the ML model
4. Show top 3 cake recommendations

### Step 3: Review Results

You'll see:
- 🥇 **Top 3 cakes** with match percentages
- 📊 **Probability chart** showing confidence
- 💡 **Explanations** from association rules
- 📋 **Details** about each cake

### Step 4: Provide Feedback

Click one of:
- 👍 **Love it!**
- 🤔 **Not sure**
- 👎 **Not interested**

## Example: Stressed + Rainy

1. Slide mood → "Stressed"
2. Select weather → "Rainy"
3. Temperature → 12°C
4. Time → "Evening"
5. Sweetness → 9
6. Health → 2

**Result:**
- 🥇 Dark Chocolate Sea Salt Cake (95% confidence)
- Explanation: "Because you're feeling stressed and it's rainy..."

## Features

✅ **Real-time predictions** - <1 second response  
✅ **Beautiful charts** - Bar chart showing all options  
✅ **Smart explanations** - Based on mood + weather patterns  
✅ **Cake details** - Sweetness, health, flavor, category  
✅ **Mobile friendly** - Works on phone/tablet  
✅ **Zero config** - Just run and start!  

## Troubleshooting

### App won't start?
```bash
# Make sure you're in the right directory
cd /Users/queenceline/Downloads/Beige\ AI

# Check files exist
ls best_model.joblib preprocessor.joblib feature_info.joblib
```

### Slow predictions?
- First run loads the model (1-2 sec)
- Subsequent runs are instant (<300ms)
- This is normal!

### Can't find Streamlit?
```bash
# Install it
pip install streamlit
```

## Model Details

- **Accuracy**: 78.80%
- **Type**: Random Forest
- **Training Data**: 50,000 customer profiles
- **Cakes**: 8 categories

## Next Steps

1. Try different mood/weather combinations
2. Notice how explanations change
3. Provide feedback on recommendations
4. Share with friends!

---

**🚀 Ready?** Just run: `streamlit run beige_ai_app.py`
