#!/usr/bin/env python3
"""
Dump all properties of frames that look like input fields
"""

import os
import sys
import json
from figma_to_html import FigmaToHTMLConverter

def dump_frame_properties(node, depth=0):
    """Find and dump properties of input-field-like frames"""
    node_type = node.get("type", "UNKNOWN")
    
    # Check if this looks like an input field
    bbox = node.get("absoluteBoundingBox", {})
    width = bbox.get("width", 0)
    height = bbox.get("height", 0)
    has_border = bool(node.get("strokes"))
    
    # Input field detection
    if node_type == "FRAME" and has_border and 40 < height < 100 and 200 < width < 500:
        print("\n" + "="*70)
        print(f"🎯 INPUT FIELD FRAME FOUND")
        print(f"   Name: {node.get('name', 'Unnamed')}")
        print(f"   Size: {width}x{height}")
        print("="*70)
        print("\n📋 ALL PROPERTIES (JSON dump):")
        print("-"*70)
        
        # Pretty print all properties except children
        props = {k: v for k, v in node.items() if k != "children"}
        print(json.dumps(props, indent=2))
        print("-"*70)
        
        print("\n🔍 CORNER/RADIUS PROPERTIES:")
        found_any = False
        for key, value in node.items():
            if any(word in key.lower() for word in ["corner", "radius", "round", "smooth"]):
                print(f"   ✅ {key}: {value}")
                found_any = True
        
        if not found_any:
            print("   ❌ NO corner or radius properties found!")
        
        print("\n" + "="*70)
    
    # Recurse
    for child in node.get("children", []):
        dump_frame_properties(child, depth + 1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 dump_input_fields.py <FILE_KEY>")
        sys.exit(1)
    
    file_key = sys.argv[1]
    api_key = os.environ.get("FIGMA_API_KEY")
    
    if not api_key:
        print("❌ FIGMA_API_KEY not set")
        sys.exit(1)
    
    print("🔍 Fetching Figma file and searching for input fields...")
    
    try:
        converter = FigmaToHTMLConverter(api_key)
        file_data = converter.get_file_data(file_key)
        document = file_data.get("document", {})
        
        dump_frame_properties(document)
        
        print("\n\n💡 This shows ALL properties from the Figma API.")
        print("   If corner/radius properties are missing, they're not in Figma.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()