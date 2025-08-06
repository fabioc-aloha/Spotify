#!/usr/bin/env python3
"""
Test script to debug config parsing issues
"""

import re
from pathlib import Path

def test_config_parsing(config_file):
    """Test the config parsing logic"""
    
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Testing config file: {config_file}")
    print("=" * 50)
    
    # Test metadata parsing
    metadata_match = re.search(r'## Metadata\s*\n(.*?)\n\n', content, re.DOTALL)
    if metadata_match:
        print("✅ Metadata section found")
        metadata_text = metadata_match.group(1)
        print(f"Metadata content:\n{metadata_text}")
        print("-" * 30)
        
        metadata_lines = metadata_text.strip().split('\n')
        config_metadata = {}
        
        for line in metadata_lines:
            print(f"Processing line: '{line}'")
            if line.startswith('- **'):
                match = re.match(r'- \*\*(.*?)\*\*:\s*(.*)', line)
                if match:
                    key = match.group(1).lower().replace(' ', '_')
                    value = match.group(2)
                    config_metadata[key] = value
                    print(f"  ✅ Extracted: {key} = '{value}'")
                else:
                    print(f"  ❌ Failed to match pattern")
            else:
                print(f"  ⏭️  Skipped (doesn't start with '- **')")
        
        print("\nFinal metadata config:")
        for key, value in config_metadata.items():
            print(f"  {key}: {value}")
            
        name = config_metadata.get('name', 'NOT FOUND')
        print(f"\n🎯 Playlist name: '{name}'")
        
    else:
        print("❌ No metadata section found")
        
        # Try to find what's actually there
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'metadata' in line.lower():
                print(f"Found 'metadata' on line {i+1}: '{line}'")

if __name__ == "__main__":
    test_config_parsing("playlist-configs/binaural-beat-therapy.md")
    print("\n" + "=" * 50)
    test_config_parsing("playlist-configs/adhd-focus-protocol.md")
