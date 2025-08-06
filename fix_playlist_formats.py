#!/usr/bin/env python3
"""
Fix metadata format in all playlist configurations to match template
"""

import re
from pathlib import Path

def fix_metadata_format(config_file):
    """Fix metadata format to match template requirements"""
    config_path = Path(config_file)
    
    if not config_path.exists():
        return f"❌ File not found: {config_file}"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return f"❌ Error reading {config_file}: {e}"

    # Find the Name field that needs fixing
    # Look for **Name**: without the bullet point prefix
    pattern = r'^(\*\*Name\*\*:.*)$'
    match = re.search(pattern, content, re.MULTILINE)
    
    if match:
        old_line = match.group(1)
        new_line = f"- {old_line}"
        
        # Replace the line
        new_content = content.replace(old_line, new_line)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return f"✅ Fixed: {config_path.stem}"
        except Exception as e:
            return f"❌ Error writing {config_file}: {e}"
    else:
        return f"⏭️ Skipped: {config_path.stem} (already correct or no Name field found)"

def main():
    playlist_dir = Path('playlist-configs')
    
    if not playlist_dir.exists():
        print("❌ playlist-configs directory not found!")
        return
    
    config_files = list(playlist_dir.glob('*.md'))
    # Exclude template and README
    config_files = [f for f in config_files if f.stem not in ['TEMPLATE-universal', 'README']]
    
    print(f"🔧 Fixing metadata format in {len(config_files)} playlist configurations...\n")
    
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    for config_file in sorted(config_files):
        result = fix_metadata_format(config_file)
        print(result)
        
        if result.startswith('✅'):
            fixed_count += 1
        elif result.startswith('⏭️'):
            skipped_count += 1
        else:
            error_count += 1
    
    print(f"\n" + "="*60)
    print(f"📊 SUMMARY:")
    print(f"✅ Fixed: {fixed_count}")
    print(f"⏭️ Skipped (already correct): {skipped_count}")
    print(f"❌ Errors: {error_count}")
    
    if fixed_count > 0:
        print(f"\n🎉 Successfully fixed {fixed_count} playlist configurations!")
        print("All playlists should now have consistent metadata format.")

if __name__ == "__main__":
    main()
