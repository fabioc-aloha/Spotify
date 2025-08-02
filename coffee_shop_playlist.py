#!/usr/bin/env python3
"""
Coffee Shop Playlist Creator
Perfect ambient music for your coffee shop visit!
"""

import os
import sys
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class CoffeeShopPlaylistMaker:
    def __init__(self):
        """Initialize with your Spotify credentials."""
        load_dotenv()
        self.setup_spotify()
    
    def setup_spotify(self):
        """Set up Spotify client with authentication."""
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8888/callback')
        
        scope = "playlist-modify-public playlist-modify-private user-library-read"
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope
        )
        
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        print("☕ Connected to Spotify for coffee shop vibes!")
    
    def search_coffee_tracks(self):
        """Find perfect coffee shop tracks using search."""
        coffee_queries = [
            "acoustic coffee shop",
            "chill indie folk",
            "lo-fi coffee",
            "mellow acoustic",
            "indie folk acoustic",
            "coffee house jazz",
            "chill acoustic guitar",
            "singer songwriter",
            "indie acoustic chill",
            "coffee shop ambient"
        ]
        
        tracks = []
        print("🔍 Searching for perfect coffee shop vibes...")
        
        for query in coffee_queries:
            try:
                results = self.sp.search(q=query, type='track', limit=5)
                if results['tracks']['items']:
                    for track in results['tracks']['items']:
                        if track['id'] not in [t['id'] for t in tracks]:  # Avoid duplicates
                            tracks.append({
                                'id': track['id'],
                                'name': track['name'],
                                'artist': track['artists'][0]['name'],
                                'uri': track['uri'],
                                'popularity': track['popularity']
                            })
            except Exception as e:
                print(f"   ⚠️ Search issue with '{query}': {e}")
                continue
        
        # Sort by popularity and take top 25
        tracks = sorted(tracks, key=lambda x: x['popularity'], reverse=True)[:25]
        print(f"✅ Found {len(tracks)} perfect coffee shop tracks!")
        return tracks
    
    def preview_tracks(self, tracks):
        """Show the user what tracks will be in their playlist."""
        print("\n☕ Your Coffee Shop Playlist Preview:")
        print("=" * 50)
        
        for i, track in enumerate(tracks, 1):
            print(f"{i:2d}. {track['name']} - {track['artist']}")
        
        print("\n🎵 This playlist features:")
        print("   • Acoustic and indie folk vibes")
        print("   • Mellow, non-intrusive background music")
        print("   • Perfect tempo for coffee sipping")
        print("   • Chill, focused atmosphere")
        
        response = input("\n👍 Create this playlist? (y/n): ").lower().strip()
        return response == 'y' or response == 'yes'
    
    def create_playlist(self, tracks):
        """Create the coffee shop playlist."""
        user_id = self.sp.current_user()['id']
        
        # Create playlist
        playlist_name = "☕ Coffee Shop Vibes - Alex Method"
        description = "Perfect ambient music for coffee shop productivity and relaxation. Created with The Alex Method."
        
        playlist = self.sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=True,
            description=description
        )
        
        # Add tracks in batches
        track_uris = [track['uri'] for track in tracks]
        batch_size = 50
        
        for i in range(0, len(track_uris), batch_size):
            batch = track_uris[i:i + batch_size]
            self.sp.playlist_add_items(playlist['id'], batch)
        
        print(f"\n🎉 SUCCESS! Created '{playlist_name}'")
        print(f"📱 {len(tracks)} tracks added")
        print(f"🔗 Playlist URL: {playlist['external_urls']['spotify']}")
        print(f"\n☕ Perfect for your coffee shop visit! Enjoy!")
        
        return playlist['id']

def main():
    """Create the perfect coffee shop playlist."""
    print("☕🎵 COFFEE SHOP PLAYLIST CREATOR")
    print("=" * 40)
    print("Creating the perfect ambient soundtrack for your coffee shop visit!")
    print()
    
    try:
        maker = CoffeeShopPlaylistMaker()
        
        # Find tracks
        tracks = maker.search_coffee_tracks()
        
        if not tracks:
            print("❌ Couldn't find enough tracks. Check your internet connection.")
            return
        
        # Preview and confirm
        if maker.preview_tracks(tracks):
            playlist_id = maker.create_playlist(tracks)
            print(f"\n🚀 Ready to go! Open Spotify and search for 'Coffee Shop Vibes - Alex Method'")
        else:
            print("👋 No playlist created. Maybe next time!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your .env file is configured correctly!")

if __name__ == "__main__":
    main()
