#!/usr/bin/env python3
"""
Figma to HTML/CSS Converter

This tool extracts design data from Figma files via the Figma REST API
and generates pixel-perfect HTML/CSS representations.
"""

import os
import sys
import json
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class NodeType(Enum):
    """Figma node types"""
    DOCUMENT = "DOCUMENT"
    CANVAS = "CANVAS"
    FRAME = "FRAME"
    GROUP = "GROUP"
    VECTOR = "VECTOR"
    BOOLEAN_OPERATION = "BOOLEAN_OPERATION"
    STAR = "STAR"
    LINE = "LINE"
    ELLIPSE = "ELLIPSE"
    REGULAR_POLYGON = "REGULAR_POLYGON"
    RECTANGLE = "RECTANGLE"
    TEXT = "TEXT"
    SLICE = "SLICE"
    COMPONENT = "COMPONENT"
    COMPONENT_SET = "COMPONENT_SET"
    INSTANCE = "INSTANCE"


@dataclass
class Color:
    """Represents a color with RGBA values"""
    r: float
    g: float
    b: float
    a: float = 1.0

    def to_css(self) -> str:
        """Convert to CSS rgba string"""
        r = int(self.r * 255)
        g = int(self.g * 255)
        b = int(self.b * 255)
        if self.a < 1.0:
            return f"rgba({r}, {g}, {b}, {self.a})"
        return f"rgb({r}, {g}, {b})"

    def to_hex(self) -> str:
        """Convert to hex string"""
        r = int(self.r * 255)
        g = int(self.g * 255)
        b = int(self.b * 255)
        return f"#{r:02x}{g:02x}{b:02x}"


