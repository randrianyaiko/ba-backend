#!/bin/bash
# File: build_lambda_code.sh
# Purpose: Package Lambda application code and move zip to terraform/

set -euo pipefail

# ----------------------------
# Variables
# ----------------------------
FUNCTION_NAME="myLambda"
ZIP_FILE="code.zip"
TERRAFORM_DIR="terraform"

# ----------------------------
# Clean previous zip
# ----------------------------
rm -f "$ZIP_FILE"

# ----------------------------
# Package Lambda source code
# ----------------------------
echo "📦 Zipping Lambda source files..."
# Include your app directories / main lambda file here
zip -r "$ZIP_FILE" app src lambda_function.py > /dev/null

# ----------------------------
# Move zip to Terraform folder
# ----------------------------
mv "$ZIP_FILE" "$TERRAFORM_DIR/"

echo "✅ Lambda code packaged and moved to $TERRAFORM_DIR/$ZIP_FILE"
