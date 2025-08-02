#!/usr/bin/env python3
"""
Spotify Playlist Creation Tutorial with NEWBORN Enhanced Learning
================================================================

This tutorial demonstrates how to create Spotify playlists using the Spotify Web API,
featuring approval workflows and smart playlist generation capabilities.

Requirements:
- Spotify Developer Account
- App credentials configured in .env file
- Python packages: spotipy, python-dotenv

Environment Setup:
1. Copy .env.template to .env
2. Fill in your Spotify API credentials
3. Run this tutorial to learn playlist creation

Learning Objectives:
- Authenticate with Spotify Web API
- Search for tracks and artists
- Create playlists with approval workflow
- Analyze audio features for smart playlists
- Implement user-controlled playlist generation

Version: 1.2.0 - Enhanced with secure credential management
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import json
from typing import List, Dict, Optional
import time

# Load environment variables from .env file
load_dotenv()

class SpotifyPlaylistCreator:
    """
    Enhanced Spotify playlist creator with approval workflows and secure credential management.
    
    Features:
    - Secure credential loading from .env file
    - Preview-approve-create workflow
    - Audio feature analysis for smart playlists
    - Error handling and user feedback
    """
    
    def __init__(self):
        """Initialize with credentials from environment variables."""
        self.setup_credentials()
        self.setup_spotify_client()
    
    def setup_credentials(self):
        """Load and validate Spotify API credentials from environment variables."""
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8888/callback')
        
        # Validate required credentials
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Missing Spotify credentials. Please check your .env file.\n"
                "Required: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET\n"
                "Optional: SPOTIFY_REDIRECT_URI (defaults to http://127.0.0.1:8888)"
            )
        
        print(f"✅ Credentials loaded successfully")
        print(f"   Client ID: {self.client_id[:8]}...")
        print(f"   Redirect URI: {self.redirect_uri}")
    
    def setup_spotify_client(self):
        """Initialize Spotify client with OAuth authentication."""
        try:
            self.scope = "playlist-modify-public playlist-modify-private user-library-read"
            
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope
            )
            
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            
            # Test the connection
            user = self.sp.current_user()
            print(f"✅ Successfully connected to Spotify as: {user['display_name']}")
            self.user_id = user['id']
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Spotify: {str(e)}")

    def search_tracks(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for tracks on Spotify.
        
        Args:
            query: Search query (artist, song, album, etc.)
            limit: Maximum number of results to return
            
        Returns:
            List of track dictionaries with metadata
        """
        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []
            
            for track in results['tracks']['items']:
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity'],
                    'preview_url': track['preview_url']
                }
                tracks.append(track_info)
            
            print(f"🔍 Found {len(tracks)} tracks for query: '{query}'")
            return tracks
            
        except Exception as e:
            print(f"❌ Error searching tracks: {str(e)}")
            return []

    def preview_playlist_content(self, tracks: List[Dict]) -> None:
        """
        Display playlist content for user review before creation.
        
        Args:
            tracks: List of track dictionaries to preview
        """
        print("\n" + "="*60)
        print("🎵 PLAYLIST PREVIEW")
        print("="*60)
        
        for i, track in enumerate(tracks, 1):
            duration_min = track['duration_ms'] // 60000
            duration_sec = (track['duration_ms'] % 60000) // 1000
            
            print(f"{i:2d}. {track['name']}")
            print(f"    Artist: {track['artist']}")
            print(f"    Album: {track['album']}")
            print(f"    Duration: {duration_min}:{duration_sec:02d}")
            print(f"    Popularity: {track['popularity']}/100")
            print()
        
        total_duration = sum(track['duration_ms'] for track in tracks)
        total_min = total_duration // 60000
        total_sec = (total_duration % 60000) // 1000
        
        print(f"📊 Total tracks: {len(tracks)}")
        print(f"⏱️  Total duration: {total_min}:{total_sec:02d}")
        print("="*60)

    def create_playlist_with_approval(self, name: str, tracks: List[Dict], 
                                    description: str = "", public: bool = True) -> Optional[str]:
        """
        Create playlist with user approval workflow.
        
        Args:
            name: Playlist name
            tracks: List of track dictionaries
            description: Playlist description
            public: Whether playlist should be public
            
        Returns:
            Playlist ID if created, None if cancelled
        """
        # Preview the content
        self.preview_playlist_content(tracks)
        
        # Get user approval
        print(f"\n🎯 Ready to create playlist: '{name}'")
        print(f"📝 Description: {description}")
        print(f"🌍 Visibility: {'Public' if public else 'Private'}")
        
        while True:
            choice = input("\n✨ Create this playlist? (y/n/preview): ").lower().strip()
            
            if choice == 'y':
                break
            elif choice == 'n':
                print("❌ Playlist creation cancelled.")
                return None
            elif choice == 'preview':
                self.preview_playlist_content(tracks)
            else:
                print("Please enter 'y' for yes, 'n' for no, or 'preview' to see the content again.")
        
        # Create the playlist
        try:
            playlist = self.sp.user_playlist_create(
                user=self.user_id,
                name=name,
                public=public,
                description=description
            )
            
            # Add tracks to playlist
            track_ids = [track['id'] for track in tracks]
            if track_ids:
                # Add tracks in batches of 100 (Spotify API limit)
                for i in range(0, len(track_ids), 100):
                    batch = track_ids[i:i+100]
                    self.sp.playlist_add_items(playlist['id'], batch)
            
            print(f"✅ Successfully created playlist: '{name}'")
            print(f"🔗 Playlist URL: {playlist['external_urls']['spotify']}")
            
            return playlist['id']
            
        except Exception as e:
            print(f"❌ Error creating playlist: {str(e)}")
            return None

    def get_audio_features(self, track_ids: List[str]) -> List[Dict]:
        """
        Get audio features for tracks to enable smart playlist creation.
        
        Args:
            track_ids: List of Spotify track IDs
            
        Returns:
            List of audio feature dictionaries
        """
        try:
            # Get audio features in batches of 100 (API limit)
            all_features = []
            for i in range(0, len(track_ids), 100):
                batch = track_ids[i:i+100]
                features = self.sp.audio_features(batch)
                all_features.extend([f for f in features if f is not None])
            
            return all_features
            
        except Exception as e:
            print(f"❌ Error getting audio features: {str(e)}")
            return []

    def generate_smart_playlist(self, seed_artists: List[str], target_features: Dict, 
                              playlist_name: str, limit: int = 20) -> Optional[str]:
        """
        Generate a smart playlist based on audio features and seed artists.
        
        Args:
            seed_artists: List of artist names to base recommendations on
            target_features: Dictionary of target audio features (e.g., {'energy': 0.8, 'danceability': 0.7})
            playlist_name: Name for the generated playlist
            limit: Number of tracks to include
            
        Returns:
            Playlist ID if created, None if failed
        """
        try:
            # Search for seed artist IDs
            artist_ids = []
            for artist_name in seed_artists[:5]:  # Max 5 seed artists
                results = self.sp.search(q=artist_name, type='artist', limit=1)
                if results['artists']['items']:
                    artist_ids.append(results['artists']['items'][0]['id'])
            
            if not artist_ids:
                print("❌ No valid artists found for recommendations")
                return None
            
            # Get recommendations
            recommendations = self.sp.recommendations(
                seed_artists=artist_ids,
                limit=limit,
                **{f'target_{k}': v for k, v in target_features.items()}
            )
            
            # Format tracks for playlist creation
            tracks = []
            for track in recommendations['tracks']:
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity'],
                    'preview_url': track['preview_url']
                }
                tracks.append(track_info)
            
            if not tracks:
                print("❌ No recommendations found with these criteria")
                return None
            
            # Create description with target features
            feature_desc = ", ".join([f"{k}: {v}" for k, v in target_features.items()])
            description = f"Smart playlist based on {', '.join(seed_artists)} with features: {feature_desc}"
            
            print(f"🧠 Generated {len(tracks)} smart recommendations")
            return self.create_playlist_with_approval(playlist_name, tracks, description)
            
        except Exception as e:
            print(f"❌ Error generating smart playlist: {str(e)}")
            return None


