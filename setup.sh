#!/bin/bash

# Setup script for Figma to HTML Converter
# This script helps you get started quickly

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Figma to HTML Converter - Setup                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "   Please install Python 3.7 or later from https://python.org"
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version found"
echo ""

# Install dependencies
echo "Installing dependencies..."
if pip3 install -r requirements.txt --quiet; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Check for API key
echo "Checking for Figma API key..."
if [ -z "$FIGMA_API_KEY" ]; then
    echo "⚠️  FIGMA_API_KEY not found in environment"
    echo ""
    echo "To set your API key:"
    echo "  1. Go to https://www.figma.com/settings"
    echo "  2. Create a personal access token"
    echo "  3. Run: export FIGMA_API_KEY='your_key_here'"
    echo ""
    echo "Or add it to your shell profile (.bashrc, .zshrc, etc.):"
    echo "  echo 'export FIGMA_API_KEY=\"your_key_here\"' >> ~/.bashrc"
    echo ""
    read -p "Do you want to set it now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your Figma API key: " api_key
        export FIGMA_API_KEY="$api_key"
        echo "✅ API key set for this session"
        echo "   (To make it permanent, add it to your shell profile)"
    fi
else
    echo "✅ FIGMA_API_KEY is set"
fi
echo ""

# Run tests
echo "Running tests..."
if python3 test_converter.py > /dev/null 2>&1; then
    echo "✅ All tests passed"
else
    echo "⚠️  Some tests failed. Running with output:"
    python3 test_converter.py
fi
echo ""

# Make scripts executable
echo "Making scripts executable..."
chmod +x convert.sh test_converter.py 2>/dev/null
echo "✅ Scripts are executable"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Setup Complete! 🎉                                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Copy the assignment Figma file to your workspace"
echo "  2. Get the file key from the URL"
echo "  3. Run: python3 figma_to_html.py <FILE_KEY>"
echo ""
echo "For help, see:"
echo "  - README.md       (Full documentation)"
echo "  - QUICKSTART.md   (Quick guide for the assignment)"
echo "  - EXAMPLES.md     (Usage examples)"
echo ""
echo "Need help? Check the troubleshooting section in README.md"
echo ""
