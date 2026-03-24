"""
COPYWRITER INTEGRATION EXAMPLES
================================
Practical code snippets showing how to integrate the Beige AI Copywriter Engine
into the Streamlit app (beige_ai_app.py)

Copy these code samples directly into your app!
"""

# ============================================================================
# EXAMPLE 1: Basic Integration in display_ai_recommendations()
# ============================================================================

def display_ai_recommendations_with_copywriter():
    """
    Enhanced version of display_ai_recommendations() using copywriter.
    
    Replace the relevant section around line 950-1070 in beige_ai_app.py
    with this enhanced version.
    """
    
    # At the top of your file, add this import:
    from beige_ai_copywriter import generate_luxury_description
    
    if st.session_state.ai_result is None:
        return
    
    result = st.session_state.ai_result
    top_3_cakes = result['top_3_cakes']
    top_3_probs = result['top_3_probs']
    mood = result['mood']
    weather_condition = result['weather_condition']
    
    # Display header
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <strong style='font-size: 1.1em;'>🤖 AI Recommendation (Luxury Narrative)</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Display top 3 recommendations with luxury descriptions
    rec_cols = st.columns(3)
    
    for idx, (cake, prob) in enumerate(zip(top_3_cakes, top_3_probs)):
        with rec_cols[idx]:
            # Get cake metadata
            cake_meta = CAKE_METADATA.get(cake, {})
            
            # Generate luxury description using copywriter
            luxury_description = generate_luxury_description(
                cake_name=cake,
                category=cake_meta.get('category', 'Unknown'),
                flavor_profile=cake_meta.get('flavor_profile', 'Refined taste'),
                mood=mood,
                weather=weather_condition,
                health_preference=result.get('health_preference', 5)
            )
            
            # Display the formatted luxury narrative
            st.markdown(luxury_description)
            
            # Add confidence score
            st.caption(f"**Confidence**: {prob*100:.1f}%")
            
            # Add to basket button
            if st.button("Add to Basket", key=f"ai_{idx}_{cake}", width="stretch"):
                st.session_state.cart.append({
                    'name': cake,
                    'price': 9.00
                })
                st.success(f"✓ {cake} added!")


# ============================================================================
# EXAMPLE 2: Standalone Function Usage
# ============================================================================

def get_cake_description(cake_name, user_mood, user_weather, user_health_pref):
    """
    Simple function to get luxury description for any cake.
    
    Usage:
        description = get_cake_description(
            "Matcha Zen Cake",
            "Happy",
            "Sunny",
            health_pref=8
        )
        st.markdown(description)
    """
    
    from beige_ai_copywriter import generate_luxury_description
    from frontend.data_mapping import CAKE_METADATA
    
    cake_meta = CAKE_METADATA.get(cake_name, {})
    
    if not cake_meta:
        return f"Cake '{cake_name}' not found."
    
    return generate_luxury_description(
        cake_name=cake_name,
        category=cake_meta.get('category'),
        flavor_profile=cake_meta.get('flavor_profile'),
        mood=user_mood,
        weather=user_weather,
        health_preference=user_health_pref
    )


# ============================================================================
# EXAMPLE 3: Integration with Hybrid Recommendation System
# ============================================================================

def display_hybrid_recommendations_with_copywriter(hybrid_results, cluster_id, mood, weather):
    """
    Display hybrid system recommendations with luxury copywriter narratives.
    
    Args:
        hybrid_results: Dict from hybrid_system.infer()
        cluster_id: Assigned cluster from hybrid system
        mood: User's mood
        weather: Current weather
    
    Usage:
        results, cluster_id = hybrid_system.infer(user_input)
        display_hybrid_recommendations_with_copywriter(results, cluster_id, mood, weather)
    """
    
    from beige_ai_copywriter import generate_luxury_description
    from frontend.data_mapping import CAKE_METADATA
    
    # Sort by final_score
    sorted_results = sorted(
        hybrid_results.items(),
        key=lambda x: x[1]['final_score'],
        reverse=True
    )
    
    # Display top 3 with luxury narratives
    st.markdown("## Your Top 3 Recommendations")
    
    cols = st.columns(3)
    
    for idx, (cake_name, cake_result) in enumerate(sorted_results[:3]):
        with cols[idx]:
            cake_meta = CAKE_METADATA.get(cake_name, {})
            
            # Generate luxury description
            description = generate_luxury_description(
                cake_name=cake_name,
                category=cake_meta.get('category'),
                flavor_profile=cake_meta.get('flavor_profile'),
                mood=mood,
                weather=weather,
                health_preference=cake_result.get('health_alignment', 5) * 10
            )
            
            # Display description
            st.markdown(description)
            
            # Show hybrid system insights
            st.caption(f"**Score**: {cake_result['final_score']:.3f}")
            st.caption(f"**ML Confidence**: {cake_result['ml_probability']:.1%}")
            
            # Add to basket
            if st.button(f"Add {cake_name}", key=f"hybrid_{idx}_{cake_name}"):
                st.session_state.cart.append({
                    'name': cake_name,
                    'price': 9.00
                })
                st.success(f"✓ Added to basket!")


