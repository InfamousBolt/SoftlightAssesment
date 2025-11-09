# SoftlightAssesment - Figma to HTML/CSS Converter

A Python-based tool that converts Figma designs into HTML/CSS representations using the Figma REST API.

## Features

- ✅ **Accurate Layout Conversion**: Preserves absolute positioning, dimensions, and spacing
- ✅ **Complete Styling Support**: 
  - Colors (solid, gradients)
  - Typography (fonts, sizes, weights, line-height, letter-spacing)
  - Borders and strokes
  - Shadows and effects
  - Opacity
  - Images and image fills
- ✅ **Text Rendering**: Full text styling with proper font loading
- ✅ **Nested Components**: Handles complex nested structures
- ✅ **Generalizable**: Works with any Figma file, not just specific designs

## Prerequisites

- Python 3.7+
- Figma account with API access
- Figma API key (personal access token)

## Quick Start

### 1. Install Dependencies

```bash
pip install requests
```

Or use the automated setup:

```bash
./setup.sh
```

### 2. Get Your Figma API Key

1. Go to your Figma account settings: https://www.figma.com/settings
2. Scroll down to "Personal access tokens"
3. Click "Create a new personal access token"
4. Give it a name (e.g., "HTML Converter")
5. Copy the token - you'll need this for the converter

### 3. Get the Figma File Key of copid figma design

The Figma file key is in the URL of your Figma file:
```
https://www.figma.com/file/ABC123DEF456/My-Design
                           ^^^^^^^^^^^^
                          This is your file key
```

**Important:** You need to duplicate the provided Figma file into your own workspace so you can access it with your personal API key.

## Usage

### Basic Usage

```bash
python3 figma_to_html.py <FILE_KEY> --api-key <YOUR_API_KEY>
```

### With Environment Variable (Recommended)

```bash
export FIGMA_API_KEY="your-api-key-here"
python3 figma_to_html.py <FILE_KEY>
```

### Specify Output File

```bash
python3 figma_to_html.py <FILE_KEY> --output my-design.html
```

### Export Specific Frame

```bash
python3 figma_to_html.py <FILE_KEY> --frame "Frame Name"
```

### Using Helper Scripts

```bash
# Easy conversion with validation
./convert.sh <FILE_KEY> --output design.html
```

## Example

```bash
# Set your API key
export FIGMA_API_KEY="figd_your_api_key_here"

# Convert the Figma file
python3 figma_to_html.py ABC123DEF456 --output design.html

# Open in browser
open design.html  # macOS
# or
xdg-open design.html  # Linux
```

## How It Works

1. **API Fetch**: Retrieves the complete Figma file structure via REST API
2. **Node Traversal**: Recursively processes all visible nodes in the design
3. **Style Extraction**: Converts Figma properties to CSS:
   - Fills → background colors/gradients
   - Strokes → borders
   - Text styles → font properties
   - Effects → shadows and filters
   - Layout → absolute positioning
4. **HTML Generation**: Creates a static HTML file with inline styles
5. **Font Loading**: Automatically includes Google Fonts for custom typography

## Architecture

### Core Components

- **FigmaToHTMLConverter**: Main class handling API interaction and conversion
- **Color Class**: Utility for color format conversion (RGBA → CSS)
- **Node Processing**: Recursive traversal of Figma's tree structure
- **Style Mapping**: Direct mapping from Figma properties to CSS

### Supported Node Types

- FRAME (container frames)
- GROUP (grouped elements)
- RECTANGLE (shapes with fills)
- TEXT (text layers with full typography)
- ELLIPSE, VECTOR, LINE (basic shapes)
- COMPONENT & INSTANCE (design system components)

### CSS Generation

The converter generates:
- Inline styles for pixel-perfect positioning
- Absolute positioning based on Figma coordinates
- All visual properties (colors, borders, shadows, etc.)
- Proper font loading via Google Fonts
- Individual corner radius support via CSS `border-radius` shorthand

## Project Files

### Core Files
- `figma_to_html.py` - Main converter (520+ lines)
- `requirements.txt` - Python dependencies
- `README.md` - This file

### Helper Scripts
- `setup.sh` - Interactive setup wizard
- `convert.sh` - Easy conversion helper

### Debug Tools
- `debug_figma.py` - Inspect Figma file structure
- `find_input_fields.py` - Analyze specific elements
- `dump_input_fields.py` - Dump all properties of frames

### Testing
- `test_converter.py` - Automated test suite (7 tests)

## Known Limitations

### 1. **Absolute Positioning**
Output uses absolute positioning which is less flexible than modern CSS layouts (Flexbox/Grid). This is intentional to match Figma's exact positioning but means the output is not responsive by default.

### 2. **Complex Vector Shapes**
Very complex vector shapes may not render perfectly. Simple shapes (rectangles, circles) work well, but intricate SVG paths may have reduced fidelity.

### 3. **Auto-layout to Flexbox**
Figma's auto-layout is converted to absolute positioning rather than CSS Flexbox/Grid. While this ensures pixel-perfect accuracy, it loses the semantic meaning of the layout structure.

### 4. **Responsive Design**
Output is fixed-width matching the Figma frame dimensions. It is not responsive and does not adapt to different screen sizes without manual CSS modifications.

### 5. **Interactive Elements**
Buttons, links, and interactive prototypes are rendered as static `<div>` elements. Interactivity would need to be added manually with JavaScript.


## Border Radius Issue & Resolution

During development and testing, a critical issue was discovered where input fields with rounded corners in Figma were rendering with sharp corners in the HTML output.

### The Problem
Input fields in the generated HTML lacked rounded corners despite appearing rounded in Figma. The converter wasn't detecting or applying border-radius CSS to these elements.

### Iteration 1: Node Type Restrictions
Initially suspected the converter only applied border-radius to RECTANGLE nodes. Updated the logic to check all node types (FRAME, GROUP, etc.), but the issue persisted.

### Iteration 2: Individual Corner Properties
Enhanced the `get_border_radius()` function to check for multiple individual corner property formats (`rectangleCornerTopLeftRadius`, `topLeftRadius`, `cornerTopLeftRadius`), assuming Figma used one of these naming conventions. Still no success.

### Root Cause Discovery
Used diagnostic scripts (`dump_input_fields.py`) to inspect the raw Figma API response. This revealed that Figma actually uses a **`rectangleCornerRadii` array property** (e.g., `[8.0, 8.0, 0.0, 0.0]`) rather than individual corner properties. The converter wasn't checking for this array format.

### Final Fix
Added support for the `rectangleCornerRadii` array as the primary detection method in `get_border_radius()`:

This successfully parses the array into CSS border-radius values (e.g., `8.0px 8.0px 0.0px 0.0px`), which correctly renders rounded corners on input fields, including cases where only some corners are rounded (like input fields with rounded top corners and square bottom corners).


## Testing

Run the automated test suite:

```bash
python3 test_converter.py
```

All tests passing:
```
✅ Import Test
✅ Converter Import
✅ Color Conversion
✅ API Key Detection
✅ Converter Instantiation
✅ Style Methods
✅ HTML Generation

Results: 7/7 tests passed
```
- Google Fonts for typography support
- The `rectangleCornerRadii` discovery that solved the border-radius challenge
