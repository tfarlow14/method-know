#!/bin/bash

# Build script for Lambda deployment package
# This script prepares the code and dependencies for SAM deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building Lambda deployment package..."

# Create build directory
BUILD_DIR="$SCRIPT_DIR/.aws-sam"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Install dependencies in a Lambda-compatible location
echo "Installing dependencies..."
pip install -r requirements.txt -t "$BUILD_DIR" --upgrade

# Copy application code
echo "Copying application code..."
cp -r "$SCRIPT_DIR"/*.py "$BUILD_DIR/" 2>/dev/null || true
cp -r "$SCRIPT_DIR/models" "$BUILD_DIR/" 2>/dev/null || true
cp -r "$SCRIPT_DIR/routers" "$BUILD_DIR/" 2>/dev/null || true
cp -r "$SCRIPT_DIR/services" "$BUILD_DIR/" 2>/dev/null || true
cp -r "$SCRIPT_DIR/utils" "$BUILD_DIR/" 2>/dev/null || true

# Remove unnecessary files
find "$BUILD_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true

echo "Build complete! Ready for SAM deployment."
echo "Run 'sam build' to build with SAM, or 'sam deploy' to build and deploy."

