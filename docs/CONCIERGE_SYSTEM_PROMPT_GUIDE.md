# Beige AI — Concierge System Prompt Documentation

**Date**: March 19, 2026  
**Status**: ✅ Integrated & Production-Ready

---

## Overview

The **Concierge System Prompt** is the core instruction set for Beige AI's LLM-powered recommendation generation. It ensures all AI-generated cake recommendations:

✅ Feel like **editorial assistant guidance**, not system output  
✅ Use **sensory, atmospheric language**  
✅ Prioritize **emotional and flavor alignment**  
✅ Follow a **strict, consistent output format**  
✅ **Never reveal internal logic** or data insights  

---

## File Location

```
backend/concierge_system_prompt.py
```

This module exports:
- `CONCIERGE_SYSTEM_PROMPT` — Full system instruction set
- `get_concierge_prompt()` — Function to retrieve prompt
- `get_concierge_recommendation_template()` — Reference for output format
- `SYSTEM_MESSAGE_FOR_GEMINI` — Formatted for Gemini API use

---

## How It's Used

### In Streamlit App

**File**: `frontend/beige_ai_app.py`  
**Function**: `generate_cake_explanation()`

The system prompt is passed directly to Gemini:

```python
from concierge_system_prompt import CONCIERGE_SYSTEM_PROMPT

model = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction=CONCIERGE_SYSTEM_PROMPT
)
```

**Input User Prompt**:
```
User context:
- Current mood: happy
- Weather: sunny
- Time of day: afternoon
- Sweetness preference: 5/10
- Health consciousness: 7/10

Recommended cake:
- Name: Berry Garden Cake
- Flavor profile: fresh, fruity
- Category: light & refreshing

Generate a personalized recommendation...
```

**Output** (Concierge style):
```
Primary Match:
A bright, verdant cake that captures the ease of a sunny afternoon. 
Layers of fresh berries and light cream create a sensation of natural 
sweetness without heaviness—exactly what the moment demands.

Counter-Mood Alternative:
If you find yourself seeking something more indulgent, a chocolate-
based option would provide grounding comfort instead.
```

---

## Key Principles

### 1. Editorial Tone, Not Data Science

| ❌ Don't Say | ✅ Do Say |
|-------------|----------|
| "78% confidence match" | "This cake leans into..." |
| "Ingredients: cocoa, cream, sugar" | "Deep cocoa notes unfold slowly" |
| "Recommended for: sunny weather" | "Perfect for bright afternoons" |
| "Alternative option #2" | "If you're drawn toward lightness..." |

### 2. Strict Output Format

Always deliver EXACTLY 2 sections:

#### Section 1: Primary Match (2-3 sentences)
- One cohesive paragraph
- Sensory language (taste, texture, aroma)
- Emotional resonance with user's state
- Connection to context (weather, time, mood)

#### Section 2: Counter-Mood Alternative (1 sentence)
- Gentle pivot, not a ranking
- Contrasting emotional direction
- Starts with: "If you're drawn toward..." or similar

### 3. Never Include

❌ Confidence scores or percentages  
❌ Product tags or labels  
❌ Ingredient lists  
❌ Technical descriptions  
❌ System logic or dataset references  
❌ Multiple alternatives or rankings  

### 4. Data Integrity

- Use ONLY information provided in cake_menu
- Do NOT invent ingredients, flavors, or textures
- Do NOT assume missing context
- Do NOT justify missing data

---

## Integration Points

### Gemini API (Streamlit App)

```python
from concierge_system_prompt import CONCIERGE_SYSTEM_PROMPT
import google.generativeai as genai

model = genai.GenerativeModel(
    'gemini-pro',
    system_instruction=CONCIERGE_SYSTEM_PROMPT
)

response = model.generate_content(
    user_prompt,
    generation_config={
        'temperature': 0.8,
        'max_output_tokens': 150
    }
)
```

### Other LLM Providers

To use with OpenAI, Anthropic, or other providers:

```python
from backend.concierge_system_prompt import get_concierge_prompt

# For other LLM providers (OpenAI, etc.)
messages = [
    {"role": "system", "content": get_concierge_prompt()},
    {"role": "user", "content": user_prompt}
]
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages
)
```

### Reference Without LLM

For testing or documentation:

```python
from backend.concierge_system_prompt import (
    get_concierge_recommendation_template,
    CONCIERGE_SYSTEM_PROMPT
)

# Get reference for output validation
template = get_concierge_recommendation_template()

# Review full system prompt
full_prompt = CONCIERGE_SYSTEM_PROMPT
```

---

## Example Recommendations

### Example 1: Sunny Afternoon, Happy Mood

**Context**:
- Mood: Happy
- Weather: Sunny
- Time: Afternoon
- Sweetness: 5/10
- Health: 8/10

**Expected Output**:
```
Primary Match:
A bright, balanced cake that mirrors the lightness you're feeling right now. 
Subtle citrus notes and delicate texture make this the perfect choice for 
an afternoon that calls for something refreshing but substantial.

Counter-Mood Alternative:
If a richer chocolate experience appeals to you instead, darker notes 
would ground the same moment differently.
```

### Example 2: Rainy Evening, Stressed Mood

