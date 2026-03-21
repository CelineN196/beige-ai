#!/usr/bin/env python3
"""
Comprehensive script to add analyst mode and dual-view system to beige_ai_app.py
This approach reads the entire file and applies all changes in a structured way.
"""

with open('frontend/beige_ai_app.py', 'r') as f:
    lines = f.readlines()

# Find key insertion points
session_state_line = None
basket_button_line = None
display_func_line = None
chart_line = None

for i, line in enumerate(lines):
    if 'if \'order_logged\' not in st.session_state:' in line:
        session_state_line = i
    elif 'st.session_state.page = \'checkout\'' in line and 'header_basket' in lines[i-1]:
        basket_button_line = i
    elif 'def display_checkout():' in line:
        display_func_line = i
    elif '# Display chart' in line:
        chart_line = i

print(f"Found insertion points:")
print(f"  Session state: {session_state_line}")
print(f"  Basket button: {basket_button_line}")
print(f"  Display_checkout function: {display_func_line}")
print(f"  Chart section: {chart_line}")

# 1. Add analyst_mode session state after order_logged
if session_state_line:
    # Find the next block boundary (blank line and comment)
    insert_pos = session_state_line
    while insert_pos < len(lines) and '# ========' not in lines[insert_pos]:
        insert_pos += 1
    
    analyst_state = """if 'analyst_mode' not in st.session_state:
    st.session_state.analyst_mode = False

"""
    lines.insert(insert_pos, analyst_state)
    print(f"✓ Inserted analyst_mode session state at line {insert_pos}")

# 2. Add sidebar toggle after basket button
if basket_button_line:
    insert_pos = basket_button_line + 1
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
    for line_to_insert in reversed(sidebar_code.split('\n')):
        lines.insert(insert_pos, line_to_insert + '\n')
    print(f"✓ Inserted sidebar toggle at line {insert_pos}")

# 3. Wrap chart and explanation in analyst_mode check
if chart_line:
    # Insert opening if statement
    lines.insert(chart_line, "    if st.session_state.analyst_mode:\n")
    
    # Find the end of the explanation section (before display_checkout function)
    chart_end = chart_line + 1
    for i in range(chart_line + 1, len(lines)):
        if 'def display_checkout' in lines[i]:
            chart_end = i
            break
    
    # Indent all lines from chart_line+1 to chart_end-1
    for i in range(chart_line + 1, chart_end):
        if lines[i].strip():  # Only indent non-empty lines
            lines[i] = '    ' + lines[i]
    
    print(f"✓ Wrapped chart section (lines {chart_line}-{chart_end}) in analyst_mode check")

# Write the modified file
with open('frontend/beige_ai_app.py', 'w') as f:
    f.writelines(lines)

print("\n✅ Applied all analyst mode changes successfully!")
