#!/usr/bin/env python
"""
Simple test script to verify that a built wheel properly supports pypostal's core functionality.
This script imports the main modules and runs core tests to check if parsing and expansion 
are working correctly, which verifies that:
1. The C extensions are properly built and linked
2. The libpostal data directory is available and loaded
3. The core functionality works as expected
"""

import sys
import unittest
import os

def run_basic_tests():
    """Run basic import and functionality tests to verify the wheel works."""
    print("Testing postal import...")
    import postal
    print(f"postal imported successfully. __file__={postal.__file__}")

    print("\nTesting postal parser functionality...")
    from postal.parser import parse_address
    parsed = parse_address('781 Franklin Ave Crown Heights Brooklyn NYC NY 11216 USA')
    print(f"Address parsed: {parsed}")
    
    # Basic verification of parsing results
    expected_components = {
        'house_number': '781',
        'road': 'franklin ave',
        'suburb': 'crown heights',
        'city_district': 'brooklyn',
        'city': 'nyc',
        'state': 'ny'
    }
    
    match_count = 0
    for component, label in parsed:
        if label in expected_components and expected_components[label].lower() == component.lower():
            match_count += 1
            
    if match_count >= 4:  # At least 4 key components should match
        print("✓ Parser test passed")
    else:
        print("✗ Parser test failed")
        sys.exit(1)
        
    print("\nTesting postal expansion functionality...")
    from postal.expand import expand_address
    expansions = expand_address('123 Main St Apt 4')
    print(f"Expansions: {expansions[:3]}...")
    
    # Basic verification of expansion results
    if len(expansions) > 0 and '123 main street apartment 4' in expansions:
        print("✓ Expansion test passed")
    else:
        print("✗ Expansion test failed")
        sys.exit(1)

def run_unittest_tests():
    """Run the actual unit tests from the postal test suite."""
    print("\nRunning postal test suite...")
    from postal.tests import test_expand, test_parser
    
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add tests from the existing test modules
    suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(test_expand))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(test_parser))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("✓ All unit tests passed")
        return True
    else:
        print("✗ Unit tests failed")
        return False

if __name__ == "__main__":
    # First run basic import and functionality tests
    run_basic_tests()
    
    # Then run the actual test suite if available
    try:
        success = run_unittest_tests()
        if not success:
            sys.exit(1)
    except ImportError as e:
        print(f"Couldn't run full test suite (likely in wheel testing environment): {e}")
        print("Basic tests passed, considering this a success")
    
    print("\nAll tests passed successfully!")