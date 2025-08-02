#!/usr/bin/env python3
"""
Alex Method DJ - Multi-Platform Support
Creates DJ playlists across different music platforms using The Alex Method

Supported Platforms:
- Spotify (fully implemented)
- YouTube Music (beta - requires API setup)

Features:
- Platform-agnostic playlist creation
- Consistent configuration format across platforms
- Duration targeting with ±10% variance (The Alex Method)
- Smart content curation and filtering
- Support for both standard and phased playlists

Usage:
    python universal_playlist_creator.py <config_file> [--platform spotify|youtube]
"""

import sys
import argparse
from typing import Dict, Any, Optional
from pathlib import Path

def get_available_platforms():
    """Get list of available platforms based on installed dependencies."""
    platforms = {}
    
    # Check Spotify availability
    try:
        from src.platforms.spotify_creator import SpotifyPlaylistCreator
        platforms['spotify'] = SpotifyPlaylistCreator
    except ImportError as e:
        print(f"⚠️ Spotify unavailable: {e}")
    
    # Check YouTube Music availability
    try:
        from src.platforms.youtube_creator import YouTubeMusicPlaylistCreator
        platforms['youtube'] = YouTubeMusicPlaylistCreator
    except ImportError as e:
        print(f"⚠️ YouTube Music unavailable: {e}")
    
    return platforms

def create_playlist_alex_method_dj(config_file: str, platform: str = 'spotify') -> bool:
    """Create playlist using specified platform."""
    
    # Get available platforms
    available_platforms = get_available_platforms()
    
    if not available_platforms:
        print("❌ No platforms available. Please install required dependencies:")
        print("   Spotify: pip install spotipy python-dotenv")
        print("   YouTube: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return False
    
    if platform not in available_platforms:
        print(f"❌ Platform '{platform}' not available")
        print(f"Available platforms: {', '.join(available_platforms.keys())}")
        return False
    
    try:
        # Create platform-specific creator
        CreatorClass = available_platforms[platform]
        creator = CreatorClass()
        
        print(f"🎵 Alex Method DJ - {creator.get_platform_name()}")
        print(f"📁 Loading configuration: {config_file}")
        
        # Load configuration
        config = creator.load_config(config_file)
        
        # Display configuration summary
        metadata = config.get('metadata', {})
        playlist_name = metadata.get('name', 'Unnamed Playlist')
        target_duration = metadata.get('duration_target', 'Not specified')
        emoji = metadata.get('emoji', '🎵')
        
        print(f"\n{emoji} Playlist: {playlist_name}")
        print(f"🎯 Target Duration: {target_duration}")
        print(f"🔍 Search Queries: {len(config.get('search_queries', []))}")
        
        # Check for phased playlist
        if creator.has_track_categories():
            phases = creator.parse_track_categories()
            print(f"🎭 Phased Playlist: {len(phases)} phases")
            for phase_name, phase_info in phases.items():
                print(f"   • {phase_name}: {phase_info['duration']} minutes")
        
        # Search for content
        print(f"\n🔍 Searching for content on {creator.get_platform_name()}...")
        
        if hasattr(creator, 'search_tracks'):
            # Use Spotify-specific method for backward compatibility
            content = creator.search_tracks()
        else:
            # Use generic search for other platforms
            all_content = []
            for query in config.get('search_queries', []):
                results = creator.search_content(query, limit=50)
                for item in results:
                    if creator.is_content_suitable(item):
                        content_info = creator.extract_content_info(item, query)
                        all_content.append(content_info)
            
            # Apply duration targeting if specified
            target_duration_str = metadata.get('duration_target', '')
            target_minutes = creator.parse_target_duration(target_duration_str)
            
            if target_minutes:
                content = creator.apply_duration_targeting(all_content, target_minutes)
            else:
                content = all_content[:config.get('track_limits', {}).get('total_tracks', 50)]
        
        if not content:
            print("❌ No suitable content found. Try adjusting your search queries or filters.")
            return False
        
        total_duration = sum(item.get('duration_minutes', item.get('duration_min', 0)) for item in content)
        print(f"✅ Found {len(content)} items ({total_duration:.1f} minutes)")
        
        # Create playlist
        print(f"\n🆕 Creating playlist on {creator.get_platform_name()}...")
        
        playlist_description = metadata.get('description', f'Created with Alex Method DJ for {creator.get_platform_name()}')
        is_public = metadata.get('privacy', 'public').lower() == 'public'
        
        # Check if playlist exists
        existing_playlist = creator.find_existing_playlist(playlist_name)
        
        if existing_playlist:
            print(f"🔄 Found existing playlist '{playlist_name}' - would you like to refresh it? (y/n): ", end="")
            response = input().strip().lower()
            if response in ['y', 'yes']:
                # For now, create new playlist (refresh logic platform-specific)
                print("🔄 Refreshing playlist...")
            else:
                print("❌ Playlist creation cancelled")
                return False
        
        # Create new playlist
        playlist_id = creator.create_playlist(playlist_name, playlist_description, is_public)
        
        # Add content to playlist
        content_ids = [item['id'] for item in content]
        creator.add_content_to_playlist(playlist_id, content_ids)
        
        # Success message
        print(f"\n🎉 SUCCESS! Created '{playlist_name}' on {creator.get_platform_name()}")
        print(f"📱 {len(content)} items added")
        print(f"⏱️ Total Duration: {total_duration:.1f} minutes ({total_duration/60:.1f} hours)")
        
        if hasattr(creator, 'sp') and existing_playlist:
            # Spotify-specific URL
            print(f"🔗 Playlist URL: https://open.spotify.com/playlist/{playlist_id}")
        elif platform == 'youtube':
            print(f"🔗 Playlist URL: https://www.youtube.com/playlist?list={playlist_id}")
        
        print(f"\n{emoji} Ready to enjoy your curated playlist!")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_file}")
        return False
    except Exception as e:
        print(f"❌ Error creating playlist: {e}")
        return False

