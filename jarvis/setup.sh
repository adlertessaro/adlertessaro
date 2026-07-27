#!/bin/bash
# Jarvis — Setup Script for macOS
set -e

echo "╔══════════════════════════════════════════╗"
echo "║       J.A.R.V.I.S. — Setup              ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install it with: brew install python"
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"

# Check brew
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Install it from https://brew.sh"
    exit 1
fi
echo "✓ Homebrew found"

# Install portaudio (required by PyAudio)
echo ""
echo "→ Installing system dependencies..."
brew install portaudio 2>/dev/null || echo "  portaudio already installed"

# Create virtual environment
echo ""
echo "→ Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
echo ""
echo "→ Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Download Vosk model
VOSK_DIR="$HOME/.jarvis"
MODEL_DIR="$VOSK_DIR/vosk-model-pt"
MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip"

if [ ! -d "$MODEL_DIR" ]; then
    echo ""
    echo "→ Downloading Portuguese speech model (~40MB)..."
    mkdir -p "$VOSK_DIR"
    cd "$VOSK_DIR"
    curl -LO "$MODEL_URL"
    unzip -q vosk-model-small-pt-0.3.zip
    mv vosk-model-small-pt-0.3 vosk-model-pt
    rm vosk-model-small-pt-0.3.zip
    cd -
    echo "✓ Speech model installed at $MODEL_DIR"
else
    echo "✓ Speech model already exists at $MODEL_DIR"
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║       Setup complete!                    ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Before running, set your API key:"
echo "  export ANTHROPIC_API_KEY='your-key-here'"
echo ""
echo "Then run:"
echo "  source .venv/bin/activate"
echo "  python main.py"
echo ""
