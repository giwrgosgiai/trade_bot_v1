#!/usr/bin/env python3
"""
Test script to verify project setup
"""
import sys
import os
from pathlib import Path

# Add freqtrade to path
sys.path.insert(0, str(Path("/Users/georgegiailoglou/Documents/GitHub/trade_bot_v1/freqtrade")))

def test_imports():
    """Test if we can import freqtrade"""
    try:
        import freqtrade
        print("✅ FreqTrade import successful")
        return True
    except ImportError as e:
        print(f"❌ FreqTrade import failed: {e}")
        return False

def test_strategy():
    """Test if strategy exists"""
    strategy_path = Path("/Users/georgegiailoglou/Documents/GitHub/trade_bot_v1/user_data/strategies/NFI5MOHO_WIP.py")
    if strategy_path.exists():
        print("✅ Strategy file exists")
        return True
    else:
        print("❌ Strategy file not found")
        return False

def test_config():
    """Test if config exists"""
    config_path = Path("/Users/georgegiailoglou/Documents/GitHub/trade_bot_v1/configs/hyperopt_config.json")
    if config_path.exists():
        print("✅ Config file exists")
        return True
    else:
        print("❌ Config file not found")
        return False

def main():
    print("🧪 Testing project setup...")
    print(f"📁 Project root: /Users/georgegiailoglou/Documents/GitHub/trade_bot_v1")

    tests = [
        ("FreqTrade Import", test_imports),
        ("Strategy File", test_strategy),
        ("Config File", test_config)
    ]

    passed = 0
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1

    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All tests passed! Project is ready to use.")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    main()
