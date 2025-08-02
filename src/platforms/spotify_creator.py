#!/usr/bin/env python3
"""
Spotify Universal Playlist Creator - Alex Method
Standardized Spotify playlist creation using markdown configuration files

Features:
- Search-based track discovery with excellent duration targeting (±10% accuracy)
- Support for both standard and phased playlists
- Markdown configuration system
- Smart refresh functionality
- Sophisticated duration optimization algorithms

Note: AI recommendation features removed - search-based system provides excellent results.
Part of Universal Platform Playlist Creator system.
"""

import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import Dict, List, Optional, Any
from ..core.base_playlist_creator import BasePlaylistCreator

class SpotifyPlaylistCreator(BasePlaylistCreator):
    def __init__(self):
        """Initialize with Spotify credentials."""
        super().__init__()
        load_dotenv()
        self.setup_platform_client()
        
    def setup_platform_client(self):
        """Set up Spotify client with authentication."""
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8888/callback')
        
        if not client_id or not client_secret:
            raise ValueError("Missing Spotify credentials in .env file")
        
        scope = "playlist-modify-public playlist-modify-private user-library-read"
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope
        )
        
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        
    def get_platform_name(self) -> str:
        """Return the platform name for display purposes."""
        return "Spotify"
    
    def search_content(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for content (tracks) on Spotify."""
        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            if results and 'tracks' in results and results['tracks']:
                return results['tracks']['items']
            return []
        except Exception as e:
            print(f"Search error for query '{query}': {e}")
            return []
    
    def search_tracks(self) -> List[Dict[str, Any]]:
        """Search for tracks based on configuration."""
        if not self.config:
            raise ValueError("No configuration loaded. Call load_config() first.")

        # Check if this is a phased playlist (has Track Categories section)
        if self.has_track_categories():
            return self.create_phased_playlist()
        
        tracks = []
        
        # Parse target duration for dynamic search sizing
        target_duration_str = self.config['metadata'].get('duration_target', '')
        target_minutes = self.parse_target_duration(target_duration_str)
        
        # Calculate dynamic limits based on target duration
        # For 90min playlist: need ~25 tracks, so search for 400+ to find good combinations
        estimated_tracks_needed = max(20, int(target_minutes / 3.5)) if target_minutes else 20
        search_pool_size = estimated_tracks_needed * 15  # 15x more tracks for selection flexibility
        total_limit = max(self.config['track_limits'].get('total_tracks', 50), estimated_tracks_needed)
        per_query_limit = min(50, self.config['track_limits'].get('per_query', 20))  # Increase per-query limit
        
        emoji = self.config['metadata'].get('emoji', '🎵')
        print(f"{emoji} Searching for tracks...")
        
        if target_minutes:
            print(f"   🎯 Target duration: {target_minutes} minutes (±10% = {target_minutes*0.9:.1f}-{target_minutes*1.1:.1f} minutes)")
            print(f"   🎯 Searching for {search_pool_size} tracks to find optimal {estimated_tracks_needed} for duration targeting")
        
        for query in self.config['search_queries']:
            # Use dynamic search pool size based on duration target
            if len(tracks) >= search_pool_size:  # Gather much larger pool for duration targeting
                break
                
            try:
                # Increase search results to get more options
                search_limit = min(50, per_query_limit * 2)  # Get more tracks per query
                results = self.sp.search(q=query, type='track', limit=search_limit)
                if results and results['tracks']['items']:
                    for track in results['tracks']['items']:
                        if len(tracks) >= search_pool_size:
                            break
                            
                        if self.is_content_suitable(track) and track['id'] not in [t['id'] for t in tracks]:
                            track_info = self.extract_content_info(track, query)
                            tracks.append(track_info)
                            
            except Exception as e:
                print(f"   ⚠️ Search issue with '{query}': {e}")
                continue
        
        # Apply any special sorting or filtering
        tracks = self.apply_special_processing(tracks)
        
        # Apply duration targeting
        if target_minutes:
            tracks = self.apply_duration_targeting(tracks, target_minutes)
        
        duration_total = sum(t['duration_min'] for t in tracks)
        print(f"✅ Found {len(tracks)} suitable tracks ({duration_total:.1f} minutes)")
        
        if target_minutes:
            variance = abs(duration_total - target_minutes) / target_minutes * 100
            if variance <= 10:
                print(f"   🎯 Duration target achieved! ({variance:.1f}% variance)")
            else:
                print(f"   ⚠️ Duration variance: {variance:.1f}% (target: ±10%)")
        
        return tracks
    
    def parse_target_duration(self, duration_str: str) -> Optional[int]:
        """Parse target duration from config string."""
        if not duration_str:
            return None
        
        # Extract number from strings like "90 minutes", "2 hours", "120min", etc.
        duration_str = duration_str.lower()
        
        # Look for patterns like "90 minutes" or "2 hours"
        minutes_match = re.search(r'(\d+)\s*(?:minute|min)', duration_str)
        if minutes_match:
            return int(minutes_match.group(1))
        
        hours_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:hour|hr)', duration_str)
        if hours_match:
            return int(float(hours_match.group(1)) * 60)
        
        # Just a number - assume minutes
        number_match = re.search(r'(\d+)', duration_str)
        if number_match:
            return int(number_match.group(1))
        
        return None
    
    def apply_duration_targeting(self, content_list: List[Dict[str, Any]], target_minutes: int) -> List[Dict[str, Any]]:
        """Apply duration targeting to stay within ±10% of target."""
        if not content_list or not target_minutes:
            return content_list
        
        tracks = content_list  # Keep using tracks for internal logic
        target_min = target_minutes * 0.9  # -10%
        target_max = target_minutes * 1.1  # +10%
        
        print(f"   🎯 Optimizing {len(tracks)} tracks for {target_minutes}min target ({target_min:.1f}-{target_max:.1f}min)")
        
        # Check if we have insufficient tracks for the target duration
        estimated_tracks_needed = max(15, target_minutes // 4)  # Rough estimate: 4min per track
        if len(tracks) < estimated_tracks_needed * 1.2:  # Less than 120% of estimated need (more aggressive)
            print(f"   🔄 Insufficient tracks ({len(tracks)}) for {target_minutes}min target - searching with relaxed filters...")
            relaxed_tracks = self.search_with_relaxed_filters()
            if relaxed_tracks:
                print(f"   🔄 Found {len(relaxed_tracks)} additional tracks with relaxed filters")
                # Combine and deduplicate
                all_track_ids = {t['id'] for t in tracks}
                for track in relaxed_tracks:
                    if track['id'] not in all_track_ids:
                        tracks.append(track)
                        all_track_ids.add(track['id'])
                print(f"   🔄 Total tracks after relaxed search: {len(tracks)}")
        
        # Use dynamic programming approach for better track selection
        best_combination = self.find_optimal_track_combination(tracks, target_min, target_max)
        
        if not best_combination:
            # Fallback to greedy approach if DP fails
            best_combination = self.greedy_track_selection(tracks, target_min, target_max)
        
        total_duration = sum(t['duration_min'] for t in best_combination)
        variance = abs(total_duration - target_minutes) / target_minutes
        print(f"   🎯 Duration optimization: {total_duration:.1f}min with {len(best_combination)} tracks")
        
        if variance > 0.15:  # More than 15% variance
            print(f"   ⚠️ High variance ({variance*100:.1f}%) - consider expanding search terms or relaxing filters")
        
        return best_combination
    
    def find_optimal_track_combination(self, tracks: List[Dict[str, Any]], target_min: float, target_max: float) -> List[Dict[str, Any]]:
        """Find optimal combination of tracks using subset sum approach."""
        if len(tracks) > 30:  # Avoid exponential complexity for large track lists
            return self.greedy_track_selection(tracks, target_min, target_max)
        
        best_combination = []
        best_score = float('inf')
        
        # Try different combinations (limited to avoid performance issues)
        from itertools import combinations
        
        for r in range(min(len(tracks), 25), 0, -1):  # Start with larger combinations
            for combo in combinations(tracks, r):
                total_duration = sum(t['duration_min'] for t in combo)
                
                if target_min <= total_duration <= target_max:
                    # Perfect fit - prefer longer durations within range
                    score = target_max - total_duration
                    if score < best_score:
                        best_score = score
                        best_combination = list(combo)
                        if total_duration >= (target_min + target_max) / 2:  # Close to middle of target range
                            break
            
            if best_combination:  # Found good combination
                break
        
        return best_combination
    
    def greedy_track_selection(self, tracks: List[Dict[str, Any]], target_min: float, target_max: float) -> List[Dict[str, Any]]:
        """Greedy track selection for duration targeting."""
        # Sort tracks by duration (mix of long and short for better fitting)
        sorted_tracks = sorted(tracks, key=lambda x: x['duration_min'])
        
        selected_tracks = []
        current_duration = 0
        
        # First pass: add tracks greedily
        for track in sorted_tracks:
            potential_duration = current_duration + track['duration_min']
            if potential_duration <= target_max:
                selected_tracks.append(track)
                current_duration = potential_duration
                if current_duration >= target_min:
                    break
        
        # Second pass: if we're under target, try to add more tracks
        if current_duration < target_min:
            remaining_tracks = [t for t in tracks if t not in selected_tracks]
            for track in remaining_tracks:
                potential_duration = current_duration + track['duration_min']
                if potential_duration <= target_max:
                    selected_tracks.append(track)
                    current_duration = potential_duration
                    if current_duration >= target_min:
                        break
        
        return selected_tracks
    
    def extract_content_info(self, item: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Extract standardized information from Spotify track."""
        return self.extract_track_info(item, query)
    
    def is_content_suitable(self, item: Dict[str, Any]) -> bool:
        """Determine if track meets quality and filtering criteria."""
        return self.is_track_suitable(item)
    
    def is_track_suitable(self, track: Dict[str, Any]) -> bool:
        """Check if track meets the configuration criteria."""
        if not self.config:
            return False
            
        name_lower = track['name'].lower()
        artist_lower = track['artists'][0]['name'].lower()
        
        # Check exclude keywords
        exclude_keywords = self.config['track_filters'].get('exclude', [])
        for keyword in exclude_keywords:
            if keyword.lower() in name_lower or keyword.lower() in artist_lower:
                return False
        
        # Check include keywords (if specified)
        include_keywords = self.config['track_filters'].get('include', [])
        if include_keywords:
            has_include = False
            for keyword in include_keywords:
                if keyword.lower() in name_lower or keyword.lower() in artist_lower:
                    has_include = True
                    break
            if not has_include:
                return False
        
        # Check duration constraints
        duration_filters = self.config['track_filters'].get('duration', {})
        duration_min = track['duration_ms'] / 60000
        
        if 'minimum' in duration_filters and duration_min < duration_filters['minimum']:
            return False
        if 'maximum' in duration_filters and duration_filters['maximum'] and duration_min > duration_filters['maximum']:
            return False
        
        # Check popularity threshold
        popularity_threshold = self.config['track_limits'].get('popularity_threshold')
        if popularity_threshold and track['popularity'] < popularity_threshold:
            return False
            
        return True
    
    def extract_track_info(self, track: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Extract relevant track information."""
        duration_min = track['duration_ms'] / 60000
        
        return {
            'id': track['id'],
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'uri': track['uri'],
            'duration_ms': track['duration_ms'],
            'duration_min': duration_min,
            'popularity': track['popularity'],
            'query': query,
            'category': self.categorize_track(query)
        }
    
    def categorize_track(self, query: str) -> str:
        """Categorize track based on query and configuration."""
        # If we have track categories defined, try to match
        if self.config and self.config['track_categories']:
            for category_name, category_info in self.config['track_categories'].items():
                if any(q.lower() in query.lower() for q in category_info.get('queries', [])):
                    return category_name
        
        # Default categorization
        return 'General'
    
    def apply_special_processing(self, tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply special processing based on configuration."""
        # If we have categories with target minutes, organize accordingly
        if self.config and self.config['track_categories']:
            return self.organize_by_categories(tracks)
        
        # Otherwise, just sort by some criteria
        return sorted(tracks, key=lambda x: x['duration_min'], reverse=True)
    
    def organize_by_categories(self, tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Organize tracks by categories with time targets."""
        if not self.config:
            return tracks
            
        # Group tracks by category
        categorized = {}
        for track in tracks:
            category = track['category']
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(track)
        
        # Sort within each category and build final list
        organized_tracks = []
        
        for category_name, category_info in self.config['track_categories'].items():
            if category_name in categorized:
                category_tracks = categorized[category_name]
                
                # Sort by duration (longer first for deeper experiences)
                category_tracks = sorted(category_tracks, key=lambda x: x['duration_min'], reverse=True)
                
                # Apply time target if specified
                target_minutes = category_info.get('target_minutes', 0)
                if target_minutes > 0:
                    current_duration = 0
                    selected_tracks = []
                    for track in category_tracks:
                        if current_duration < target_minutes:
                            selected_tracks.append(track)
                            current_duration += track['duration_min']
                        else:
                            break
                    organized_tracks.extend(selected_tracks)
                else:
                    organized_tracks.extend(category_tracks)
        
        # Add any uncategorized tracks
        for track in tracks:
            if track['category'] not in self.config['track_categories'] and track not in organized_tracks:
                organized_tracks.append(track)
        
        return organized_tracks
    
    def preview_playlist(self, tracks: List[Dict[str, Any]]) -> bool:
        """Preview the playlist and get user confirmation."""
        if not self.config:
            return False
            
        emoji = self.config['metadata'].get('emoji', '🎵')
        name = self.config['metadata'].get('name', 'Unnamed Playlist')
        
        print(f"\n{emoji} {name}")
        print("=" * 60)
        
        # Show by category if we have them
        if self.config['track_categories']:
            current_category = None
            for i, track in enumerate(tracks, 1):
                if track['category'] != current_category:
                    current_category = track['category']
                    print(f"\n🌀 {current_category}:")
                    print("-" * 30)
                
                print(f"{i:2d}. {track['name']} - {track['artist']} ({track['duration_min']:.1f}m)")
        else:
            for i, track in enumerate(tracks, 1):
                print(f"{i:2d}. {track['name']} - {track['artist']} ({track['duration_min']:.1f}m)")
        
        total_duration = sum(t['duration_min'] for t in tracks)
        target_duration = self.config['metadata'].get('duration_target', '').split()[0] if self.config['metadata'].get('duration_target') else 'N/A'
        
        print(f"\n🎵 Playlist Features:")
        print(f"   • Total Duration: {total_duration:.1f} minutes ({total_duration/60:.1f} hours)")
        print(f"   • Target Duration: {target_duration} minutes")
        print(f"   • {len(tracks)} carefully curated tracks")
        
        # Show special instructions
        if self.config['special_instructions']:
            print(f"   • Special features:")
            for instruction in self.config['special_instructions'][:3]:  # Show first 3
                print(f"     - {instruction}")
        
        response = input(f"\n👍 Create this playlist? (y/n): ").lower().strip()
        return response in ['y', 'yes']
    
    def find_existing_playlist(self, playlist_name: str) -> Optional[Dict[str, Any]]:
        """Find existing playlist by name in user's library."""
        try:
            # Get user's playlists (handle pagination)
            playlists = []
            results = self.sp.current_user_playlists(limit=50)
            
            while results:
                playlists.extend(results['items'])
                if results['next']:
                    results = self.sp.next(results)
                else:
                    break
            
            # Look for exact match (case-insensitive)
            for playlist in playlists:
                if playlist['name'].lower() == playlist_name.lower():
                    return playlist
                    
            return None
            
        except Exception as e:
            print(f"⚠️ Warning: Could not search existing playlists: {e}")
            return None
    
    def refresh_playlist(self, playlist_id: str, tracks: List[Dict[str, Any]]) -> str:
        """Replace all tracks in existing playlist with new tracks."""
        # Clear existing tracks
        existing_tracks = self.sp.playlist_tracks(playlist_id, fields='items.track.uri')
        
        if existing_tracks and existing_tracks.get('items'):
            # Remove tracks in batches of 100 (Spotify's limit)
            track_uris = [item['track']['uri'] for item in existing_tracks['items'] if item.get('track') and item['track']]
            batch_size = 100
            
            for i in range(0, len(track_uris), batch_size):
                batch = track_uris[i:i + batch_size]
                self.sp.playlist_remove_all_occurrences_of_items(playlist_id, batch)
        
        # Add new tracks in batches
        track_uris = [track['uri'] for track in tracks]
        batch_size = 50
        
        for i in range(0, len(track_uris), batch_size):
            batch = track_uris[i:i + batch_size]
            self.sp.playlist_add_items(playlist_id, batch)
            
        return playlist_id

    def create_or_refresh_playlist(self, tracks: List[Dict[str, Any]]) -> str:
        """Create new playlist or refresh existing one."""
        if not self.config:
            raise ValueError("No configuration loaded")
            
        user_info = self.sp.current_user()
        if not user_info:
            raise ValueError("Could not get user information")
        user_id = user_info['id']
        
        # Get playlist details from config
        name = self.config['metadata'].get('name', 'Alex Method Playlist')
        description = self.config['metadata'].get('description', 'Created with Alex Method Universal Playlist Creator')
        is_private = self.config['metadata'].get('privacy', 'public').lower() == 'private'
        
        # Check if playlist already exists
        existing_playlist = self.find_existing_playlist(name)
        
        if existing_playlist:
            print(f"🔄 Found existing playlist '{name}' - refreshing content...")
            playlist_id = self.refresh_playlist(existing_playlist['id'], tracks)
            playlist = existing_playlist
            action = "refreshed"
        else:
            print(f"🆕 Creating new playlist '{name}'...")
            # Create new playlist
            playlist = self.sp.user_playlist_create(
                user=user_id,
                name=name,
                public=not is_private,
                description=description
            )
            
            if not playlist:
                raise ValueError("Failed to create playlist")
                
            # Add tracks in batches
            track_uris = [track['uri'] for track in tracks]
            batch_size = 50
            
            for i in range(0, len(track_uris), batch_size):
                batch = track_uris[i:i + batch_size]
                self.sp.playlist_add_items(playlist['id'], batch)
                
            playlist_id = playlist['id']
            action = "created"
        
        # Success message
        total_duration = sum(t['duration_min'] for t in tracks)
        emoji = self.config['metadata'].get('emoji', '🎵')
        
        print(f"\n🎉 SUCCESS! {action.title()} '{name}'")
        print(f"📱 {len(tracks)} tracks {action}")
        print(f"⏱️ Total Duration: {total_duration:.1f} minutes ({total_duration/60:.1f} hours)")
        print(f"🔗 Playlist URL: {playlist['external_urls']['spotify']}")
        print(f"\n{emoji} Ready to enjoy your curated playlist!")
        
        return playlist_id

    def create_phased_playlist(self):
        """Create a multi-phase playlist with specific durations for each phase."""
        if not self.has_track_categories():
            # Fallback to standard search if no phases detected
            return self.search_standard_tracks()
        
        print(f"   🎭 Creating phased playlist with category-specific durations...")
        
        # Parse phases from Track Categories section
        phases = self.parse_track_categories()
        if not phases:
            return self.search_standard_tracks()
        
        all_tracks = []
        used_track_ids = set()
        
        for phase_name, phase_info in phases.items():
            duration_minutes = phase_info['duration']
            queries = phase_info['queries']
            
            print(f"   🎯 Phase: {phase_name} ({duration_minutes} minutes)")
            
            # Search for tracks specific to this phase
            phase_tracks = []
            per_query_limit = 30
            
            for query in queries:
                try:
                    results = self.sp.search(q=query, type='track', limit=per_query_limit)
                    if results and results['tracks']['items']:
                        for track in results['tracks']['items']:
                            if track['id'] not in used_track_ids and self.is_track_suitable(track):
                                track_info = self.extract_track_info(track, query)
                                track_info['phase'] = phase_name
                                phase_tracks.append(track_info)
                                
                                if len(phase_tracks) >= duration_minutes * 4:  # 4x target for selection
                                    break
                except Exception as e:
                    print(f"   ⚠️ Error searching for phase '{phase_name}' with query '{query}': {e}")
                    continue
            
            # Apply duration targeting for this phase
            if phase_tracks:
                optimal_tracks = self.apply_duration_targeting(phase_tracks, duration_minutes)
                print(f"   ✅ Phase {phase_name}: {len(optimal_tracks)} tracks ({sum(t['duration_min'] for t in optimal_tracks):.1f}min)")
                
                # Add to main playlist and mark as used
                all_tracks.extend(optimal_tracks)
                used_track_ids.update(track['id'] for track in optimal_tracks)
            else:
                print(f"   ⚠️ No tracks found for phase {phase_name}")
        
        return all_tracks
    
    def has_track_categories(self):
        """Check if config has Track Categories section for phased playlists."""
        content = getattr(self, '_raw_config_content', '')
        return '## Track Categories' in content
    
    def parse_track_categories(self):
        """Parse Track Categories section into phases with durations and queries."""
        content = getattr(self, '_raw_config_content', '')
        if not content:
            return {}
        
        phases = {}
        categories_match = re.search(r'## Track Categories\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        
        if not categories_match:
            return {}
        
        categories_content = categories_match.group(1)
        
        # Parse each phase: ### Grounding (10 minutes)
        phase_pattern = r'### ([^(]+)\((\d+)\s*minutes?\)'
        query_pattern = r'- Queries?: (.+)'
        
        current_phase = None
        for line in categories_content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check for phase header
            phase_match = re.match(phase_pattern, line)
            if phase_match:
                phase_name = phase_match.group(1).strip()
                duration = int(phase_match.group(2))
                current_phase = phase_name
                phases[current_phase] = {
                    'duration': duration,
                    'queries': []
                }
                continue
            
            # Check for queries line
            if current_phase and line.startswith('- Queries'):
                query_match = re.match(query_pattern, line)
                if query_match:
                    query_text = query_match.group(1)
                    # Split by commas and clean up
                    queries = [q.strip() for q in query_text.split(',') if q.strip()]
                    phases[current_phase]['queries'].extend(queries)
        
        return phases
    
    def search_with_relaxed_filters(self):
        """Search for additional tracks with relaxed vocal/lyric filters for duration targeting."""
        if not self.config:
            return []
            
        # Temporarily relax both exclude keywords and include keyword requirements
        original_track_filters = self.config.get('track_filters', {}).copy()
        original_excludes = self.config.get('exclude_keywords', []).copy()
        
        # For track_filters, relax vocal restrictions and reduce include keyword requirements
        relaxed_filters = original_track_filters.copy()
        
        # Relax exclude keywords (remove vocal-related ones)
        if 'exclude' in relaxed_filters:
            relaxed_filters['exclude'] = [word for word in relaxed_filters['exclude'] 
                                        if word not in ['vocals', 'vocal', 'lyrics', 'singing', 'sung', 'singer', 'voice']]
        
        # Relax include keywords (remove some requirements for duration targeting)
        if 'include' in relaxed_filters and len(relaxed_filters['include']) > 3:
            # Keep only the most essential include keywords
            essential_keywords = relaxed_filters['include'][:3]  # Keep first 3 most important
            relaxed_filters['include'] = essential_keywords
            print(f"   🔄 Relaxed include keywords to: {essential_keywords}")
        
        # Apply relaxed filters temporarily
        self.config['track_filters'] = relaxed_filters
        
        # Search with relaxed filters
        relaxed_tracks = []
        per_query_limit = min(30, self.config.get('track_limits', {}).get('per_query', 20))
        
        # Use a subset of search queries for relaxed search
        search_queries = self.config.get('search_queries', [])
        for query in search_queries[:5]:  # Limited search for efficiency
            try:
                results = self.sp.search(q=query, type='track', limit=per_query_limit)
                if results and results['tracks']['items']:
                    for track in results['tracks']['items']:
                        if len(relaxed_tracks) >= 100:  # Limit relaxed search
                            break
                            
                        if self.is_track_suitable(track) and track['id'] not in [t['id'] for t in relaxed_tracks]:
                            track_info = self.extract_track_info(track, query)
                            relaxed_tracks.append(track_info)
            except Exception as e:
                print(f"   ⚠️ Error in relaxed search for '{query}': {e}")
                continue
        
        # Restore original filters
        self.config['track_filters'] = original_track_filters
        
        return relaxed_tracks

    def search_standard_tracks(self):
        """Standard track search for non-phased playlists."""
        if not self.config:
            return []
            
        tracks = []
        
        # Parse target duration for dynamic search sizing
        target_duration_str = self.config.get('metadata', {}).get('duration_target', '')
        target_minutes = self.parse_target_duration(target_duration_str)
        
        # Calculate dynamic limits based on target duration
        estimated_tracks_needed = max(20, int(target_minutes / 3.5)) if target_minutes else 20
        search_pool_size = estimated_tracks_needed * 15  # 15x more tracks for selection flexibility
        # Use the HIGHER of config limit or duration-based calculation
        config_total_limit = self.config.get('track_limits', {}).get('total_tracks', 50)
        total_limit = max(config_total_limit, estimated_tracks_needed * 2)  # At least 2x needed tracks
        search_pool_size = max(search_pool_size, config_total_limit * 5)  # At least 5x config limit
        per_query_limit = min(50, self.config.get('track_limits', {}).get('per_query', 20))
        
        emoji = self.config.get('metadata', {}).get('emoji', '🎵')
        print(f"{emoji} Searching for tracks...")
        
        if target_minutes:
            print(f"   🎯 Target duration: {target_minutes} minutes (±10% = {target_minutes*0.9:.1f}-{target_minutes*1.1:.1f} minutes)")
            print(f"   🎯 Searching for {search_pool_size} tracks to find optimal {estimated_tracks_needed} for duration targeting")

        search_queries = self.config.get('search_queries', [])
        for query in search_queries:
            if len(tracks) >= search_pool_size:
                break
                
            try:
                search_limit = min(50, per_query_limit * 2)
                results = self.sp.search(q=query, type='track', limit=search_limit)
                if results and results['tracks']['items']:
                    for track in results['tracks']['items']:
                        if len(tracks) >= search_pool_size:
                            break
                            
                        if self.is_track_suitable(track) and track['id'] not in [t['id'] for t in tracks]:
                            track_info = self.extract_track_info(track, query)
                            tracks.append(track_info)
            except Exception as e:
                print(f"   ⚠️ Error searching for '{query}': {e}")
                continue
        
        return tracks

    def create_playlist(self, name: str, description: str, public: bool = True) -> str:
        """Create a new playlist and return its ID."""
        user_info = self.sp.current_user()
        if not user_info:
            raise ValueError("Could not get user information")
        user_id = user_info['id']
        
        playlist = self.sp.user_playlist_create(
            user=user_id,
            name=name,
            public=public,
            description=description
        )
        
        if not playlist:
            raise ValueError("Failed to create playlist")
            
        return playlist['id']
    
    def add_content_to_playlist(self, playlist_id: str, content_ids: List[str]) -> None:
        """Add tracks to a playlist."""
        # Convert track IDs to URIs if needed
        track_uris = []
        for content_id in content_ids:
            if content_id.startswith('spotify:track:'):
                track_uris.append(content_id)
            else:
                track_uris.append(f'spotify:track:{content_id}')
        
        # Add tracks in batches of 50 (Spotify API limit)
        batch_size = 50
        for i in range(0, len(track_uris), batch_size):
            batch = track_uris[i:i + batch_size]
            self.sp.playlist_add_items(playlist_id, batch)

def main():
    """Main function to create playlist from config file."""
    if len(sys.argv) != 2:
        print("Usage: python universal_playlist_creator.py <config_file.md>")
        print("\nAvailable configs:")
        config_dir = Path("playlist-configs")
        if config_dir.exists():
            for config_file in config_dir.glob("*.md"):
                print(f"  - {config_file.name}")
        else:
            print("  - No playlist-configs directory found")
        return
    
    config_file = sys.argv[1]
    
    # If just filename provided, look in playlist-configs directory
    if not os.path.exists(config_file) and not os.path.dirname(config_file):
        config_file = os.path.join("playlist-configs", config_file)
    
    try:
        print("🎵 UNIVERSAL PLAYLIST CREATOR - Alex Method")
        print("=" * 50)
        
        creator = SpotifyPlaylistCreator()
        
        # Load configuration
        print(f"📖 Loading configuration from {config_file}...")
        config = creator.load_config(config_file)
        
        print(f"🎯 Target: {config['metadata'].get('name', 'Unnamed Playlist')}")
        print(f"⏱️ Duration: {config['metadata'].get('duration_target', 'Not specified')}")
        print()
        
        # Search for tracks
        tracks = creator.search_tracks()
        
        if not tracks:
            print("❌ Couldn't find suitable tracks. Check your configuration or internet connection.")
            return
        
        # Preview and confirm
        if creator.preview_playlist(tracks):
            playlist_id = creator.create_or_refresh_playlist(tracks)
            print(f"\n🚀 Playlist ready! Find it in your Spotify library.")
        else:
            print("👋 No playlist created. Configuration saved for future use!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        if "credentials" in str(e).lower():
            print("Make sure your .env file is configured correctly!")

if __name__ == "__main__":
    main()
