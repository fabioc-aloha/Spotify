#!/usr/bin/env python3
"""
Alex Method DJ Platform - Cover Art Utilities
Helper functions for managing playlist cover art files

Usage:
    python cover_art_utils.py --list
    python cover_art_utils.py --check playlist-configs/neural-network-symphony.md
    python cover_art_utils.py --find neural-network-symphony
"""

import sys
from pathlib import Path
from generate_cover_art_v2 import check_existing_cover_art, get_cover_art_path, GENERATED_DIR
import argparse

def list_all_cover_art():
    """List all generated cover art files"""
    print("🎨 Alex Method DJ Platform - Cover Art Inventory")
    print("=" * 50)
    
    cover_files = {}
    
    # Scan generated directory
    for file_path in GENERATED_DIR.glob("*"):
        if file_path.suffix in ['.jpg', '.png'] or file_path.name.endswith('_base64.txt'):
            # Extract playlist name from filename
            if file_path.name.endswith('_base64.txt'):
                playlist_name = file_path.stem.replace('_base64', '')
                file_type = 'base64'
            else:
                playlist_name = file_path.stem
                file_type = file_path.suffix[1:]  # Remove the dot
            
            if playlist_name not in cover_files:
                cover_files[playlist_name] = {}
            
            cover_files[playlist_name][file_type] = file_path
    
    if not cover_files:
        print("📁 No cover art files found")
        return
    
    for playlist_name, files in sorted(cover_files.items()):
        print(f"\n🎵 {playlist_name}")
        for file_type, file_path in sorted(files.items()):
            size_kb = file_path.stat().st_size / 1024
            print(f"   ✅ {file_type.upper()}: {file_path.name} ({size_kb:.1f} KB)")

def check_playlist_cover_art(config_file: str):
    """Check cover art status for a specific playlist"""
    if not Path(config_file).exists():
        print(f"❌ Playlist config not found: {config_file}")
        return
    
    playlist_name = Path(config_file).stem
    print(f"🎵 Checking cover art for: {playlist_name}")
    print("=" * 50)
    
    existing_art = check_existing_cover_art(config_file)
    
    found_any = False
    for format_name, path in existing_art.items():
        if path:
            size_kb = path.stat().st_size / 1024
            print(f"✅ {format_name.upper()}: {path.name} ({size_kb:.1f} KB)")
            found_any = True
        else:
            print(f"❌ {format_name.upper()}: Not found")
    
    if found_any:
        print(f"\n🎨 Cover art is ready for: {playlist_name}")
    else:
        print(f"\n📋 Generate cover art with: python generate_cover_art_v2.py {config_file}")

def find_cover_art(playlist_name: str):
    """Find cover art files for a playlist name"""
    print(f"🔍 Searching for cover art: {playlist_name}")
    print("=" * 50)
    
    # Look for files matching the playlist name
    found_files = []
    
    for suffix in ['.jpg', '.png']:
        path = GENERATED_DIR / f"{playlist_name}{suffix}"
        if path.exists():
            found_files.append(path)
    
    base64_path = GENERATED_DIR / f"{playlist_name}_base64.txt"
    if base64_path.exists():
        found_files.append(base64_path)
    
    if found_files:
        print("✅ Found cover art files:")
        for file_path in found_files:
            size_kb = file_path.stat().st_size / 1024
            print(f"   📁 {file_path.name} ({size_kb:.1f} KB)")
        
        # Show how to use these files
        print(f"\n🎵 Usage examples:")
        jpeg_path = get_cover_art_path(f"playlist-configs/{playlist_name}.md", 'jpeg')
        if jpeg_path:
            print(f"   Visual preview: {jpeg_path}")
        
        base64_path = get_cover_art_path(f"playlist-configs/{playlist_name}.md", 'base64')
        if base64_path:
            print(f"   Spotify API: {base64_path}")
    else:
        print("❌ No cover art found")
        print(f"📋 Generate with: python generate_cover_art_v2.py playlist-configs/{playlist_name}.md")

def main():
    parser = argparse.ArgumentParser(description='Alex Method DJ Cover Art Utilities')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true', help='List all generated cover art')
    group.add_argument('--check', type=str, help='Check cover art for specific playlist config')
    group.add_argument('--find', type=str, help='Find cover art by playlist name')
    
    args = parser.parse_args()
    
    if args.list:
        list_all_cover_art()
    elif args.check:
        check_playlist_cover_art(args.check)
    elif args.find:
        find_cover_art(args.find)

if __name__ == "__main__":
    main()
