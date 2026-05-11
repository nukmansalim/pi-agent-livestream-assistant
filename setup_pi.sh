#!/bin/bash
# Pi Agent - Quick Setup for Raspberry Pi

# ============================================================
# Pi Agent Setup Script for Raspberry Pi
# ============================================================

echo "🤖 Pi Agent - Raspberry Pi Setup"
echo "=================================="

# 1. Check Python
echo ""
echo "1️⃣  Checking Python..."
python3 --version || (echo "❌ Python3 not found"; exit 1)

# 2. Create virtual environment
echo ""
echo "2️⃣  Creating virtual environment..."
python3 -m venv yt-agent-env

# 3. Activate virtual environment
echo ""
echo "3️⃣  Activating virtual environment..."
source yt-agent-env/bin/activate

# 4. Upgrade pip
echo ""
echo "4️⃣  Upgrading pip..."
pip install --upgrade pip

# 5. Install requirements
echo ""
echo "5️⃣  Installing dependencies..."
echo "   This may take a few minutes on Raspberry Pi..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1. Get credentials:"
echo "   - Download client_secrets.json from Google Cloud"
echo "   - Get Telegram bot token from @BotFather"
echo ""
echo "2. Set environment variable:"
echo "   export TELEGRAM_BOT_TOKEN='your_token_here'"
echo ""
echo "3. Run the bot:"
echo "   source yt-agent-env/bin/activate"
echo "   python main.py telegram"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
