#!/usr/bin/env python3
"""Fix indentation for analyst_mode block in beige_ai_app.py"""

with open('frontend/beige_ai_app.py', 'r') as f:
    lines = f.readlines()

# Find the line with "if st.session_state.analyst_mode:" in the chart section
analyst_start = None
analyst_end = None

for i, line in enumerate(lines):
    if 'if st.session_state.analyst_mode:' in line and i > 700:
        analyst_start = i
        print(f"Found analyst_mode check at line {i+1}: {line.strip()}")
        break

# If found, indent from the next line to the "def display_checkout" line
if analyst_start is not None:
    # Find where the explanation section ends (before "def display_checkout")
    for i in range(analyst_start + 1, len(lines)):
        if 'def display_checkout' in lines[i]:
            analyst_end = i - 1
            break
    
    print(f"Analyst mode block: lines {analyst_start+1} to {analyst_end+1}")
    
    # Indent all lines in this range (except empty lines)
    for i in range(analyst_start + 1, analyst_end + 1):
        if lines[i].strip():  # Only indent non-empty lines
            lines[i] = '    ' + lines[i]
        print(f"  Line {i+1}: {lines[i][:50]}...")

    with open('frontend/beige_ai_app.py', 'w') as f:
        f.writelines(lines)

    print("✅ Indentation applied successfully")
else:
    print("❌ Could not find analyst_mode check")
