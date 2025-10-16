#!/bin/bash
# File: build_layer.sh
# Purpose: Build AWS Lambda Python layer and move to terraform/
# Optimized to rebuild only if dependencies change

set -euo pipefail

# ----------------------------
# Configuration
# ----------------------------
LAYER_DIR="python"
LAYER_ZIP="layer.zip"
TERRAFORM_DIR="terraform"
REQ_FILE="requirements.txt"
HASH_FILE=".layer_hash"

# ----------------------------
# Compute hash of dependencies
# ----------------------------
NEW_HASH=$(md5sum "$REQ_FILE" | awk '{print $1}')
if [[ -f "$HASH_FILE" ]]; then
    OLD_HASH=$(cat "$HASH_FILE")
else
    OLD_HASH=""
fi

if [[ "$NEW_HASH" == "$OLD_HASH" && -f "$TERRAFORM_DIR/$LAYER_ZIP" ]]; then
    echo "✅ Dependencies unchanged. Skipping Lambda layer build."
    exit 0
fi

# ----------------------------
# Clean previous build
# ----------------------------
rm -rf "$LAYER_DIR" "$LAYER_ZIP"
mkdir -p "$LAYER_DIR"

# ----------------------------
# Install dependencies
# ----------------------------
echo "🔄 Installing Python dependencies..."
pip install --upgrade pip
pip install --target="$LAYER_DIR" -r "$REQ_FILE"

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

# ----------------------------
# Save hash
# ----------------------------
echo "$NEW_HASH" > "$HASH_FILE"

echo "✅ Lambda layer created and moved to $TERRAFORM_DIR/$LAYER_ZIP"
