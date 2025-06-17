#!/usr/bin/env python3

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path.cwd() / "user_data" / "strategies"))

try:
    from NFI5MOHO_WIP import NFI5MOHO_WIP
    print("✅ Strategy imported successfully!")

    # Create instance
    strategy = NFI5MOHO_WIP()
    print(f"✅ Strategy instance created: {strategy.__class__.__name__}")

    # Check some basic attributes
    print(f"📊 Timeframe: {strategy.timeframe}")
    print(f"🛑 Stoploss: {strategy.stoploss}")
    print(f"📈 ROI: {strategy.minimal_roi}")

except ImportError as e:
    print(f"❌ Import error: {e}")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")