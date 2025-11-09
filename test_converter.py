#!/usr/bin/env python3
"""
Test script for Figma to HTML converter
Run this to validate the converter works correctly
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import requests
        print("  ✅ requests module available")
    except ImportError:
        print("  ❌ requests module missing - run: pip install requests")
        return False
    
    try:
        import json
        import dataclasses
        import enum
        print("  ✅ Standard library modules available")
    except ImportError as e:
        print(f"  ❌ Standard library import error: {e}")
        return False
    
    return True


def test_converter_import():
    """Test that the converter module can be imported"""
    print("\nTesting converter import...")
    try:
        from figma_to_html import FigmaToHTMLConverter, Color, NodeType
        print("  ✅ Converter module imported successfully")
        return True
    except ImportError as e:
        print(f"  ❌ Failed to import converter: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error importing converter: {e}")
        return False


def test_color_conversion():
    """Test color conversion utilities"""
    print("\nTesting color conversion...")
    try:
        from figma_to_html import Color
        
        # Test RGB conversion
        color = Color(r=1.0, g=0.5, b=0.0, a=1.0)
        css = color.to_css()
        assert css == "rgb(255, 127, 0)", f"Expected 'rgb(255, 127, 0)', got '{css}'"
        print(f"  ✅ RGB conversion: {css}")
        
        # Test RGBA conversion
        color_alpha = Color(r=1.0, g=0.5, b=0.0, a=0.5)
        css_alpha = color_alpha.to_css()
        assert "rgba" in css_alpha and "0.5" in css_alpha
        print(f"  ✅ RGBA conversion: {css_alpha}")
        
        # Test hex conversion
        hex_color = color.to_hex()
        assert hex_color == "#ff7f00", f"Expected '#ff7f00', got '{hex_color}'"
        print(f"  ✅ Hex conversion: {hex_color}")
        
        return True
    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error in color conversion: {e}")
        return False


def test_api_key_detection():
    """Test API key detection"""
    print("\nTesting API key detection...")
    api_key = os.environ.get("FIGMA_API_KEY")
    if api_key:
        print(f"  ✅ FIGMA_API_KEY found (length: {len(api_key)})")
        return True
    else:
        print("  ⚠️  FIGMA_API_KEY not set in environment")
        print("     This is OK for testing, but required for actual conversion")
        return True  # Not a failure, just a warning


def test_converter_instantiation():
    """Test that converter can be instantiated"""
    print("\nTesting converter instantiation...")
    try:
        from figma_to_html import FigmaToHTMLConverter
        converter = FigmaToHTMLConverter("test_api_key")
        print("  ✅ Converter instantiated successfully")
        
        # Check attributes
        assert hasattr(converter, 'get_file_data')
        assert hasattr(converter, 'generate_html')
        assert hasattr(converter, 'node_to_html')
        print("  ✅ Required methods present")
        
        return True
    except Exception as e:
        print(f"  ❌ Error instantiating converter: {e}")
        return False


def test_style_methods():
    """Test style conversion methods"""
    print("\nTesting style conversion methods...")
    try:
        from figma_to_html import FigmaToHTMLConverter
        converter = FigmaToHTMLConverter("test_api_key")
        
        # Test fills conversion
        solid_fill = [{
            "type": "SOLID",
            "visible": True,
            "color": {"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0}
        }]
        result = converter.get_fills_css(solid_fill)
        assert "rgb" in result or "#" in result
        print(f"  ✅ Solid fill conversion: {result}")
        
        # Test empty fills
        empty_result = converter.get_fills_css([])
        assert empty_result == "transparent"
        print(f"  ✅ Empty fill conversion: {empty_result}")
        
        # Test border radius
        node_with_radius = {"cornerRadius": 10}
        radius = converter.get_border_radius(node_with_radius)
        assert radius == "10px"
        print(f"  ✅ Border radius conversion: {radius}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error in style methods: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_html_structure():
    """Test HTML generation structure"""
    print("\nTesting HTML generation...")
    try:
        from figma_to_html import FigmaToHTMLConverter
        converter = FigmaToHTMLConverter("test_api_key")
        
        # Test complete HTML generation structure
        sample_content = '<div>Test</div>'
        html = converter.build_complete_html(sample_content, 800, 600)
        
        assert '<!DOCTYPE html>' in html
        assert '<html' in html
        assert '<head>' in html
        assert '<body>' in html
        assert sample_content in html
        assert '800px' in html
        assert '600px' in html
        
        print("  ✅ HTML structure valid")
        print("  ✅ Content injection works")
        print("  ✅ Dimensions properly set")
        
        return True
    except Exception as e:
        print(f"  ❌ Error in HTML generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("  Figma to HTML Converter - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Converter Import", test_converter_import),
        ("Color Conversion", test_color_conversion),
        ("API Key Detection", test_api_key_detection),
        ("Converter Instantiation", test_converter_instantiation),
        ("Style Methods", test_style_methods),
        ("HTML Generation", test_html_structure),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed! The converter is ready to use.")
        return 0
    else:
        print("\n  ⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
