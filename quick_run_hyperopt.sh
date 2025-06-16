#!/bin/bash

# Quick Run Script for NFI5MOHO Hyperopt
# Automatically fixes paths and runs hyperopt

echo "🎯 NFI5MOHO Quick Run Script"
echo "============================"

# Change to project directory
cd "/Users/georgegiailoglou/Documents/GitHub/trade_bot_v1"

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
