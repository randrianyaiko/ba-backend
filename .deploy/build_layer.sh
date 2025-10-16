#!/bin/bash
# File: build_layer.sh
# Purpose: Build AWS Lambda Python layer and move to terraform/

set -euo pipefail

# ----------------------------
# Layer root directory
# ----------------------------
LAYER_DIR="python"
LAYER_ZIP="layer.zip"
TERRAFORM_DIR="terraform"

# ----------------------------
# Clean previous build
# ----------------------------
rm -rf "$LAYER_DIR" "$LAYER_ZIP"
mkdir -p "$LAYER_DIR"

# ----------------------------
# Install dependencies from requirements.txt
# ----------------------------
echo "🔄 Installing Python dependencies..."
pip install --upgrade pip
pip install --target="$LAYER_DIR" -r requirements.txt

# ----------------------------
# Zip the layer
# ----------------------------
echo "🔄 Creating Lambda layer zip..."
zip -r9 "$LAYER_ZIP" "$LAYER_DIR"

# ----------------------------
# Move zip to Terraform folder
# ----------------------------
mv "$LAYER_ZIP" "$TERRAFORM_DIR/"

# ----------------------------
# Clean up build directory
# ----------------------------
rm -rf "$LAYER_DIR"

echo "✅ Lambda layer created and moved to $TERRAFORM_DIR/$LAYER_ZIP"
