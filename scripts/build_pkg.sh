#!/bin/bash
# Build Second Brain .pkg installer from .app bundle
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VERSION="1.0.0"
APP_NAME="Second Brain"
IDENTIFIER="com.secondbrain.app"

cd "$PROJECT_DIR"

echo "=== Building Second Brain.pkg ==="

# Check if .app bundle exists
if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "Error: dist/${APP_NAME}.app not found"
    echo "Run ./scripts/build_app.sh first"
    exit 1
fi

# Create pkg output directory
mkdir -p pkg

# Build .pkg installer using pkgbuild
echo "Creating .pkg installer..."
pkgbuild \
    --root "dist/" \
    --identifier "$IDENTIFIER" \
    --version "$VERSION" \
    --install-location "/Applications" \
    "pkg/SecondBrain-${VERSION}.pkg"

if [ -f "pkg/SecondBrain-${VERSION}.pkg" ]; then
    echo ""
    echo "✓ Built: pkg/SecondBrain-${VERSION}.pkg"
    echo ""
    PKG_SIZE=$(du -sh "pkg/SecondBrain-${VERSION}.pkg" | cut -f1)
    echo "Package size: $PKG_SIZE"
    echo ""
    echo "To install:"
    echo "  - Double-click: pkg/SecondBrain-${VERSION}.pkg"
    echo "  - Command line: sudo installer -pkg pkg/SecondBrain-${VERSION}.pkg -target /"
else
    echo "✗ Build failed"
    exit 1
fi
