#!/usr/bin/env python3
"""
Pre-Training Checklist & Configuration Wizard

This file helps verify everything is ready before training starts.
Run this to make sure all dependencies, data, and directories are set up correctly.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class PreTrainingChecklist:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []
        self.errors = []
    
    def print_header(self, text):
        print(f"\n{'='*70}")
        print(f"  {text}")
        print(f"{'='*70}\n")
    
    def check_python(self):
        """Check Python version"""
        print("📋 Checking Python Environment...")
        version = sys.version_info
        
        print(f"   Python {version.major}.{version.minor}.{version.micro}")
        
        if version.major >= 3 and version.minor >= 8:
            print("   ✅ Python 3.8+ (OK)")
            self.checks_passed += 1
            return True
        else:
            print("   ❌ Python 3.8+ required")
            self.errors.append("Python version < 3.8")
            self.checks_failed += 1
            return False
    
    def check_directories(self):
        """Check and create required directories"""
        print("\n📁 Checking Directory Structure...")
        
        required_dirs = [
            (self.base_dir / "backend" / "data", "Data directory"),
            (self.base_dir / "backend" / "models", "Models output"),
            (self.base_dir / "backend" / "training", "Training scripts"),
            (self.base_dir / "docs", "Documentation"),
        ]
        
        all_good = True
        for dir_path, desc in required_dirs:
            if dir_path.exists():
                print(f"   ✅ {desc}: {dir_path}")
                self.checks_passed += 1
            else:
                print(f"   ⚠️  {desc}: {dir_path} (will be created if needed)")
                dir_path.mkdir(parents=True, exist_ok=True)
                self.warnings.append(f"Created {desc}")
        
        return all_good
    
    def check_data(self):
        """Check if training data exists"""
        print("\n📊 Checking Training Data...")
        
        data_dir = self.base_dir / "backend" / "data"
        dataset_file = data_dir / "beige_ai_cake_dataset_v2.csv"
        
        if dataset_file.exists():
            # Check file size and basic validity
            file_size = dataset_file.stat().st_size
            size_mb = file_size / (1024 * 1024)
            
            print(f"   ✅ Dataset found: {dataset_file}")
            print(f"      Size: {size_mb:.2f} MB")
            
            # Try to read first few lines
            try:
                with open(dataset_file, 'r') as f:
                    headers = f.readline().strip().split(',')
                    print(f"      Columns: {len(headers)}")
                    print(f"      Sample columns: {', '.join(headers[:5])}")
                
                self.checks_passed += 1
                return True
            except Exception as e:
                print(f"   ❌ Error reading dataset: {e}")
                self.errors.append(f"Dataset read error: {e}")
                self.checks_failed += 1
                return False
        else:
            print(f"   ❌ Dataset not found: {dataset_file}")
            print(f"      Expected: beige_ai_cake_dataset_v2.csv")
            self.errors.append("Training data not found")
            self.checks_failed += 1
            return False
    
    def check_packages(self):
        """Check required Python packages"""
        print("\n📦 Checking Python Packages...")
        
        packages = [
            ('numpy', 'NumPy'),
            ('pandas', 'Pandas'),
            ('sklearn', 'scikit-learn'),
            ('matplotlib', 'Matplotlib'),
            ('joblib', 'joblib'),
        ]
        
        all_good = True
        for module_name, display_name in packages:
            try:
                __import__(module_name)
                print(f"   ✅ {display_name}")
                self.checks_passed += 1
            except ImportError:
                print(f"   ❌ {display_name} (MISSING)")
                self.warnings.append(f"Install {display_name}: pip install {module_name}")
                self.checks_failed += 1
                all_good = False
        
        return all_good
    
    def check_scripts(self):
        """Check if training scripts exist"""
        print("\n🐍 Checking Training Scripts...")
        
        scripts = [
            (self.base_dir / "backend" / "training" / "compare_models.py", "Main training script"),
            (self.base_dir / "backend" / "training" / "run.py", "Setup & runner script"),
            (self.base_dir / "backend" / "training" / "requirements.txt", "Dependencies"),
        ]
        
        all_good = True
        for script_path, desc in scripts:
            if script_path.exists():
                file_size = script_path.stat().st_size
                print(f"   ✅ {desc}: {file_size} bytes")
                self.checks_passed += 1
            else:
                print(f"   ❌ {desc}: NOT FOUND")
                self.errors.append(f"Missing: {script_path}")
                self.checks_failed += 1
                all_good = False
        
        return all_good
    
    def check_documentation(self):
        """Check if documentation exists"""
        print("\n📖 Checking Documentation...")
        
        docs = [
            (self.base_dir / "docs" / "README.md", "Documentation index"),
            (self.base_dir / "docs" / "QUICK_REFERENCE.md", "Quick reference"),
            (self.base_dir / "docs" / "COMPLETE_SUMMARY.md", "Complete summary"),
            (self.base_dir / "docs" / "MODEL_USAGE_GUIDE.md", "Usage guide"),
            (self.base_dir / "docs" / "MODEL_COMPARISON_GUIDE.md", "Comparison guide"),
        ]
        
        found_count = 0
        for doc_path, desc in docs:
            if doc_path.exists():
                print(f"   ✅ {desc}")
                self.checks_passed += 1
                found_count += 1
            else:
                print(f"   ⚠️  {desc}: Not found")
                self.warnings.append(f"Missing doc: {desc}")
        
        return found_count >= 3
    
    def estimate_memory(self):
        """Estimate memory requirements"""
        print("\n💾 Memory Requirements Estimate...")
        
        data_dir = self.base_dir / "backend" / "data"
        dataset_file = data_dir / "beige_ai_cake_dataset_v2.csv"
        
        if dataset_file.exists():
            file_size = dataset_file.stat().st_size
            # Rough estimate: loaded data uses ~2-3x file size
            estimated_ram = (file_size * 2.5) / (1024 * 1024)
            
            print(f"   📊 Dataset size: {file_size / (1024*1024):.2f} MB")
            print(f"   🧠 Estimated RAM needed: {estimated_ram:.0f} MB")
            print(f"   ⏱️  Estimated training time: 3-5 minutes")
            print(f"   ✅ Likely available: {estimated_ram < 2048}")
        else:
            print(f"   ⚠️  Cannot estimate - dataset not found")
    
    def summarize(self):
        """Print summary and recommendations"""
        total = self.checks_passed + self.checks_failed
        passed_pct = (self.checks_passed / total * 100) if total > 0 else 0
        
        self.print_header(f"Summary: {self.checks_passed}/{total} checks passed ({passed_pct:.0f}%)")
        
        if self.checks_failed == 0:
            print("✅ ALL CHECKS PASSED - Ready to train!")
            return True
        else:
            print(f"⚠️  {self.checks_failed} check(s) need attention")
            
            if self.errors:
                print("\n🔴 ERRORS (must fix):")
                for error in self.errors:
                    print(f"   • {error}")
            
            if self.warnings:
                print("\n🟡 WARNINGS (should fix):")
                for warning in self.warnings:
                    print(f"   • {warning}")
            
            return False
    
    def generate_report(self):
        """Generate a detailed checklist report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
            'checks_passed': self.checks_passed,
            'checks_failed': self.checks_failed,
            'errors': self.errors,
            'warnings': self.warnings,
            'ready_to_train': self.checks_failed == 0,
        }
        
        report_path = self.base_dir / "docs" / "pre_training_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved: {report_path}")
    
    def run_all(self):
        """Run all checks"""
        self.print_header("🏁 PRE-TRAINING CHECKLIST")
        print("Verifying environment and dependencies...\n")
        
        self.check_python()
        self.check_directories()
        self.check_data()
        self.check_packages()
        self.check_scripts()
        self.check_documentation()
        self.estimate_memory()
        
        ready = self.summarize()
        self.generate_report()
        
        print("\n" + "="*70)
        
        if ready:
            print("\n📊 Next Step: Run the training")
            print("   python backend/training/run.py")
            print("   or")
            print("   python backend/training/compare_models.py")
            return 0
        else:
            print("\n⚠️  Fix the issues above, then run this checklist again.")
            print("   python docs/pre_training_checklist.py")
            return 1


def main():
    checklist = PreTrainingChecklist()
    exit_code = checklist.run_all()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
