#!/usr/bin/env python3
"""
Spotify Playlist Creation Tutorial - Simplified Alex Method
Learn to create playlists programmatically using Spotify Web API
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
from datetime import datetime

class SpotifyPlaylistCreator:
    def __init__(self, client_id, client_secret, redirect_uri):
        """
        Initialize Spotify API connection
        
        To get credentials:
        1. Go to https://developer.spotify.com/dashboard
        2. Create a new app
        3. Get Client ID and Client Secret
        4. Set redirect URI (e.g., http://localhost:8080/callback)
        """
        scope = "playlist-modify-public playlist-modify-private user-library-read"
        
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope
        ))
        
        # Get current user info
        self.user = self.sp.current_user()
        print(f"✅ Connected to Spotify as: {self.user['display_name']}")

    def create_basic_playlist(self, name, description="", public=True):
        """Create a new empty playlist"""
        playlist = self.sp.user_playlist_create(
            user=self.user['id'],
            name=name,
            public=public,
            description=description
        )
        
        print(f"🎵 Created playlist: '{name}'")
        print(f"   URL: {playlist['external_urls']['spotify']}")
        return playlist

    def search_and_add_tracks(self, playlist_id, search_queries):
        """
        Search for tracks and add them to playlist
        
        search_queries: List of strings like ["artist - song", "another song"]
        """
        track_ids = []
        
        for query in search_queries:
            # Search for track
            results = self.sp.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                track_ids.append(track['id'])
                print(f"✅ Found: {track['artists'][0]['name']} - {track['name']}")
            else:
                print(f"❌ Not found: {query}")
        
        # Add tracks to playlist in batches (Spotify limit: 100 tracks per request)
        if track_ids:
            for i in range(0, len(track_ids), 100):
                batch = track_ids[i:i+100]
                self.sp.playlist_add_items(playlist_id, batch)
            
            print(f"🎵 Added {len(track_ids)} tracks to playlist")
        
        return track_ids

    def preview_playlist_content(self, track_list):
        """Preview playlist contents before creation - get user approval"""
        print("\n🎵 PLAYLIST PREVIEW")
        print("=" * 50)
        
        found_tracks = []
        not_found = []
        
        for i, query in enumerate(track_list, 1):
            # Search for track
            results = self.sp.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                found_tracks.append({
                    'query': query,
                    'track': track,
                    'id': track['id']
                })
                duration_ms = track['duration_ms']
                duration_min = duration_ms // 60000
                duration_sec = (duration_ms % 60000) // 1000
                
                print(f"{i:2d}. ✅ {track['artists'][0]['name']} - {track['name']}")
                print(f"     Album: {track['album']['name']} ({duration_min}:{duration_sec:02d})")
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
        print(f"\n🤔 Create '{theme_name}' playlist with {len(found_tracks)} tracks?")
        approval = input("   Type 'yes' to create playlist, or 'no' to cancel: ").lower().strip()
        
        if approval not in ['yes', 'y']:
            print("❌ Playlist creation cancelled.")
            return None
        
        # Step 3: Create playlist with approved content
        print(f"\n🚀 Creating '{theme_name}' playlist...")
        
        description = f"A {theme_name.lower()} playlist created with the Alex Method"
        playlist = self.create_basic_playlist(
            name=f"{theme_name} Mix - {datetime.now().strftime('%b %Y')}",
            description=description
        )
        
        # Add only the found tracks
        track_ids = [track['id'] for track in found_tracks]
        if track_ids:
            for i in range(0, len(track_ids), 100):
                batch = track_ids[i:i+100]
                self.sp.playlist_add_items(playlist['id'], batch)
            
            print(f"✅ Successfully added {len(track_ids)} tracks to playlist")
        
        return playlist

    def create_themed_playlist(self, theme_name, track_list):
        """Create a themed playlist with predefined tracks (legacy method)"""
        return self.create_playlist_with_approval(theme_name, track_list)

    def analyze_playlist_energy(self, playlist_id):
        """
        Analyze the energy flow of a playlist using Spotify's audio features
        This is part of Alex's advanced DJ technique
        """
        # Get playlist tracks
        tracks = self.sp.playlist_tracks(playlist_id)
        track_ids = [item['track']['id'] for item in tracks['items'] if item['track']]
        
        # Get audio features
        audio_features = self.sp.audio_features(track_ids)
        
        energy_analysis = {
            'track_count': len(track_ids),
            'avg_energy': sum(f['energy'] for f in audio_features if f) / len(audio_features),
            'avg_tempo': sum(f['tempo'] for f in audio_features if f) / len(audio_features),
            'avg_valence': sum(f['valence'] for f in audio_features if f) / len(audio_features),
            'energy_flow': [f['energy'] for f in audio_features if f]
        }
        
        print("\n📊 Playlist Energy Analysis:")
        print(f"   Tracks: {energy_analysis['track_count']}")
        print(f"   Average Energy: {energy_analysis['avg_energy']:.2f}")
        print(f"   Average Tempo: {energy_analysis['avg_tempo']:.0f} BPM")
        print(f"   Average Mood: {energy_analysis['avg_valence']:.2f}")
        
    def generate_smart_playlist(self, theme, preferences=None):
        """
        Generate smart playlist suggestions based on theme and user preferences
        User approves before API creation
        """
        print(f"\n🧠 Generating smart '{theme}' playlist suggestions...")
        
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

        return energy_analysis

def interactive_playlist_creator():
    """Interactive playlist creation with user approval workflow"""
    
    # NOTE: Replace these with your actual Spotify app credentials
    CLIENT_ID = "your_client_id_here"
    CLIENT_SECRET = "your_client_secret_here"
    REDIRECT_URI = "http://localhost:8080/callback"
    
    print("🎧 Interactive Spotify Playlist Creator")
    print("=" * 50)
    print("This tool will preview playlists before creating them via API")
    print("You'll approve the content before any playlist is created.")
    
    # Uncomment when you have credentials:
    # creator = SpotifyPlaylistCreator(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    
    # Demo workflow (uncomment when ready):
    # print("\n🎯 Available playlist themes:")
    # print("1. workout - High-energy tracks for exercise")  
    # print("2. chill - Relaxed tracks for unwinding")
    # print("3. focus - Instrumental tracks for concentration")
    # print("4. party - Upbeat tracks for celebrations")
    
    # theme = input("\nEnter theme (workout/chill/focus/party): ").strip().lower()
    # 
    # if theme in ['workout', 'chill', 'focus', 'party']:
    #     playlist = creator.generate_smart_playlist(theme)
    #     
    #     if playlist:
    #         print(f"\n🎉 Playlist created successfully!")
    #         print(f"   URL: {playlist['external_urls']['spotify']}")
    #         
    #         # Analyze the created playlist
    #         creator.analyze_playlist_energy(playlist['id'])
    #     else:
    #         print("❌ Playlist creation was cancelled or failed.")
    # else:
    #     print("❌ Invalid theme selected.")
    
    print("\n📚 To use this interactive creator:")
    print("1. Get Spotify API credentials from https://developer.spotify.com/dashboard")
    print("2. Replace CLIENT_ID, CLIENT_SECRET, and REDIRECT_URI with your values")
    print("3. Uncomment the demo code above")
    print("4. Run: python spotify_playlist_tutorial.py")

def demo_playlist_creation():
    """Demo showing different playlist creation methods"""
    
    # NOTE: Replace these with your actual Spotify app credentials
    CLIENT_ID = "your_client_id_here"
    CLIENT_SECRET = "your_client_secret_here"
    REDIRECT_URI = "http://localhost:8080/callback"
    
    print("🎧 Spotify Playlist Creation Tutorial")
    print("=" * 50)
    
    # Uncomment the following lines when you have credentials:
    
    # creator = SpotifyPlaylistCreator(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    
    # Example 1: Create a workout playlist with approval
    # workout_tracks = [
    #     "Eminem - Till I Collapse",
    #     "The Prodigy - Spitfire",
    #     "Skrillex - Bangarang",
    #     "Pendulum - Propane Nightmares",
    #     "Rage Against The Machine - Killing In The Name"
    # ]
    # 
    # workout_playlist = creator.create_playlist_with_approval("High Energy Workout", workout_tracks)
    
    # Example 2: Create a smart playlist with approval
    # chill_playlist = creator.generate_smart_playlist("chill")
    
    # Example 3: Analyze energy flow of created playlist
    # if workout_playlist:
    #     creator.analyze_playlist_energy(workout_playlist['id'])
    
    print("\n📚 To use this script:")
    print("1. Get Spotify API credentials from https://developer.spotify.com/dashboard")
    print("2. Replace CLIENT_ID, CLIENT_SECRET, and REDIRECT_URI with your values")
    print("3. Uncomment the demo code above")
    print("4. Run: python spotify_playlist_tutorial.py")
    print("\n🔄 For interactive mode, call interactive_playlist_creator() instead")

if __name__ == "__main__":
    # Choose your mode:
    demo_playlist_creation()        # Basic demo
    # interactive_playlist_creator()  # Interactive mode
