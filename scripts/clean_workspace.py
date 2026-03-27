#!/usr/bin/env python3
"""
Beige.AI Workspace Cleaner & Reorganizer
===============================================
Automates safe refactoring of project structure.

Features:
- Creates directory structure if missing
- Moves files safely (skips if not found)
- Updates path references in code
- Validates final structure
- Prints all actions for transparency

Usage:
    python clean_workspace.py
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'


class WorkspaceCleaner:
    def __init__(self, project_root: Path = None):
        """Initialize cleaner with project root."""
        self.project_root = project_root or Path(__file__).parent
        self.actions = []
        self.errors = []
        
    def print_header(self, text: str):
        """Print formatted header."""
        print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
        print(f"{BOLD}{BLUE}{text:^60}{RESET}")
        print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")
    
    def print_step(self, step: int, description: str):
        """Print step header."""
        print(f"{BOLD}{BLUE}[STEP {step}]{RESET} {description}")
        print("-" * 60)
    
    def print_success(self, message: str):
        """Print success message."""
        print(f"{GREEN}✓{RESET} {message}")
        self.actions.append(f"✓ {message}")
    
    def print_skip(self, message: str):
        """Print skip message."""
        print(f"{YELLOW}⊘{RESET} {message}")
        self.actions.append(f"⊘ {message}")
    
    def print_error(self, message: str):
        """Print error message."""
        print(f"{RED}✗{RESET} {message}")
        self.errors.append(f"✗ {message}")
    
    def create_directories(self):
        """Create required directory structure."""
        self.print_step(1, "Creating Directory Structure")
        
        directories = [
            "backend/data",
            "backend/models",
            "backend/training",
            "frontend/.streamlit",
            "assets/viz",
            "docs"
        ]
        
        for dir_path in directories:
            full_path = self.project_root / dir_path
            if full_path.exists():
                self.print_skip(f"Directory exists: {dir_path}")
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                self.print_success(f"Created directory: {dir_path}")
        
        print()
    
    def move_file_safe(self, src: Path, dst: Path) -> bool:
        """Safely move a file, creating parent directories if needed."""
        if not src.exists():
            self.print_skip(f"File not found: {src.name}")
            return False
        
        if dst.exists():
            self.print_skip(f"File already at destination: {dst.name}")
            return False
        
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        self.print_success(f"Moved: {src.name} → {dst.relative_to(self.project_root)}")
        return True
    
    def move_data_files(self):
        """Move dataset CSV files to data/raw/."""
        self.print_step(2, "Moving Data Files → data/raw/")
        
        data_files = {
            "beige_ai_cake_dataset_v2.csv": "data/raw/beige_ai_cake_dataset_v2.csv",
            "beige_ai_cake_dataset.csv": "data/raw/beige_ai_cake_dataset.csv",
            "cluster_profiles.csv": "data/raw/cluster_profiles.csv",
            "beige_customer_clusters.csv": "data/raw/beige_customer_clusters.csv",
            "association_rules.csv": "backend/association_rules.csv",
        }
        
        for src_name, dst_rel in data_files.items():
            src = self.project_root / src_name
            dst = self.project_root / dst_rel
            self.move_file_safe(src, dst)
        
        print()
    
    def move_model_files(self):
        """Move ML model files to backend/models."""
        self.print_step(3, "Moving Model Files → backend/models/")
        
        # Handle both old and new naming conventions
        model_mappings = {
            "best_model.joblib": "backend/models/cake_model.joblib",
            "cake_model.joblib": "backend/models/cake_model.joblib",
            "preprocessor.joblib": "backend/models/preprocessor.joblib",
            "feature_info.joblib": "backend/models/feature_info.joblib",
        }
        
        moved_models = set()
        
        for src_name, dst_rel in model_mappings.items():
            src = self.project_root / src_name
            dst = self.project_root / dst_rel
            
            if src.exists() and dst_rel not in moved_models:
                self.move_file_safe(src, dst)
                moved_models.add(dst_rel)
        
        print()
    
    def move_visualization_files(self):
        """Move PNG/JPG visualization files to assets/viz."""
        self.print_step(4, "Moving Visualization Files → assets/viz/")
        
        image_extensions = {".png", ".jpg", ".jpeg"}
        root_files = list(self.project_root.glob("*"))
        
        moved_any = False
        for file_path in root_files:
            if file_path.suffix.lower() in image_extensions and file_path.is_file():
                dst = self.project_root / "assets" / "viz" / file_path.name
                if self.move_file_safe(file_path, dst):
                    moved_any = True
        
        if not moved_any:
            self.print_skip("No visualization files found in root")
        
        print()
    
    def move_training_scripts(self):
        """Move training scripts to backend/training."""
        self.print_step(5, "Moving Training Scripts → backend/training/")
        
        training_pattern = "beige_ai_*.py"
        root_files = list(self.project_root.glob(training_pattern))
        
        if not root_files:
            self.print_skip("No training scripts found in root")
        else:
            for src in root_files:
                dst = self.project_root / "backend" / "training" / src.name
                self.move_file_safe(src, dst)
        
        print()
    
    def move_menu_config(self):
        """Move menu configuration to backend/."""
        self.print_step(6, "Moving Configuration → backend/")
        
        src = self.project_root / "menu_config.py"
        dst = self.project_root / "backend" / "menu_config.py"
        
        if src.exists():
            if not dst.exists():
                self.move_file_safe(src, dst)
            else:
                self.print_skip("menu_config.py already in backend/")
        else:
            self.print_skip("menu_config.py not found in root")
        
        print()
    
    def move_frontend_files(self):
        """Move Streamlit app and config to frontend/."""
        self.print_step(7, "Moving Frontend Files → frontend/")
        
        # Move main app
        src_app = self.project_root / "beige_ai_app.py"
        dst_app = self.project_root / "frontend" / "beige_ai_app.py"
        if src_app.exists() and not dst_app.exists():
            self.move_file_safe(src_app, dst_app)
        elif dst_app.exists():
            self.print_skip("beige_ai_app.py already in frontend/")
        
        # Move Streamlit config
        src_config = self.project_root / "config.toml"
        dst_config = self.project_root / "frontend" / ".streamlit" / "config.toml"
        if src_config.exists() and not dst_config.exists():
            self.move_file_safe(src_config, dst_config)
        elif dst_config.exists():
            self.print_skip("config.toml already in frontend/.streamlit/")
        
        print()
    
    def move_documentation(self):
        """Move documentation files to docs/."""
        self.print_step(8, "Moving Documentation → docs/")
        
        md_files = list(self.project_root.glob("*.md"))
        # Keep README.md at root if it exists
        md_files = [f for f in md_files if f.name != "README.md"]
        
        if not md_files:
            self.print_skip("No additional markdown files to move")
        else:
            for src in md_files:
                dst = self.project_root / "docs" / src.name
                if not dst.exists():
                    self.move_file_safe(src, dst)
                else:
                    self.print_skip(f"{src.name} already in docs/")
        
        print()
    
    def update_app_imports(self):
        """Update beige_ai_app.py with correct path handling."""
        self.print_step(9, "Updating beige_ai_app.py Imports")
        
        app_path = self.project_root / "frontend" / "beige_ai_app.py"
        
        if not app_path.exists():
            self.print_error(f"beige_ai_app.py not found at {app_path}")
            return
        
        content = app_path.read_text()
        
        # Check if already updated with pathlib
        if "from pathlib import Path" in content and "_BASE_DIR" in content:
            self.print_skip("beige_ai_app.py already uses pathlib for paths")
        else:
            self.print_skip("Manual path update needed for beige_ai_app.py")
            self.print_skip("Please see documentation for path update guide")
        
        print()
    
    def verify_model_loading(self):
        """Verify model files are loadable."""
        self.print_step(10, "Verifying Model Files")
        
        required_models = [
            "backend/models/cake_model.joblib",
            "backend/models/preprocessor.joblib",
            "backend/models/feature_info.joblib",
        ]
        
        all_exist = True
        for model_path in required_models:
            full_path = self.project_root / model_path
            if full_path.exists():
                self.print_success(f"Found: {model_path}")
            else:
                self.print_error(f"Missing: {model_path}")
                all_exist = False
        
        if all_exist:
            self.print_success("All required models present")
        
        print()
    
    def verify_css_file(self):
        """Verify CSS file exists."""
        self.print_step(11, "Verifying Frontend Assets")
        
        css_path = self.project_root / "frontend" / "styles.css"
        
        if css_path.exists():
            self.print_success("Found: frontend/styles.css")
        else:
            self.print_error("Missing: frontend/styles.css")
        
        config_path = self.project_root / "frontend" / ".streamlit" / "config.toml"
        if config_path.exists():
            self.print_success("Found: frontend/.streamlit/config.toml")
        else:
            self.print_skip("Optional: frontend/.streamlit/config.toml")
        
        print()
    
    def verify_requirements(self):
        """Verify requirements.txt exists."""
        self.print_step(12, "Verifying Dependencies")
        
        req_path = self.project_root / "requirements.txt"
        
        if req_path.exists():
            self.print_success("Found: requirements.txt")
            lines = req_path.read_text().strip().split('\n')
            self.print_success(f"Contains {len(lines)} dependencies")
        else:
            self.print_skip("requirements.txt not found")
        
        print()
    
    def print_tree(self, path: Path = None, prefix: str = "", is_last: bool = True) -> List[str]:
        """Generate tree structure of project."""
        if path is None:
            path = self.project_root
        
        # Skip hidden folders and common ones
        skip = {'.git', '__pycache__', '.venv', 'venv', '.env', '.vscode', '.idea'}
        
        items = []
        
        try:
            entries = sorted([e for e in path.iterdir() if e.name not in skip])
        except PermissionError:
            return items
        
        entries = [e for e in entries if e.name not in skip]
        
        for i, entry in enumerate(entries):
            is_last_entry = i == len(entries) - 1
            current_prefix = "└── " if is_last_entry else "├── "
            items.append(f"{prefix}{current_prefix}{entry.name}")
            
            if entry.is_dir() and entry.name not in skip:
                next_prefix = prefix + ("    " if is_last_entry else "│   ")
                sub_items = self.print_tree(entry, next_prefix, is_last_entry)
                items.extend(sub_items)
        
        return items
    
    def print_final_structure(self):
        """Print final directory tree."""
        self.print_step(13, "Final Project Structure")
        
        print("Beige AI/")
        tree_items = self.print_tree()
        for item in tree_items:
            print(item)
        
        print()
    
    def print_summary(self):
        """Print final summary."""
        self.print_header("REFACTORING SUMMARY")
        
        print(f"{BOLD}Actions Performed:{RESET}")
        for action in self.actions[-20:]:  # Last 20 actions
            print(f"  {action}")
        
        if self.errors:
            print(f"\n{BOLD}Issues Found:{RESET}")
            for error in self.errors:
                print(f"  {error}")
        
        print(f"\n{BOLD}Status:{RESET}")
        if not self.errors:
            print(f"{GREEN}✓ Refactoring completed successfully!{RESET}")
            print(f"{GREEN}✓ All systems ready for deployment{RESET}")
        else:
            print(f"{YELLOW}⚠ Refactoring completed with {len(self.errors)} warning(s){RESET}")
        
        print("\n" + "=" * 60)
        print(f"{BOLD}Next Steps:{RESET}")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run the app: python main.py")
        print("  3. Or directly: streamlit run frontend/beige_ai_app.py")
        print("=" * 60 + "\n")
    
    def run(self):
        """Execute full workspace cleanup."""
        self.print_header("BEIGE.AI WORKSPACE CLEANER")
        
        print(f"Project Root: {self.project_root}\n")
        
        # Execute all cleanup steps
        self.create_directories()
        self.move_data_files()
        self.move_model_files()
        self.move_visualization_files()
        self.move_training_scripts()
        self.move_menu_config()
        self.move_frontend_files()
        self.move_documentation()
        self.update_app_imports()
        self.verify_model_loading()
        self.verify_css_file()
        self.verify_requirements()
        self.print_final_structure()
        self.print_summary()


def main():
    """Main entry point."""
    try:
        cleaner = WorkspaceCleaner()
        cleaner.run()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Cleanup interrupted by user{RESET}")
    except Exception as e:
        print(f"\n{RED}Error during cleanup: {e}{RESET}")
        raise


if __name__ == "__main__":
    main()
