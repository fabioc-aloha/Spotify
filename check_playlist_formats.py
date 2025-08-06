#!/usr/bin/env python3
"""
Check all playlist configurations for template format compliance
"""

import re
from pathlib import Path

def check_metadata_format(config_file):
    """Check if metadata format matches template requirements"""
    config_path = Path(config_file)
    
    if not config_path.exists():
        return f"❌ File not found: {config_file}"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return f"❌ Error reading {config_file}: {e}"

    # Parse metadata section
    metadata_match = re.search(r'## Metadata\s*\n(.*?)(?=\n##|\n\n|$)', content, re.DOTALL)
    if not metadata_match:
        return f"❌ No metadata section found in {config_file}"
    
    metadata_lines = metadata_match.group(1).strip().split('\n')
    
    # Check for Name field specifically
    name_found = False
    name_format_correct = False
    
    for line in metadata_lines:
        if 'Name' in line:
            name_found = True
            # Check if it starts with bullet point
            if line.startswith('- **Name**:'):
                name_format_correct = True
                # Extract the name value
                match = re.match(r'- \*\*Name\*\*:\s*(.*)', line)
                name_value = match.group(1) if match else "Could not extract"
                return f"✅ {config_path.stem}: {name_value}"
            elif line.startswith('**Name**:'):
                # Missing bullet point
                match = re.match(r'\*\*Name\*\*:\s*(.*)', line)
                name_value = match.group(1) if match else "Could not extract"
                return f"🔧 {config_path.stem}: NEEDS FIX - {name_value}"
    
    if not name_found:
        return f"❌ {config_path.stem}: No Name field found"
    
    return f"❓ {config_path.stem}: Name field format unclear"

def main():
    playlist_dir = Path('playlist-configs')
    
    if not playlist_dir.exists():
        print("❌ playlist-configs directory not found!")
        return
    
    config_files = list(playlist_dir.glob('*.md'))
    # Exclude template and README
    config_files = [f for f in config_files if f.stem not in ['TEMPLATE-universal', 'README']]
    
    print(f"🔍 Checking {len(config_files)} playlist configurations...\n")
    
    needs_fix = []
    ready = []
    errors = []
    
    for config_file in sorted(config_files):
        result = check_metadata_format(config_file)
        print(result)
        
        if result.startswith('✅'):
            ready.append(config_file.stem)
        elif result.startswith('🔧'):
            needs_fix.append(config_file.stem)
        else:
            errors.append(config_file.stem)
    
    print(f"\n" + "="*60)
    print(f"📊 SUMMARY:")
    print(f"✅ Ready to run: {len(ready)}")
    print(f"🔧 Need format fix: {len(needs_fix)}")
    print(f"❌ Errors: {len(errors)}")
    
    if needs_fix:
        print(f"\n🔧 Files needing format fix:")
        for file in needs_fix:
            print(f"   - {file}.md")
    
    if errors:
        print(f"\n❌ Files with errors:")
        for file in errors:
            print(f"   - {file}.md")

if __name__ == "__main__":
    main()
