#!/usr/bin/env python3
"""
Beige.AI Application Launcher
==============================
Entry point for the Streamlit application.

Usage:
    python main.py
"""

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """
    Launch the Beige.AI Streamlit application.
    
    Works from any directory by automatically locating the project root
    and running the Streamlit app with proper working directory context.
    """
    # Get project root (parent of this script)
    project_root = Path(__file__).resolve().parent
    
    # Change to project root to ensure relative paths work correctly
    os.chdir(project_root)
    
    # Run Streamlit app
    app_script = "frontend/beige_ai_app.py"
    
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", app_script],
            check=False
        )
    except KeyboardInterrupt:
        print("\n\n👋 Beige.AI terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error launching Beige.AI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
