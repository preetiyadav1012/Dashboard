#!/bin/bash
# Installation guide script

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Claims Management Dashboard - Installation Guide      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "📥 Install from: https://nodejs.org/"
    exit 1
else
    echo "✅ Node.js $(node -v)"
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed"
    echo "📥 Install from: https://python.org/"
    exit 1
else
    echo "✅ Python $(python3 --version)"
fi

echo ""
echo "📋 Installation Steps:"
echo "1. Backend Setup:"
echo "   cd backend"
echo "   pip install -r requirements.txt"
echo "   cp .env.example .env"
echo "   # Edit .env with your ServiceNow credentials"
echo "   python app.py"
echo ""
echo "2. Frontend Setup (in another terminal):"
echo "   cd frontend"
echo "   npm install"
echo "   npm start"
echo ""
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "✅ You're all set!"
