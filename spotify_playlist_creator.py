#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alex Method DJ - Spotify Playlist Creator
Simple, focused Spotify playlist creation using The Alex Method

Features:
- KISS principle: Simple, direct Spotify playlist creation
- DRY principle: Minimal code duplication
- Search-based track discovery with excellent duration targeting (±10% accuracy)
- Support for both standard and phased playlists
- Markdown configuration system
- Smart refresh functionality

Usage:
    python spotify_playlist_creator.py <playlist_config.md> [--force] [--force-ascii]
"""

import os
import sys
import re
import time
from pathlib import Path
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import Dict, List, Optional, Any
import argparse
from datetime import datetime

# Import modular components
from src.smart_print import safe_print, set_force_ascii_mode
from src.config_parser import PlaylistConfigParser


class SpotifyPlaylistCreator:
    """Simple Spotify playlist creator following KISS and DRY principles"""
    
    def __init__(self):
        """Initialize with Spotify credentials."""
        load_dotenv()
        self.setup_spotify_client()
        self.config = None
        
    def setup_spotify_client(self):
        """Set up Spotify client with authentication."""
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8888/callback')
        
        if not client_id or not client_secret:
            raise ValueError("Missing Spotify credentials in .env file")
        
        scope = "playlist-modify-public playlist-modify-private user-library-read ugc-image-upload"
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope
        )
        
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from markdown file."""
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        content = config_path.read_text(encoding='utf-8')
        
        # Parse metadata section
        metadata = self._parse_metadata(content)
        
        # Parse search queries
        search_queries = self._parse_search_queries(content)
        
        # Parse track categories (for phased playlists)
        track_categories = self._parse_track_categories(content)
        
        # Parse filters
        filters = self._parse_filters(content)
        
        # KISS/DRY: Ensure all playlists have track_categories (convert standard to single-phase)
        if not track_categories and search_queries:
            # Create single phase using search queries and target duration
            target_duration = self._parse_duration(metadata.get('duration_target', '90 minutes'))
            if not target_duration:
                target_duration = 90  # Default fallback
            
            # Use playlist name or default phase name
            phase_name = metadata.get('name', 'Main Phase').replace(' - Alex Method', '').strip()
            if phase_name.endswith(')'):
                # Remove duration suffix if present (e.g., "(90min)")
                phase_name = re.sub(r'\s*\([^)]*\)\s*$', '', phase_name)
            
            track_categories = {
                phase_name: {
                    'duration': target_duration,
                    'queries': search_queries
                }
            }
        
        self.config = {
            'metadata': metadata,
            'search_queries': search_queries,
            'track_categories': track_categories,
            'filters': filters,
            'config_file': config_file,
            'content': content
        }
        
        return self.config
    
    def _parse_metadata(self, content: str) -> Dict[str, Any]:
        """Parse metadata section from config content."""
        metadata = {}
        
        # Extract basic fields
        patterns = {
            'name': r'(?:- )?\*\*Name\*\*:\s*([^\n]+)',
            'description': r'(?:- )?\*\*Description\*\*:\s*([^\n]+)',
            'emoji': r'(?:- )?\*\*Emoji\*\*:\s*([^\n]+)',
            'duration_target': r'(?:- )?\*\*Duration Target\*\*:\s*([^\n]+)',
            'privacy': r'(?:- )?\*\*Privacy\*\*:\s*([^\n]+)',
            'randomize_selection': r'(?:- )?\*\*Randomize Selection\*\*:\s*([^\n]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                metadata[key] = match.group(1).strip()
        
        # Set defaults
        metadata.setdefault('name', 'Alex Method Playlist')
        metadata.setdefault('description', 'Created with Alex Method DJ')
        metadata.setdefault('emoji', '[MUSIC]')
        metadata.setdefault('privacy', 'public')
        metadata.setdefault('randomize_selection', 'false')
        
        return metadata
    
    def _parse_search_queries(self, content: str) -> List[str]:
        """Parse search queries from config content."""
        queries = []
        
        # Look for Search Queries section
        search_section = re.search(r'## Search Queries\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if search_section:
            for line in search_section.group(1).strip().split('\n'):
                line = line.strip()
                if line and line.startswith('- '):
                    query = line[2:].strip()
                    if query:
                        queries.append(query)
        
        return queries
    
    def _parse_track_categories(self, content: str) -> Dict[str, Any]:
        """Parse track categories for phased playlists."""
        categories = {}
        
        # Look for Track Categories section
        categories_section = re.search(r'## Track Categories\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if not categories_section:
            return categories
        
        current_category = None
        current_duration = 30  # Default duration
        current_queries = []
        
        for line in categories_section.group(1).strip().split('\n'):
            line = line.strip()
            
            # Category header (### Category Name (duration))
            category_match = re.match(r'###\s+(.+?)\s*\((\d+)\s*minutes?\)', line)
            if category_match:
                # Save previous category
                if current_category and current_queries:
                    categories[current_category] = {
                        'duration': current_duration,
                        'queries': current_queries.copy()
                    }
                    safe_print(f"   [DEBUG] Saved category: '{current_category}' with {len(current_queries)} queries")
                
                # Start new category
                current_category = category_match.group(1).strip()
                current_duration = int(category_match.group(2))
                current_queries = []
                safe_print(f"   [DEBUG] Found category header: '{current_category}' -> Duration: {current_duration} minutes")
                continue
            
            # Queries line
            if line.startswith('- Queries: '):
                query = line[11:].strip()  # Remove "- Queries: "
                if query:
                    current_queries.append(query)
        
        # Save last category
        if current_category and current_queries:
            categories[current_category] = {
                'duration': current_duration,
                'queries': current_queries
            }
            safe_print(f"   [DEBUG] Final category: '{current_category}' -> Duration: {current_duration} minutes")
        
        return categories
    
    def _parse_filters(self, content: str) -> Dict[str, List[str]]:
        """Parse include/exclude filters."""
        filters = {'include': [], 'exclude': []}
        
        # Look for Track Filters section
        filters_section = re.search(r'## Track Filters\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if not filters_section:
            return filters
        
        current_filter_type = None
        
        for line in filters_section.group(1).strip().split('\n'):
            line = line.strip()
            
            # Filter type headers
            if line.startswith('### Include Keywords'):
                current_filter_type = 'include'
                continue
            elif line.startswith('### Exclude Keywords'):
                current_filter_type = 'exclude'
                continue
            
            # Filter items
            if current_filter_type and line.startswith('- '):
                keyword = line[2:].strip()
                if keyword:
                    filters[current_filter_type].append(keyword.lower())
        
        return filters
    
    def search_tracks(self) -> List[Dict[str, Any]]:
        """Search for tracks based on configuration - all playlists treated as phased."""
        if not self.config:
            raise ValueError("No configuration loaded")
        
        # All playlists use phased logic (KISS/DRY principle)
        return self._create_phased_playlist()
    
    def _create_phased_playlist(self) -> List[Dict[str, Any]]:
        """Create a phased playlist with category-specific durations."""
        if not self.config:
            raise ValueError("No configuration loaded")
            
        safe_print(f"   [THEATER] Creating phased playlist...")
        
        all_tracks = []
        used_track_ids = set()
        
        for phase_name, phase_info in self.config['track_categories'].items():
            duration_minutes = phase_info['duration']
            queries = phase_info['queries']
            
            safe_print(f"   [TARGET] Phase: {phase_name} ({duration_minutes} minutes)")
            
            # Search for tracks for this phase - using direct, intentional search terms
            phase_tracks = []
            for query in queries:
                try:
                    # Use higher limit to get more relevant results for better selection
                    results = self.sp.search(q=query, type='track', limit=50)
                    safe_print(f"   [SEARCH] Direct query '{query}': {len(results['tracks']['items']) if results and results['tracks']['items'] else 0} results")
                    
                    if results and results['tracks']['items']:
                        suitable_count = 0
                        # Tracks are already in relevance order from Spotify - preserve this order
                        for track in results['tracks']['items']:
                            if self._is_track_suitable(track) and track['id'] not in used_track_ids:
                                track_info = self._extract_track_info(track, query)
                                track_info['phase'] = phase_name
                                track_info['relevance_rank'] = len(phase_tracks)  # Track original relevance position
                                phase_tracks.append(track_info)
                                used_track_ids.add(track['id'])
                                suitable_count += 1
                                
                                # Get more tracks for better selection, but maintain relevance order
                                if len(phase_tracks) >= duration_minutes * 6:  # 6x for better selection
                                    break
                        safe_print(f"   [RELEVANCE] {suitable_count} relevant tracks found for '{query}'")
                except Exception as e:
                    safe_print(f"   Warning: Error searching phase '{phase_name}' with query '{query}': {e}")
                    continue
            
            # Apply duration targeting for this phase
            if phase_tracks:
                # Apply diversity filtering before duration targeting
                diverse_tracks = self._apply_diversity_filter(phase_tracks, max_per_artist=2, max_per_album=2)
                optimal_tracks = self._apply_duration_targeting(diverse_tracks, duration_minutes)
                all_tracks.extend(optimal_tracks)
                safe_print(f"   [SUCCESS] Phase {phase_name}: {len(optimal_tracks)} tracks ({sum(t['duration_min'] for t in optimal_tracks):.1f}min)")
            else:
                safe_print(f"   Warning: No tracks found for phase {phase_name}")
        
        # Apply randomization if enabled
        if self._should_randomize():
            all_tracks = self._apply_randomization(all_tracks)
        
        return all_tracks
    
    def _is_track_suitable(self, track: Dict[str, Any]) -> bool:
        """Check if track meets filter criteria."""
        if not self.config:
            return True  # If no config loaded, accept all tracks
            
        # Basic track validation - check if track has basic info
        if not track.get('id') or not track.get('name'):
            return False
        
        # Get track details
        track_name = track['name'].lower()
        artist_name = track['artists'][0]['name'].lower() if track['artists'] else ''
        
        # Check exclude filters
        for exclude_term in self.config['filters']['exclude']:
            if exclude_term in track_name or exclude_term in artist_name:
                return False
        
        # Check include filters (if any)
        if self.config['filters']['include']:
            has_include_term = False
            for include_term in self.config['filters']['include']:
                if include_term in track_name or include_term in artist_name:
                    has_include_term = True
                    break
            if not has_include_term:
                return False
        
        return True
    
    def _extract_track_info(self, track: Dict[str, Any], source_query: str) -> Dict[str, Any]:
        """Extract relevant track information."""
        return {
            'id': track['id'],
            'name': track['name'],
            'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown Artist',
            'album': track['album']['name'] if track.get('album') else 'Unknown Album',
            'duration_min': track['duration_ms'] / 60000,
            'popularity': track.get('popularity', 0),
            'preview_url': track.get('preview_url', ''),
            'external_url': track['external_urls']['spotify'],
            'source_query': source_query
        }
    
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string to minutes."""
        if not duration_str:
            return None
        
        # Extract numbers from duration string
        numbers = re.findall(r'\d+', duration_str)
        if numbers:
            return int(numbers[0])
        
        return None
    
    def _apply_diversity_filter(self, tracks: List[Dict[str, Any]], max_per_artist: int = 2, max_per_album: int = 2) -> List[Dict[str, Any]]:
        """Apply diversity filtering while preserving relevance order - limit tracks per artist and album."""
        if not tracks:
            return tracks
        
        artist_count = {}
        album_count = {}
        diverse_tracks = []
        
        # Process tracks in relevance order (don't sort, preserve original order)
        for track in tracks:
            artist_name = track['artist']
            album_name = track['album']
            
            # Count current occurrences
            current_artist_count = artist_count.get(artist_name, 0)
            current_album_count = album_count.get(album_name, 0)
            
            # Check if adding this track would exceed limits
            if current_artist_count >= max_per_artist:
                continue
            if current_album_count >= max_per_album:
                continue
            
            # Add track and update counts
            diverse_tracks.append(track)
            artist_count[artist_name] = current_artist_count + 1
            album_count[album_name] = current_album_count + 1
        
        # Log diversity results
        total_artists = len(set(t['artist'] for t in diverse_tracks))
        total_albums = len(set(t['album'] for t in diverse_tracks))
        safe_print(f"   [RELEVANCE+DIVERSITY] {len(diverse_tracks)} tracks from {total_artists} artists, {total_albums} albums")
        
        return diverse_tracks

    def _apply_duration_targeting(self, tracks: List[Dict[str, Any]], target_minutes: int) -> List[Dict[str, Any]]:
        """Apply The Alex Method duration targeting with relevance-based selection (±10% variance)."""
        if not tracks:
            return tracks
        
        # Keep tracks in relevance order (Spotify's default search order)
        # Don't sort by duration - preserve search relevance ranking
        
        selected_tracks = []
        current_duration = 0
        target_duration = target_minutes
        variance_range = (target_duration * 0.9, target_duration * 1.1)
        
        # First pass: prioritize most relevant tracks that fit
        for track in tracks:
            track_duration = track['duration_min']
            
            # Check if adding this track would exceed upper limit
            if current_duration + track_duration > variance_range[1]:
                continue
            
            selected_tracks.append(track)
            current_duration += track_duration
            
            # Stop if we're within the target range and have enough tracks
            if (current_duration >= variance_range[0] and 
                len(selected_tracks) >= target_minutes / 4):  # At least 1 track per 4 minutes
                break
        
        # If we haven't reached minimum duration, add more tracks prioritizing relevance
        if current_duration < variance_range[0]:
            remaining_tracks = [t for t in tracks if t not in selected_tracks]
            for track in remaining_tracks:
                track_duration = track['duration_min']
                if current_duration + track_duration <= variance_range[1]:
                    selected_tracks.append(track)
                    current_duration += track_duration
                    if current_duration >= variance_range[0]:
                        break
        
        safe_print(f"   Relevance-based targeting: {current_duration:.1f}min (target: {target_minutes}min ±10%)")
        return selected_tracks
    
    def _should_randomize(self) -> bool:
        """Check if randomization is enabled."""
        if not self.config:
            return False  # Default to no randomization if no config
            
        randomize_str = self.config['metadata'].get('randomize_selection', 'false').lower()
        return randomize_str in ('true', 'yes', '1')
    
    def _apply_randomization(self, tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply randomization to track list."""
        import random
        
        # Use time-based seed for different results each run
        random.seed(int(time.time()))
        randomized_tracks = tracks.copy()
        random.shuffle(randomized_tracks)
        
        safe_print(f"   [REFRESH] Randomization applied with time-based seed")
        return randomized_tracks
    
    def create_or_refresh_playlist(self, tracks: List[Dict[str, Any]], force: bool = False) -> str:
        """Create new playlist or refresh existing one."""
        if not self.config:
            safe_print("[ERROR] No configuration loaded")
            return ""
            
        if not tracks:
            raise ValueError("No tracks to add to playlist")
        
        playlist_name = self.config['metadata']['name']
        playlist_description = self.config['metadata']['description']
        is_public = self.config['metadata']['privacy'].lower() == 'public'
        
        # Check for existing playlist
        existing_playlist = self._find_existing_playlist(playlist_name)
        
        if existing_playlist and not force:
            safe_print(f"[FOLDER] Found existing playlist '{playlist_name}'")
            response = input("Refresh existing playlist? (y/n): ").strip().lower()
            if response not in ['y', 'yes']:
                safe_print("Playlist creation cancelled")
                return ""
        
        playlist_id = None
        
        if existing_playlist:
            # Refresh existing playlist
            playlist_id = existing_playlist['id']
            self._replace_playlist_tracks(playlist_id, tracks)
            self._update_playlist_description(playlist_id, playlist_description, tracks)
            safe_print(f"[SUCCESS] Refreshed existing playlist: {playlist_name}")
        else:
            # Create new playlist
            try:
                current_user = self.sp.current_user()
                if not current_user:
                    raise ValueError("Failed to get current user")
                user_id = current_user['id']
                
                new_playlist = self.sp.user_playlist_create(
                    user=user_id,
                    name=playlist_name,
                    description=playlist_description,
                    public=is_public
                )
                if not new_playlist:
                    raise ValueError("Failed to create playlist")
                playlist_id = new_playlist['id']
            except Exception as e:
                safe_print(f"[ERROR] Failed to create playlist: {e}")
                return ""
            
            # Add tracks
            track_uris = [f"spotify:track:{track['id']}" for track in tracks]
            
            # Add tracks in batches (Spotify limit is 100)
            for i in range(0, len(track_uris), 100):
                batch = track_uris[i:i + 100]
                self.sp.playlist_add_items(playlist_id, batch)
            
            safe_print(f"[SUCCESS] Created new playlist: {playlist_name}")
        
        # Update config file with playlist metadata
        self._update_config_with_playlist_metadata(playlist_id, tracks)
        
        # Display results
        total_duration = sum(t['duration_min'] for t in tracks)
        safe_print(f"[MUSIC] {len(tracks)} tracks added")
        safe_print(f"[EMOJI] Total Duration: {total_duration:.1f} minutes ({total_duration/60:.1f} hours)")
        safe_print(f"[EMOJI] Playlist URL: https://open.spotify.com/playlist/{playlist_id}")
        
        return playlist_id
    
    def _find_existing_playlist(self, playlist_name: str) -> Optional[Dict[str, Any]]:
        """Find existing playlist by name."""
        try:
            playlists = self.sp.current_user_playlists(limit=50)
            if playlists and 'items' in playlists:
                for playlist in playlists['items']:
                    if playlist['name'] == playlist_name:
                        return playlist
        except Exception:
            pass
        return None
    
    def _replace_playlist_tracks(self, playlist_id: str, tracks: List[Dict[str, Any]]):
        """Replace all tracks in existing playlist."""
        # Clear existing tracks
        self.sp.playlist_replace_items(playlist_id, [])
        
        # Add new tracks
        track_uris = [f"spotify:track:{track['id']}" for track in tracks]
        
        for i in range(0, len(track_uris), 100):
            batch = track_uris[i:i + 100]
            self.sp.playlist_add_items(playlist_id, batch)
    
    def _update_playlist_description(self, playlist_id: str, base_description: str, tracks: List[Dict[str, Any]]):
        """Update playlist description with enhanced information."""
        if not self.config:
            return  # Skip description update if no config
            
        # Add phase timestamps for phased playlists
        enhanced_description = base_description
        
        if self.config['track_categories']:
            enhanced_description += self._generate_phase_timestamps(tracks)
        
        # Update the playlist
        self.sp.playlist_change_details(playlist_id, description=enhanced_description)
    
    def _generate_phase_timestamps(self, tracks: List[Dict[str, Any]]) -> str:
        """Generate phase timestamps for phased playlists."""
        if not tracks:
            return ""
        
        # Group tracks by phase and calculate timestamps
        phase_info = {}
        current_time = 0
        
        for track in tracks:
            phase = track.get('phase', 'Unknown')
            if phase not in phase_info:
                phase_info[phase] = {'start_time': current_time, 'track_count': 0}
            
            phase_info[phase]['track_count'] += 1
            current_time += track['duration_min']
        
        # Generate timestamp description
        timestamps = []
        for phase, info in phase_info.items():
            start_min = int(info['start_time'])
            start_sec = int((info['start_time'] - start_min) * 60)
            timestamps.append(f"{start_min}:{start_sec:02d} {phase}")
        
        if timestamps:
            return f" | Phases: {' | '.join(timestamps)}"
        
        return ""
    
    def _update_config_with_playlist_metadata(self, playlist_id: str, tracks: List[Dict[str, Any]]):
        """Update config file with playlist metadata."""
        if not self.config or 'config_file' not in self.config:
            safe_print("[WARNING] Cannot update config file - no file path available")
            return
            
        config_path = Path(self.config['config_file'])
        content = config_path.read_text(encoding='utf-8')
        
        # Create metadata section (without track list)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_duration = sum(t['duration_min'] for t in tracks)
        
        metadata_section = f"""## Spotify Playlist Metadata
- **Spotify URL**: https://open.spotify.com/playlist/{playlist_id}
- **Spotify ID**: {playlist_id}
- **Last Updated**: {timestamp}
- **Track Count**: {len(tracks)}
- **Duration**: {total_duration:.1f} minutes
"""
        
        # Create track list section (to be added at the end)
        track_list_section = f"""
### Track List
"""
        for i, track in enumerate(tracks, 1):
            track_list_section += f" {i:2d}. {track['name']} - {track['artist']} ({track['duration_min']:.1f}m)\n"
        
        # Replace or add metadata section
        metadata_pattern = re.compile(r'^## Spotify Playlist Metadata\n.*?(?=^##|\Z)', re.MULTILINE | re.DOTALL)
        
        if metadata_pattern.search(content):
            content = metadata_pattern.sub(metadata_section.rstrip() + '\n\n', content)
        else:
            # Add after main metadata section
            main_metadata_pattern = re.compile(r'(^## Metadata\n.*?(?=^##))', re.MULTILINE | re.DOTALL)
            match = main_metadata_pattern.search(content)
            
            if match:
                insert_pos = match.end()
                content = content[:insert_pos] + '\n' + metadata_section + content[insert_pos:]
            else:
                content = metadata_section + '\n' + content
        
        # Remove any existing track list at the end
        content = re.sub(r'\n### Track List\n.*$', '', content, flags=re.DOTALL)
        
        # Add track list at the very end
        content = content.rstrip() + '\n' + track_list_section
        
        # Write back to file
        config_path.write_text(content, encoding='utf-8')
        safe_print(f"[SUCCESS] Updated playlist metadata in {self.config['config_file']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Alex Method DJ - Spotify Playlist Creator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python spotify_playlist_creator.py playlist-configs/coffee-shop.md
  python spotify_playlist_creator.py playlist-configs/coffee-shop.md --force
  python spotify_playlist_creator.py playlist-configs/coffee-shop.md --force-ascii
        """
    )
    
    parser.add_argument(
        'config_file',
        help='Path to playlist configuration file (.md format)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force refresh of existing playlist without prompting'
    )
    
    parser.add_argument(
        '--force-ascii',
        action='store_true',
        help='Force ASCII output (disable emojis) for compatibility with older terminals'
    )
    
    args = parser.parse_args()
    
    # Set global ASCII mode using the smart print module
    set_force_ascii_mode(args.force_ascii)
    
    try:
        # Create playlist creator
        creator = SpotifyPlaylistCreator()
        
        safe_print(f"🎵 Alex Method DJ - Spotify Playlist Creator")
        safe_print(f"📁 Loading configuration: {args.config_file}")
        
        # Load configuration using modular parser
        parser_config = PlaylistConfigParser(args.config_file)
        metadata = parser_config.get_metadata()
        visual_theme = parser_config.get_visual_theme()
        
        # Load configuration using legacy method for compatibility
        config = creator.load_config(args.config_file)
        
        # Display configuration summary
        safe_print(f"\n{metadata['emoji']} Playlist: {metadata['name']}")
        safe_print(f"🎯 Target Duration: {metadata.get('duration_target', 'Not specified')}")
        safe_print(f"🔍 Search Queries: {len(config['search_queries'])}")
        
        if config['track_categories']:
            safe_print(f"[THEATER] Phased Playlist: {len(config['track_categories'])} phases")
            for phase_name, phase_info in config['track_categories'].items():
                safe_print(f"   • {phase_name}: {phase_info['duration']} minutes")
        
        # Search for tracks
        safe_print(f"\n[SEARCH] Searching for content on Spotify...")
        tracks = creator.search_tracks()
        
        if not tracks:
            safe_print("[ERROR] No suitable tracks found. Try adjusting your search queries or filters.")
            sys.exit(1)
        
        total_duration = sum(t['duration_min'] for t in tracks)
        safe_print(f"[SUCCESS] Found {len(tracks)} tracks ({total_duration:.1f} minutes)")
        
        # Create playlist
        safe_print(f"\n[EMOJI] Creating playlist on Spotify...")
        playlist_id = creator.create_or_refresh_playlist(tracks, args.force)
        
        if playlist_id:
            safe_print(f"\n[EMOJI] SUCCESS! Playlist ready on Spotify!")
            safe_print(f"{metadata['emoji']} Ready to enjoy your curated playlist!")
        
    except FileNotFoundError:
        safe_print(f"[ERROR] Configuration file not found: {args.config_file}")
        sys.exit(1)
    except Exception as e:
        safe_print(f"[ERROR] Error creating playlist: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
