#!/bin/bash

# Quick Run Script for NFI5MOHO Hyperopt
# Automatically fixes paths and runs hyperopt

echo "🎯 Ξεκινάω Hyperopt για NFI5MOHO_WIP strategy..."

# Παράμετροι
STRATEGY="NFI5MOHO_WIP"
CONFIG="user_data/config.json"
LOSS_FUNCTION="SharpeHyperOptLoss"
EPOCHS=500
TIMERANGE="20241201-20241217"
SPACES="buy sell"

echo "📊 Στρατηγική: $STRATEGY"
echo "⏰ Timerange: $TIMERANGE"
echo "🎲 Epochs: $EPOCHS"
echo "📈 Loss Function: $LOSS_FUNCTION"
echo "🔧 Spaces: $SPACES"

# Δημιουργία φακέλου για αποτελέσματα
mkdir -p hyperopt_results

# Εκτέλεση hyperopt
freqtrade hyperopt \
    --config "$CONFIG" \
    --strategy "$STRATEGY" \
    --hyperopt-loss "$LOSS_FUNCTION" \
    --epochs $EPOCHS \
    --spaces $SPACES \
    --timerange "$TIMERANGE"

echo "✅ Hyperopt ολοκληρώθηκε!"
echo "📁 Αποτελέσματα στο φάκελο: hyperopt_results/"
