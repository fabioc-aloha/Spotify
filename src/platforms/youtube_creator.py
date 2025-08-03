#!/usr/bin/env python3
"""
YouTube Music Playlist Creator - Universal Platform Support
Creates intelligent video playlists using YouTube Data API v3

Features:
- Video search with content type filtering (music videos, live performances, official content)
- Duration targeting with ±10% variance (The Alex Method)
- Smart content curation with quality filtering
- Support for both standard and phased playlists
- Comprehensive error handling and OAuth2 authentication

Part of the Universal Platform Playlist Creator system.
"""

import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
from ..core.base_playlist_creator import BasePlaylistCreator

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    import pickle
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False

class YouTubeMusicPlaylistCreator(BasePlaylistCreator):
    """YouTube Music implementation of playlist creator."""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "YouTube Music"
        self.credentials = None
        self.youtube = None
        
        # Quota optimization settings
        self.quota_used = 0
        self.max_quota_per_session = 8000  # Leave buffer for other operations
        self.search_cache = {}  # Cache search results
        self.batch_size = 8  # Optimized batch size for searches
        
        # Load API key from environment
        load_dotenv()
        api_key = os.getenv('YOUTUBE_API_KEY')
        
        if not api_key:
            print("❌ YouTube API key not found in environment variables")
            print("Please set YOUTUBE_API_KEY in your .env file")
            return
        
        try:
            # Initialize YouTube API client
            self.youtube = build('youtube', 'v3', developerKey=api_key)
            print("✅ YouTube Data API client authenticated successfully")
        except Exception as e:
            print(f"❌ Error initializing YouTube API: {e}")
            raise
        
    def setup_platform_client(self):
        """Set up YouTube Data API client with OAuth2 authentication."""
        # Get API credentials from environment
        api_key = os.getenv('YOUTUBE_API_KEY')
        client_id = os.getenv('YOUTUBE_CLIENT_ID')
        client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
        
        if not any([api_key, client_id]):
            raise ValueError("Missing YouTube API credentials. Need either YOUTUBE_API_KEY or YOUTUBE_CLIENT_ID/CLIENT_SECRET in .env file")
        
        # OAuth2 setup for playlist creation (requires client credentials)
        if client_id and client_secret:
            self._setup_oauth2_client(client_id, client_secret)
        elif api_key:
            # API key only (read-only access)
            self.youtube = build('youtube', 'v3', developerKey=api_key)
            print("⚠️ Using API key only - playlist creation will not be available")
        
    def _setup_oauth2_client(self, client_id: str, client_secret: str):
        """Set up OAuth2 authentication for full API access."""
        scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
        
        # Token storage file
        token_file = 'youtube_token.pickle'
        
        # Load existing credentials
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                self.credentials = pickle.load(token)
        
        # If there are no valid credentials, get new ones
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                # Create OAuth2 flow
                client_config = {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost:8080"]
                    }
                }
                
                flow = Flow.from_client_config(
                    client_config,
                    scopes=scopes,
                    redirect_uri="http://localhost:8080"
                )
                
                # Get authorization URL
                auth_url, _ = flow.authorization_url(prompt='consent')
                
                print(f"🔐 YouTube OAuth2 Setup Required")
                print(f"1. Open this URL in your browser: {auth_url}")
                print(f"2. Complete the authorization (click Advanced -> Go to Alex DJ)")
                print(f"3. After authorization, you'll see a blank page")
                print(f"4. Copy the FULL URL from your browser (starts with http://localhost:8080/?code=...)")
                
                redirect_url = input("Paste the full redirect URL here: ").strip()
                
                # Extract code from URL
                if 'code=' in redirect_url:
                    auth_code = redirect_url.split('code=')[1].split('&')[0]
                    # Exchange code for token
                    flow.fetch_token(code=auth_code)
                    self.credentials = flow.credentials
                else:
                    raise ValueError("Invalid redirect URL. Please make sure to copy the full URL.")
            
            # Save credentials for next run
            with open(token_file, 'wb') as token:
                pickle.dump(self.credentials, token)
        
        # Build YouTube service
        self.youtube = build('youtube', 'v3', credentials=self.credentials)
        print("✅ YouTube Data API client authenticated successfully")
    
    def get_platform_name(self) -> str:
        """Return the platform name for display purposes."""
        return "YouTube Music"
    
    def search_content(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Optimized search for music content with quota management and caching."""
        if not self.youtube:
            return []
        
        # Check quota limit
        if self.quota_used >= self.max_quota_per_session:
            print(f"⚠️ Quota limit reached ({self.quota_used}/{self.max_quota_per_session}). Skipping search: {query}")
            return []
        
        # Check cache first
        cache_key = f"{query}_{limit}"
        if cache_key in self.search_cache:
            print(f"📋 Using cached results for: {query}")
            return self.search_cache[cache_key]
        
        try:
            # Enhanced search with music-specific parameters
            music_query = f"{query} official music video OR audio OR song"
            
            print(f"🔍 Searching (Quota: {self.quota_used}/{self.max_quota_per_session}): {query}")
            
            search_response = self.youtube.search().list(
                q=music_query,
                part='id,snippet',
                maxResults=min(limit * 2, 50),  # Get more to filter better
                type='video',
                videoCategoryId='10',  # Music category
                order='relevance',
                regionCode='US',
                relevanceLanguage='en',
                videoDuration='medium'  # 4-20 minutes (typical music length)
            ).execute()
            
            # Track quota usage (search = ~100 units)
            self.quota_used += 100
            
            videos = []
            video_ids = []
            
            # Extract video IDs for duration lookup
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                video_ids.append(video_id)
                videos.append(item)
            
            # Get video details including duration (batch request)
            if video_ids:
                videos_response = self.youtube.videos().list(
                    part='contentDetails,statistics,snippet',
                    id=','.join(video_ids)
                ).execute()
                
                # Track quota usage (videos.list = ~1 unit per video, max 50)
                self.quota_used += min(len(video_ids), 50)
                
                # Get channel details for verification (optimized batch)
                channel_ids = list(set([v['snippet']['channelId'] for v in videos_response.get('items', [])]))
                channel_info = {}
                
                # Only get channel info if quota allows and we have reasonable number of channels
                if self.quota_used + len(channel_ids) < self.max_quota_per_session and len(channel_ids) <= 20:
                    channels_response = self.youtube.channels().list(
                        part='snippet,statistics',
                        id=','.join(channel_ids[:20])  # Limit to save quota
                    ).execute()
                    
                    # Track quota usage (channels.list = ~1 unit per channel)
                    self.quota_used += len(channel_ids)
                    channel_info = {ch['id']: ch for ch in channels_response.get('items', [])}
                
                # Merge duration and channel data, apply music filtering
                duration_map = {}
                filtered_videos = []
                
                for video in videos_response.get('items', []):
                    video_id = video['id']
                    duration_map[video_id] = video['contentDetails']['duration']
                    
                    # Enhanced music content filtering
                    if self._is_music_content(video, channel_info.get(video['snippet']['channelId']) if channel_info else None):
                        # Find corresponding search result
                        for search_video in videos:
                            if search_video['id']['videoId'] == video_id:
                                search_video['duration'] = duration_map[video_id]
                                search_video['video_details'] = video
                                filtered_videos.append(search_video)
                                break
                
                # Sort by music relevance and limit results
                filtered_videos = self._rank_music_content(filtered_videos)
                result = filtered_videos[:limit]
                
                # Cache the result
                self.search_cache[cache_key] = result
                print(f"✅ Found {len(result)} music items (cached for future use)")
                return result
            
            return videos
            
        except Exception as e:
            print(f"YouTube Music search error for query '{query}': {e}")
            return []
    
    def extract_content_info(self, item: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Extract standardized information from YouTube video."""
        video_id = item['id']['videoId']
        snippet = item['snippet']
        
        # Parse duration from ISO 8601 format (PT4M13S -> 4.22 minutes)
        duration_str = item.get('duration', 'PT0S')
        duration_minutes = self._parse_youtube_duration(duration_str)
        
        # Extract channel and title info
        title = snippet['title']
        channel = snippet['channelTitle']
        
        # Determine content type based on title and channel
        content_type = self._determine_content_type(title, channel)
        
        return {
            'id': video_id,
            'name': title,
            'artist': channel,
            'uri': f'https://www.youtube.com/watch?v={video_id}',
            'duration_ms': int(duration_minutes * 60 * 1000),
            'duration_minutes': duration_minutes,
            'content_type': content_type,
            'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
            'published': snippet.get('publishedAt', ''),
            'query': query,
            'category': self.categorize_content(query)
        }
    
    def _parse_youtube_duration(self, duration_str: str) -> float:
        """Parse YouTube duration from ISO 8601 format (PT4M13S) to minutes."""
        if not duration_str or duration_str == 'PT0S':
            return 0.0
        
        # Remove PT prefix
        duration_str = duration_str[2:]
        
        hours = 0
        minutes = 0
        seconds = 0
        
        # Parse hours
        if 'H' in duration_str:
            h_match = re.search(r'(\d+)H', duration_str)
            if h_match:
                hours = int(h_match.group(1))
        
        # Parse minutes
        if 'M' in duration_str:
            m_match = re.search(r'(\d+)M', duration_str)
            if m_match:
                minutes = int(m_match.group(1))
        
        # Parse seconds
        if 'S' in duration_str:
            s_match = re.search(r'(\d+)S', duration_str)
            if s_match:
                seconds = int(s_match.group(1))
        
        # Convert to total minutes
        total_minutes = hours * 60 + minutes + seconds / 60
        return round(total_minutes, 2)
    
    def _determine_content_type(self, title: str, channel: str) -> str:
        """Determine content type based on title and channel analysis."""
        title_lower = title.lower()
        channel_lower = channel.lower()
        
        # Official music videos
        if any(indicator in title_lower for indicator in ['official video', 'official music video', 'music video']):
            return 'music_video'
        
        # Live performances
        if any(indicator in title_lower for indicator in ['live', 'concert', 'performance', 'session']):
            return 'live_performance'
        
        # Lyrics videos
        if any(indicator in title_lower for indicator in ['lyrics', 'lyric video']):
            return 'lyrics_video'
        
        # Official channels (record labels, artist channels)
        official_indicators = ['records', 'music', 'official', 'vevo']
        if any(indicator in channel_lower for indicator in official_indicators):
            return 'official_content'
        
        # Default
        return 'user_content'
    
    def is_content_suitable(self, item: Dict[str, Any]) -> bool:
        """Determine if video content meets quality and filtering criteria."""
        if not self.config:
            return False
        
        # Extract content info first
        content_info = self.extract_content_info(item, '')
        
        title = content_info['name'].lower()
        channel = content_info['artist'].lower()
        duration_minutes = content_info['duration_minutes']
        content_type = content_info['content_type']
        
        # Check content preferences
        content_prefs = self.config.get('content_preferences', {})
        
        # Preferred content types
        preferred_types = content_prefs.get('preferred_content_types', [])
        if preferred_types and content_type not in preferred_types:
            return False
        
        # Check exclude keywords
        exclude_keywords = self.config['track_filters'].get('exclude', [])
        for keyword in exclude_keywords:
            if keyword.lower() in title or keyword.lower() in channel:
                return False
        
        # Check include keywords (if specified)
        include_keywords = self.config['track_filters'].get('include', [])
        if include_keywords:
            has_include = False
            for keyword in include_keywords:
                if keyword.lower() in title or keyword.lower() in channel:
                    has_include = True
                    break
            if not has_include:
                return False
        
        # Check duration constraints
        duration_filters = self.config['track_filters'].get('duration', {})
        
        if 'minimum' in duration_filters and duration_minutes < duration_filters['minimum']:
            return False
        if 'maximum' in duration_filters and duration_filters['maximum'] and duration_minutes > duration_filters['maximum']:
            return False
        
        # Filter out very short or very long videos
        if duration_minutes < 0.5 or duration_minutes > 15:  # 30 seconds to 15 minutes
            return False
        
        return True
    
    def categorize_content(self, query: str) -> str:
        """Categorize content based on query and configuration."""
        # Basic categorization - can be enhanced based on needs
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['8-bit', '16-bit', 'chiptune', 'retro', 'gaming']):
            return 'gaming_music'
        elif any(word in query_lower for word in ['ambient', 'chill', 'relaxing']):
            return 'ambient'
        elif any(word in query_lower for word in ['electronic', 'synthwave', 'techno']):
            return 'electronic'
        else:
            return 'general'
    
    def create_playlist(self, name: str, description: str, public: bool = True) -> str:
        """Create a new YouTube playlist and return its ID."""
        if not self.youtube or not self.credentials:
            raise ValueError("YouTube API not properly authenticated for playlist creation")
        
        try:
            playlist_body = {
                'snippet': {
                    'title': name,
                    'description': description
                },
                'status': {
                    'privacyStatus': 'public' if public else 'private'
                }
            }
            
            playlist_response = self.youtube.playlists().insert(
                part='snippet,status',
                body=playlist_body
            ).execute()
            
            return playlist_response['id']
            
        except Exception as e:
            raise ValueError(f"Failed to create YouTube playlist: {e}")
    
    def add_content_to_playlist(self, playlist_id: str, content_ids: List[str]) -> None:
        """Add videos to a YouTube playlist."""
        if not self.youtube or not self.credentials:
            raise ValueError("YouTube API not properly authenticated for playlist modification")
        
        for video_id in content_ids:
            try:
                playlist_item_body = {
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
                
                self.youtube.playlistItems().insert(
                    part='snippet',
                    body=playlist_item_body
                ).execute()
                
            except Exception as e:
                print(f"Failed to add video {video_id} to playlist: {e}")
                continue
    
    def find_existing_playlist(self, playlist_name: str) -> Optional[Dict[str, Any]]:
        """Find existing playlist by name in user's YouTube account."""
        if not self.youtube or not self.credentials:
            return None
        
        try:
            # Get user's playlists
            playlists_response = self.youtube.playlists().list(
                part='snippet',
                mine=True,
                maxResults=50
            ).execute()
            
            # Look for exact match (case-insensitive)
            for playlist in playlists_response.get('items', []):
                if playlist['snippet']['title'].lower() == playlist_name.lower():
                    return {
                        'id': playlist['id'],
                        'name': playlist['snippet']['title'],
                        'url': f"https://www.youtube.com/playlist?list={playlist['id']}"
                    }
            
            return None
            
        except Exception as e:
            print(f"Warning: Could not search existing YouTube playlists: {e}")
            return None
    
    def _is_music_content(self, video: Dict[str, Any], channel_info: Optional[Dict[str, Any]] = None) -> bool:
        """Enhanced music content detection with multiple criteria."""
        snippet = video['snippet']
        title = snippet['title'].lower()
        description = snippet.get('description', '').lower()
        channel_title = snippet['channelTitle'].lower()
        
        # Strong positive indicators for music content
        music_keywords = [
            'official music video', 'official video', 'official audio', 'music video',
            'official lyric video', 'lyrics', 'official song', 'single', 'album',
            'acoustic version', 'live performance', 'concert', 'studio version',
            'remix', 'cover', 'soundtrack', 'theme song', 'original song'
        ]
        
        # Negative indicators (exclude these)
        exclude_keywords = [
            'tutorial', 'lesson', 'how to', 'reaction', 'review', 'analysis',
            'compilation', 'mashup', 'nightcore', 'slowed + reverb', '8d audio',
            'gameplay', 'walkthrough', 'trailer', 'interview', 'behind the scenes',
            'making of', 'documentary', 'news', 'unboxing', 'vlog'
        ]
        
        # Check for positive music indicators
        music_score = 0
        for keyword in music_keywords:
            if keyword in title or keyword in description:
                music_score += 1
        
        # Check for negative indicators
        exclude_score = 0
        for keyword in exclude_keywords:
            if keyword in title or keyword in description:
                exclude_score += 1
        
        # Enhanced channel verification
        is_music_channel = False
        if channel_info:
            channel_stats = channel_info.get('statistics', {})
            subscriber_count = int(channel_stats.get('subscriberCount', 0))
            
            # Music channels typically have good subscriber counts
            if subscriber_count > 10000:
                is_music_channel = True
            
            # Check for verified music channels or labels
            music_labels = [
                'records', 'music', 'entertainment', 'label', 'official',
                'vevo', 'universal', 'sony', 'warner', 'atlantic', 'columbia'
            ]
            for label in music_labels:
                if label in channel_title:
                    is_music_channel = True
                    break
        
        # Duration check (music typically 1-10 minutes)
        duration_str = video.get('contentDetails', {}).get('duration', 'PT0S')
        duration_minutes = self._parse_youtube_duration(duration_str)
        valid_duration = 1.0 <= duration_minutes <= 10.0
        
        # Final scoring
        if exclude_score > 0:
            return False  # Exclude content with negative indicators
        
        if music_score >= 2 and is_music_channel and valid_duration:
            return True  # Strong music content
        
        if music_score >= 1 and valid_duration and 'official' in title:
            return True  # Official content with reasonable duration
        
        return False
    
    def _rank_music_content(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank videos by music content quality."""
        def music_quality_score(video):
            snippet = video['snippet']
            title = snippet['title'].lower()
            channel = snippet['channelTitle'].lower()
            
            score = 0
            
            # Prefer official content
            if 'official' in title:
                score += 10
            
            # Prefer established music channels
            if any(term in channel for term in ['records', 'music', 'vevo', 'official']):
                score += 8
            
            # Prefer music video content
            if 'music video' in title:
                score += 6
            elif 'audio' in title:
                score += 4
            
            # Prefer verified artists (check for common indicators)
            if any(term in title for term in ['feat.', 'ft.', 'featuring']):
                score += 3
            
            # Get view count if available
            if 'video_details' in video:
                stats = video['video_details'].get('statistics', {})
                view_count = int(stats.get('viewCount', 0))
                # Higher view count indicates quality
                if view_count > 1000000:  # 1M+ views
                    score += 5
                elif view_count > 100000:  # 100K+ views
                    score += 3
            
            return score
        
        return sorted(videos, key=music_quality_score, reverse=True)
    
    def search_tracks(self) -> List[Dict[str, Any]]:
        """
        Main search method called by Alex Method DJ.
        OPTIMIZED: Uses Spotify track list from config if available (quota efficient!)
        Falls back to standard search if no Spotify metadata found.
        """
        if not hasattr(self, 'config') or not self.config:
            print("❌ No configuration loaded")
            return []
        
        # Reset quota tracking for this session
        self.quota_used = 0
        print(f"🚀 YouTube Music playlist creation started (Fresh quota: {self.max_quota_per_session} units)")
        
        # Check if we have Spotify track list from config metadata (EFFICIENT!)
        spotify_tracks = self._extract_spotify_track_list()
        if spotify_tracks:
            print(f"🎯 QUOTA EFFICIENT MODE: Found {len(spotify_tracks)} tracks from Spotify playlist")
            print(f"   💾 Using cross-platform transfer - minimal YouTube searches needed!")
            return self.search_tracks_from_spotify_metadata()
        
        # Fallback to standard search if no Spotify metadata
        print("🔍 STANDARD MODE: No Spotify track list found - using search queries")
        print("   ⚠️ This will use more quota. Consider creating Spotify playlist first for efficiency.")
        
        all_content = []
        search_queries = self.config.get('search_queries', [])
        duration_target = self.config.get('metadata', {}).get('duration_target', '90 minutes')
        
        # Parse duration (simple parsing)
        target_duration = 90  # Default
        if 'minute' in duration_target.lower():
            try:
                target_duration = int(''.join(filter(str.isdigit, duration_target)))
            except:
                target_duration = 90
        
        print(f"🎯 Target duration: {target_duration} minutes")
        print(f"🔍 Original queries: {len(search_queries)} (optimizing to save quota)")
        
        # Smart query optimization: Group similar queries and use broader terms
        optimized_queries = self._optimize_search_queries(search_queries)
        print(f"⚡ Optimized to: {len(optimized_queries)} efficient searches")
        
        # Calculate content needed per query
        content_per_query = max(3, min(8, int(target_duration * 0.6 / len(optimized_queries))))
        
        for i, query in enumerate(optimized_queries):
            if self.quota_used >= self.max_quota_per_session:
                print(f"⚠️ Quota limit reached. Stopping search at {i+1}/{len(optimized_queries)} queries")
                break
                
            print(f"🔍 Query {i+1}/{len(optimized_queries)}: {query}")
            content = self.search_content(query, limit=content_per_query)
            
            if content:
                all_content.extend(content)
                print(f"   ✅ Found {len(content)} items")
            else:
                print(f"   ❌ No results")
        
        print(f"📊 Total quota used: {self.quota_used}/{self.max_quota_per_session}")
        return all_content
    
    def _optimize_search_queries(self, queries: List[str]) -> List[str]:
        """
        Optimize search queries by combining similar terms and reducing redundancy.
        """
        if len(queries) <= self.batch_size:
            return queries
        
        # Group queries by theme and combine similar ones
        optimized = []
        
        # Take every nth query to get a good distribution
        step = max(1, len(queries) // self.batch_size)
        for i in range(0, min(len(queries), self.batch_size * step), step):
            optimized.append(queries[i])
        
        # If we still have room and didn't get enough, add a few more
        if len(optimized) < self.batch_size:
            remaining = self.batch_size - len(optimized)
            for i, query in enumerate(queries):
                if query not in optimized and len(optimized) < self.batch_size:
                    optimized.append(query)
        
        return optimized[:self.batch_size]
    
    def search_tracks_from_spotify_metadata(self) -> List[Dict[str, Any]]:
        """Search for YouTube videos using Spotify track list from config metadata - QUOTA EFFICIENT!"""
        if not self.config:
            raise ValueError("No configuration loaded. Call load_config() first.")
        
        # Check if we have Spotify metadata with track list
        spotify_tracks = self._extract_spotify_track_list()
        if not spotify_tracks:
            print("❌ No Spotify track list found in config - falling back to standard search")
            return self.search_tracks()
        
        print(f"🔄 Using Spotify track list from config - QUOTA EFFICIENT MODE!")
        print(f"   📋 Found {len(spotify_tracks)} tracks from Spotify playlist")
        print(f"   🎯 Conservative YouTube search: only 1 search per track")
        
        # Check quota availability before starting
        estimated_quota = len(spotify_tracks) * 100  # ~100 quota units per search
        if self.quota_used + estimated_quota > self.max_quota_per_session:
            available_tracks = (self.max_quota_per_session - self.quota_used) // 100
            print(f"⚠️ Quota limit: Can only search {available_tracks} of {len(spotify_tracks)} tracks")
            spotify_tracks = spotify_tracks[:available_tracks]
        
        youtube_videos = []
        successful_matches = 0
        
        for i, track_info in enumerate(spotify_tracks, 1):
            if self.quota_used >= self.max_quota_per_session:
                print(f"⚠️ Quota limit reached - processed {successful_matches}/{len(spotify_tracks)} tracks")
                break
                
            # Create precise search query from Spotify track info
            artist = track_info['artist']
            title = track_info['title']
            search_query = f"{artist} {title} official music video"
            
            print(f"   {i:2d}/{len(spotify_tracks)}: {artist} - {title}")
            
            try:
                # Single precise search per track
                videos = self.search_content(search_query, limit=5)  # Only 5 results for efficiency
                
                # Find best match
                best_video = self._find_best_youtube_match(videos, artist, title)
                if best_video:
                    youtube_videos.append(best_video)
                    successful_matches += 1
                    print(f"      ✅ Found: {best_video['title']}")
                else:
                    print(f"      ❌ No good match found")
                    
            except Exception as e:
                print(f"      ⚠️ Search error: {e}")
                continue
        
        print(f"\n🎵 YouTube Music Transfer Complete:")
        print(f"   ✅ Successfully matched: {successful_matches}/{len(spotify_tracks)} tracks")
        print(f"   📊 Quota used: {self.quota_used}/{self.max_quota_per_session}")
        print(f"   💾 Quota efficiency: {successful_matches} tracks with minimal searches")
        
        return youtube_videos
    
    def _extract_spotify_track_list(self) -> List[Dict[str, Any]]:
        """Extract Spotify track list from config metadata section."""
        content = getattr(self, '_raw_config_content', '')
        if not content or "## Cross-Platform Metadata" not in content:
            return []
        
        tracks = []
        
        # Find the track list section
        import re
        track_list_match = re.search(r'### Track List \(for YouTube Music Transfer\)\s*\n(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL)
        
        if not track_list_match:
            return []
        
        track_lines = track_list_match.group(1).strip().split('\n')
        
        for line in track_lines:
            if re.match(r'^\s*\d+\.', line):  # Lines starting with numbers
                # Parse: "12. Song Name - Artist Name (4.2m)"
                match = re.match(r'^\s*\d+\.\s*(.+?)\s*-\s*(.+?)\s*\([\d.]+m\)', line)
                if match:
                    title = match.group(1).strip()
                    artist = match.group(2).strip()
                    tracks.append({
                        'title': title,
                        'artist': artist,
                        'original_line': line.strip()
                    })
        
        return tracks
    
    def _find_best_youtube_match(self, videos: List[Dict[str, Any]], target_artist: str, target_title: str) -> Optional[Dict[str, Any]]:
        """Find the best YouTube video match for a Spotify track."""
        if not videos:
            return None
        
        target_artist_lower = target_artist.lower()
        target_title_lower = target_title.lower()
        
        best_match = None
        best_score = 0
        
        for video in videos:
            if not self.is_content_suitable(video):
                continue
                
            video_title = video.get('title', '').lower()
            video_channel = video.get('channel', '').lower()
            
            # Calculate match score
            score = 0
            
            # Artist/channel match (high priority)
            if target_artist_lower in video_channel or target_artist_lower in video_title:
                score += 40
            
            # Title match (high priority)
            title_words = target_title_lower.split()
            for word in title_words:
                if len(word) > 2 and word in video_title:  # Skip short words
                    score += 15
            
            # Prefer official content
            if any(keyword in video_title for keyword in ['official', 'music video', 'audio']):
                score += 10
            
            # Prefer music channels
            if any(keyword in video_channel for keyword in ['music', 'records', 'entertainment']):
                score += 5
            
            if score > best_score:
                best_score = score
                best_match = video
        
        # Only return if we have a reasonable match
        return best_match if best_score >= 25 else None

# Main execution for testing
if __name__ == "__main__":
    print("🎵 YouTube Music Playlist Creator - Test Mode")
    
    try:
        creator = YouTubeMusicPlaylistCreator()
        print(f"✅ {creator.get_platform_name()} creator initialized successfully")
        
        # Test search
        test_query = "8-bit gaming music"
        print(f"🔍 Testing search: '{test_query}'")
        results = creator.search_content(test_query, limit=5)
        
        if results:
            print(f"✅ Found {len(results)} videos")
            for i, video in enumerate(results[:3], 1):
                info = creator.extract_content_info(video, test_query)
                print(f"   {i}. {info['name']} ({info['duration_minutes']:.1f}min) - {info['artist']}")
        else:
            print("❌ No results found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure to set up YouTube API credentials in .env file")
