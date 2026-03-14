#!/usr/bin/env python3
"""
Beige.AI Entry Point
=====================
Launches the Streamlit application for cake recommendations.

Usage:
    python main.py

Or:
    streamlit run frontend/beige_ai_app.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Streamlit app."""
    project_root = Path(__file__).parent
    app_path = project_root / "frontend" / "beige_ai_app.py"
    
    # Verify the app file exists
    if not app_path.exists():
        print(f"Error: Streamlit app not found at {app_path}")
        sys.exit(1)
    
    # Run Streamlit
    print(f"Starting Beige.AI from {app_path}")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path)],
        cwd=str(project_root)
    )

if __name__ == "__main__":
    main()
