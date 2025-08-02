#!/usr/bin/env python3
"""
Spotify API Setup Test
Quick test to verify your Spotify Web API credentials are working
"""

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def test_spotify_setup():
    """Test Spotify API connection and authentication"""
    
    # Load environment variables
    load_dotenv()
    
    # Check if credentials are loaded
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8888/callback')
    
    print("🎵 Spotify Web API Setup Test")
    print("=" * 40)
    
    # Verify credentials are loaded
    if not client_id or client_id == 'your_spotify_client_id_here':
        print("❌ SPOTIFY_CLIENT_ID not configured")
        print("   Please add your Client ID to .env file")
        return False
        
    if not client_secret or client_secret == 'your_spotify_client_secret_here':
        print("❌ SPOTIFY_CLIENT_SECRET not configured")
        print("   Please add your Client Secret to .env file")
        return False
        
    if not redirect_uri:
        print("❌ SPOTIFY_REDIRECT_URI not configured")
        return False
    
    print(f"✅ Client ID: {client_id[:8]}...")
    print(f"✅ Client Secret: {'*' * 8}")
    print(f"✅ Redirect URI: {redirect_uri}")
    print()
    
    try:
        # Set up Spotify authentication
        scope = "playlist-modify-public playlist-modify-private playlist-read-private user-read-private"
        
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            cache_path=".spotify_cache"
        )
        
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # Test API call - get current user info
        print("🔐 Testing authentication...")
        user_info = sp.current_user()
        
        print("🎉 SUCCESS! Spotify Web API connection established")
        print(f"   Connected as: {user_info['display_name']}")
        print(f"   User ID: {user_info['id']}")
        print(f"   Followers: {user_info['followers']['total']}")
        print()
        
        # Test playlist access
        print("📋 Testing playlist access...")
        playlists = sp.current_user_playlists(limit=5)
        print(f"   Found {playlists['total']} playlists")
        
        if playlists['items']:
            print("   Recent playlists:")
            for playlist in playlists['items'][:3]:
                print(f"   - {playlist['name']} ({playlist['tracks']['total']} tracks)")
        
        print()
        print("🚀 Ready to create playlists with The Alex Method!")
        return True
        
    except spotipy.exceptions.SpotifyException as e:
        print(f"❌ Spotify API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Setup Error: {e}")
        return False

if __name__ == "__main__":
    success = test_spotify_setup()
    
    if not success:
        print("\n🛠️  Setup Help:")
        print("1. Make sure you've copied .env.template to .env")
        print("2. Add your actual Spotify credentials to .env")
        print("3. Verify redirect URI in Spotify app settings")
        print("4. Run: pip install -r requirements.txt")
