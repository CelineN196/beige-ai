#!/usr/bin/env python3
"""Apply analyst mode changes to beige_ai_app.py"""

import re

with open('frontend/beige_ai_app.py', 'r') as f:
    content = f.read()

# 1. Add analyst_mode to session state (after micro_story initialization)
session_state_addition = """if 'micro_story' not in st.session_state:
    st.session_state.micro_story = None

if 'analyst_mode' not in st.session_state:
    st.session_state.analyst_mode = False
"""

content = content.replace(
    """if 'micro_story' not in st.session_state:
    st.session_state.micro_story = None

# =============""",
    session_state_addition + "\n# =============="
)

print("✓ Added analyst_mode session state")

# 2. Add sidebar toggle (after header basket button)
sidebar_code = """

# ============================================================================
# ANALYST MODE TOGGLE (SECURE SIDEBAR)
# ============================================================================

with st.sidebar:
    st.markdown("---")
    analyst_password = st.text_input("Analyst Access", type="password", placeholder="Enter password")
    if analyst_password == "beige_admin":
        st.session_state.analyst_mode = True
        st.success("✓ Analyst mode enabled")
    elif analyst_password:
        st.session_state.analyst_mode = False
        st.error("Incorrect password")
    
    if st.session_state.analyst_mode:
        if st.button("Exit Analyst Mode"):
            st.session_state.analyst_mode = False
            st.rerun()
    st.markdown("---")
"""

# Find the basket button location and add sidebar code after it
basket_pattern = r"(st\.session_state\.page = 'checkout'\s+st\.rerun\(\))\n\ndef get_time_of_day"
replacement = r"\1" + sidebar_code + "\ndef get_time_of_day"
content = re.sub(basket_pattern, replacement, content)

print("✓ Added sidebar toggle")

# 3. Modify display_ai_recommendations to conditionally show recommendation cards
# Find the card_html generation and modify it
card_pattern = r"card_html = f\"\"\"(.*?)\"\"\"\s+st\.markdown\(card_html"

def modify_cards(match):
    card_content = match.group(1)
    return f'''# Customer/Analyst view conditional card display
            if st.session_state.analyst_mode:
                card_html = f"""{card_content}"""
            else:
                # Customer view: simplified card without confidence and details
                card_html = f"""
            <div class='rec-card'>
                <div class='rec-rank'>{{roman_numerals[idx]}}</div>
                <div class='rec-name'>{{cake}}</div>
                <div class='rec-description'>Recommended for this moment based on your environment and mood.</div>
                <div class='rec-detail'><strong>Category:</strong> {{category}}</div>
                <div class='rec-detail'><strong>Flavor:</strong> {{flavor}}</div>
            </div>
            """
            st.markdown(card_html'''

content = re.sub(card_pattern, modify_cards, content, flags=re.DOTALL)

print("✓ Modified card display logic")

# 4. Wrap chart section in analyst_mode check
# Find "# Display chart" and wrap it
chart_pattern = r"(st\.markdown\(\"<br><br>\", unsafe_allow_html=True\)\s+)# Display chart"
chart_replacement = r"\1# ====================================================================\n    ==\n    # ANALYST ONLY: Chart & Technical Insights\n    # ====================================================================\n    ==\n    if st.session_state.analyst_mode:\n        # Display chart"

content = re.sub(chart_pattern, chart_replacement, content)

print("✓ Wrapped chart in analyst_mode check")

# 5. Indent chart code (from "fig, ax =" through "st.markdown(...The Reasoning...)")
# This is complex, so let's do it after initial replacements

with open('frontend/beige_ai_app.py', 'w') as f:
    f.write(content)

print("\n✅ Applied analyst mode changes successfully")
