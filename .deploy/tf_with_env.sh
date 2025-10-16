#!/bin/bash
# File: .deploy/load_tf_vars.sh
# Purpose: Load .env variables safely and pass them to Terraform in ./terraform

set -euo pipefail

# Define paths relative to this script
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"

# --- Safety checks ---
if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ .env file not found at $ENV_FILE"
  exit 1
fi

if [[ ! -d "$TERRAFORM_DIR" ]]; then
  echo "❌ Terraform directory not found at $TERRAFORM_DIR"
  exit 1
fi

# --- Load .env manually (handles spaces, comments, etc.) ---
echo "🔄 Loading environment variables from $ENV_FILE..."
while IFS='=' read -r key value; do
  # Trim spaces
  key=$(echo "$key" | xargs)
  value=$(echo "$value" | xargs)

  # Skip empty lines and comments
  [[ -z "$key" || "$key" == \#* ]] && continue

  # Export cleaned variable
  export "$key=$value"
done < "$ENV_FILE"

echo "✅ Environment variables loaded."

# --- Map uppercase vars -> Terraform-style TF_VAR_lowercase vars ---
echo "🔄 Mapping environment variables to Terraform TF_VAR_* ..."
while IFS='=' read -r key value; do
  # Skip invalid or commented lines
  [[ -z "$key" || "$key" == \#* ]] && continue

  # Normalize key to lowercase
  lowercase_key=$(echo "$key" | tr '[:upper:]' '[:lower:]' | tr -d ' ')
  eval "export TF_VAR_${lowercase_key}=\"\${$key}\""
done < <(grep -v '^#' "$ENV_FILE")

echo "✅ Terraform variables exported."

# --- Run Terraform ---
cd "$TERRAFORM_DIR"
echo "🏗️ Running Terraform command: terraform $*"
terraform "$@"
