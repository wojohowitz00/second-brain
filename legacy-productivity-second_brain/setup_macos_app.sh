#!/bin/bash
# Setup script for Second Brain macOS App

set -e

echo "================================================"
echo "  Second Brain macOS App - Setup"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Check Python
echo -e "${YELLOW}[1/4] Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}  ✓ $PYTHON_VERSION${NC}"
else
    echo "  ✗ Python 3 not found. Install with: brew install python3"
    exit 1
fi

# Step 2: Install Python dependencies
echo -e "${YELLOW}[2/4] Installing Python dependencies...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/_scripts"

if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --quiet
    echo -e "${GREEN}  ✓ Dependencies installed${NC}"
else
    echo "  ✗ requirements.txt not found"
    exit 1
fi

# Step 3: Check Xcode
echo -e "${YELLOW}[3/4] Checking Xcode...${NC}"
if command -v xcodebuild &> /dev/null; then
    XCODE_VERSION=$(xcodebuild -version | head -1)
    echo -e "${GREEN}  ✓ $XCODE_VERSION${NC}"
else
    echo "  ⚠️  Xcode not found. Install from Mac App Store"
    echo "     Then create the Xcode project manually (see QUICKSTART.md)"
    exit 1
fi

# Step 4: Instructions
echo -e "${YELLOW}[4/4] Next steps:${NC}"
echo ""
echo "To create and run the macOS app:"
echo ""
echo "1. Open Xcode"
echo "2. File → New → Project"
echo "3. Choose: macOS → App"
echo "4. Product Name: SecondBrain"
echo "5. Interface: SwiftUI"
echo "6. Language: Swift"
echo "7. Save location: $SCRIPT_DIR/SecondBrain"
echo "8. Click Create"
echo ""
echo "9. In Xcode:"
echo "   - Delete default ContentView.swift and SecondBrainApp.swift"
echo "   - Right-click project → Add Files to 'SecondBrain'"
echo "   - Select: $SCRIPT_DIR/SecondBrain/SecondBrain/"
echo "   - Check 'Copy items if needed'"
echo "   - Click Add"
echo ""
echo "10. Build and Run (⌘R)"
echo ""
echo "See QUICKSTART.md for detailed configuration instructions."
echo ""
echo -e "${GREEN}Setup complete!${NC}"