**Context**:
- Mood: Stressed
- Weather: Rainy
- Time: Evening
- Sweetness: 8/10
- Health: 3/10

**Expected Output**:
```
Primary Match:
A deep, enveloping chocolate cake that feels like comfort in cake form. 
Silken texture and rich cocoa create a moment of genuine solace—the 
kind of indulgence that makes an evening feel manageable again.

Counter-Mood Alternative:
Should your mood shift toward brightness, a lighter matcha or citrus 
option would offer a gentler kind of ease.
```

### Example 3: Cool Morning, Celebratory Mood

**Context**:
- Mood: Celebratory
- Weather: Clear/Cloudy
- Time: Morning
- Sweetness: 9/10
- Health: 5/10

**Expected Output**:
```
Primary Match:
An elegant, celebratory cake with layers that suggest both 
sophistication and genuine pleasure. This choice captures the 
special feeling of marking a moment—rich enough to dignify 
the occasion, memorable enough to stay with you.

Counter-Mood Alternative:
If you prefer to celebrate with something lighter and more 
playful, a berry-forward option brings joy without heaviness.
```

---

## Validation Checklist

Use this checklist to validate Concierge recommendations:

- [ ] No confidence scores or percentages mentioned
- [ ] No ingredient lists or technical descriptions
- [ ] No product tags or category labels
- [ ] Exactly 2 sections (Primary + Counter-Mood)
- [ ] Primary Match is 2-3 sentences
- [ ] Counter-Mood Alternative is 1 sentence
- [ ] Sensory language (taste, texture, aroma) present
- [ ] Connection to user's mood or context made
- [ ] Tone is editorial, calm, sophisticated
- [ ] No system logic or dataset references
- [ ] Output feels like helpful pause, not calculation

---

## Temperature & Generation Settings

For Gemini API and similar LLMs:

```python
generation_config={
    'temperature': 0.8,      # High enough for warmth, not too high for quality
    'top_p': 0.95,          # Reasonable diversity
    'top_k': 40,             # Standard
    'max_output_tokens': 150 # Enforces conciseness
}
```

**Why these settings?**
- `temperature=0.8`: Balances creativity with coherence
- `max_output_tokens=150`: Enforces concise, focused output
- Low values (0.7-0.8) ensure consistency; higher (0.8-0.9) add personality

---

## Fallback Behavior

If Gemini API is unavailable, Streamlit app uses simple template:

```python
fallback_explanation = f"""Our selection of {prediction['cake_name']} 
complements your moment perfectly. With its {prediction['flavor_profile']} 
notes, this {prediction['category']} cake brings exactly what the moment calls for."""
```

This maintains the Concierge tone without requiring LLM.

---

## Testing the System Prompt

### Quick Test

```bash
python backend/concierge_system_prompt.py
```

This prints:
- Full system prompt
- Template reference with expected format

### Integration Test

```bash
streamlit run frontend/beige_ai_app.py
```

Then:
1. Navigate to recommendation section
2. Check console for "Generating Concierge recommendation..."
3. Verify output follows both sections and editorial tone

### Validation Script

```python
from backend.concierge_system_prompt import get_concierge_recommendation_template
import json

template = get_concierge_recommendation_template()
print(json.dumps(template, indent=2))
```

---

## Updating the System Prompt

If you need to adjust the prompt:

1. **Edit** `backend/concierge_system_prompt.py`
2. **Update** `CONCIERGE_SYSTEM_PROMPT` constant
3. **Test** with `streamlit run frontend/beige_ai_app.py`
4. **Verify** output matches expected style

⚠️ **Important**: Changes apply everywhere the prompt is imported. Test thoroughly.

---

## Common Adjustments

### Make Recommendations More Literary

Increase `temperature` to 0.85-0.9:
```python
generation_config={'temperature': 0.9, ...}
```

### Make Recommendations More Consistent

Decrease `temperature` to 0.7:
```python
generation_config={'temperature': 0.7, ...}
```

### Change Output Length

Adjust `max_output_tokens`:
- 100 tokens: Very concise
- 150 tokens: Current (recommended)
- 200 tokens: More expansive

---

## Production Considerations

### Security
- ✅ No API keys in system prompt
- ✅ No user data stored in prompt
- ✅ Safe for multi-user environments

### Performance
- ✅ Cached in Streamlit with `@st.cache_resource`
- ✅ ~1-2 seconds per recommendation
- ✅ Graceful fallback if API unavailable

### Compliance
- ✅ No personal data retention
- ✅ User inputs not logged to model
- ✅ Follows data privacy best practices

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Mar 19, 2026 | Initial release with Gemini integration |

---

## Next Steps

1. **Test locally**: `streamlit run frontend/beige_ai_app.py`
2. **Verify output**: Check recommendations follow format
3. **Deploy**: Push to production environment
4. **Monitor**: Track recommendation quality and user feedback
5. **Iterate**: Adjust temperature/tokens based on results

---

## Support

For issues:
1. Run `python verify_gemini_api.py` to check API status
2. Check console logs for "Generating Concierge recommendation..."
3. Verify `.streamlit/secrets.toml` has valid API key
4. Review system prompt against examples above

---

**Status**: ✅ Production-Ready  
**Last Updated**: March 19, 2026  
**Maintained By**: ML Engineering Team
