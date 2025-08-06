#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alex Method DJ Platform - Source Modules
Common utilities and components for the Alex Method DJ platform

This package provides reusable modules for:
- Smart cross-platform printing with emoji intelligence
- Configuration file parsing for playlist definitions  
- File utilities and path handling
- Global ASCII mode control for compatibility

Modules:
    smart_print: Intelligent emoji handling and cross-platform printing
    config_parser: Universal playlist configuration file parser
    file_utils: File operations and metadata management

Usage:
    from src.smart_print import safe_print, set_force_ascii_mode
    from src.config_parser import PlaylistConfigParser
    from src.file_utils import safe_read_file, update_config_metadata
"""

# Import main functions for easy access
from .smart_print import safe_print, set_force_ascii_mode, get_force_ascii_mode
from .config_parser import PlaylistConfigParser
from .file_utils import (
    safe_read_file, 
    safe_write_file, 
    update_config_metadata,
    normalize_path,
    find_config_files
)

# Module version
__version__ = "1.0.0"

# Package information
__author__ = "Alex Method DJ Platform"
__description__ = "Common utilities for the Alex Method DJ platform"

# Export main components
__all__ = [
    # Smart Print
    'safe_print',
    'set_force_ascii_mode', 
    'get_force_ascii_mode',
    
    # Config Parser
    'PlaylistConfigParser',
    
    # File Utils
    'safe_read_file',
    'safe_write_file',
    'update_config_metadata',
    'normalize_path',
    'find_config_files'
]


def test_all_modules():
    """Test all modules in the package."""
    print(f"Testing Alex Method DJ Platform Modules v{__version__}")
    print("=" * 50)
    
    # Test smart_print module
    try:
        from .smart_print import test_smart_print
        test_smart_print()
        print("✅ Smart Print module test passed")
    except Exception as e:
        print(f"❌ Smart Print module test failed: {e}")
    
    print("-" * 30)
    
    # Test config_parser module
    try:
        from .config_parser import test_config_parser
        test_config_parser()
        print("✅ Config Parser module test passed")
    except Exception as e:
        print(f"❌ Config Parser module test failed: {e}")
    
    print("-" * 30)
    
    # Test file_utils module
    try:
        from .file_utils import test_file_utils
        test_file_utils()
        print("✅ File Utils module test passed")
    except Exception as e:
        print(f"❌ File Utils module test failed: {e}")
    
    print("=" * 50)
    print("Module testing complete!")


if __name__ == "__main__":
    test_all_modules()