def main():
    """Main entry point for Alex Method DJ playlist creator."""
    parser = argparse.ArgumentParser(
        description="Alex Method DJ - Multi-Platform Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python universal_playlist_creator.py douglas-retro-gaming.md
  python universal_playlist_creator.py douglas-retro-gaming.md --platform spotify
  python universal_playlist_creator.py douglas-retro-gaming.md --platform youtube
  
Supported Platforms:
  spotify    - Spotify (requires spotipy, credentials in .env)
  youtube    - YouTube Music (requires google-api-python-client, API key/OAuth)
        """
    )
    
    parser.add_argument(
        'config_file',
        nargs='?',
        help='Path to playlist configuration file (.md format)'
    )
    
    parser.add_argument(
        '--platform', '-p',
        choices=['spotify', 'youtube'],
        default='spotify',
        help='Target platform for playlist creation (default: spotify)'
    )
    
    parser.add_argument(
        '--list-platforms',
        action='store_true',
        help='List available platforms and exit'
    )
    
    args = parser.parse_args()
    
    # List platforms mode
    if args.list_platforms:
        print("🎵 Alex Method DJ - Available Platforms")
        platforms = get_available_platforms()
        
        if platforms:
            for platform_name in platforms.keys():
                print(f"✅ {platform_name}")
        else:
            print("❌ No platforms available")
            print("Install dependencies:")
            print("  Spotify: pip install spotipy python-dotenv")
            print("  YouTube: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        
        return
    
    # Validate config file
    if not args.config_file:
        parser.print_help()
        sys.exit(1)
    
    config_path = Path(args.config_file)
    if not config_path.exists():
        print(f"❌ Configuration file not found: {args.config_file}")
        sys.exit(1)
    
    # Create playlist
    success = create_playlist_alex_method_dj(args.config_file, args.platform)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