# ============================================================================
# EXAMPLE 4: Batch Description Generation for All Cakes
# ============================================================================

def generate_all_cake_descriptions(mood="Happy", weather="Sunny", health_pref=5):
    """
    Generate luxury descriptions for all cakes at once.
    
    Useful for:
    - Pre-computing descriptions on app startup
    - Caching all descriptions for fast UI display
    - A/B testing different moods
    
    Usage:
        all_descriptions = generate_all_cake_descriptions("Happy", "Sunny")
        # Then access: all_descriptions["Matcha Zen Cake"]
    """
    
    from beige_ai_copywriter import generate_luxury_description
    from frontend.data_mapping import CAKE_METADATA
    
    descriptions = {}
    
    for cake_name, cake_meta in CAKE_METADATA.items():
        description = generate_luxury_description(
            cake_name=cake_name,
            category=cake_meta.get('category'),
            flavor_profile=cake_meta.get('flavor_profile'),
            mood=mood,
            weather=weather,
            health_preference=health_pref
        )
        descriptions[cake_name] = description
    
    return descriptions


# ============================================================================
# EXAMPLE 5: Real-Time Mood-Based Description Switching
# ============================================================================

def mood_based_cake_explorer():
    """
    Interactive cake explorer that updates descriptions based on mood slider.
    
    Perfect for:
    - "Try different moods" feature
    - A/B testing copywriter
    - Exploring how mood affects recommendations
    """
    
    from beige_ai_copywriter import generate_luxury_description
    from frontend.data_mapping import CAKE_METADATA
    
    st.markdown("## Explore How Mood Changes Our Recommendations")
    
    # Mood selector
    mood_options = ["Happy", "Stressed", "Tired", "Lonely", "Celebratory"]
    selected_mood = st.select_slider("Try different moods:", mood_options)
    
    weather_options = ["Sunny", "Rainy", "Cloudy", "Snowy", "Stormy"]
    selected_weather = st.select_slider("Select weather:", weather_options)
    
    # Display 3 sample cakes with descriptions for selected mood/weather
    sample_cakes = ["Matcha Zen Cake", "Dark Chocolate Sea Salt Cake", "Café Tiramisu"]
    
    cols = st.columns(3)
    
    for idx, cake_name in enumerate(sample_cakes):
        with cols[idx]:
            cake_meta = CAKE_METADATA.get(cake_name)
            
            description = generate_luxury_description(
                cake_name=cake_name,
                category=cake_meta.get('category'),
                flavor_profile=cake_meta.get('flavor_profile'),
                mood=selected_mood,
                weather=selected_weather,
                health_preference=5
            )
            
            st.markdown(description)
    
    st.markdown(f"**Note**: Each narrative adapts subtly for **{selected_mood}** mood in **{selected_weather}** weather!")


# ============================================================================
# EXAMPLE 6: Copywriter with Caching for Performance
# ============================================================================

@st.cache_data
def get_cached_description(cake_name, mood, weather, health_pref):
    """
    Cached version of copywriter for faster performance.
    
    Caches descriptions so repeated calls are instant.
    """
    
    from beige_ai_copywriter import generate_luxury_description
    from frontend.data_mapping import CAKE_METADATA
    
    cake_meta = CAKE_METADATA.get(cake_name)
    
    return generate_luxury_description(
        cake_name=cake_name,
        category=cake_meta.get('category'),
        flavor_profile=cake_meta.get('flavor_profile'),
        mood=mood,
        weather=weather,
        health_preference=health_pref
    )


