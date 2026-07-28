#!/bin/bash
# Check if .env file has all required variables from .env.example

set -e

BACKEND_DIR="backend"
ENV_FILE="$BACKEND_DIR/.env"
ENV_EXAMPLE="$BACKEND_DIR/.env.example"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found. Copy $ENV_EXAMPLE to $ENV_FILE first."
    exit 1
fi

echo "Checking $ENV_FILE against $ENV_EXAMPLE..."

# Read required variables from .env.example (lines without # and containing =)
required_vars=$(grep -E '^[^#]*=' "$ENV_EXAMPLE" | cut -d= -f1 | tr -d ' ')

missing_vars=()
for var in $required_vars; do
    if ! grep -q "^${var}=" "$ENV_FILE"; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -eq 0 ]; then
    echo "✓ All required variables are set in $ENV_FILE"
    exit 0
else
    echo "✗ Missing variables in $ENV_FILE:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Add these variables to $ENV_FILE or copy from $ENV_EXAMPLE"
    exit 1
fi
