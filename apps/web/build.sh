#!/bin/bash

# Build script for Svelte web app
# This script installs dependencies and builds the app for production

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building Svelte web app..."

# Check if API URL is provided
if [ -z "$VITE_API_URL" ]; then
    echo "Warning: VITE_API_URL environment variable is not set."
    echo "The app will use the default API URL from client.ts"
    echo "To set it, run: export VITE_API_URL=https://your-api-url.com"
fi

# Install dependencies
echo "Installing dependencies..."
pnpm install

# Build the app
echo "Building production bundle..."
pnpm build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "Error: Build failed - dist directory not found"
    exit 1
fi

echo "Build complete! Output is in the dist/ directory."
echo "Ready for deployment to S3."