# Usage in display function:
def display_with_caching():
    """Example using the cached version above."""
    
    cake_name = "Matcha Zen Cake"
    mood = st.session_state.ai_result['mood']
    weather = st.session_state.weather_condition
    health_pref = 8
    
    # This call is cached - repeated calls are instant
    description = get_cached_description(cake_name, mood, weather, health_pref)
    st.markdown(description)


# ============================================================================
# EXAMPLE 7: Comparison: Before vs. After Copywriter
# ============================================================================

def comparison_demo():
    """
    Side-by-side comparison of descriptions with/without copywriter.
    
    Great for:
    - Demonstrating the improvement
    - A/B testing
    - Showcasing the system to stakeholders
    """
    
    from beige_ai_copywriter import generate_luxury_description
    from frontend.data_mapping import CAKE_METADATA
    
    st.markdown("## Copywriter Impact Demonstration")
    
    cake_name = "Matcha Zen Cake"
    cake_meta = CAKE_METADATA[cake_name]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Without Copywriter (Generic)")
        generic_desc = cake_meta.get('description', 'Generic cake description')
        st.markdown(f"```\n{generic_desc}\n```")
    
    with col2:
        st.markdown("### With Copywriter (Luxury Narrative)")
        luxury_desc = generate_luxury_description(
            cake_name=cake_name,
            category=cake_meta.get('category'),
            flavor_profile=cake_meta.get('flavor_profile'),
            mood="Happy",
            weather="Sunny",
            health_preference=8
        )
        st.markdown(luxury_desc)
    
    st.markdown("#### Why the difference?")
    st.markdown("""
    - **Generic**: Static template, no personalization
    - **Copywriter**: Contextual, dynamic, tailored to mood + weather
    - **Tone**: Minimalist luxury vs. informational
    - **Impact**: Higher perceived value and personalization
    """)


# ============================================================================
# INTEGRATION CHECKLIST
# ============================================================================

"""
To integrate the copywriter into beige_ai_app.py:

□ Step 1: Add import at top of file
  from beige_ai_copywriter import generate_luxury_description

□ Step 2: In display_ai_recommendations() function
  - Get cake metadata for each recommendation
  - Call generate_luxury_description() with context
  - Display formatted output

□ Step 3: Test with different moods/weather
  - Happy + Sunny (should mention brightness/refresh)
  - Stressed + Rainy (should mention grounding/comfort)
  - Tired + Cloudy (should mention rest/balance)

□ Step 4: Verify output
  - Descriptions are 2 sentences exactly
  - Format is consistent
  - Mood/weather is woven in subtly
  - No input values are modified

□ Step 5: Deploy
  - Push to production
  - Monitor user engagement
  - Collect feedback on new descriptions

Optional: Set up A/B test
  - Half of users see generic descriptions
  - Half see copywriter descriptions
  - Compare engagement and purchase rates
"""

# ============================================================================
# FILES YOU'LL NEED
# ============================================================================

"""
Important files for integration:

1. frontend/beige_ai_copywriter.py
   ↳ Main copywriter engine module
   
2. test_copywriter_integration.py
   ↳ Run before deployment: python test_copywriter_integration.py
   
3. COPYWRITER_DOCUMENTATION.md
   ↳ Full technical reference
   
4. COPYWRITER_QUICK_REFERENCE.md
   ↳ Developer quick guide
   
5. frontend/data_mapping.py
   ↳ Source for CAKE_METADATA (used by copywriter)
"""

# ============================================================================
# QUICK SUMMARY
# ============================================================================

"""
COPYWRITER QUICK START

1. Import:
   from beige_ai_copywriter import generate_luxury_description

2. Use:
   description = generate_luxury_description(
       cake_name="...",
       category="...",
       flavor_profile="...",
       mood=user_mood,
       weather=current_weather
   )

3. Display:
   st.markdown(description)

That's it! The copywriter handles all styling, formatting, and contextual tone.
"""
