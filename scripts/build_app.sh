#!/bin/bash
# Build Second Brain .app bundle using PyInstaller
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== Building Second Brain.app ==="
echo "Project directory: $PROJECT_DIR"

# Clean previous builds
echo ""
echo "Cleaning previous builds..."
rm -rf build dist

# Add _scripts to Python path for imports
export PYTHONPATH="$PROJECT_DIR/backend/_scripts:$PYTHONPATH"

# Build .app bundle using PyInstaller
echo ""
echo "Building .app bundle with PyInstaller..."
cd "$PROJECT_DIR/backend"
uv run pyinstaller ../SecondBrain.spec --noconfirm

# Move dist to project root
cd "$PROJECT_DIR"
if [ -d "backend/dist" ]; then
    mv backend/dist .
fi

# Also move build directory
if [ -d "backend/build" ]; then
    mv backend/build .
fi

# Verify bundle exists
echo ""
if [ -d "dist/Second Brain.app" ]; then
    echo "✓ Built: dist/Second Brain.app"
    echo ""
    echo "Bundle size: $(du -sh 'dist/Second Brain.app' | cut -f1)"
    echo ""
    echo "To test: open 'dist/Second Brain.app'"
else
    echo "✗ Build failed - no .app bundle created"
    ls -la dist/ 2>/dev/null || echo "dist/ directory not found"
    exit 1
fi
