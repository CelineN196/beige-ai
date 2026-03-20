#!/usr/bin/env python3
"""
Beige.AI Entry Point
=====================
Launches the Streamlit application for personalized cake recommendations.

Usage:
    Local development:
        python main.py
    
    Or (for Streamlit Cloud):
        streamlit run frontend/beige_ai_app.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Streamlit app locally."""
    project_root = Path(__file__).parent
    app_path = project_root / "frontend" / "beige_ai_app.py"
    
    # Verify the app file exists
    if not app_path.exists():
        print(f"❌ Error: Streamlit app not found at {app_path}")
        sys.exit(1)
    
    # Run Streamlit with project root as working directory
    print(f"🚀 Starting Beige.AI from {app_path}")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path)],
        cwd=str(project_root)
    )

if __name__ == "__main__":
    main()
