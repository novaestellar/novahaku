#!/usr/bin/env bash
# Novahaku Installer for Linux/macOS
# Agent: Haku — Unified Security Research Agent
# https://github.com/novaestellar/novahaku

set -euo pipefail

HERMES_HOME="$HOME/.hermes/skills"
TARGET_DIR="$HERMES_HOME/novahaku"
REPO_URL="https://github.com/novaestellar/novahaku.git"

echo ""
echo "========================================"
echo "  Novahaku Installer (Haku Agent)"
echo "  Unified Security Research Agent"
echo "========================================"
echo ""

# Check git
if ! command -v git &> /dev/null; then
    echo "[ERROR] Git is not installed."
    echo "Install: sudo apt install git (Ubuntu/Debian)"
    echo "         brew install git (macOS)"
    exit 1
fi

# Check Python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "[WARN] Python not found. Some features may not work."
fi

# Create directory
mkdir -p "$HERMES_HOME"

# Remove existing installation
if [ -d "$TARGET_DIR" ]; then
    echo "[*] Removing existing installation..."
    rm -rf "$TARGET_DIR"
fi

# Clone repository
echo "[*] Cloning novahaku repository..."
git clone --depth 1 "$REPO_URL" "$TARGET_DIR"

if [ ! -f "$TARGET_DIR/SKILL.md" ]; then
    echo "[ERROR] Installation failed: SKILL.md not found"
    exit 1
fi

# Install Python dependencies
if [ -n "$PYTHON_CMD" ]; then
    echo "[*] Installing Python dependencies..."
    "$PYTHON_CMD" -m pip install --quiet pycryptodome requests 2>/dev/null || true
fi

# Cleanup git metadata
rm -rf "$TARGET_DIR/.git"

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "Location: $TARGET_DIR"
echo ""
echo "Quick Start:"
echo "  # Web testing"
echo "  python3 $TARGET_DIR/testing/scripts/webtest.py https://target.com"
echo ""
echo "  # Prompt techniques"
echo "  cat $TARGET_DIR/techniques/methods/01-boundary/m-01003-delimiter-injection.md"
echo ""
echo "  # Reframe"
echo "  python3 $TARGET_DIR/reframe/dmf_cli.py \"text\" --fresh"
echo ""
