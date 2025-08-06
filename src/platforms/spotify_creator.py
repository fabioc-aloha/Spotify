#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alex Method DJ Spotify Creator - Professional DJ Playlist Creation
The Alex Method: Professional DJ techniques for creating perfect musical journeys
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
import requests
from ..core.base_playlist_creator import BasePlaylistCreator
from ..utils.safe_print import safe_print

from ..core.base_playlist_creator import BasePlaylistCreator
from ..utils.safe_print import safe_print

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
        
        scope = "playlist-modify-public playlist-modify-private user-library-read ugc-image-upload"
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
            safe_print(f"Search error for query '{query}': {e}")
            return []
    
    def search_tracks(self) -> List[Dict[str, Any]]:
        """Search for tracks based on configuration."""
        if not self.config:
            raise ValueError("No configuration loaded. Call load_config() first.")
            
        # Check if randomization is enabled
        randomize = False
        if 'metadata' in self.config:
            randomize_str = self.config['metadata'].get('randomize_selection', 'false').lower()
            randomize = randomize_str in ('true', 'yes', '1')
            
        if randomize:
            safe_print(f"   🔀 RANDOMIZATION ENABLED: Track selection will be different on each refresh")

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
        safe_print(f"{emoji} Searching for tracks...")
        
        if target_minutes:
            safe_print(f"   🎯 Target duration: {target_minutes} minutes (±10% = {target_minutes*0.9:.1f}-{target_minutes*1.1:.1f} minutes)")
            safe_print(f"   🎯 Searching for {search_pool_size} tracks to find optimal {estimated_tracks_needed} for duration targeting")
        
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
                safe_print(f"   ⚠️ Search issue with '{query}': {e}")
                continue
        
        # Apply any special sorting or filtering
        tracks = self.apply_special_processing(tracks)
        
        # Apply final deduplication to standard playlists as well
        deduplicated_tracks = self.apply_final_deduplication(tracks)
        if len(deduplicated_tracks) != len(tracks):
            safe_print(f"   🔄 Final deduplication: {len(tracks)} → {len(deduplicated_tracks)} tracks")
        tracks = deduplicated_tracks
        
        # Apply duration targeting
        if target_minutes:
            tracks = self.apply_duration_targeting(tracks, target_minutes)
        
        duration_total = sum(t['duration_min'] for t in tracks)
        safe_print(f"✅ Found {len(tracks)} suitable tracks ({duration_total:.1f} minutes)")
        
        if target_minutes:
            variance = abs(duration_total - target_minutes) / target_minutes * 100
            if variance <= 10:
                safe_print(f"   🎯 Duration target achieved! ({variance:.1f}% variance)")
            else:
                safe_print(f"   ⚠️ Duration variance: {variance:.1f}% (target: ±10%)")
        
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
        
        safe_print(f"   🎯 Optimizing {len(tracks)} tracks for {target_minutes}min target ({target_min:.1f}-{target_max:.1f}min)")
        
        # Check if we have insufficient tracks for the target duration
        estimated_tracks_needed = max(15, target_minutes // 4)  # Rough estimate: 4min per track
        if len(tracks) < estimated_tracks_needed * 1.2:  # Less than 120% of estimated need (more aggressive)
            safe_print(f"   🔄 Insufficient tracks ({len(tracks)}) for {target_minutes}min target - searching with relaxed filters...")
            relaxed_tracks = self.search_with_relaxed_filters()
            if relaxed_tracks:
                safe_print(f"   🔄 Found {len(relaxed_tracks)} additional tracks with relaxed filters")
                # Combine and deduplicate using enhanced deduplication
                existing_track_ids = {t['id'] for t in tracks}
                existing_track_names = set()
                for t in tracks:
                    normalized_identifier = self.normalize_track_identifier(t['name'], t['artist'])
                    existing_track_names.add(normalized_identifier)
                
                for track in relaxed_tracks:
                    # Check both ID and name-based duplicates
                    normalized_identifier = self.normalize_track_identifier(track['name'], track['artist'])
                    if track['id'] not in existing_track_ids and normalized_identifier not in existing_track_names:
                        tracks.append(track)
                        existing_track_ids.add(track['id'])
                        existing_track_names.add(normalized_identifier)
                safe_print(f"   🔄 Total tracks after relaxed search: {len(tracks)}")
        
        # Use dynamic programming approach for better track selection
        best_combination = self.find_optimal_track_combination(tracks, target_min, target_max)
        
        if not best_combination:
            # Fallback to greedy approach if DP fails
            best_combination = self.greedy_track_selection(tracks, target_min, target_max)
        
        total_duration = sum(t['duration_min'] for t in best_combination)
        variance = abs(total_duration - target_minutes) / target_minutes
        safe_print(f"   🎯 Duration optimization: {total_duration:.1f}min with {len(best_combination)} tracks")
        
        if variance > 0.15:  # More than 15% variance
            safe_print(f"   ⚠️ High variance ({variance*100:.1f}%) - consider expanding search terms or relaxing filters")
        
        return best_combination
    
    def find_optimal_track_combination(self, tracks: List[Dict[str, Any]], target_min: float, target_max: float) -> List[Dict[str, Any]]:
        """Find optimal combination of tracks using subset sum approach."""
        # Store the original track order 
        original_tracks = tracks.copy()
        
        # IMPORTANT: We don't randomize here anymore. 
        # Randomization should already be applied BEFORE calling this function
        # This function should just preserve the existing order
        
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
        
        # Preserve original track order (tracks might already be randomized or sorted earlier)
        if best_combination:
            # Find indices of selected tracks in original list
            selected_ids = {track['id'] for track in best_combination}
            preserved_tracks = [track for track in original_tracks if track['id'] in selected_ids]
            if len(preserved_tracks) == len(best_combination):
                safe_print(f"   � Preserving original track order in optimal combination")
                return preserved_tracks
        
        return best_combination
    
    def greedy_track_selection(self, tracks: List[Dict[str, Any]], target_min: float, target_max: float) -> List[Dict[str, Any]]:
        """Greedy track selection for duration targeting."""
        # Store the original track order
        original_tracks = tracks.copy()
        
        # Always use the original order (tracks are already randomized or sorted as needed)
        tracks_to_use = tracks
        safe_print(f"   � Using existing track order for greedy selection")
        
        selected_tracks = []
        current_duration = 0
        
        # First pass: add tracks greedily
        for track in tracks_to_use:
            potential_duration = current_duration + track['duration_min']
            if potential_duration <= target_max:
                selected_tracks.append(track)
                current_duration = potential_duration
                if current_duration >= target_min:
                    break
        
        # Second pass: if we're under target, try to add more tracks
        if current_duration < target_min:
            # Use remaining tracks in original order to preserve randomization or sort order
            remaining_tracks = [t for t in original_tracks if t not in selected_tracks]
            
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
    
    def normalize_track_identifier(self, track_name: str, artist_name: str) -> str:
        """Create a normalized identifier for duplicate detection."""
        import re
        
        # Normalize track name: remove special characters, convert to lowercase
        normalized_name = re.sub(r'[^\w\s]', '', track_name.lower())
        normalized_name = re.sub(r'\s+', ' ', normalized_name).strip()
        
        # Normalize artist name: remove special characters, convert to lowercase
        normalized_artist = re.sub(r'[^\w\s]', '', artist_name.lower())
        normalized_artist = re.sub(r'\s+', ' ', normalized_artist).strip()
        
        # Create combined identifier
        return f"{normalized_artist}::{normalized_name}"
    
    def is_duplicate_track(self, track_info: Dict[str, Any], existing_tracks: List[Dict[str, Any]], 
                          used_track_ids: set, used_track_names: set) -> bool:
        """Check if track is a duplicate by ID or name+artist combination."""
        track_id = track_info['id']
        track_name = track_info['name']
        artist_name = track_info['artist']
        
        # Check for ID-based duplicate
        if track_id in used_track_ids:
            return True
        
        # Check for name+artist based duplicate
        normalized_identifier = self.normalize_track_identifier(track_name, artist_name)
        if normalized_identifier in used_track_names:
            return True
        
        return False
    
    def add_track_to_dedup_sets(self, track_info: Dict[str, Any], used_track_ids: set, used_track_names: set):
        """Add track to deduplication sets for ID and name-based duplicate detection."""
        used_track_ids.add(track_info['id'])
        normalized_identifier = self.normalize_track_identifier(track_info['name'], track_info['artist'])
        used_track_names.add(normalized_identifier)

    def apply_final_deduplication(self, tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply final deduplication to remove any duplicate tracks that may have slipped through."""
        if not tracks:
            return tracks
        
        seen_ids = set()
        seen_names = set()
        deduplicated_tracks = []
        
        for track in tracks:
            track_id = track['id']
            normalized_identifier = self.normalize_track_identifier(track['name'], track['artist'])
            
            # Check if we've already seen this track
            if track_id not in seen_ids and normalized_identifier not in seen_names:
                deduplicated_tracks.append(track)
                seen_ids.add(track_id)
                seen_names.add(normalized_identifier)
        
        return deduplicated_tracks

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
        
        # Apply randomization using the standardized helper method
        tracks = self.apply_randomization(tracks, "standard_playlist")
        
        # If randomization was not applied, sort by duration as fallback
        if not self.should_randomize_tracks():
            tracks = sorted(tracks, key=lambda x: x['duration_min'], reverse=True)
            
        return tracks
    
    def organize_by_categories(self, tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Organize tracks by categories with time targets."""
        if not self.config:
            return tracks
        
        # Check if randomization is enabled
        randomize = False
        if 'metadata' in self.config:
            randomize_str = self.config['metadata'].get('randomize_selection', 'false').lower()
            randomize = randomize_str in ('true', 'yes', '1')
            
            if randomize:
                safe_print(f"   🎲 Randomization enabled for this playlist (randomize_selection: true)")
            else:
                safe_print(f"   📊 Using consistent track selection (randomize_selection: false/not set)")
            
        # Group tracks by category
        categorized = {}
        for track in tracks:
            category = track['category']
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(track)
        
        # Sort or randomize within each category and build final list
        organized_tracks = []
        
        for category_name, category_info in self.config['track_categories'].items():
            if category_name in categorized:
                category_tracks = categorized[category_name]
                
                if randomize:
                    # Randomize tracks within this category
                    import random
                    import time
                    # Set a random seed based on current time to ensure different results each run
                    seed = int(time.time()) + hash(category_name)
                    random.seed(seed)
                    safe_print(f"   🔀 Randomizing tracks in category '{category_name}' with seed: {seed}")
                    random.shuffle(category_tracks)
                    
                    # Print first few tracks to verify randomization
                    if category_tracks:
                        safe_print(f"      🎵 First 3 tracks in '{category_name}' after randomization:")
                        for i, track in enumerate(category_tracks[:3]):
                            safe_print(f"         {i+1}. {track['name']} - {track['artists'][0]['name']}")
                else:
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
        
        safe_print(f"\n{emoji} {name}")
        safe_print("=" * 60)
        
        # Show by category if we have them
        if self.config['track_categories']:
            current_category = None
            for i, track in enumerate(tracks, 1):
                if track['category'] != current_category:
                    current_category = track['category']
                    safe_print(f"\n🌀 {current_category}:")
                    safe_print("-" * 30)
                
                safe_print(f"{i:2d}. {track['name']} - {track['artist']} ({track['duration_min']:.1f}m)")
        else:
            for i, track in enumerate(tracks, 1):
                safe_print(f"{i:2d}. {track['name']} - {track['artist']} ({track['duration_min']:.1f}m)")
        
        total_duration = sum(t['duration_min'] for t in tracks)
        target_duration = self.config['metadata'].get('duration_target', '').split()[0] if self.config['metadata'].get('duration_target') else 'N/A'
        
        safe_print(f"\n🎵 Playlist Features:")
        safe_print(f"   • Total Duration: {total_duration:.1f} minutes ({total_duration/60:.1f} hours)")
        safe_print(f"   • Target Duration: {target_duration} minutes")
        safe_print(f"   • {len(tracks)} carefully curated tracks")
        
        # Show special instructions
        if self.config['special_instructions']:
            safe_print(f"   • Special features:")
            for instruction in self.config['special_instructions'][:3]:  # Show first 3
                safe_print(f"     - {instruction}")
        
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
            safe_print(f"⚠️ Warning: Could not search existing playlists: {e}")
            return None
    
    def refresh_playlist(self, playlist_id: str, tracks: List[Dict[str, Any]]) -> str:
        """Replace all tracks in existing playlist with new tracks and update description."""
        # Update playlist description with enhanced version
        if self.config:
            base_description = self.config['metadata'].get('description', 'Created with Alex Method DJ')
            enhanced_description = self.generate_enhanced_description(base_description, tracks)
            
            try:
                # Update playlist details including description
                self.sp.playlist_change_details(
                    playlist_id=playlist_id,
                    description=enhanced_description
                )
                safe_print(f"📝 Updated playlist description with phase timestamps")
            except Exception as e:
                safe_print(f"⚠️ Warning: Could not update playlist description: {e}")
        
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

    def generate_enhanced_description(self, base_description: str, tracks: List[Dict[str, Any]]) -> str:
        """Generate enhanced description with phase timestamps for phased playlists."""
        if not self.has_track_categories():
            return base_description
        
        # Calculate timestamps for each phase
        current_time = 0.0
        phase_timestamps = []
        current_phase = None
        
        for track in tracks:
            phase_name = track.get('phase')
            if phase_name and phase_name != current_phase:
                # New phase starting
                minutes = int(current_time)
                seconds = int((current_time - minutes) * 60)
                timestamp = f"{minutes}:{seconds:02d}"
                phase_timestamps.append(f"{timestamp} {phase_name}")
                current_phase = phase_name
            
            current_time += track['duration_min']
        
        # Build enhanced description with character limit (Spotify max is 300 chars)
        enhanced_description = base_description
        if phase_timestamps:
            timeline_text = " | ".join(phase_timestamps)
            # Check if we can fit the timeline
            test_description = f"{base_description} | Phases: {timeline_text}"
            
            if len(test_description) <= 300:
                enhanced_description = test_description
            else:
                # Truncate base description to fit timeline
                available_chars = 300 - len(f" | Phases: {timeline_text}")
                if available_chars > 50:  # Ensure base description isn't too short
                    truncated_base = base_description[:available_chars-3] + "..."
                    enhanced_description = f"{truncated_base} | Phases: {timeline_text}"
                else:
                    # Timeline too long, use short format
                    short_timeline = " | ".join([f"{ts.split(' ')[0]} {ts.split(' ')[1][:3]}" for ts in phase_timestamps])
                    enhanced_description = f"{base_description} | {short_timeline}"
        
        # Ensure description is within Spotify's 300 character limit
        if len(enhanced_description) > 300:
            enhanced_description = enhanced_description[:297] + "..."
        
        return enhanced_description

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
        base_description = self.config['metadata'].get('description', 'Created with Alex Method DJ')
        # Generate enhanced description with timestamps for phased playlists
        description = self.generate_enhanced_description(base_description, tracks)
        is_private = self.config['metadata'].get('privacy', 'public').lower() == 'private'
        
        # Check if playlist already exists
        existing_playlist = self.find_existing_playlist(name)
        
        if existing_playlist:
            safe_print(f"🔄 Found existing playlist '{name}' - refreshing content...")
            playlist_id = self.refresh_playlist(existing_playlist['id'], tracks)
            # Get updated playlist object with fresh metadata
            try:
                playlist = self.sp.playlist(existing_playlist['id'])
                if not playlist:
                    playlist = existing_playlist  # Fallback to existing if refresh fails
            except:
                playlist = existing_playlist  # Fallback to existing if API call fails
            action = "refreshed"
        else:
            safe_print(f"🆕 Creating new playlist '{name}'...")
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
        
        safe_print(f"\n🎉 SUCCESS! {action.title()} '{name}'")
        safe_print(f"📱 {len(tracks)} tracks {action}")
        safe_print(f"⏱️ Total Duration: {total_duration:.1f} minutes ({total_duration/60:.1f} hours)")
        safe_print(f"🔗 Playlist URL: {playlist['external_urls']['spotify']}")
        
        # Upload cover art if available
        if hasattr(self, 'config_file_path') and self.config_file_path:
            cover_art_path = self.get_cover_art_path()
            if cover_art_path and os.path.exists(cover_art_path):
                safe_print(f"🎨 Uploading cover art...")
                self.upload_cover_art(playlist_id, cover_art_path)
            else:
                safe_print(f"⚠️ No cover art found - playlist will use default Spotify image")
        
        # Save playlist URL and track info to config file for cross-platform usage
        self._save_playlist_metadata(playlist, tracks, action)
        
        safe_print(f"\n{emoji} Ready to enjoy your curated playlist!")
        
        return playlist_id

    def create_phased_playlist(self):
        """Create a multi-phase playlist with specific durations for each phase."""
        if not self.has_track_categories():
            # Fallback to standard search if no phases detected
            return self.search_standard_tracks()
        
        safe_print(f"   🎭 Creating phased playlist with category-specific durations...")
        
        # Parse phases from Track Categories section
        phases = self.parse_track_categories()
        if not phases:
            return self.search_standard_tracks()
        
        all_tracks = []
        used_track_ids = set()
        used_track_names = set()  # Add name-based deduplication
        
        for phase_name, phase_info in phases.items():
            duration_minutes = phase_info['duration']
            queries = phase_info['queries']
            
            safe_print(f"   🎯 Phase: {phase_name} ({duration_minutes} minutes)")
            
            # Search for tracks specific to this phase
            phase_tracks = []
            per_query_limit = 30
            
            # Check if randomization is enabled - we'll need it later for ordering, not for search
            randomize = False
            if self.config and 'metadata' in self.config:
                randomize_str = self.config['metadata'].get('randomize_selection', 'false').lower()
                randomize = randomize_str in ('true', 'yes', '1')
                
            # For EACH phase, get the same search results regardless of randomization
            # Randomization will be applied later after collecting ALL tracks for this phase
            for query in queries:
                try:
                    # Use a small varied offset (0, 10, 20) to add some variety to searches
                    # but keep it consistent so searches are predictable
                    search_offset = hash(query + phase_name) % 20 * 5
                    
                    results = self.sp.search(q=query, type='track', limit=per_query_limit, offset=search_offset)
                    if results and results['tracks']['items']:
                        for track in results['tracks']['items']:
                            if self.is_track_suitable(track):
                                track_info = self.extract_track_info(track, query)
                                
                                # Enhanced deduplication check (ID + name+artist)
                                if not self.is_duplicate_track(track_info, phase_tracks, used_track_ids, used_track_names):
                                    track_info['phase'] = phase_name
                                    phase_tracks.append(track_info)
                                    # Mark as used to prevent collection in other phases
                                    self.add_track_to_dedup_sets(track_info, used_track_ids, used_track_names)
                                    
                                    if len(phase_tracks) >= duration_minutes * 4:  # 4x target for selection
                                        break
                except Exception as e:
                    safe_print(f"   ⚠️ Error searching for phase '{phase_name}' with query '{query}': {e}")
                    continue
            
            # Apply randomization or sorting based on config BEFORE duration targeting
            phase_tracks = self.apply_randomization(phase_tracks, f"phase_{phase_name}")
            
            # Display sample of tracks to verify processing (randomization or sorting)
            if phase_tracks:
                processing_type = "randomization" if self.should_randomize_tracks() else "duration sorting"
                safe_print(f"      🎵 First 3 tracks in '{phase_name}' after {processing_type}:")
                for i, track in enumerate(phase_tracks[:3]):
                    safe_print(f"         {i+1}. {track['name']} - {track['artist']}")
            
            # Apply duration targeting for this phase (on processed tracks)
            if phase_tracks:
                optimal_tracks = self.apply_duration_targeting(phase_tracks, duration_minutes)
                safe_print(f"   ✅ Phase {phase_name}: {len(optimal_tracks)} tracks ({sum(t['duration_min'] for t in optimal_tracks):.1f}min)")
                
                # Debug: Show what tracks are being added from this phase
                if optimal_tracks:
                    safe_print(f"      📋 Adding tracks from {phase_name}:")
                    for i, track in enumerate(optimal_tracks[:3]):  # Show first 3
                        safe_print(f"         {i+1}. {track['name']} - {track['artist']}")
                    if len(optimal_tracks) > 3:
                        safe_print(f"         ... and {len(optimal_tracks) - 3} more tracks")
                
                # Add to main playlist (tracks already marked as used above)
                all_tracks.extend(optimal_tracks)
                safe_print(f"      📊 Total tracks so far: {len(all_tracks)}")
            else:
                safe_print(f"   ⚠️ No tracks found for phase {phase_name}")
        
        safe_print(f"\n🎭 PHASED PLAYLIST SUMMARY:")
        safe_print(f"   📊 Total phases processed: {len(phases)}")
        safe_print(f"   📊 Total tracks collected: {len(all_tracks)}")
        safe_print(f"   ⏱️ Total duration: {sum(t['duration_min'] for t in all_tracks):.1f} minutes")
        
        if all_tracks:
            safe_print(f"   📋 Phase breakdown:")
            phase_counts = {}
            for track in all_tracks:
                phase = track.get('phase', 'Unknown')
                phase_counts[phase] = phase_counts.get(phase, 0) + 1
            for phase, count in phase_counts.items():
                safe_print(f"      • {phase}: {count} tracks")
        
        # Apply final deduplication across all collected tracks
        deduplicated_tracks = self.apply_final_deduplication(all_tracks)
        if len(deduplicated_tracks) != len(all_tracks):
            safe_print(f"   🔄 Final deduplication: {len(all_tracks)} → {len(deduplicated_tracks)} tracks")
        
        return deduplicated_tracks
    
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
            safe_print(f"   🔄 Relaxed include keywords to: {essential_keywords}")
        
        # Apply relaxed filters temporarily
        self.config['track_filters'] = relaxed_filters
        
        # Search with relaxed filters
        relaxed_tracks = []
        used_track_ids = set()
        used_track_names = set()  # Add name-based deduplication
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
                            
                        if self.is_track_suitable(track):
                            track_info = self.extract_track_info(track, query)
                            
                            # Enhanced deduplication check (ID + name+artist)
                            if not self.is_duplicate_track(track_info, relaxed_tracks, used_track_ids, used_track_names):
                                relaxed_tracks.append(track_info)
                                self.add_track_to_dedup_sets(track_info, used_track_ids, used_track_names)
            except Exception as e:
                safe_print(f"   ⚠️ Error in relaxed search for '{query}': {e}")
                continue
        
        # Restore original filters
        self.config['track_filters'] = original_track_filters
        
        return relaxed_tracks

    def search_standard_tracks(self):
        """Standard track search for non-phased playlists."""
        if not self.config:
            return []
        
        import time  # Import time for seed generation
            
        tracks = []
        used_track_ids = set()
        used_track_names = set()  # Add name-based deduplication
        
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
        safe_print(f"{emoji} Searching for tracks...")
        
        # Check if randomization is enabled for standard playlists
        if self.should_randomize_tracks():
            safe_print(f"   🔀 Randomizing tracks with time-based seed: {int(time.time())}")
            
        if target_minutes:
            safe_print(f"   🎯 Target duration: {target_minutes} minutes (±10% = {target_minutes*0.9:.1f}-{target_minutes*1.1:.1f} minutes)")
            safe_print(f"   🎯 Searching for {search_pool_size} tracks to find optimal {estimated_tracks_needed} for duration targeting")

        search_queries = self.config.get('search_queries', [])
        for query in search_queries:
            if len(tracks) >= search_pool_size:
                break
                
            try:
                search_limit = min(50, per_query_limit * 2)
                
                # For consistency, use a hash-based offset between searches
                # but don't randomize per run - that will happen later
                search_offset = hash(query) % 15 * 5  # 0, 5, 10, 15, ..., 70
                
                results = self.sp.search(q=query, type='track', limit=search_limit, offset=search_offset)
                if results and results['tracks']['items']:
                    for track in results['tracks']['items']:
                        if len(tracks) >= search_pool_size:
                            break
                            
                        if self.is_track_suitable(track):
                            track_info = self.extract_track_info(track, query)
                            
                            # Enhanced deduplication check (ID + name+artist)
                            if not self.is_duplicate_track(track_info, tracks, used_track_ids, used_track_names):
                                tracks.append(track_info)
                                self.add_track_to_dedup_sets(track_info, used_track_ids, used_track_names)
            except Exception as e:
                safe_print(f"   ⚠️ Error searching for '{query}': {e}")
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
    
    def upload_cover_art(self, playlist_id: str, cover_art_path: str) -> bool:
        """Upload cover art to a playlist with enhanced SSL handling and retry logic."""
        import time
        import base64
        import requests
        from urllib3.util.retry import Retry
        from requests.adapters import HTTPAdapter
        
        try:
            if not os.path.exists(cover_art_path):
                safe_print(f"⚠️ Cover art file not found: {cover_art_path}")
                return False
            
            # Handle base64 files vs image files differently
            if cover_art_path.endswith('_base64.txt'):
                # Read base64 data directly
                with open(cover_art_path, 'r') as f:
                    image_b64 = f.read().strip()
                safe_print(f"📝 Using base64 data from: {os.path.basename(cover_art_path)}")
                # For base64 files, we can't check file size easily, but they should be pre-optimized
            else:
                # Handle regular image files
                file_size = os.path.getsize(cover_art_path)
                if file_size > 256 * 1024:  # 256KB
                    safe_print(f"⚠️ Cover art file too large: {file_size/1024:.1f}KB (max: 256KB)")
                    return False
                
                # Read and encode image data
                with open(cover_art_path, "rb") as image_file:
                    image_data = image_file.read()
                image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Try method 1: Direct spotipy with enhanced retry
            for attempt in range(5):  # Increased attempts
                try:
                    safe_print(f"🔄 Uploading cover art (attempt {attempt + 1}/5)...")
                    self.sp.playlist_upload_cover_image(playlist_id, image_b64)
                    safe_print(f"✅ Cover art uploaded successfully")
                    return True
                    
                except Exception as e:
                    error_str = str(e).lower()
                    if any(term in error_str for term in ["ssl", "eof", "connection", "timeout", "read timed out"]):
                        if attempt < 4:  # Not the last attempt
                            wait_time = min(2 ** attempt, 10)  # Exponential backoff: 1, 2, 4, 8, 10 seconds
                            safe_print(f"⚠️ Network error, retrying in {wait_time}s... ({e})")
                            time.sleep(wait_time)
                            continue
                        else:
                            safe_print(f"⚠️ Spotipy method failed after 5 attempts, trying direct API...")
                            break
                    else:
                        safe_print(f"❌ Non-network error: {e}")
                        return False
            
            # Method 2: Direct API call with requests and custom session
            try:
                safe_print(f"� Trying direct API approach...")
                
                # Create a session with retry strategy
                session = requests.Session()
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["PUT"]
                )
                adapter = HTTPAdapter(max_retries=retry_strategy)
                session.mount("https://", adapter)
                session.mount("http://", adapter)
                
                # Get access token from spotipy
                try:
                    if hasattr(self.sp, 'auth_manager') and self.sp.auth_manager:
                        token_info = self.sp.auth_manager.get_access_token()
                        access_token = token_info['access_token']
                    else:
                        # Alternative: use spotipy's token method
                        access_token = self.sp._auth
                        if not access_token:
                            raise Exception("No access token in auth")
                except Exception as token_error:
                    safe_print(f"⚠️ Could not get access token: {token_error}")
                    raise Exception("Failed to get access token for direct API call")
                
                # Make direct API call
                url = f"https://api.spotify.com/v1/playlists/{playlist_id}/images"
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'image/jpeg'
                }
                
                response = session.put(url, data=image_b64, headers=headers, timeout=30)
                
                if response.status_code == 202:  # Accepted
                    safe_print(f"✅ Cover art uploaded successfully via direct API")
                    return True
                else:
                    safe_print(f"⚠️ API returned status {response.status_code}: {response.text}")
                    
            except Exception as e:
                safe_print(f"⚠️ Direct API method also failed: {e}")
            
            # Method 3: Fallback with user guidance
            safe_print(f"❌ All upload methods failed due to network connectivity issues")
            safe_print(f"💡 Manual upload instructions:")
            safe_print(f"   1. Open Spotify and go to your playlist")
            safe_print(f"   2. Click the playlist image area")
            safe_print(f"   3. Upload: {os.path.abspath(cover_art_path)}")
            return False
                        
        except Exception as e:
            safe_print(f"❌ Unexpected error uploading cover art: {e}")
            return False
    
    def get_cover_art_path(self) -> Optional[str]:
        """Get the path to the cover art file for the current playlist configuration."""
        if not hasattr(self, 'config_file_path') or not self.config_file_path:
            return None
            
        # Extract playlist name from config file path
        config_path = Path(self.config_file_path)
        playlist_name = config_path.stem  # Remove .md extension
        
        # Look for cover art in cover-art directory
        cover_art_dir = Path("cover-art")
        if not cover_art_dir.exists():
            return None
            
        # Prefer JPEG files (optimized for Spotify upload with automatic base64 conversion)
        jpg_path = cover_art_dir / f"{playlist_name}.jpg"
        if jpg_path.exists():
            return str(jpg_path)
            
        # Fall back to PNG files
        png_path = cover_art_dir / f"{playlist_name}.png"
        if png_path.exists():
            return str(png_path)
            
        # Legacy support: base64 files for backward compatibility
        base64_path = cover_art_dir / f"{playlist_name}_base64.txt"
        if base64_path.exists():
            return str(base64_path)
            
        # Final fallback to other image formats
        for ext in ['.jpeg']:
            cover_art_path = cover_art_dir / f"{playlist_name}{ext}"
            if cover_art_path.exists():
                return str(cover_art_path)
                
        return None
    
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
    
    def _save_playlist_metadata(self, playlist: Dict[str, Any], tracks: List[Dict[str, Any]], action: str):
        """Save playlist URL and track information to the config file for cross-platform usage."""
        try:
            if not hasattr(self, 'config_file_path') or not self.config_file_path:
                safe_print("⚠️ Config file path not available - skipping metadata save")
                return
            
            safe_print(f"💾 Saving playlist metadata to {self.config_file_path}")
            
            # Read current config file
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prepare metadata section
            playlist_url = playlist['external_urls']['spotify']
            total_duration = sum(t['duration_min'] for t in tracks)
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")  # Use actual date
            
            # Check if randomization is enabled
            randomized = False
            if self.config and 'metadata' in self.config:
                randomize_str = self.config['metadata'].get('randomize_selection', 'false').lower()
                randomized = randomize_str in ('true', 'yes', '1')
            
            randomization_note = " (Tracks randomized on each refresh)" if randomized else ""
            
            metadata_section = f"""
## Cross-Platform Metadata
- **Spotify URL**: {playlist_url}
- **Spotify ID**: {playlist['id']}
- **Last Updated**: {current_date}
- **Action**: {action}
- **Track Count**: {len(tracks)}
- **Duration**: {total_duration:.1f} minutes
- **Generated Tracks**: Ready for YouTube Music transfer{randomization_note}

### Track List (for YouTube Music Transfer)
"""
            
            # Add track list for YouTube Music transfer
            if randomized:
                metadata_section += "Note: Tracks are randomized on each refresh - track list below represents current selection only.\n"
                
            for i, track in enumerate(tracks, 1):
                metadata_section += f"{i:2d}. {track['name']} - {track['artist']} ({track['duration_min']:.1f}m)\n"
            
            # Check if Cross-Platform Metadata section already exists
            if "## Cross-Platform Metadata" in content:
                # Replace existing section
                import re
                pattern = r'\n## Cross-Platform Metadata.*?(?=\n## |\Z)'
                # Escape special regex characters in the replacement string
                escaped_metadata = metadata_section.replace('\\', '\\\\')
                content = re.sub(pattern, escaped_metadata, content, flags=re.DOTALL)
                safe_print("🔄 Updated existing Cross-Platform Metadata section")
            else:
                # Add new section at the end
                content += "\n" + metadata_section
                safe_print("✨ Added new Cross-Platform Metadata section")
            
            # Write back to file
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            safe_print(f"✅ Successfully saved playlist metadata")
            safe_print(f"🔄 YouTube Music can now use this track list without additional searches")
            safe_print(f"   📋 Saved {len(tracks)} tracks for cross-platform transfer")
            
        except Exception as e:
            safe_print(f"⚠️ Warning: Could not save playlist metadata: {e}")
            import traceback
            traceback.print_exc()

    def should_randomize_tracks(self):
        """Check if randomization is enabled in the playlist configuration."""
        if self.config and 'metadata' in self.config:
            randomize_str = self.config['metadata'].get('randomize_selection', 'false').lower()
            return randomize_str in ('true', 'yes', '1')
        return False
        
    def apply_randomization(self, tracks, context_name=""):
        """Apply randomization to the track list if enabled in config, otherwise sort by duration."""
        if not tracks:
            return tracks
            
        # Check if randomization is enabled
        if self.should_randomize_tracks():
            import random
            import time
            # Use time as base seed but add context name for different randomization in different contexts
            seed = int(time.time()) + hash(context_name or "default")
            random.seed(seed)
            safe_print(f"   🔀 Randomizing tracks{' for ' + context_name if context_name else ''} with seed: {seed}")
            random.shuffle(tracks)
            
            # Display sample of tracks to verify randomization
            if tracks:
                safe_print(f"      🎵 First 3 tracks after randomization:")
                for i, track in enumerate(tracks[:3]):
                    safe_print(f"         {i+1}. {track['name']} - {track['artist']}")
        else:
            # Sort by duration (longest first) for consistent quality-focused selection
            tracks = sorted(tracks, key=lambda x: x.get('duration_ms', 0), reverse=True)
            safe_print(f"   📊 Sorted tracks{' for ' + context_name if context_name else ''} by duration (longest first)")
            
            # Display sample to verify sorting
            if tracks:
                safe_print(f"      🎵 First 3 tracks after duration sorting:")
                for i, track in enumerate(tracks[:3]):
                    duration_str = f"{track.get('duration_min', 0):.1f}min"
                    safe_print(f"         {i+1}. {track['name']} - {track['artist']} ({duration_str})")
                    
        return tracks

