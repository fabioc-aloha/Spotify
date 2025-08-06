#!/usr/bin/env python3
"""
Test script to verify config parsing
"""

import re
from pathlib import Path

def test_config_parsing(config_file):
    """Test the config parsing logic"""
    config_path = Path(config_file)
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()

    config = {
        'metadata': {},
        'search_queries': []
    }

    # Parse metadata section
    metadata_match = re.search(r'## Metadata\s*\n(.*?)(?=\n##|\n\n|$)', content, re.DOTALL)
    if metadata_match:
        metadata_lines = metadata_match.group(1).strip().split('\n')
        for line in metadata_lines:
            # Handle both bullet point format (- **Name**:) and direct format (**Name**:)
            if line.startswith('- **'):
                match = re.match(r'- \*\*(.*?)\*\*:\s*(.*)', line)
                if match:
                    key = match.group(1).lower().replace(' ', '_')
                    value = match.group(2)
                    config['metadata'][key] = value
            elif line.startswith('**') and ':' in line:
                match = re.match(r'\*\*(.*?)\*\*:\s*(.*)', line)
                if match:
                    key = match.group(1).lower().replace(' ', '_')
                    value = match.group(2)
                    config['metadata'][key] = value

    # Parse search queries
    queries_match = re.search(r'## Search Queries\s*\n(.*?)(?=\n##|\n\n|$)', content, re.DOTALL)
    if queries_match:
        queries_lines = queries_match.group(1).strip().split('\n')
        for line in queries_lines:
            if line.startswith('- ') and not line.startswith('- **'):
                # Skip format instruction lines and only get actual query lines
                query = line[2:].strip()
                if query and not query.startswith('FORMAT:') and not query.startswith('FOCUS ON:'):
                    config['search_queries'].append(query)

    return config

if __name__ == "__main__":
    config = test_config_parsing('playlist-configs/binaural-beat-therapy.md')
    
    print("=== METADATA PARSING TEST ===")
    for key, value in config['metadata'].items():
        print(f"  {key}: {value}")
    
    print(f"\n=== SEARCH QUERIES PARSING TEST ===")
    print(f"Found {len(config['search_queries'])} queries:")
    for i, query in enumerate(config['search_queries'], 1):
        print(f"  {i}. {query}")
    
    # Test if name is found
    name = config['metadata'].get('name', 'NOT FOUND')
    print(f"\n=== NAME EXTRACTION TEST ===")
    print(f"Playlist name: {name}")
