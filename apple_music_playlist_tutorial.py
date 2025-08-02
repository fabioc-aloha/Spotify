#!/usr/bin/env python3
"""
Apple Music Playlist Creation Tutorial - Simplified Alex Method
Learn to create playlists programmatically using Apple Music API (MusicKit)
"""

import requests
import json
import time
import jwt
from datetime import datetime, timedelta
import os

class AppleMusicPlaylistCreator:
    def __init__(self, team_id, key_id, private_key_path):
        """
        Initialize Apple Music API connection
        
        To get credentials:
        1. Join Apple Developer Program ($99/year)
        2. Go to https://developer.apple.com/account/resources/authkeys/list
        3. Create a new key with MusicKit enabled
        4. Download the .p8 private key file
        5. Get your Team ID from Apple Developer account
        6. Get Key ID from the created key
        """
        self.team_id = team_id
        self.key_id = key_id
        self.private_key_path = private_key_path
        self.base_url = "https://api.music.apple.com/v1"
        
        # Generate JWT token for authentication
        self.token = self._generate_jwt_token()
        
        # Test connection
        self._test_connection()

    def _generate_jwt_token(self):
        """Generate JWT token for Apple Music API authentication"""
        try:
            with open(self.private_key_path, 'r') as key_file:
                private_key = key_file.read()
        except FileNotFoundError:
            raise Exception(f"Private key file not found: {self.private_key_path}")
        
        # JWT payload
        payload = {
            'iss': self.team_id,
            'iat': int(time.time()),
            'exp': int(time.time()) + 15777000,  # 6 months
            'aud': 'appstoreconnect-v1'
        }
        
        # Generate token
        token = jwt.encode(
            payload,
            private_key,
            algorithm='ES256',
            headers={'kid': self.key_id}
        )
        
        return token

    def _test_connection(self):
        """Test Apple Music API connection"""
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Music-User-Token': 'user_token_here'  # Will be set later
        }
        
        try:
            response = requests.get(f"{self.base_url}/me/library/playlists", headers=headers)
            if response.status_code == 401:
                print("⚠️  JWT token generated successfully, but user authentication needed")
                print("   Note: Apple Music requires user login for playlist creation")
            else:
                print("✅ Connected to Apple Music API")
        except Exception as e:
            print(f"❌ Connection test failed: {e}")

    def set_user_token(self, user_token):
        """Set user music token for authenticated requests"""
        self.user_token = user_token
        print("✅ User token set for Apple Music API")

    def search_tracks(self, query, limit=1):
        """Search for tracks in Apple Music catalog"""
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        
        params = {
            'term': query,
            'types': 'songs',
            'limit': limit
        }
        
        response = requests.get(f"{self.base_url}/catalog/us/search", headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('results', {}).get('songs', {}).get('data', [])
        else:
            print(f"❌ Search failed: {response.status_code} - {response.text}")
            return []

    def preview_playlist_content(self, track_list):
        """Preview playlist contents before creation - get user approval"""
        print("\n🎵 APPLE MUSIC PLAYLIST PREVIEW")
        print("=" * 55)
        
        found_tracks = []
        not_found = []
        
        for i, query in enumerate(track_list, 1):
            # Search for track
            tracks = self.search_tracks(query)
            
            if tracks:
                track = tracks[0]
                found_tracks.append({
                    'query': query,
                    'track': track,
                    'id': track['id']
                })
                
                # Get track details
                artist_name = track['attributes']['artistName']
                song_name = track['attributes']['name']
                album_name = track['attributes']['albumName']
                duration_ms = track['attributes']['durationInMillis']
                duration_min = duration_ms // 60000
                duration_sec = (duration_ms % 60000) // 1000
                
                print(f"{i:2d}. ✅ {artist_name} - {song_name}")
                print(f"     Album: {album_name} ({duration_min}:{duration_sec:02d})")
                
                # Show preview URL if available
                if 'previews' in track['attributes']:
                    preview_url = track['attributes']['previews'][0]['url']
                    print(f"     Preview: {preview_url}")
            else:
                not_found.append(query)
                print(f"{i:2d}. ❌ NOT FOUND: {query}")
        
        print(f"\n📊 Summary: {len(found_tracks)} found, {len(not_found)} not found")
        
        if not_found:
            print("\n⚠️  Tracks not found:")
            for track in not_found:
                print(f"   • {track}")
        
        return found_tracks, not_found

    def create_playlist_with_approval(self, theme_name, track_list):
        """Create playlist with user approval workflow"""
        
        # Step 1: Preview content
        found_tracks, not_found = self.preview_playlist_content(track_list)
        
        if not found_tracks:
            print("❌ No tracks found. Cannot create playlist.")
            return None
        
        # Step 2: Get user approval
        print(f"\n🤔 Create '{theme_name}' Apple Music playlist with {len(found_tracks)} tracks?")
        approval = input("   Type 'yes' to create playlist, or 'no' to cancel: ").lower().strip()
        
        if approval not in ['yes', 'y']:
            print("❌ Playlist creation cancelled.")
            return None
        
        # Step 3: Create playlist with approved content
        print(f"\n🚀 Creating '{theme_name}' Apple Music playlist...")
        
        if not hasattr(self, 'user_token'):
            print("❌ User authentication required. Please set user token first.")
            print("   Apple Music requires user login for playlist creation.")
            return None
        
        # Create playlist
        playlist_data = {
            "attributes": {
                "name": f"{theme_name} Mix - {datetime.now().strftime('%b %Y')}",
                "description": f"A {theme_name.lower()} playlist created with the Alex Method"
            },
            "relationships": {
                "tracks": {
                    "data": [
                        {
                            "id": track['id'],
                            "type": "songs"
                        } for track in found_tracks
                    ]
                }
            }
        }
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Music-User-Token': self.user_token,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{self.base_url}/me/library/playlists",
            headers=headers,
            json={'data': [playlist_data]}
        )
        
        if response.status_code == 201:
            playlist = response.json()['data'][0]
            print(f"✅ Successfully created playlist with {len(found_tracks)} tracks")
            return playlist
        else:
            print(f"❌ Failed to create playlist: {response.status_code} - {response.text}")
            return None

    def generate_smart_playlist(self, theme, preferences=None):
        """
        Generate smart playlist suggestions based on theme and user preferences
        User approves before API creation
        """
        print(f"\n🧠 Generating smart '{theme}' Apple Music playlist suggestions...")
        
        # Predefined track suggestions by theme
        theme_suggestions = {
            'workout': [
                "Eminem - Till I Collapse",
                "The Prodigy - Spitfire", 
                "Skrillex - Bangarang",
                "Pendulum - Propane Nightmares",
                "Rage Against The Machine - Killing In The Name",
                "Linkin Park - One Step Closer",
                "Foo Fighters - The Pretender",
                "System of a Down - Chop Suey",
                "Daft Punk - Harder Better Faster Stronger",
                "Kanye West - Stronger"
            ],
            'chill': [
                "Bonobo - Kiara",
                "Thievery Corporation - Lebanese Blonde",
                "Zero 7 - In The Waiting Line", 
                "Massive Attack - Teardrop",
                "Portishead - Glory Box",
                "Air - La Femme d'Argent",
                "Boards of Canada - Roygbiv",
                "Nujabes - Aruarian Dance",
                "Emancipator - Soon It Will Be Cold Enough",
                "Tycho - A Walk"
            ],
            'focus': [
                "Max Richter - On The Nature of Daylight",
                "Ólafur Arnalds - Near Light",
                "Nils Frahm - Says", 
                "GoGo Penguin - Hopopono",
                "Kiasmos - Blurred EP",
                "Jon Hopkins - Immunity",
                "Aphex Twin - Avril 14th",
                "Rival Consoles - Recovery",
                "Ben Lukas Boysen - Golden Times 1",
                "Clark - Winter Linn"
            ],
            'party': [
                "Dua Lipa - Don't Start Now",
                "The Weeknd - Blinding Lights",
                "Bruno Mars - Uptown Funk",
                "Daft Punk - Get Lucky",
                "Mark Ronson - Uptown Funk",
                "Calvin Harris - Feel So Close",
                "David Guetta - Titanium",
                "Swedish House Mafia - Don't You Worry Child",
                "Avicii - Wake Me Up",
                "Pitbull - Give Me Everything"
            ]
        }
        
        suggested_tracks = theme_suggestions.get(theme.lower(), [])
        
        if not suggested_tracks:
            print(f"❌ No suggestions available for theme '{theme}'")
            print("Available themes:", list(theme_suggestions.keys()))
            return None
        
        # Create playlist with approval workflow
        return self.create_playlist_with_approval(theme.title(), suggested_tracks)

    def get_user_playlists(self):
        """Get user's existing Apple Music playlists"""
        if not hasattr(self, 'user_token'):
            print("❌ User authentication required. Please set user token first.")
            return []
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Music-User-Token': self.user_token
        }
        
        response = requests.get(f"{self.base_url}/me/library/playlists", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            playlists = data.get('data', [])
            
            print(f"\n📚 Your Apple Music Playlists ({len(playlists)} total):")
            for i, playlist in enumerate(playlists[:10], 1):  # Show first 10
                name = playlist['attributes']['name']
                track_count = playlist['attributes'].get('trackCount', 'Unknown')
                print(f"{i:2d}. {name} ({track_count} tracks)")
            
            return playlists
        else:
            print(f"❌ Failed to get playlists: {response.status_code}")
            return []

    def analyze_track_features(self, track_ids):
        """
        Analyze audio features of tracks (simplified version)
        Note: Apple Music API has limited audio analysis compared to Spotify
        """
        print(f"\n📊 Analyzing {len(track_ids)} tracks...")
        print("Note: Apple Music API provides limited audio analysis features")
        
        # Apple Music doesn't provide detailed audio features like Spotify
        # This is a placeholder for basic track information analysis
        features = {
            'track_count': len(track_ids),
            'analysis_note': "Apple Music API provides limited audio feature analysis",
            'recommendation': "Use iTunes/Music app for detailed audio analysis"
        }
        
        print(f"   Tracks analyzed: {features['track_count']}")
        print(f"   Note: {features['analysis_note']}")
        
        return features

def interactive_apple_music_creator():
    """Interactive Apple Music playlist creation with user approval workflow"""
    
    # NOTE: Replace these with your actual Apple Music credentials
    TEAM_ID = "your_team_id_here"
    KEY_ID = "your_key_id_here"
    PRIVATE_KEY_PATH = "path/to/your/private_key.p8"
    
    print("🍎 Interactive Apple Music Playlist Creator")
    print("=" * 55)
    print("This tool will preview playlists before creating them via Apple Music API")
    print("You'll approve the content before any playlist is created.")
    print("\n⚠️  Note: Apple Music requires user authentication for playlist creation")
    
    # Uncomment when you have credentials:
    # try:
    #     creator = AppleMusicPlaylistCreator(TEAM_ID, KEY_ID, PRIVATE_KEY_PATH)
    #     
    #     # Note: You'll need to implement user authentication flow
    #     # user_token = get_user_music_token()  # Implement this function
    #     # creator.set_user_token(user_token)
    #     
    #     print("\n🎯 Available playlist themes:")
    #     print("1. workout - High-energy tracks for exercise")  
    #     print("2. chill - Relaxed tracks for unwinding")
    #     print("3. focus - Instrumental tracks for concentration")
    #     print("4. party - Upbeat tracks for celebrations")
    #     
    #     theme = input("\nEnter theme (workout/chill/focus/party): ").strip().lower()
    #     
    #     if theme in ['workout', 'chill', 'focus', 'party']:
    #         playlist = creator.generate_smart_playlist(theme)
    #         
    #         if playlist:
    #             print(f"\n🎉 Apple Music playlist created successfully!")
    #             print(f"   ID: {playlist['id']}")
    #             
    #             # Show existing playlists
    #             creator.get_user_playlists()
    #         else:
    #             print("❌ Playlist creation was cancelled or failed.")
    #     else:
    #         print("❌ Invalid theme selected.")
    #         
    # except Exception as e:
    #     print(f"❌ Error: {e}")
    
    print("\n📚 To use this Apple Music creator:")
    print("1. Join Apple Developer Program ($99/year)")
    print("2. Get MusicKit credentials from https://developer.apple.com/account/resources/authkeys/list")
    print("3. Download your .p8 private key file")
    print("4. Replace TEAM_ID, KEY_ID, and PRIVATE_KEY_PATH with your values")
    print("5. Implement user authentication flow (MusicKit JS or native)")
    print("6. Uncomment the demo code above")
    print("7. Run: python apple_music_playlist_tutorial.py")

def demo_apple_music_creation():
    """Demo showing Apple Music playlist creation methods"""
    
    # NOTE: Replace these with your actual Apple Music credentials
    TEAM_ID = "your_team_id_here"
    KEY_ID = "your_key_id_here"
    PRIVATE_KEY_PATH = "path/to/your/private_key.p8"
    
    print("🍎 Apple Music Playlist Creation Tutorial")
    print("=" * 55)
    print("Note: Apple Music API requires Apple Developer Program membership ($99/year)")
    
    # Uncomment the following lines when you have credentials:
    
    # try:
    #     creator = AppleMusicPlaylistCreator(TEAM_ID, KEY_ID, PRIVATE_KEY_PATH)
    #     
    #     # Note: User authentication required for playlist creation
    #     # user_token = get_user_music_token()  # You need to implement this
    #     # creator.set_user_token(user_token)
    #     
    #     # Example 1: Create a workout playlist with approval
    #     workout_tracks = [
    #         "Eminem - Till I Collapse",
    #         "The Prodigy - Spitfire",
    #         "Skrillex - Bangarang",
    #         "Pendulum - Propane Nightmares",
    #         "Rage Against The Machine - Killing In The Name"
    #     ]
    #     
    #     workout_playlist = creator.create_playlist_with_approval("High Energy Workout", workout_tracks)
    #     
    #     # Example 2: Create a smart playlist with approval
    #     chill_playlist = creator.generate_smart_playlist("chill")
    #     
    #     # Example 3: Show user's existing playlists
    #     creator.get_user_playlists()
    #     
    # except Exception as e:
    #     print(f"❌ Error: {e}")
    
    print("\n📚 To use this script:")
    print("1. Join Apple Developer Program at https://developer.apple.com")
    print("2. Create MusicKit credentials and download .p8 private key")
    print("3. Replace TEAM_ID, KEY_ID, and PRIVATE_KEY_PATH with your values")
    print("4. Implement user authentication (see Apple's MusicKit documentation)")
    print("5. Uncomment the demo code above")
    print("6. Run: python apple_music_playlist_tutorial.py")
    print("\n🔄 For interactive mode, call interactive_apple_music_creator() instead")
    print("\n💡 Comparison with Spotify:")
    print("   • Apple Music: Requires $99/year Developer Program + user auth")
    print("   • Spotify: Free developer account + simpler OAuth")
    print("   • Apple Music: Limited audio analysis features")
    print("   • Spotify: Comprehensive audio features (energy, tempo, etc.)")

if __name__ == "__main__":
    # Choose your mode:
    demo_apple_music_creation()        # Basic demo
    # interactive_apple_music_creator()  # Interactive mode
