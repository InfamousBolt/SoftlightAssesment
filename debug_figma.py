#!/usr/bin/env python3
"""
Debug script to inspect Figma file structure
This will help identify why border radius isn't showing up
"""

import os
import sys
import json
from figma_to_html import FigmaToHTMLConverter

def print_node_info(node, depth=0):
    """Print detailed node information"""
    indent = "  " * depth
    node_type = node.get("type", "UNKNOWN")
    node_name = node.get("name", "Unnamed")
    
    print(f"{indent}📦 {node_type}: {node_name}")
    
    # Check for corner radius properties
    radius_props = {}
    for key in node.keys():
        if "radius" in key.lower() or "corner" in key.lower():
            radius_props[key] = node[key]
    
    if radius_props:
        print(f"{indent}   🔵 Radius properties found:")
        for key, value in radius_props.items():
            print(f"{indent}      {key}: {value}")
    
    # Check for fills
    if node.get("fills"):
        print(f"{indent}   🎨 Has fills: {len(node['fills'])} fill(s)")
    
    # Check for strokes
    if node.get("strokes"):
        print(f"{indent}   ✏️  Has strokes: {len(node['strokes'])} stroke(s)")
    
    # Recurse into children
    children = node.get("children", [])
    if children and depth < 3:  # Limit depth to avoid too much output
        for child in children[:10]:  # Limit to first 10 children
            print_node_info(child, depth + 1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 debug_figma.py <FILE_KEY>")
        print("\nThis will show you the structure of your Figma file")
        print("and help identify why border radius isn't showing up.")
        sys.exit(1)
    
    file_key = sys.argv[1]
    
    api_key = os.environ.get("FIGMA_API_KEY")
    if not api_key:
        print("❌ Error: FIGMA_API_KEY not set")
        print("Run: export FIGMA_API_KEY='your_key_here'")
        sys.exit(1)
    
    print("=" * 60)
    print("  Figma File Structure Inspector")
    print("=" * 60)
    print()
    
    try:
        converter = FigmaToHTMLConverter(api_key)
        print("📥 Fetching Figma file data...")
        file_data = converter.get_file_data(file_key)
        
        print(f"✅ File name: {file_data.get('name', 'Unknown')}")
        print()
        
        document = file_data.get("document", {})
        
        print("📂 Document structure:")
        print()
        
        print_node_info(document)
        
        print()
        print("=" * 60)
        print("💡 Tips:")
        print("   - Look for nodes that should have rounded corners")
        print("   - Check if they have any 'radius' or 'corner' properties")
        print("   - If you see them here but not in output.html, that's the bug!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()