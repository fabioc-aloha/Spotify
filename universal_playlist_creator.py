#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
    python universal_playlist_creator.py <config_file> [--platform spotify|youtube-music]
"""

import sys
import os

# Set UTF-8 encoding for Windows console to handle emoji characters
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Import safe print utility
try:
    from src.utils.safe_print import safe_print
except ImportError:
    # Fallback if import fails
    def safe_print(message):
        try:
            print(message)
        except UnicodeEncodeError:
            safe_message = message.replace('🎵', '[MUSIC]').replace('❌', '[ERROR]').replace('📁', '[FOLDER]')
            safe_message = safe_message.replace('✅', '[SUCCESS]').replace('', '[BRAIN]').replace('🎭', '[THEATER]')
            safe_message = safe_message.replace('🔍', '[SEARCH]').replace('🎯', '[TARGET]').replace('🔄', '[REFRESH]')
            print(safe_message)

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
        safe_print(f"⚠️ Spotify unavailable: {e}")
    
    # Check Enhanced YouTube Music availability (preferred)
    try:
        from src.platforms.enhanced_youtube_music_creator import EnhancedYouTubeMusicCreator
        platforms['youtube-music'] = EnhancedYouTubeMusicCreator
    except ImportError:
        # Fallback to original YouTube creator
        try:
            from src.platforms.youtube_creator import YouTubeMusicPlaylistCreator
            platforms['youtube-music'] = YouTubeMusicPlaylistCreator
        except ImportError as e:
            safe_print(f"⚠️ YouTube Music unavailable: {e}")
    
    return platforms

def create_playlist_alex_method_dj(config_file: str, platform: str = 'spotify') -> bool:
    """Create playlist using specified platform."""
    
    # Get available platforms
    available_platforms = get_available_platforms()
    
    if not available_platforms:
        safe_print("❌ No platforms available. Please install required dependencies:")
        safe_print("   Spotify: pip install spotipy python-dotenv")
        safe_print("   YouTube: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return False
    
    if platform not in available_platforms:
        safe_print(f"❌ Platform '{platform}' not available")
        safe_print(f"Available platforms: {', '.join(available_platforms.keys())}")
        return False
    
    try:
        # Create platform-specific creator
        CreatorClass = available_platforms[platform]
        creator = CreatorClass()
        
        safe_print(f"🎵 Alex Method DJ - {creator.get_platform_name()}")
        safe_print(f"📁 Loading configuration: {config_file}")
        
        # Load configuration
        config = creator.load_config(config_file)
        
        # Display configuration summary
        metadata = config.get('metadata', {})
        playlist_name = metadata.get('name', 'Unnamed Playlist')
        target_duration = metadata.get('duration_target', 'Not specified')
        emoji = metadata.get('emoji', '🎵')
        
        safe_print(f"\n{emoji} Playlist: {playlist_name}")
        safe_print(f"🎯 Target Duration: {target_duration}")
        safe_print(f"🔍 Search Queries: {len(config.get('search_queries', []))}")
        
        # Check for phased playlist
        if creator.has_track_categories():
            phases = creator.parse_track_categories()
            safe_print(f"🎭 Phased Playlist: {len(phases)} phases")
            for phase_name, phase_info in phases.items():
                safe_print(f"   • {phase_name}: {phase_info['duration']} minutes")
        
        # Search for content
        safe_print(f"\n🔍 Searching for content on {creator.get_platform_name()}...")
        
        if hasattr(creator, 'search_tracks'):
            # Use Spotify-specific method for backward compatibility
            content = creator.search_tracks()
        elif hasattr(creator, 'search_tracks_from_spotify_metadata'):
            # Use enhanced YouTube Music cross-platform method
            content = creator.search_tracks_from_spotify_metadata()
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
            safe_print("❌ No suitable content found. Try adjusting your search queries or filters.")
            return False
        
        total_duration = sum(item.get('duration_minutes', item.get('duration_min', 0)) for item in content)
        safe_print(f"✅ Found {len(content)} items ({total_duration:.1f} minutes)")
        
        # Create playlist using platform-specific method if available
        safe_print(f"\n🆕 Creating playlist on {creator.get_platform_name()}...")
        
        # Use Spotify-specific enhanced method if available
        if hasattr(creator, 'create_or_refresh_playlist'):
            # Spotify has enhanced playlist management with metadata saving
            playlist_id = creator.create_or_refresh_playlist(content)
        elif hasattr(creator, 'create_youtube_music_playlist_from_metadata'):
            # Enhanced YouTube Music has metadata-based playlist creation
            playlist_id = creator.create_youtube_music_playlist_from_metadata(config_file)
            if playlist_id:
                safe_print(f"\n🎉 SUCCESS! Created '{playlist_name}' on YouTube Music")
                safe_print(f"📱 {len(content)} tracks processed")
                total_duration = sum(item.get('duration_minutes', item.get('duration_min', 0)) for item in content)
                safe_print(f"⏱️ Total Duration: {total_duration:.1f} minutes ({total_duration/60:.1f} hours)")
                safe_print(f"🔗 Playlist URL: https://music.youtube.com/playlist?list={playlist_id}")
                safe_print(f"\n{emoji} Ready to enjoy your curated playlist!")
        else:
            # Generic platform method for other platforms
            playlist_description = metadata.get('description', f'Created with Alex Method DJ for {creator.get_platform_name()}')
            is_public = metadata.get('privacy', 'public').lower() == 'public'
            
            # Check if playlist exists
            existing_playlist = creator.find_existing_playlist(playlist_name)
            
            if existing_playlist:
                print(f"🔄 Found existing playlist '{playlist_name}' - would you like to refresh it? (y/n): ", end="")
                response = input().strip().lower()
                if response in ['y', 'yes']:
                    print("🔄 Refreshing playlist...")
                else:
                    print("❌ Playlist creation cancelled")
                    return False
            
            # Create new playlist
            playlist_id = creator.create_playlist(playlist_name, playlist_description, is_public)
            
            # Add content to playlist
            content_ids = [item['id'] for item in content]
            creator.add_content_to_playlist(playlist_id, content_ids)
            
            # Success message for generic platforms
            safe_print(f"\n🎉 SUCCESS! Created '{playlist_name}' on {creator.get_platform_name()}")
            safe_print(f"📱 {len(content)} items added")
            safe_print(f"⏱️ Total Duration: {total_duration:.1f} minutes ({total_duration/60:.1f} hours)")
            
            if platform == 'youtube-music':
                safe_print(f"🔗 Playlist URL: https://www.youtube.com/playlist?list={playlist_id}")
            
            safe_print(f"\n{emoji} Ready to enjoy your curated playlist!")
        
        return True
        
    except FileNotFoundError:
        safe_print(f"❌ Configuration file not found: {config_file}")
        return False
    except Exception as e:
        safe_print(f"❌ Error creating playlist: {e}")
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
  python universal_playlist_creator.py douglas-retro-gaming.md --platform youtube-music
  
Supported Platforms:
  spotify       - Spotify (requires spotipy, credentials in .env)
  youtube-music - YouTube Music (requires google-api-python-client, API key/OAuth)
        """
    )
    
    parser.add_argument(
        'config_file',
        nargs='?',
        help='Path to playlist configuration file (.md format)'
    )
    
    parser.add_argument(
        '--platform', '-p',
        choices=['spotify', 'youtube-music'],
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
