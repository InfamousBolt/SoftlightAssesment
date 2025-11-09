#!/bin/bash

# Figma to HTML Converter Helper Script
# This script helps you run the converter with easy commands

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "    Figma to HTML/CSS Converter"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check if requests is installed
if ! python3 -c "import requests" 2>/dev/null; then
    echo -e "${YELLOW}Installing required dependencies...${NC}"
    pip3 install -r requirements.txt
fi

# Check for API key
if [ -z "$FIGMA_API_KEY" ]; then
    echo -e "${YELLOW}No FIGMA_API_KEY environment variable found${NC}"
    echo ""
    echo "Please set your Figma API key:"
    echo "  export FIGMA_API_KEY='your-api-key-here'"
    echo ""
    echo "Or use the --api-key flag:"
    echo "  ./convert.sh <FILE_KEY> --api-key your-api-key"
    echo ""
    
    if [ -z "$1" ]; then
        echo "Usage: ./convert.sh <FILE_KEY> [--frame FRAME_NAME] [--output OUTPUT_FILE]"
        exit 1
    fi
fi

# Run the converter
echo -e "${GREEN}Running converter...${NC}"
python3 figma_to_html.py "$@"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Conversion successful!${NC}"
    echo ""
    echo "Open the HTML file in your browser to view the result."
else
    echo ""
    echo -e "${RED}❌ Conversion failed. Check the error message above.${NC}"
    exit 1
fi