def tutorial_basic_playlist():
    """Tutorial: Create a basic playlist with manual track selection."""
    print("\n🎓 TUTORIAL: Basic Playlist Creation")
    print("="*50)
    
    try:
        # Initialize the creator
        creator = SpotifyPlaylistCreator()
        
        # Search for some tracks
        print("\n1. Searching for tracks...")
        tracks = []
        
        search_queries = [
            "The Beatles Hey Jude",
            "Queen Bohemian Rhapsody", 
            "Led Zeppelin Stairway to Heaven",
            "Pink Floyd Wish You Were Here",
            "The Rolling Stones Paint It Black"
        ]
        
        for query in search_queries:
            results = creator.search_tracks(query, limit=1)
            if results:
                tracks.extend(results)
        
        # Create playlist with approval
        playlist_id = creator.create_playlist_with_approval(
            name="Classic Rock Essentials",
            tracks=tracks,
            description="Handpicked classic rock masterpieces",
            public=True
        )
        
        if playlist_id:
            print(f"🎉 Tutorial completed! Playlist created with ID: {playlist_id}")
        
    except Exception as e:
        print(f"❌ Tutorial failed: {str(e)}")


def tutorial_smart_playlist():
    """Tutorial: Generate a smart playlist using audio features."""
    print("\n🎓 TUTORIAL: Smart Playlist Generation")
    print("="*50)
    
    try:
        # Initialize the creator
        creator = SpotifyPlaylistCreator()
        
        # Generate a high-energy workout playlist
        print("\n1. Generating high-energy workout playlist...")
        
        seed_artists = ["Daft Punk", "Justice", "Disclosure"]
        target_features = {
            'energy': 0.8,
            'danceability': 0.7,
            'valence': 0.6,
            'tempo': 120
        }
        
        playlist_id = creator.generate_smart_playlist(
            seed_artists=seed_artists,
            target_features=target_features,
            playlist_name="AI Generated Workout Mix",
            limit=25
        )
        
        if playlist_id:
            print(f"🎉 Smart playlist created with ID: {playlist_id}")
        
    except Exception as e:
        print(f"❌ Smart playlist tutorial failed: {str(e)}")


def main():
    """Main function to run the tutorials."""
    print("🎵 Spotify Playlist Creation Tutorial")
    print("====================================")
    
    # Check environment setup
    if not os.getenv('SPOTIFY_CLIENT_ID'):
        print("⚠️  Environment Setup Required!")
        print("1. Copy .env.template to .env")
        print("2. Fill in your Spotify API credentials")
        print("3. Run this tutorial again")
        return
    
    print("\nChoose a tutorial:")
    print("1. Basic playlist creation")
    print("2. Smart playlist generation")
    print("3. Both tutorials")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        tutorial_basic_playlist()
    elif choice == '2':
        tutorial_smart_playlist()
    elif choice == '3':
        tutorial_basic_playlist()
        tutorial_smart_playlist()
    else:
        print("Invalid choice. Please run again and select 1, 2, or 3.")


if __name__ == "__main__":
    main()