class FigmaToHTMLConverter:
    """Main converter class that handles Figma API interaction and HTML/CSS generation"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.figma.com/v1"
        self.headers = {"X-Figma-Token": api_key}
        self.image_fills = {}
        self.fonts_used = set()

    def get_file_data(self, file_key: str) -> Dict[str, Any]:
        """Fetch Figma file data from API"""
        url = f"{self.base_url}/files/{file_key}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch Figma file: {response.status_code} - {response.text}")
        
        return response.json()

    def get_image_fills(self, file_key: str, node_ids: List[str]) -> Dict[str, str]:
        """Get image URLs for image fills"""
        if not node_ids:
            return {}
        
        ids_param = ",".join(node_ids)
        url = f"{self.base_url}/images/{file_key}?ids={ids_param}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("images", {})
        return {}

    def parse_color(self, color_data: Dict[str, float]) -> Color:
        """Parse Figma color data"""
        return Color(
            r=color_data.get("r", 0),
            g=color_data.get("g", 0),
            b=color_data.get("b", 0),
            a=color_data.get("a", 1.0)
        )

    def get_fills_css(self, fills: List[Dict], node_id: str = "") -> str:
        """Convert Figma fills to CSS background"""
        if not fills or not any(fill.get("visible", True) for fill in fills):
            return "transparent"

        visible_fills = [f for f in fills if f.get("visible", True)]
        
        if len(visible_fills) == 1:
            fill = visible_fills[0]
            fill_type = fill.get("type")
            
            if fill_type == "SOLID":
                color = self.parse_color(fill.get("color", {}))
                opacity = fill.get("opacity", 1.0)
                color.a *= opacity
                return color.to_css()
            
            elif fill_type == "GRADIENT_LINEAR":
                return self.parse_gradient(fill)
            
            elif fill_type == "IMAGE":
                if node_id in self.image_fills:
                    return f"url('{self.image_fills[node_id]}')"
                return "#cccccc"
        
        # Multiple fills - use the first visible one
        return self.get_fills_css([visible_fills[0]], node_id)

    def parse_gradient(self, gradient_fill: Dict) -> str:
        """Parse Figma gradient to CSS"""
        gradient_type = gradient_fill.get("type")
        
        if gradient_type == "GRADIENT_LINEAR":
            stops = gradient_fill.get("gradientStops", [])
            handles = gradient_fill.get("gradientHandlePositions", [])
            
            if len(handles) >= 2:
                x1, y1 = handles[0].get("x", 0), handles[0].get("y", 0)
                x2, y2 = handles[1].get("x", 1), handles[1].get("y", 1)
                
                # Calculate angle
                import math
                angle = math.atan2(y2 - y1, x2 - x1) * 180 / math.pi + 90
                
                stop_strings = []
                for stop in stops:
                    color = self.parse_color(stop.get("color", {}))
                    position = stop.get("position", 0) * 100
                    stop_strings.append(f"{color.to_css()} {position:.1f}%")
                
                return f"linear-gradient({angle:.1f}deg, {', '.join(stop_strings)})"
        
        # Fallback
        return "transparent"

    def get_strokes_css(self, node: Dict) -> Tuple[str, str, str]:
        """Get border CSS properties from strokes"""
        strokes = node.get("strokes", [])
        if not strokes or not any(s.get("visible", True) for s in strokes):
            return "", "", ""
        
        stroke = next((s for s in strokes if s.get("visible", True)), None)
        if not stroke:
            return "", "", ""
        
        # Border width
        stroke_weight = node.get("strokeWeight", 1)
        border_width = f"{stroke_weight}px"
        
        # Border color
        if stroke.get("type") == "SOLID":
            color = self.parse_color(stroke.get("color", {}))
            opacity = stroke.get("opacity", 1.0)
            color.a *= opacity
            border_color = color.to_css()
        else:
            border_color = "#000000"
        
        # Border style
        border_style = "solid"
        
        return border_width, border_style, border_color

    def get_effects_css(self, effects: List[Dict]) -> List[str]:
        """Convert Figma effects to CSS (shadows, blurs)"""
        css_effects = []
        
        for effect in effects:
            if not effect.get("visible", True):
                continue
            
            effect_type = effect.get("type")
            
            if effect_type in ["DROP_SHADOW", "INNER_SHADOW"]:
                offset = effect.get("offset", {})
                x = offset.get("x", 0)
                y = offset.get("y", 0)
                radius = effect.get("radius", 0)
                spread = effect.get("spread", 0)
                color = self.parse_color(effect.get("color", {}))
                
                shadow = f"{x}px {y}px {radius}px {spread}px {color.to_css()}"
                if effect_type == "INNER_SHADOW":
                    shadow = f"inset {shadow}"
                css_effects.append(shadow)
            
            elif effect_type == "LAYER_BLUR":
                radius = effect.get("radius", 0)
                css_effects.append(f"blur({radius}px)")
        
        return css_effects

    def get_border_radius(self, node: Dict) -> str:
        """Get border radius CSS"""
        # Check for uniform corner radius first
        if "cornerRadius" in node:
            radius = node["cornerRadius"]
            return f"{radius}px"
        
        # Check for rectangleCornerRadii array (Figma's way of specifying individual corners)
        if "rectangleCornerRadii" in node:
            radii = node["rectangleCornerRadii"]
            # Array format: [topLeft, topRight, bottomRight, bottomLeft]
            if len(radii) == 4:
                # If all corners are the same
                if all(r == radii[0] for r in radii):
                    if radii[0] == 0:
                        return "0px"
                    return f"{radii[0]}px"
                # Individual corners
                return f"{radii[0]}px {radii[1]}px {radii[2]}px {radii[3]}px"
        
        # Check for individual corner radii with multiple possible property name formats
        # Figma might use different naming conventions in some cases
        corner_names = {
            "topLeft": ["rectangleCornerTopLeftRadius", "topLeftRadius", "cornerTopLeftRadius"],
            "topRight": ["rectangleCornerTopRightRadius", "topRightRadius", "cornerTopRightRadius"],
            "bottomRight": ["rectangleCornerBottomRightRadius", "bottomRightRadius", "cornerBottomRightRadius"],
            "bottomLeft": ["rectangleCornerBottomLeftRadius", "bottomLeftRadius", "cornerBottomLeftRadius"]
        }
        
        radii = []
        has_any_radius = False
        
        for corner in ["topLeft", "topRight", "bottomRight", "bottomLeft"]:
            radius = 0
            # Try each possible property name format
            for prop_name in corner_names[corner]:
                if prop_name in node:
                    radius = node[prop_name]
                    has_any_radius = True
                    break
            radii.append(radius)
        
        # If no radius found at all, return 0px
        if not has_any_radius:
            return "0px"
        
        # If all corners are the same (including all 0), return single value
        if all(r == radii[0] for r in radii):
            if radii[0] == 0:
                return "0px"
            return f"{radii[0]}px"
        
        # Return individual corner values (top-left, top-right, bottom-right, bottom-left)
        return f"{radii[0]}px {radii[1]}px {radii[2]}px {radii[3]}px"

    def get_text_styles(self, node: Dict) -> Dict[str, str]:
        """Extract text styling from text node"""
        style = node.get("style", {})
        styles = {}
        
        # Font family
        font_family = style.get("fontFamily", "Arial")
        self.fonts_used.add(font_family)
        styles["font-family"] = f"'{font_family}', sans-serif"
        
        # Font size
        font_size = style.get("fontSize", 16)
        styles["font-size"] = f"{font_size}px"
        
        # Font weight
        font_weight = style.get("fontWeight", 400)
        styles["font-weight"] = str(font_weight)
        
        # Line height
        if "lineHeightPx" in style:
            line_height = style["lineHeightPx"]
            styles["line-height"] = f"{line_height}px"
        elif "lineHeightPercentFontSize" in style:
            line_height_percent = style["lineHeightPercentFontSize"]
            styles["line-height"] = f"{line_height_percent}%"
        
        # Letter spacing
        if "letterSpacing" in style:
            letter_spacing = style["letterSpacing"]
            styles["letter-spacing"] = f"{letter_spacing}px"
        
        # Text align
        text_align = style.get("textAlignHorizontal", "LEFT").lower()
        if text_align == "justified":
            text_align = "justify"
        styles["text-align"] = text_align
        
        # Text decoration
        if style.get("textDecoration") == "UNDERLINE":
            styles["text-decoration"] = "underline"
        elif style.get("textDecoration") == "STRIKETHROUGH":
            styles["text-decoration"] = "line-through"
        
        # Text transform
        if style.get("textCase") == "UPPER":
            styles["text-transform"] = "uppercase"
        elif style.get("textCase") == "LOWER":
            styles["text-transform"] = "lowercase"
        elif style.get("textCase") == "TITLE":
            styles["text-transform"] = "capitalize"
        
        # Text color
        fills = node.get("fills", [])
        if fills:
            color = self.get_fills_css(fills)
            styles["color"] = color
        
        return styles

    def node_to_html(self, node: Dict, parent_box: Optional[Dict] = None, depth: int = 0) -> str:
        """Recursively convert Figma node to HTML"""
        node_type = node.get("type")
        node_id = node.get("id", "")
        node_name = node.get("name", "")
        
        # Skip invisible nodes
        if not node.get("visible", True):
            return ""
        
        # Get node bounds
        bbox = node.get("absoluteBoundingBox", {})
        if not bbox:
            # If no bounding box, try to process children
            children = node.get("children", [])
            html_parts = []
            for child in children:
                child_html = self.node_to_html(child, parent_box, depth)
                if child_html:
                    html_parts.append(child_html)
            return "\n".join(html_parts)
        
        x = bbox.get("x", 0)
        y = bbox.get("y", 0)
        width = bbox.get("width", 0)
        height = bbox.get("height", 0)
        
        # Calculate relative position
        if parent_box:
            rel_x = x - parent_box.get("x", 0)
            rel_y = y - parent_box.get("y", 0)
        else:
            rel_x = x
            rel_y = y
            parent_box = bbox
        
        # Start building styles
        styles = {
            "position": "absolute",
            "left": f"{rel_x}px",
            "top": f"{rel_y}px",
            "width": f"{width}px",
            "height": f"{height}px",
        }
        
        # Handle different node types
        if node_type == "TEXT":
            # Text node
            text_content = node.get("characters", "")
            text_styles = self.get_text_styles(node)
            styles.update(text_styles)
            
            # Background
            fills = node.get("fills", [])
            if fills and fills[0].get("type") != "SOLID":
                bg = self.get_fills_css(fills, node_id)
                if bg != "transparent":
                    styles["background"] = bg
            
            # Effects
            effects = node.get("effects", [])
            if effects:
                shadows = [e for e in self.get_effects_css(effects) if "blur" not in e]
                if shadows:
                    styles["text-shadow"] = ", ".join(shadows)
            
            # Build HTML
            style_str = "; ".join(f"{k}: {v}" for k, v in styles.items())
            return f'<div class="text-node" style="{style_str}">{text_content}</div>'
        
        else:
            # Container node (FRAME, GROUP, RECTANGLE, etc.)
            
            # Background/Fill
            fills = node.get("fills", [])
            if fills:
                bg = self.get_fills_css(fills, node_id)
                styles["background"] = bg
            
            # Border/Stroke
            border_width, border_style, border_color = self.get_strokes_css(node)
            if border_width:
                styles["border"] = f"{border_width} {border_style} {border_color}"
            
            # Border radius - check for any type of corner radius
            border_radius = self.get_border_radius(node)
            if border_radius != "0px":
                styles["border-radius"] = border_radius
                # Add overflow hidden to prevent children from breaking rounded corners
                styles["overflow"] = "hidden"
            
            # Effects (shadows)
            effects = node.get("effects", [])
            if effects:
                css_effects = self.get_effects_css(effects)
                shadows = [e for e in css_effects if "blur" not in e]
                if shadows:
                    styles["box-shadow"] = ", ".join(shadows)
            
            # Opacity
            opacity = node.get("opacity", 1.0)
            if opacity < 1.0:
                styles["opacity"] = str(opacity)
            
            # Build style string
            style_str = "; ".join(f"{k}: {v}" for k, v in styles.items())
            
            # Process children
            children = node.get("children", [])
            children_html = []
            for child in children:
                child_html = self.node_to_html(child, bbox, depth + 1)
                if child_html:
                    children_html.append(child_html)
            
            # Build HTML
            class_name = f"{node_type.lower()}-node"
            if children_html:
                children_str = "\n".join(children_html)
                return f'<div class="{class_name}" style="{style_str}">\n{children_str}\n</div>'
            else:
                return f'<div class="{class_name}" style="{style_str}"></div>'

    def find_frames(self, node: Dict, frames: List[Dict] = None) -> List[Dict]:
        """Find all top-level frames in the document"""
        if frames is None:
            frames = []
        
        node_type = node.get("type")
        
        if node_type == "FRAME" and node.get("visible", True):
            frames.append(node)
        
        # Recurse into children
        for child in node.get("children", []):
            self.find_frames(child, frames)
        
        return frames

    def generate_html(self, file_key: str, frame_name: Optional[str] = None) -> str:
        """Generate complete HTML from Figma file"""
        print(f"Fetching Figma file data...")
        file_data = self.get_file_data(file_key)
        
        document = file_data.get("document", {})
        
        # Find all frames
        frames = self.find_frames(document)
        
        if not frames:
            raise Exception("No frames found in the Figma file")
        
        # Select frame
        if frame_name:
            selected_frame = next((f for f in frames if f.get("name") == frame_name), None)
            if not selected_frame:
                print(f"Frame '{frame_name}' not found. Available frames:")
                for f in frames:
                    print(f"  - {f.get('name')}")
                raise Exception(f"Frame '{frame_name}' not found")
        else:
            selected_frame = frames[0]
            print(f"Using frame: {selected_frame.get('name')}")
        
        # Collect image fill nodes
        image_nodes = []
        self.collect_image_nodes(selected_frame, image_nodes)
        
        if image_nodes:
            print(f"Fetching {len(image_nodes)} image fills...")
            self.image_fills = self.get_image_fills(file_key, image_nodes)
        
        # Convert frame to HTML
        print("Generating HTML...")
        body_html = self.node_to_html(selected_frame)
        
        # Get frame dimensions
        bbox = selected_frame.get("absoluteBoundingBox", {})
        frame_width = bbox.get("width", 800)
        frame_height = bbox.get("height", 600)
        
        # Build complete HTML
        html = self.build_complete_html(body_html, frame_width, frame_height)
        
        return html

    def collect_image_nodes(self, node: Dict, image_nodes: List[str]):
        """Recursively collect nodes with image fills"""
        node_id = node.get("id")
        fills = node.get("fills", [])
        
        for fill in fills:
            if fill.get("type") == "IMAGE" and fill.get("visible", True):
                image_nodes.append(node_id)
                break
        
        for child in node.get("children", []):
            self.collect_image_nodes(child, image_nodes)

    def build_complete_html(self, body_content: str, width: float, height: float) -> str:
        """Build complete HTML document with CSS"""
        
        # Google Fonts import for used fonts
        fonts_import = ""
        if self.fonts_used:
            font_params = "|".join(f.replace(" ", "+") for f in self.fonts_used)
            fonts_import = f'<link href="https://fonts.googleapis.com/css2?family={font_params}:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">'
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Figma to HTML Export</title>
    {fonts_import}
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        
        #figma-frame {{
            position: relative;
            width: {width}px;
            height: {height}px;
            background: white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .text-node {{
            overflow: hidden;
            word-wrap: break-word;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div id="figma-frame">
        {body_content}
    </div>
</body>
</html>"""
        
        return html


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert Figma designs to HTML/CSS")
    parser.add_argument("file_key", help="Figma file key (from the URL)")
    parser.add_argument("--frame", help="Specific frame name to export (optional)")
    parser.add_argument("--output", default="output.html", help="Output HTML file path")
    parser.add_argument("--api-key", help="Figma API key (or set FIGMA_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("FIGMA_API_KEY")
    if not api_key:
        print("Error: Figma API key required. Set FIGMA_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    try:
        # Create converter
        converter = FigmaToHTMLConverter(api_key)
        
        # Generate HTML
        html = converter.generate_html(args.file_key, args.frame)
        
        # Write to file
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"\n✅ Successfully generated: {args.output}")
        print(f"   Fonts used: {', '.join(converter.fonts_used) if converter.fonts_used else 'None'}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()