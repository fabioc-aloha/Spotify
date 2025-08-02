#!/usr/bin/env python3
"""
Therapeutic Ketamine Infusion Playlist Creator
3-hour curated playlist for medical ketamine therapy sessions
Designed for maximum relaxation and therapeutic benefit
"""

import os
import sys
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class KetamineTherapyPlaylistMaker:
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
        print("🧘 Connected to Spotify for therapeutic ketamine session")
    
    def search_therapeutic_tracks(self):
        """Find therapeutic tracks optimized for ketamine therapy."""
        # Specific therapeutic music categories for ketamine infusion
        therapeutic_queries = [
            # Ambient & Drone (Foundation - 45 minutes)
            "ambient drone meditation",
            "deep ambient soundscapes",
            "therapeutic ambient music",
            "healing ambient drones",
            "cosmic ambient meditation",
            "ethereal ambient therapy",
            
            # Nature & Binaural (Grounding - 30 minutes)
            "nature sounds ambient",
            "forest ambient therapy",
            "ocean ambient meditation",
            "rain ambient healing",
            "binaural beats therapy",
            
            # Classical & Neoclassical (Emotional Processing - 45 minutes)
            "neoclassical ambient piano",
            "therapeutic classical music",
            "ambient classical meditation",
            "healing piano ambient",
            "minimalist classical therapy",
            
            # Sacred & Spiritual (Transcendence - 30 minutes)
            "tibetan singing bowls",
            "crystal bowl meditation",
            "sacred ambient music",
            "spiritual healing music",
            "ceremonial ambient",
            
            # Post-Rock & Cinematic (Integration - 30 minutes)
            "post rock ambient",
            "cinematic ambient therapy",
            "epic ambient meditation",
            "atmospheric post rock",
            "healing soundtracks",
            
            # Extended Ambient (Deep Journey - 30 minutes)
            "long form ambient",
            "extended meditation music",
            "ambient therapy sessions",
            "deep relaxation ambient"
        ]
        
        tracks = []
        print("🔍 Searching for therapeutic ketamine session music...")
        print("   Target: 3 hours of carefully curated healing tracks")
        
        for query in therapeutic_queries:
            try:
                results = self.sp.search(q=query, type='track', limit=8)
                if results['tracks']['items']:
                    for track in results['tracks']['items']:
                        # Filter for therapeutic qualities
                        if self.is_therapeutic_track(track) and track['id'] not in [t['id'] for t in tracks]:
                            duration_min = track['duration_ms'] / 60000
                            tracks.append({
                                'id': track['id'],
                                'name': track['name'],
                                'artist': track['artists'][0]['name'],
                                'uri': track['uri'],
                                'duration_ms': track['duration_ms'],
                                'duration_min': duration_min,
                                'popularity': track['popularity'],
                                'category': self.categorize_track(query)
                            })
            except Exception as e:
                print(f"   ⚠️ Search issue with '{query}': {e}")
                continue
        
        # Sort and curate for 3-hour therapeutic journey
        tracks = self.curate_therapeutic_journey(tracks)
        total_duration = sum(t['duration_min'] for t in tracks)
        print(f"✅ Curated {len(tracks)} therapeutic tracks ({total_duration:.1f} minutes)")
        return tracks
    
    def is_therapeutic_track(self, track):
        """Filter tracks for therapeutic suitability."""
        # Exclude tracks with potentially disruptive characteristics
        name_lower = track['name'].lower()
        artist_lower = track['artists'][0]['name'].lower()
        
        # Avoid tracks with jarring elements
        avoid_keywords = [
            'remix', 'club', 'dance', 'party', 'bass', 'beat', 'trap',
            'rap', 'hip hop', 'rock', 'metal', 'punk', 'hardcore'
        ]
        
        for keyword in avoid_keywords:
            if keyword in name_lower or keyword in artist_lower:
                return False
        
        # Prefer longer tracks (better for therapeutic flow)
        duration_min = track['duration_ms'] / 60000
        if duration_min < 2:  # Avoid very short tracks
            return False
            
        return True
    
    def categorize_track(self, query):
        """Categorize tracks by therapeutic phase."""
        if 'drone' in query or 'deep ambient' in query:
            return 'Foundation'
        elif 'nature' in query or 'binaural' in query:
            return 'Grounding'
        elif 'classical' in query or 'piano' in query:
            return 'Processing'
        elif 'singing bowl' in query or 'sacred' in query:
            return 'Transcendence'
        elif 'post rock' in query or 'cinematic' in query:
            return 'Integration'
        else:
            return 'Deep Journey'
    
    def curate_therapeutic_journey(self, tracks):
        """Organize tracks into a therapeutic 3-hour journey."""
        # Group by category
        categories = {
            'Foundation': [],
            'Grounding': [],
            'Processing': [],
            'Transcendence': [],
            'Integration': [],
            'Deep Journey': []
        }
        
        for track in tracks:
            categories[track['category']].append(track)
        
        # Sort each category by duration (longer tracks first for deeper states)
        for category in categories:
            categories[category] = sorted(categories[category], 
                                        key=lambda x: x['duration_min'], reverse=True)
        
        # Build therapeutic progression (3 hours = 180 minutes)
        journey = []
        target_minutes = {
            'Foundation': 45,      # Deep ambient start
            'Grounding': 30,       # Nature connection
            'Processing': 45,      # Emotional work
            'Transcendence': 30,   # Peak experience
            'Integration': 30,     # Coming together
            'Deep Journey': 20     # Extended healing
        }
        
        for category, target in target_minutes.items():
            current_duration = 0
            for track in categories[category]:
                if current_duration < target:
                    journey.append(track)
                    current_duration += track['duration_min']
                else:
                    break
        
        return journey[:60]  # Limit to 60 tracks max for playlist management
    
    def preview_therapeutic_journey(self, tracks):
        """Show the therapeutic journey structure."""
        print("\n🧘 Your 3-Hour Ketamine Therapy Journey:")
        print("=" * 60)
        
        # Group by category for preview
        current_category = None
        total_duration = 0
        
        for i, track in enumerate(tracks, 1):
            if track['category'] != current_category:
                current_category = track['category']
                print(f"\n🌀 {current_category} Phase:")
                print("-" * 30)
            
            print(f"{i:2d}. {track['name']} - {track['artist']} ({track['duration_min']:.1f}m)")
            total_duration += track['duration_min']
        
        print(f"\n🎵 Therapeutic Journey Features:")
        print(f"   • Total Duration: {total_duration:.1f} minutes ({total_duration/60:.1f} hours)")
        print(f"   • {len(tracks)} carefully curated tracks")
        print(f"   • Progressive phases for optimal therapeutic experience")
        print(f"   • No jarring transitions or disruptive elements")
        print(f"   • Designed for medical ketamine infusion sessions")
        
        print(f"\n⚕️ Medical Note: This playlist is designed for supervised")
        print(f"   medical ketamine therapy sessions only.")
        
        response = input("\n👍 Create this therapeutic journey playlist? (y/n): ").lower().strip()
        return response == 'y' or response == 'yes'
    
    def create_therapeutic_playlist(self, tracks):
        """Create the ketamine therapy playlist."""
        user_id = self.sp.current_user()['id']
        
        # Create playlist
        playlist_name = "🧘 Ketamine Therapy Journey - Alex Method (3hrs)"
        description = ("3-hour therapeutic playlist for medical ketamine infusion sessions. "
                      "Carefully curated for maximum relaxation and therapeutic benefit. "
                      "Created with The Alex Method for supervised medical use only.")
        
        playlist = self.sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,  # Keep private for medical use
            description=description
        )
        
        # Add tracks in batches
        track_uris = [track['uri'] for track in tracks]
        batch_size = 50
        
        for i in range(0, len(track_uris), batch_size):
            batch = track_uris[i:i + batch_size]
            self.sp.playlist_add_items(playlist['id'], batch)
        
        total_duration = sum(t['duration_min'] for t in tracks)
        print(f"\n🎉 SUCCESS! Created '{playlist_name}'")
        print(f"📱 {len(tracks)} therapeutic tracks added")
        print(f"⏱️ Total Duration: {total_duration:.1f} minutes ({total_duration/60:.1f} hours)")
        print(f"🔗 Playlist URL: {playlist['external_urls']['spotify']}")
        print(f"\n🧘 Perfect for your supervised ketamine therapy session!")
        print(f"⚕️ Remember: For medical supervision only")
        
        return playlist['id']

def main():
    """Create the perfect ketamine therapy playlist."""
    print("🧘⚕️ KETAMINE THERAPY PLAYLIST CREATOR")
    print("=" * 50)
    print("Creating a 3-hour therapeutic journey for medical ketamine infusion")
    print("⚕️ For supervised medical ketamine therapy sessions only")
    print()
    
    try:
        maker = KetamineTherapyPlaylistMaker()
        
        # Find therapeutic tracks
        tracks = maker.search_therapeutic_tracks()
        
        if not tracks:
            print("❌ Couldn't find enough therapeutic tracks. Check your internet connection.")
            return
        
        # Preview and confirm
        if maker.preview_therapeutic_journey(tracks):
            playlist_id = maker.create_therapeutic_playlist(tracks)
            print(f"\n🚀 Therapeutic journey ready! Find it in your Spotify library.")
            print(f"🧘 Wishing you a healing and transformative session.")
        else:
            print("👋 No playlist created. Stay safe and well!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your .env file is configured correctly!")

if __name__ == "__main__":
    main()
