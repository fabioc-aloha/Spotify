#!/usr/bin/env python3
"""
DJ Live Performance Playlist Creator
Curating acclaimed and highly-played DJ live performances
"""

import os
import sys
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class DJLivePerformancePlaylistMaker:
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
        print("🎧 Connected to Spotify for legendary DJ live performances!")
    
    def search_dj_live_performances(self):
        """Find acclaimed DJ live performances and sets."""
        # World-renowned DJ live performance searches
        dj_performance_queries = [
            # Legendary Electronic DJ Sets
            "Carl Cox live",
            "Armin van Buuren live trance",
            "Tiësto live performance",
            "David Guetta live set",
            "Swedish House Mafia live",
            "Deadmau5 live performance",
            "Calvin Harris live",
            "Martin Garrix live set",
            
            # House & Techno Legends
            "Solomun live",
            "Tale of Us live",
            "Nina Kraviz live",
            "Charlotte de Witte live",
            "Amelie Lens live",
            "Boris Brejcha live",
            "Adam Beyer live",
            "Richie Hawtin live",
            
            # Festival & Club Legends
            "Eric Prydz live",
            "Above & Beyond live",
            "Kaskade live set",
            "Diplo live",
            "Skrillex live performance",
            "Marshmello live",
            "The Chainsmokers live",
            "Zedd live performance",
            
            # Underground & Deep House
            "Dixon live",
            "Âme live",
            "Maceo Plex live",
            "Hot Since 82 live",
            "Jamie Jones live",
            "Marco Carola live",
            "Luciano live set",
            "Ricardo Villalobos live",
            
            # Trance Legends
            "Paul van Dyk live",
            "Ferry Corsten live",
            "Markus Schulz live",
            "Aly & Fila live",
            "Andrew Rayel live",
            "Cosmic Gate live",
            
            # Festival Anthems
            "Tomorrowland live",
            "Ultra Miami live",
            "EDC live performance",
            "Coachella DJ set",
            "Ibiza live set",
            "Burning Man live"
        ]
        
        tracks = []
        print("🔍 Searching for legendary DJ live performances...")
        print("   Targeting acclaimed festival sets and club performances")
        
        for query in dj_performance_queries:
            try:
                results = self.sp.search(q=query, type='track', limit=6)
                if results and results.get('tracks') and results['tracks'].get('items'):
                    for track in results['tracks']['items']:
                        # Filter for live performance characteristics
                        if (track and self.is_live_performance(track) and 
                            track.get('id') not in [t['id'] for t in tracks]):
                            duration_min = track['duration_ms'] / 60000
                            tracks.append({
                                'id': track['id'],
                                'name': track['name'],
                                'artist': track['artists'][0]['name'],
                                'uri': track['uri'],
                                'duration_ms': track['duration_ms'],
                                'duration_min': duration_min,
                                'popularity': track['popularity'],
                                'dj_category': self.categorize_dj_style(query)
                            })
            except Exception as e:
                print(f"   ⚠️ Search issue with '{query}': {e}")
                continue
        
        # Sort and curate for the best live performances
        tracks = self.curate_dj_performance_journey(tracks)
        total_duration = sum(t['duration_min'] for t in tracks)
        print(f"✅ Curated {len(tracks)} legendary DJ performances ({total_duration:.1f} minutes)")
        return tracks
    
    def is_live_performance(self, track):
        """Filter tracks for live performance characteristics."""
        name_lower = track['name'].lower()
        artist_lower = track['artists'][0]['name'].lower()
        
        # Look for live performance indicators
        live_indicators = [
            'live', 'set', 'mix', 'session', 'performance', 'festival',
            'club', 'radio', 'recorded live', 'dj set', 'live from',
            'tomorrowland', 'ultra', 'edc', 'coachella', 'ibiza',
            'burning man', 'essential mix', 'live at'
        ]
        
        # Check if it's likely a live performance
        has_live_indicator = any(indicator in name_lower for indicator in live_indicators)
        
        # Prefer longer tracks (live sets are typically longer)
        duration_min = track['duration_ms'] / 60000
        is_good_length = duration_min > 3  # At least 3 minutes
        
        # Avoid obvious non-live tracks
        avoid_keywords = ['remix', 'edit', 'vocal', 'instrumental', 'radio edit']
        has_avoid_keyword = any(keyword in name_lower for keyword in avoid_keywords)
        
        return (has_live_indicator or duration_min > 8) and is_good_length and not has_avoid_keyword
    
    def categorize_dj_style(self, query):
        """Categorize DJ performance by style."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['trance', 'armin', 'paul van dyk', 'ferry']):
            return 'Trance Legends'
        elif any(word in query_lower for word in ['house', 'solomun', 'dixon', 'âme', 'maceo']):
            return 'House Masters'
        elif any(word in query_lower for word in ['techno', 'nina', 'charlotte', 'amelie', 'adam']):
            return 'Techno Titans'
        elif any(word in query_lower for word in ['festival', 'tomorrowland', 'ultra', 'edc']):
            return 'Festival Anthems'
        elif any(word in query_lower for word in ['progressive', 'eric prydz', 'deadmau5']):
            return 'Progressive Heroes'
        elif any(word in query_lower for word in ['mainstream', 'calvin', 'david guetta', 'martin']):
            return 'Mainstage Legends'
        else:
            return 'Electronic Legends'
    
    def curate_dj_performance_journey(self, tracks):
        """Organize tracks into an epic DJ performance journey."""
        # Group by category
        categories = {
            'Mainstage Legends': [],
            'Festival Anthems': [],
            'Trance Legends': [],
            'House Masters': [],
            'Techno Titans': [],
            'Progressive Heroes': [],
            'Electronic Legends': []
        }
        
        for track in tracks:
            categories[track['dj_category']].append(track)
        
        # Sort each category by popularity and duration
        for category in categories:
            categories[category] = sorted(categories[category], 
                                        key=lambda x: (x['popularity'], x['duration_min']), 
                                        reverse=True)
        
        # Build diverse DJ journey
        journey = []
        tracks_per_category = 8  # Approximately 8 tracks per style
        
        for category, tracks_list in categories.items():
            journey.extend(tracks_list[:tracks_per_category])
        
        # Final sort by popularity to ensure quality
        journey = sorted(journey, key=lambda x: x['popularity'], reverse=True)
        return journey[:50]  # Limit to 50 tracks for optimal playlist length
    
    def preview_dj_journey(self, tracks):
        """Show the DJ performance journey structure."""
        print("\n🎧 Your Legendary DJ Live Performance Playlist:")
        print("=" * 60)
        
        # Group by category for preview
        current_category = None
        total_duration = 0
        category_counts = {}
        
        for i, track in enumerate(tracks, 1):
            if track['dj_category'] != current_category:
                current_category = track['dj_category']
                category_counts[current_category] = category_counts.get(current_category, 0) + 1
                if category_counts[current_category] == 1:  # Only show header once per category
                    print(f"\n🎵 {current_category}:")
                    print("-" * 30)
            
            print(f"{i:2d}. {track['name']} - {track['artist']} ({track['duration_min']:.1f}m)")
            total_duration += track['duration_min']
        
        print(f"\n🎧 Legendary Performance Features:")
        print(f"   • Total Duration: {total_duration:.1f} minutes ({total_duration/60:.1f} hours)")
        print(f"   • {len(tracks)} acclaimed DJ live performances")
        print(f"   • Multiple genres: Trance, House, Techno, Progressive")
        print(f"   • Festival anthems and club legends")
        print(f"   • World-renowned DJs and legendary sets")
        
        print(f"\n🌟 Featured DJ Styles:")
        for category, count in category_counts.items():
            print(f"   • {category}: {count} performances")
        
        response = input("\n👍 Create this legendary DJ performance playlist? (y/n): ").lower().strip()
        return response == 'y' or response == 'yes'
    
    def create_dj_playlist(self, tracks):
        """Create the DJ live performance playlist."""
        try:
            user_info = self.sp.current_user()
            if not user_info:
                raise Exception("Could not get user information")
            user_id = user_info['id']
            
            # Create playlist
            playlist_name = "🎧 Legendary DJ Live Performances - Alex Method"
            description = ("Acclaimed DJ live performances from world-renowned artists. "
                          "Festival anthems, club legends, and iconic sets from the best DJs. "
                          "Created with The Alex Method.")
            
            playlist = self.sp.user_playlist_create(
                user=user_id,
                name=playlist_name,
                public=True,
                description=description
            )
            
            if not playlist:
                raise Exception("Could not create playlist")
            
            # Add tracks in batches
            track_uris = [track['uri'] for track in tracks]
            batch_size = 50
            
            for i in range(0, len(track_uris), batch_size):
                batch = track_uris[i:i + batch_size]
                self.sp.playlist_add_items(playlist['id'], batch)
            
            total_duration = sum(t['duration_min'] for t in tracks)
            print(f"\n🎉 SUCCESS! Created '{playlist_name}'")
            print(f"📱 {len(tracks)} legendary performances added")
            print(f"⏱️ Total Duration: {total_duration:.1f} minutes ({total_duration/60:.1f} hours)")
            
            if playlist.get('external_urls') and playlist['external_urls'].get('spotify'):
                print(f"🔗 Playlist URL: {playlist['external_urls']['spotify']}")
            
            print(f"\n🎧 Ready to experience legendary DJ performances!")
            print(f"🌟 From Tomorrowland to Ibiza, these are the sets that made history!")
            
            return playlist['id']
        
        except Exception as e:
            print(f"❌ Error creating playlist: {e}")
            return None

def main():
    """Create the legendary DJ live performance playlist."""
    print("🎧🌟 LEGENDARY DJ LIVE PERFORMANCE CREATOR")
    print("=" * 50)
    print("Curating acclaimed DJ live performances from world-renowned artists!")
    print("Festival anthems, club legends, and iconic sets that made history!")
    print()
    
    try:
        maker = DJLivePerformancePlaylistMaker()
        
        # Find legendary performances
        tracks = maker.search_dj_live_performances()
        
        if not tracks:
            print("❌ Couldn't find enough DJ performances. Check your internet connection.")
            return
        
        # Preview and confirm
        if maker.preview_dj_journey(tracks):
            playlist_id = maker.create_dj_playlist(tracks)
            print(f"\n🚀 Epic DJ journey ready! Find it in your Spotify library.")
            print(f"🎧 Time to experience the legendary performances!")
        else:
            print("👋 No playlist created. The legend lives on!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your .env file is configured correctly!")

if __name__ == "__main__":
    main()
