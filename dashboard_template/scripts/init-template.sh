#!/bin/bash
# Initialize template: copy .env.example to .env and print next steps

set -e

echo "Initializing Analytics Dashboard Template..."
echo ""

# Copy backend .env.example to .env
BACKEND_DIR="backend"
if [ ! -f "$BACKEND_DIR/.env" ]; then
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
    echo "✓ Created $BACKEND_DIR/.env from .env.example"
else
    echo "! $BACKEND_DIR/.env already exists (skipping)"
fi

# Copy frontend .env.example to .env
FRONTEND_DIR="frontend"
if [ -f "$FRONTEND_DIR/.env.example" ] && [ ! -f "$FRONTEND_DIR/.env" ]; then
    cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env"
    echo "✓ Created $FRONTEND_DIR/.env from .env.example"
else
    echo "! $FRONTEND_DIR/.env already exists or .env.example not found (skipping)"
fi

echo ""
echo "Next steps:"
echo "1. Edit backend/.env to set your API key and other variables"
echo "2. Edit frontend/.env to set VITE_DASHBOARD_API_URL"
echo "3. Install backend dependencies: cd backend && uv sync"
echo "4. Install frontend dependencies: cd frontend && npm install"
echo "5. Start backend: cd backend && uv run python -m app.main"
echo "6. Start frontend: cd frontend && npm run dev"
echo ""
echo "For more information, see README.md"
