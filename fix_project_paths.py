#!/usr/bin/env python3
"""
Project Path Fixer Script
Φτιάχνει όλα τα paths και dependencies που έχουν καταστραφεί μετά την αλλαγή του directory name
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
import sqlite3
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fix_project.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProjectPathFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.freqtrade_dir = self.project_root / "freqtrade"
        self.user_data_dir = self.project_root / "user_data"
        self.configs_dir = self.project_root / "configs"
        self.scripts_dir = self.project_root / "scripts"
        self.logs_dir = self.project_root / "logs"

        logger.info(f"🔧 Project root: {self.project_root}")

    def check_project_structure(self):
        """Ελέγχει αν υπάρχουν όλα τα απαραίτητα directories"""
        logger.info("📁 Checking project structure...")

        required_dirs = [
            self.freqtrade_dir,
            self.user_data_dir,
            self.configs_dir,
            self.scripts_dir
        ]

        missing_dirs = []
        for dir_path in required_dirs:
            if not dir_path.exists():
                missing_dirs.append(dir_path)
                logger.warning(f"❌ Missing directory: {dir_path}")
            else:
                logger.info(f"✅ Found directory: {dir_path}")

        return len(missing_dirs) == 0

    def create_missing_directories(self):
        """Δημιουργεί τα directories που λείπουν"""
        logger.info("📂 Creating missing directories...")

        dirs_to_create = [
            self.logs_dir,
            self.user_data_dir / "data",
            self.user_data_dir / "logs",
            self.user_data_dir / "hyperopt_results",
            self.user_data_dir / "backtest_results",
            self.user_data_dir / "plot"
        ]

        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created/verified directory: {dir_path}")

    def fix_hyperopt_config(self):
        """Φτιάχνει το hyperopt config file"""
        logger.info("⚙️ Fixing hyperopt configuration...")

        config_file = self.configs_dir / "hyperopt_config.json"

        if not config_file.exists():
            logger.error(f"❌ Config file not found: {config_file}")
            return False

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Fix paths in config
            config["strategy_path"] = "user_data/strategies/"
            config["user_data_dir"] = "user_data"
            config["db_url"] = "sqlite:///user_data/hyperopt_nfi5moho.sqlite"
            config["logfile"] = "logs/hyperopt_nfi5moho.log"

            # Ensure datadir is correct
            if "datadir" not in config:
                config["datadir"] = "user_data/data"

            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)

            logger.info("✅ Fixed hyperopt configuration")
            return True

        except Exception as e:
            logger.error(f"❌ Error fixing hyperopt config: {e}")
            return False

    def fix_run_scripts(self):
        """Φτιάχνει τα run scripts"""
        logger.info("🔧 Fixing run scripts...")

        # Fix run_hyperopt_nfi5moho.sh
        bash_script = self.project_root / "run_hyperopt_nfi5moho.sh"
        if bash_script.exists():
            content = bash_script.read_text()
            # Replace the python command to use correct path
            content = content.replace(
                "python3 scripts/run_hyperopt_nfi5moho.py",
                f"cd {self.project_root} && python3 scripts/run_hyperopt_nfi5moho.py"
            )
            bash_script.write_text(content)
            bash_script.chmod(0o755)  # Make executable
            logger.info("✅ Fixed run_hyperopt_nfi5moho.sh")

        # Fix Python hyperopt script
        python_script = self.scripts_dir / "run_hyperopt_nfi5moho.py"
        if python_script.exists():
            content = python_script.read_text()

            # Fix the freqtrade path
            content = content.replace(
                'sys.path.append(str(Path(__file__).parent.parent / "freqtrade"))',
                f'sys.path.append(str(Path("{self.freqtrade_dir}")))'
            )

            # Fix config path
            content = content.replace(
                'self.config_file = "configs/hyperopt_config.json"',
                f'self.config_file = "{self.configs_dir / "hyperopt_config.json"}"'
            )

            python_script.write_text(content)
            logger.info("✅ Fixed run_hyperopt_nfi5moho.py")

    def check_freqtrade_installation(self):
        """Ελέγχει αν το freqtrade είναι εγκατεστημένο σωστά"""
        logger.info("🔍 Checking FreqTrade installation...")

        # Check if freqtrade directory exists and has the main module
        freqtrade_main = self.freqtrade_dir / "freqtrade" / "__main__.py"
        if not freqtrade_main.exists():
            logger.warning("❌ FreqTrade main module not found")
            return False

        # Check if we can import freqtrade
        try:
            sys.path.insert(0, str(self.freqtrade_dir))
            import freqtrade
            logger.info("✅ FreqTrade can be imported successfully")
            return True
        except ImportError as e:
            logger.error(f"❌ Cannot import FreqTrade: {e}")
            return False

    def fix_strategy_paths(self):
        """Φτιάχνει τα paths στις strategies"""
        logger.info("📈 Fixing strategy paths...")

        strategy_file = self.user_data_dir / "strategies" / "NFI5MOHO_WIP.py"
        if not strategy_file.exists():
            logger.error(f"❌ Strategy file not found: {strategy_file}")
            return False

        logger.info("✅ Strategy file exists")
        return True

    def create_test_script(self):
        """Δημιουργεί ένα test script για να ελέγξει αν όλα δουλεύουν"""
        logger.info("🧪 Creating test script...")

        test_script_content = f'''#!/usr/bin/env python3
"""
Test script to verify project setup
"""
import sys
import os
from pathlib import Path

# Add freqtrade to path
sys.path.insert(0, str(Path("{self.freqtrade_dir}")))

def test_imports():
    """Test if we can import freqtrade"""
    try:
        import freqtrade
        print("✅ FreqTrade import successful")
        return True
    except ImportError as e:
        print(f"❌ FreqTrade import failed: {{e}}")
        return False

def test_strategy():
    """Test if strategy exists"""
    strategy_path = Path("{self.user_data_dir}/strategies/NFI5MOHO_WIP.py")
    if strategy_path.exists():
        print("✅ Strategy file exists")
        return True
    else:
        print("❌ Strategy file not found")
        return False

def test_config():
    """Test if config exists"""
    config_path = Path("{self.configs_dir}/hyperopt_config.json")
    if config_path.exists():
        print("✅ Config file exists")
        return True
    else:
        print("❌ Config file not found")
        return False

def main():
    print("🧪 Testing project setup...")
    print(f"📁 Project root: {Path.cwd()}")

    tests = [
        ("FreqTrade Import", test_imports),
        ("Strategy File", test_strategy),
        ("Config File", test_config)
    ]

    passed = 0
    for test_name, test_func in tests:
        print(f"\\n🔍 Testing {{test_name}}...")
        if test_func():
            passed += 1

    print(f"\\n📊 Results: {{passed}}/{{len(tests)}} tests passed")

    if passed == len(tests):
        print("🎉 All tests passed! Project is ready to use.")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    main()
'''

        test_script = self.project_root / "test_project_setup.py"
        test_script.write_text(test_script_content)
        test_script.chmod(0o755)
        logger.info("✅ Created test script")

    def create_quick_run_script(self):
        """Δημιουργεί ένα απλό script για γρήγορο τρέξιμο"""
        logger.info("🚀 Creating quick run script...")

        quick_run_content = f'''#!/bin/bash

# Quick Run Script for NFI5MOHO Hyperopt
# Automatically fixes paths and runs hyperopt

echo "🎯 NFI5MOHO Quick Run Script"
echo "============================"

# Change to project directory
cd "{self.project_root}"

# Check if everything is set up
echo "🔍 Checking project setup..."
python3 test_project_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Project setup OK, starting hyperopt..."
    echo ""

    # Run hyperopt
    python3 scripts/run_hyperopt_nfi5moho.py
else
    echo ""
    echo "❌ Project setup failed. Please run fix_project_paths.py first."
    exit 1
fi
'''

        quick_run_script = self.project_root / "quick_run_hyperopt.sh"
        quick_run_script.write_text(quick_run_content)
        quick_run_script.chmod(0o755)
        logger.info("✅ Created quick run script")

    def run_full_fix(self):
        """Τρέχει όλες τις διορθώσεις"""
        logger.info("🔧 Starting full project fix...")

        steps = [
            ("Checking project structure", self.check_project_structure),
            ("Creating missing directories", self.create_missing_directories),
            ("Fixing hyperopt configuration", self.fix_hyperopt_config),
            ("Fixing run scripts", self.fix_run_scripts),
            ("Checking FreqTrade installation", self.check_freqtrade_installation),
            ("Fixing strategy paths", self.fix_strategy_paths),
            ("Creating test script", self.create_test_script),
            ("Creating quick run script", self.create_quick_run_script)
        ]

        success_count = 0
        for step_name, step_func in steps:
            logger.info(f"\\n🔄 {step_name}...")
            try:
                if step_func():
                    success_count += 1
                    logger.info(f"✅ {step_name} completed successfully")
                else:
                    logger.warning(f"⚠️ {step_name} completed with warnings")
            except Exception as e:
                logger.error(f"❌ {step_name} failed: {e}")

        logger.info(f"\\n📊 Fix Summary: {success_count}/{len(steps)} steps completed successfully")

        if success_count >= len(steps) - 1:  # Allow one step to fail
            logger.info("🎉 Project fix completed successfully!")
            logger.info("\\n📋 Next steps:")
            logger.info("1. Run: python3 test_project_setup.py")
            logger.info("2. If tests pass, run: ./quick_run_hyperopt.sh")
            logger.info("3. Or manually run: python3 scripts/run_hyperopt_nfi5moho.py")
            return True
        else:
            logger.error("❌ Project fix completed with errors. Check the log above.")
            return False

def main():
    """Main function"""
    print("🔧 Project Path Fixer")
    print("=" * 50)

    fixer = ProjectPathFixer()
    success = fixer.run_full_fix()

    if success:
        print("\\n🎉 Project has been fixed successfully!")
        print("You can now run your hyperopt scripts.")
    else:
        print("\\n❌ Some issues remain. Check the log file: fix_project.log")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())