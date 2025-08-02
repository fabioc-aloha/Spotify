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
    """YouTube Music Playlist Creator with video content curation."""
    
    def __init__(self):
        """Initialize with YouTube Data API credentials."""
        if not YOUTUBE_AVAILABLE:
            raise ImportError("YouTube Data API dependencies not installed. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        
        super().__init__()
        load_dotenv()
        self.youtube = None
        self.credentials = None
        self.setup_platform_client()
        
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
                    "web": {
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
                print(f"2. Complete the authorization")
                print(f"3. Copy the authorization code from the redirect URL")
                
                auth_code = input("Enter the authorization code: ").strip()
                
                # Exchange code for token
                flow.fetch_token(code=auth_code)
                self.credentials = flow.credentials
            
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
        """Search for video content on YouTube."""
        if not self.youtube:
            return []
        
        try:
            # Enhanced search with music-specific parameters
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=min(limit, 50),  # YouTube API limit
                type='video',
                videoCategoryId='10',  # Music category
                order='relevance',
                regionCode='US',
                relevanceLanguage='en'
            ).execute()
            
            videos = []
            video_ids = []
            
            # Extract video IDs for duration lookup
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                video_ids.append(video_id)
                videos.append(item)
            
            # Get video details including duration
            if video_ids:
                videos_response = self.youtube.videos().list(
                    part='contentDetails,statistics',
                    id=','.join(video_ids)
                ).execute()
                
                # Merge duration data
                duration_map = {}
                for video in videos_response.get('items', []):
                    duration_map[video['id']] = video['contentDetails']['duration']
                
                # Add duration to search results
                for video in videos:
                    video_id = video['id']['videoId']
                    if video_id in duration_map:
                        video['duration'] = duration_map[video_id]
            
            return videos
            
        except Exception as e:
            print(f"YouTube search error for query '{query}': {e}")
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