def main():
    """Main function to create playlist from config file."""
    if len(sys.argv) != 2:
        safe_print("Usage: python universal_playlist_creator.py <config_file.md>")
        safe_print("\nAvailable configs:")
        config_dir = Path("playlist-configs")
        if config_dir.exists():
            for config_file in config_dir.glob("*.md"):
                safe_print(f"  - {config_file.name}")
        else:
            safe_print("  - No playlist-configs directory found")
        return
    
    config_file = sys.argv[1]
    
    # If just filename provided, look in playlist-configs directory
    if not os.path.exists(config_file) and not os.path.dirname(config_file):
        config_file = os.path.join("playlist-configs", config_file)
    
    try:
        safe_print("🎵 ALEX METHOD DJ - Spotify Platform")
        safe_print("=" * 50)
        
        creator = SpotifyPlaylistCreator()
        
        # Load configuration
        safe_print(f"📖 Loading configuration from {config_file}...")
        config = creator.load_config(config_file)
        
        safe_print(f"🎯 Target: {config['metadata'].get('name', 'Unnamed Playlist')}")
        safe_print(f"⏱️ Duration: {config['metadata'].get('duration_target', 'Not specified')}")
        safe_print("")
        
        # Search for tracks
        tracks = creator.search_tracks()
        
        if not tracks:
            safe_print("❌ Couldn't find suitable tracks. Check your configuration or internet connection.")
            return
        
        # Preview and confirm
        if creator.preview_playlist(tracks):
            playlist_id = creator.create_or_refresh_playlist(tracks)
            safe_print(f"\n🚀 Playlist ready! Find it in your Spotify library.")
        else:
            safe_print("👋 No playlist created. Configuration saved for future use!")
    
    except Exception as e:
        safe_print(f"❌ Error: {e}")
        if "credentials" in str(e).lower():
            safe_print("Make sure your .env file is configured correctly!")

if __name__ == "__main__":
    main()
