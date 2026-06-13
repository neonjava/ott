#!/bin/bash
# GenOTT Setup Script — Fedora
# Run once: bash setup.sh

set -e

echo ""
echo "══════════════════════════════════"
echo "  GenOTT — Phase 2 Setup"
echo "══════════════════════════════════"
echo ""

# 1. Check Python
if ! command -v python3 &>/dev/null; then
  echo "[!] Python3 not found. Installing..."
  sudo dnf install -y python3 python3-pip
fi

echo "[✓] Python: $(python3 --version)"

# 2. Virtual environment
if [ ! -d "venv" ]; then
  echo "[*] Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate
echo "[✓] Virtual environment active"

# 3. Install dependencies
echo "[*] Installing dependencies..."
pip install -q -r requirements.txt
echo "[✓] Dependencies installed"

# 4. Check .env
if grep -q "your_api_key_here" .env; then
  echo ""
  echo "════════════════════════════════════════"
  echo "  ACTION REQUIRED: Set your API key"
  echo "════════════════════════════════════════"
  echo "  Edit the .env file and replace:"
  echo "  ANTHROPIC_API_KEY=your_api_key_here"
  echo "  with your actual key from:"
  echo "  https://console.anthropic.com"
  echo "════════════════════════════════════════"
  echo ""
  read -p "Press Enter after you've set the API key..."
fi

# 5. Run
echo ""
echo "[*] Starting GenOTT..."
echo "[✓] Open http://localhost:5000 in your browser"
echo ""
python3 app.py
