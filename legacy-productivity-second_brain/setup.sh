#!/bin/bash
# Second Brain System - Installation Script for macOS
# Run with: chmod +x setup.sh && ./setup.sh

set -e

echo "================================================"
echo "  Second Brain System - Installation"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
VAULT_PATH="$HOME/SecondBrain"
SCRIPTS_PATH="$VAULT_PATH/_scripts"

# Step 1: Check Python and uv
echo -e "${YELLOW}[1/8] Checking Python and uv installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}  ✓ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}  ✗ Python 3 not found. Install with: brew install python3${NC}"
    exit 1
fi

if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    echo -e "${GREEN}  ✓ $UV_VERSION${NC}"
else
    echo -e "${RED}  ✗ uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi

# Step 2: Create Obsidian vault structure
echo -e "${YELLOW}[2/8] Creating Obsidian vault structure...${NC}"
mkdir -p "$VAULT_PATH"/{people,projects,ideas,admin,daily,_inbox_log,_scripts/.state}
echo -e "${GREEN}  ✓ Created $VAULT_PATH${NC}"

# Step 3: Copy scripts to vault
echo -e "${YELLOW}[3/8] Installing scripts...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -d "$SCRIPT_DIR/_scripts" ]; then
    cp "$SCRIPT_DIR/_scripts/"*.py "$SCRIPTS_PATH/"
    cp "$SCRIPT_DIR/_scripts/requirements.txt" "$SCRIPTS_PATH/"
    cp "$SCRIPT_DIR/_scripts/.env.example" "$SCRIPTS_PATH/"
    echo -e "${GREEN}  ✓ Scripts copied to $SCRIPTS_PATH${NC}"
else
    echo -e "${YELLOW}  ! Scripts already in place${NC}"
fi

# Step 4: Create virtual environment and install dependencies
echo -e "${YELLOW}[4/8] Creating virtual environment...${NC}"
cd "$SCRIPTS_PATH"
if [ ! -d ".venv" ]; then
    uv venv
    echo -e "${GREEN}  ✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}  ✓ Virtual environment already exists${NC}"
fi

echo -e "${YELLOW}[4/8] Installing Python dependencies...${NC}"
uv pip install -r requirements.txt --quiet
echo -e "${GREEN}  ✓ Dependencies installed${NC}"

# Step 5: Copy dashboard to vault root
echo -e "${YELLOW}[5/8] Setting up Obsidian dashboard...${NC}"
if [ ! -f "$VAULT_PATH/dashboard.md" ]; then
    if [ -f "$SCRIPT_DIR/dashboard.md" ]; then
        cp "$SCRIPT_DIR/dashboard.md" "$VAULT_PATH/"
    fi
fi
echo -e "${GREEN}  ✓ Dashboard ready${NC}"

# Step 6: Environment setup
echo -e "${YELLOW}[6/8] Environment configuration...${NC}"
if [ ! -f "$SCRIPTS_PATH/.env" ]; then
    cp "$SCRIPTS_PATH/.env.example" "$SCRIPTS_PATH/.env"
    echo -e "${YELLOW}  ! Created .env file - EDIT THIS FILE with your Slack credentials${NC}"
    echo -e "    $SCRIPTS_PATH/.env"
else
    echo -e "${GREEN}  ✓ .env already exists${NC}"
fi

# Step 7: Cron setup instructions
echo -e "${YELLOW}[7/8] Cron job setup...${NC}"
echo ""
echo -e "${YELLOW}To enable automatic processing, add these cron jobs:${NC}"
echo ""
echo "  Run: crontab -e"
echo ""
echo "  Then add these lines:"
echo "  ┌──────────────────────────────────────────────────────────────┐"
echo "  │ # Process Slack inbox every 2 minutes                       │"
echo "  │ */2 * * * * cd $SCRIPTS_PATH && source .env && uv run python3 process_inbox.py >> /tmp/wry_sb.log 2>&1"
echo "  │                                                              │"
echo "  │ # Health check every hour                                    │"
echo "  │ 0 * * * * cd $SCRIPTS_PATH && source .env && uv run python3 health_check.py --quiet >> /tmp/wry_sb-health.log 2>&1"
echo "  │                                                              │"
echo "  │ # Process fix commands every 5 minutes                       │"
echo "  │ */5 * * * * cd $SCRIPTS_PATH && source .env && uv run python3 fix_handler.py >> /tmp/wry_sb-fix.log 2>&1"
echo "  └──────────────────────────────────────────────────────────────┘"
echo ""

echo "================================================"
echo -e "${GREEN}  Installation Complete!${NC}"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Edit $SCRIPTS_PATH/.env with your Slack credentials"
echo "  2. Create a Slack app at https://api.slack.com/apps"
echo "  3. Install the Dataview plugin in Obsidian"
echo "  4. Open $VAULT_PATH in Obsidian"
echo "  5. Set up cron jobs (see above)"
echo ""
echo "For full documentation, see README.md"
