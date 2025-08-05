# 🍎 Apple Music API - Comprehensive Developer Documentation
**Alex Method DJ Platform - Apple Music Integration**
**Release Date**: August 4, 2025

**⚠️ CRITICAL LIMITATIONS NOTICE:**
- **PLAYLIST CREATION NOT SUPPORTED**: Apple Music API does not support creating user playlists via API
- **LIBRARY WRITE OPERATIONS LIMITED**: Cannot add/remove songs from user library via public API
- **READ-ONLY ACCESS**: API primarily provides catalog search and read-only library access
- **MusicKit.js REQUIRED**: User interactions require client-side MusicKit.js, not server-side API

## Table of Contents
1. [Authentication & Setup](#authentication--setup)
2. [Music Catalog & Search](#music-catalog--search)
3. [Library Management (Read-Only)](#library-management-read-only)
4. [API Limitations & Workarounds](#api-limitations--workarounds)
5. [Artist & Album Data](#artist--album-data)
6. [User Profile & Preferences (Limited)](#user-profile--preferences-limited)
7. [Recommendations & Discovery](#recommendations--discovery)
8. [Charts & Editorial](#charts--editorial)
9. [Subscription & Storefront](#subscription--storefront)
10. [MusicKit.js Integration](#musickit-js-integration)
11. [Code Examples (Read-Only Operations)](#code-examples-read-only-operations)
12. [Best Practices](#best-practices)
13. [Error Handling](#error-handling)
14. [Rate Limits & Optimization](#rate-limits--optimization)
15. [Alternative Solutions](#alternative-solutions)

---

## Authentication & Setup

Apple Music API uses a unique authentication approach combining JWT (JSON Web Tokens) with Apple's developer certificates. Unlike traditional OAuth flows, Apple Music requires a MusicKit developer token generated using your Apple Developer account private key. This approach provides secure, server-to-server authentication while maintaining user privacy through Apple's ecosystem. The authentication process involves creating a signed JWT token that identifies your application to Apple's services.

### Required Setup Components
```python
# Essential components for Apple Music API access
REQUIRED_CREDENTIALS = {
    "team_id": "YOUR_APPLE_DEVELOPER_TEAM_ID",        # 10-character team identifier
    "key_id": "YOUR_MUSICKIT_KEY_ID",                 # MusicKit key identifier
    "private_key_path": "path/to/AuthKey_KEYID.p8",   # Downloaded private key file
    "bundle_id": "com.yourcompany.yourapp"            # iOS app bundle identifier (optional)
}
```

### MusicKit Developer Token Generation
```python
import jwt
import time
from datetime import datetime, timedelta

def generate_developer_token(team_id, key_id, private_key_path):
    """
    Generate Apple Music API developer token using JWT

    Args:
        team_id: Apple Developer Team ID (10 characters)
        key_id: MusicKit key identifier
        private_key_path: Path to AuthKey_KEYID.p8 file

    Returns:
        str: Signed JWT token valid for 6 months
    """

    # Read the private key
    with open(private_key_path, 'r') as key_file:
        private_key = key_file.read()

    # JWT headers
    headers = {
        "alg": "ES256",
        "kid": key_id,
        "typ": "JWT"
    }

    # JWT payload
    now = datetime.utcnow()
    payload = {
        "iss": team_id,                                    # Issuer (Team ID)
        "iat": int(now.timestamp()),                       # Issued at
        "exp": int((now + timedelta(days=180)).timestamp()) # Expires (6 months max)
    }

    # Generate and return the token
    return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)

# Usage example
developer_token = generate_developer_token(
    team_id="ABCD123456",
    key_id="XYZ789ABC1",
    private_key_path="./AuthKey_XYZ789ABC1.p8"
)
```

### Apple Music API Client Setup
```python
import requests
import json
from typing import Dict, List, Optional

class AppleMusicAPI:
    """
    Apple Music API client for The Alex Method DJ Platform
    Handles authentication, requests, and response parsing
    """

    def __init__(self, developer_token: str, storefront: str = "us"):
        """
        Initialize Apple Music API client

        Args:
            developer_token: JWT token for API authentication
            storefront: Country/region code (us, gb, jp, etc.)
        """
        self.base_url = "https://api.music.apple.com/v1"
        self.developer_token = developer_token
        self.storefront = storefront

        # Standard headers for all requests
        self.headers = {
            "Authorization": f"Bearer {developer_token}",
            "Content-Type": "application/json",
            "User-Agent": "Alex-Method-DJ-Platform/1.0"
        }

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated request to Apple Music API"""
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Apple Music API Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise
```

---

## Music Catalog & Search

Apple Music's catalog contains over 100 million songs with rich metadata including lyrics, credits, and high-quality artwork. The search functionality supports complex queries with filters for content type, genre, and release date. Understanding the catalog structure is essential for creating precise searches that return the most relevant results for playlist curation.

### Search Operations
```python
def search_music(self, query: str, types: List[str] = None, limit: int = 25) -> Dict:
    """
    Search Apple Music catalog

    Args:
        query: Search query string
        types: List of content types ['songs', 'albums', 'artists', 'playlists']
        limit: Number of results per type (max 25)

    Returns:
        Dict: Search results with metadata
    """
    if types is None:
        types = ['songs']

    params = {
        'term': query,
        'types': ','.join(types),
        'limit': limit,
        'l': 'en-us'  # Language preference
    }

    return self._make_request(f"catalog/{self.storefront}/search", params)

# Advanced search with filters
def search_songs_advanced(self, query: str, genre: str = None,
                         year_range: tuple = None, explicit: bool = None) -> Dict:
    """
    Advanced song search with genre and year filtering

    Args:
        query: Base search term
        genre: Genre filter (pop, rock, hip-hop, etc.)
        year_range: Tuple of (start_year, end_year)
        explicit: Filter explicit content (True/False/None)

    Returns:
        Dict: Filtered search results
    """
    # Build advanced search query
    search_terms = [query]

    if genre:
        search_terms.append(f"genre:{genre}")

    if year_range:
        start, end = year_range
        search_terms.append(f"year:{start}-{end}")

    if explicit is not None:
        explicit_filter = "clean" if not explicit else "explicit"
        search_terms.append(f"explicit:{explicit_filter}")

    advanced_query = " ".join(search_terms)

    return self.search_music(advanced_query, types=['songs'])
```

### Song Metadata Extraction
```python
def extract_song_metadata(self, song_data: Dict) -> Dict:
    """
    Extract comprehensive metadata from Apple Music song object

    Args:
        song_data: Raw song data from API response

    Returns:
        Dict: Cleaned and structured metadata
    """
    attributes = song_data.get('attributes', {})

    metadata = {
        # Basic Information
        'id': song_data.get('id'),
        'type': song_data.get('type'),
        'title': attributes.get('name'),
        'artist': attributes.get('artistName'),
        'album': attributes.get('albumName'),

        # Duration and Technical
        'duration_ms': attributes.get('durationInMillis'),
        'duration_formatted': self._format_duration(attributes.get('durationInMillis')),
        'track_number': attributes.get('trackNumber'),
        'disc_number': attributes.get('discNumber'),

        # Release Information
        'release_date': attributes.get('releaseDate'),
        'year': self._extract_year(attributes.get('releaseDate')),
        'genre': self._extract_primary_genre(attributes.get('genreNames', [])),
        'genres': attributes.get('genreNames', []),

        # Content Information
        'explicit': attributes.get('contentRating') == 'explicit',
        'preview_url': attributes.get('previews', [{}])[0].get('url'),
        'isrc': attributes.get('isrc'),

        # Artwork
        'artwork_url': self._format_artwork_url(attributes.get('artwork', {})),
        'artwork_width': attributes.get('artwork', {}).get('width'),
        'artwork_height': attributes.get('artwork', {}).get('height'),

        # Apple Music Specific
        'apple_music_url': attributes.get('url'),
        'playable': attributes.get('playParams') is not None,
        'composer': attributes.get('composerName'),

        # Relationships (if available)
        'album_id': self._extract_relationship_id(song_data, 'albums'),
        'artist_id': self._extract_relationship_id(song_data, 'artists'),
    }

    return metadata

def _format_duration(self, duration_ms: int) -> str:
    """Convert milliseconds to MM:SS format"""
    if not duration_ms:
        return "0:00"

    total_seconds = duration_ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"

def _extract_year(self, release_date: str) -> int:
    """Extract year from release date string"""
    if release_date:
        return int(release_date.split('-')[0])
    return None

def _extract_primary_genre(self, genres: List[str]) -> str:
    """Get primary genre from genre list"""
    return genres[0] if genres else "Unknown"

def _format_artwork_url(self, artwork: Dict, size: int = 600) -> str:
    """Generate artwork URL with specified size"""
    if not artwork or 'url' not in artwork:
        return None

    template_url = artwork['url']
    return template_url.replace('{w}', str(size)).replace('{h}', str(size))

def _extract_relationship_id(self, data: Dict, relationship_type: str) -> str:
    """Extract ID from relationship data"""
    relationships = data.get('relationships', {})
    relationship_data = relationships.get(relationship_type, {}).get('data', [])

    if relationship_data:
        return relationship_data[0].get('id')
    return None
```

---

## Library Management (Read-Only)

**⚠️ CRITICAL LIMITATION**: The Apple Music API does **NOT** support writing to user libraries. You cannot add songs, create playlists, or modify user data through the server-side API. These operations require MusicKit.js client-side implementation with user interaction.

### Available Read-Only Operations
```python
def get_user_library_songs(self, limit: int = 100, offset: int = 0) -> Dict:
    """
    Retrieve songs from user's Apple Music library (READ-ONLY)

    Args:
        limit: Number of songs to retrieve (max 100)
        offset: Pagination offset

    Returns:
        Dict: User's library songs with metadata
    """
    params = {
        'limit': limit,
        'offset': offset,
        'include': 'catalog'  # Include catalog relationship for full metadata
    }

    return self._make_request("me/library/songs", params)

def get_user_library_playlists(self, limit: int = 100) -> Dict:
    """
    Retrieve user's existing playlists (READ-ONLY)

    Args:
        limit: Number of playlists to retrieve

    Returns:
        Dict: User's existing playlists
    """
    params = {'limit': limit}
    return self._make_request("me/library/playlists", params)

# ❌ THESE OPERATIONS ARE NOT SUPPORTED BY APPLE MUSIC API:
# - create_playlist()
# - add_songs_to_playlist()
# - remove_from_library()
# - add_to_library()
```

### Why Library Write Operations Are Not Available
Apple Music API is designed with strict privacy and security controls:
- **User Privacy**: Apple restricts programmatic modifications to user data
- **App Store Guidelines**: Playlist creation requires user interaction through Apple's interfaces
- **Security Model**: Write operations must go through MusicKit.js with explicit user consent
- **Platform Integration**: Apple prioritizes native app experiences over third-party automation

---

## API Limitations & Workarounds

### Critical Limitations for Playlist Creation Platforms

**1. No Server-Side Playlist Creation**
```python
# ❌ THIS DOES NOT WORK - Apple Music API limitation
def create_playlist_NOT_POSSIBLE(self, name: str, description: str = "") -> Dict:
    """
    Apple Music API does NOT support playlist creation via server-side API.
    This operation requires MusicKit.js client-side implementation.
    """
    raise NotImplementedError(
        "Apple Music API does not support server-side playlist creation. "
        "Use MusicKit.js for client-side operations with user interaction."
    )
```

**2. Limited User Library Access**
```python
# ✅ SUPPORTED: Read user's existing content
def analyze_user_music_preferences(self) -> Dict:
    """
    Analyze user's existing library for recommendation insights
    This is the primary use case for Apple Music API integration
    """
    library_songs = self.get_user_library_songs(limit=100)

    # Extract genres, artists, and listening patterns
    analysis = {
        'top_genres': self._extract_genres(library_songs),
        'favorite_artists': self._extract_artists(library_songs),
        'decade_preferences': self._analyze_decades(library_songs)
    }

    return analysis

# ❌ NOT SUPPORTED: Modifying user library
def add_recommended_songs_NOT_POSSIBLE(self, song_ids: List[str]) -> bool:
    """Apple Music API cannot add songs to user library programmatically"""
    raise NotImplementedError("Use MusicKit.js for user library modifications")
```

**3. Workarounds for Alex Method DJ Platform**

```python
class AppleMusicReadOnlyIntegration:
    """
    Apple Music integration focused on catalog search and analysis
    Cannot create playlists but can provide Apple Music song recommendations
    """

    def find_apple_music_equivalent(self, spotify_track: Dict) -> Dict:
        """
        Find Apple Music catalog equivalent of Spotify track
        Useful for cross-platform track mapping
        """
        search_query = f"{spotify_track['artist']} {spotify_track['title']}"
        results = self.search_music(search_query, types=['songs'], limit=5)

        # Find best match based on artist, title, and duration
        best_match = self._find_best_match(results, spotify_track)
        return best_match

    def generate_apple_music_recommendations(self, playlist_config: Dict) -> List[Dict]:
        """
        Generate Apple Music song recommendations based on playlist configuration
        Users must manually add these to their Apple Music library
        """
        recommendations = []

        for search_term in playlist_config['search_queries']:
            search_results = self.search_music(search_term, types=['songs'])
            processed_tracks = self._process_and_filter_tracks(
                search_results,
                playlist_config['filters']
            )
            recommendations.extend(processed_tracks)

        return self._deduplicate_and_optimize(recommendations, playlist_config)

    def export_for_manual_import(self, recommendations: List[Dict]) -> str:
        """
        Export recommendations in format for manual Apple Music import
        Since API cannot create playlists, provide user-friendly export
        """
        export_text = "Apple Music Songs for Manual Addition:\n\n"

        for i, track in enumerate(recommendations, 1):
            export_text += f"{i}. {track['artist']} - {track['title']}\n"
            export_text += f"   Album: {track['album']}\n"
            export_text += f"   Apple Music Link: {track['apple_music_url']}\n\n"

        return export_text
```---

## Artist & Album Data

Apple Music provides comprehensive artist and album information including biographies, discographies, and related artists. This data is valuable for playlist curation and understanding musical relationships.

### Artist Information
```python
def get_artist_details(self, artist_id: str, include_albums: bool = True) -> Dict:
    """
    Get comprehensive artist information

    Args:
        artist_id: Apple Music artist ID
        include_albums: Whether to include album discography

    Returns:
        Dict: Artist details with optional albums
    """
    include_params = ['genres']
    if include_albums:
        include_params.append('albums')

    params = {
        'include': ','.join(include_params)
    }

    return self._make_request(f"catalog/{self.storefront}/artists/{artist_id}", params)

def get_artist_top_songs(self, artist_id: str, limit: int = 10) -> Dict:
    """
    Get artist's most popular songs

    Args:
        artist_id: Apple Music artist ID
        limit: Number of top songs to retrieve

    Returns:
        Dict: Top songs data
    """
    params = {'limit': limit}

    return self._make_request(
        f"catalog/{self.storefront}/artists/{artist_id}/songs",
        params
    )

def search_artist_discography(self, artist_name: str, album_type: str = None) -> Dict:
    """
    Search for artist's complete discography

    Args:
        artist_name: Artist name to search
        album_type: Filter by album type (album, single, compilation)

    Returns:
        Dict: Artist's albums and singles
    """
    # First find the artist
    artist_search = self.search_music(artist_name, types=['artists'])

    if not artist_search.get('results', {}).get('artists', {}).get('data'):
        return {"error": "Artist not found"}

    artist_id = artist_search['results']['artists']['data'][0]['id']

    # Get artist's albums
    albums_data = self._make_request(
        f"catalog/{self.storefront}/artists/{artist_id}/albums"
    )

    # Filter by album type if specified
    if album_type and albums_data.get('data'):
        filtered_albums = [
            album for album in albums_data['data']
            if album.get('attributes', {}).get('albumType') == album_type
        ]
        albums_data['data'] = filtered_albums

    return albums_data
```

---

## User Profile & Preferences (Limited)

**⚠️ LIMITED ACCESS**: Apple Music API provides very limited user profile data compared to Spotify. Most personal listening data is not accessible via the server-side API.

### Available User Data
```python
def get_user_storefront(self) -> Dict:
    """
    Get user's current storefront (country/region)
    This is the primary user data available via Apple Music API

    Returns:
        Dict: User's storefront information
    """
    return self._make_request("me/storefront")

# ❌ NOT AVAILABLE via Apple Music API:
# - User listening history (requires MusicKit.js)
# - Top artists/songs (not exposed in public API)
# - User preferences (private data)
# - Personalized recommendations (limited access)

def get_limited_user_insights(self) -> Dict:
    """
    Extract limited insights from available user data
    Much more restricted than Spotify's user data access
    """
    try:
        storefront = self.get_user_storefront()
        library_sample = self.get_user_library_songs(limit=50)

        # Extract basic insights from library
        insights = {
            'storefront': storefront.get('data', [{}])[0].get('id', 'us'),
            'library_size_sample': len(library_sample.get('data', [])),
            'has_apple_music_subscription': bool(library_sample.get('data')),
            'note': 'Apple Music API provides very limited user insights'
        }

        return insights

    except Exception as e:
        return {'error': f'Unable to access user data: {e}'}
```---

## Recommendations & Discovery (Limited)

**⚠️ LIMITED RECOMMENDATIONS**: Apple Music API has very limited recommendation capabilities compared to Spotify. Most recommendation features require MusicKit.js client-side implementation.

### Available Discovery Features
```python
def get_editorial_playlists(self, genre: str = None) -> Dict:
    """
    Get Apple Music editorial playlists (read-only)

    Args:
        genre: Filter by genre (optional)

    Returns:
        Dict: Editorial playlists
    """
    params = {}
    if genre:
        params['genre'] = genre

    return self._make_request(f"catalog/{self.storefront}/playlists", params)

def get_new_releases(self, limit: int = 50) -> Dict:
    """
    Get new music releases from Apple Music catalog

    Args:
        limit: Number of releases to retrieve

    Returns:
        Dict: New releases data
    """
    params = {'limit': limit}

    return self._make_request(f"catalog/{self.storefront}/albums", params)

# ❌ NOT AVAILABLE via Apple Music API:
# - Personalized recommendations based on listening history
# - Seed-based recommendations (requires MusicKit.js)
# - Similar artists/songs algorithms
# - User taste profile analysis

def discover_similar_content_via_search(self, reference_artist: str,
                                      reference_genre: str = None) -> Dict:
    """
    Workaround: Use search and genre filtering to find similar content
    Not as sophisticated as Spotify's recommendation engine
    """
    try:
        # Search for artists in similar genres
        search_params = {
            'term': reference_artist,
            'types': ['artists', 'songs'],
            'limit': 25
        }

        if reference_genre:
            search_params['term'] += f" {reference_genre}"

        results = self._make_request("catalog/{}/search".format(self.storefront),
                                   search_params)

        return {
            'similar_artists': results.get('results', {}).get('artists', {}),
            'related_songs': results.get('results', {}).get('songs', {}),
            'note': 'Limited discovery via search - not true recommendations'
        }

    except Exception as e:
        return {'error': f'Discovery search failed: {e}'}
```
```

---

## Charts & Editorial

Apple Music charts provide trending music data across different regions and time periods. This information is valuable for understanding current musical trends and popular content.

### Charts Access
```python
def get_charts(self, chart_type: str = 'songs', genre: str = None) -> Dict:
    """
    Get Apple Music charts

    Args:
        chart_type: 'songs', 'albums', or 'playlists'
        genre: Specific genre charts (optional)

    Returns:
        Dict: Chart data
    """
    endpoint = f"catalog/{self.storefront}/charts"

    params = {'types': chart_type}
    if genre:
        params['genre'] = genre

    return self._make_request(endpoint, params)

def get_trending_searches(self) -> Dict:
    """
    Get trending search terms

    Returns:
        Dict: Trending search data
    """
    return self._make_request(f"catalog/{self.storefront}/search/trending")
```

---

## Code Examples (Read-Only Operations)

### ⚠️ IMPORTANT: Apple Music API CANNOT create playlists

The following examples show **READ-ONLY** operations available with Apple Music API. For actual playlist creation, users must manually create playlists or use MusicKit.js.

### Music Discovery Workflow
```python
def discover_music_for_manual_playlist(api_client, search_criteria):
    """
    Discover music that users can manually add to Apple Music playlists

    Args:
        api_client: AppleMusicAPI instance
        search_criteria: Configuration dict with search parameters

    Returns:
        Dict: Track recommendations for manual playlist creation
    """

    discovered_tracks = []

    # Step 1: Search for tracks matching criteria
    for genre in search_criteria.get('genres', []):
        search_results = api_client.search_music(
            query=f"{genre} {search_criteria.get('mood', '')}",
            types=['songs'],
            limit=50
        )

        if search_results.get('results', {}).get('songs', {}).get('data'):
            discovered_tracks.extend(
                search_results['results']['songs']['data']
            )

    # Step 2: Filter by criteria (tempo, energy, etc.)
    filtered_tracks = []
    for track in discovered_tracks:
        attributes = track.get('attributes', {})

        # Basic filtering (Apple Music has limited audio features)
        if (attributes.get('durationInMillis', 0) >=
            search_criteria.get('min_duration_ms', 30000)):
            filtered_tracks.append({
                'id': track['id'],
                'name': attributes.get('name'),
                'artist': attributes.get('artistName'),
                'album': attributes.get('albumName'),
                'preview_url': attributes.get('previews', [{}])[0].get('url'),
                'apple_music_url': attributes.get('url'),
                'manual_add_instructions': 'Copy this URL and add manually to Apple Music'
            })

    return {
        'tracks_for_manual_creation': filtered_tracks[:search_criteria.get('limit', 30)],
        'total_discovered': len(filtered_tracks),
        'note': 'These tracks must be manually added to Apple Music playlists',
        'instructions': 'Use Apple Music app or MusicKit.js for playlist creation'
    }

def generate_apple_music_export_format(track_list):
    """
    Generate export format for sharing track lists with Apple Music users

    Args:
        track_list: List of track dictionaries

    Returns:
        Dict: Various export formats for manual playlist creation
    """

    export_formats = {
        'text_list': [],
        'csv_format': 'Artist,Song,Album,Apple Music URL\n',
        'markdown_format': '# Playlist Tracks\n\n',
        'apple_shortcuts_format': []
    }

    for track in track_list:
        # Text format
        export_formats['text_list'].append(
            f"{track['artist']} - {track['name']}"
        )

        # CSV format
        export_formats['csv_format'] += (
            f'"{track["artist"]}","{track["name"]}","{track["album"]}",'
            f'"{track.get("apple_music_url", "")}"\n'
        )

        # Markdown format
        export_formats['markdown_format'] += (
            f"- **{track['name']}** by {track['artist']}\n"
        )

        # Apple Shortcuts format (for iOS automation)
        if track.get('apple_music_url'):
            export_formats['apple_shortcuts_format'].append(track['apple_music_url'])

    return export_formats

    playlist_id = playlist_data['data'][0]['id']
    print(f"Created playlist: {playlist_config['name']} (ID: {playlist_id})")

    # Step 2: Search for tracks based on configuration
    all_tracks = []

    for search_term in playlist_config['search_queries']:
        search_results = api_client.search_music(
            query=search_term,
            types=['songs'],
            limit=25
        )

        songs = search_results.get('results', {}).get('songs', {}).get('data', [])

        # Filter and process tracks
        for song in songs:
            track_metadata = api_client.extract_song_metadata(song)

            # Apply filters
            if api_client._passes_filters(track_metadata, playlist_config):
                all_tracks.append(track_metadata)

    # Step 3: Remove duplicates and optimize for target duration
    unique_tracks = api_client._remove_duplicates(all_tracks)
    selected_tracks = api_client._optimize_for_duration(
        unique_tracks,
        playlist_config['target_duration_minutes']
    )

    # Step 4: Add tracks to playlist
    track_ids = [track['id'] for track in selected_tracks]

    if track_ids:
        success = api_client.add_songs_to_playlist(playlist_id, track_ids)

        if success:
            print(f"Added {len(track_ids)} tracks to playlist")
            return {
                'playlist_id': playlist_id,
                'track_count': len(track_ids),
                'total_duration': sum(t['duration_ms'] for t in selected_tracks),
                'tracks': selected_tracks
            }

    return {'error': 'Failed to create complete playlist'}

# Example configuration
playlist_config = {
    'name': 'Alex Method - Decades Journey',
    'description': 'A curated journey through musical decades with enhanced navigation',
    'search_queries': [
        '1970s hits classic rock',
        '1980s pop synth',
        '1990s alternative grunge',
        '2000s indie rock',
        '2010s electronic dance'
    ],
    'target_duration_minutes': 90,
    'filters': {
        'min_duration_ms': 120000,  # 2 minutes minimum
        'max_duration_ms': 480000,  # 8 minutes maximum
        'exclude_explicit': True
    }
}
```

---

## Best Practices

### Performance Optimization
```python
class AppleMusicOptimizer:
    """
    Performance optimization utilities for Apple Music API
    """

    @staticmethod
    def batch_requests(items: List, batch_size: int = 20):
        """Split large requests into manageable batches"""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]

    @staticmethod
    def cache_search_results(cache_duration_hours: int = 24):
        """Decorator for caching search results"""
        def decorator(func):
            cache = {}
            cache_timestamps = {}

            def wrapper(*args, **kwargs):
                cache_key = str(args) + str(kwargs)
                now = time.time()

                if (cache_key in cache and
                    now - cache_timestamps[cache_key] < cache_duration_hours * 3600):
                    return cache[cache_key]

                result = func(*args, **kwargs)
                cache[cache_key] = result
                cache_timestamps[cache_key] = now

                return result

            return wrapper
        return decorator

    @staticmethod
    def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
        """Decorator for retrying failed requests with exponential backoff"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise e

                        delay = base_delay * (2 ** attempt)
                        time.sleep(delay)
                        print(f"Retry attempt {attempt + 1} after {delay}s delay")

            return wrapper
        return decorator
```

### Error Handling
```python
class AppleMusicAPIError(Exception):
    """Custom exception for Apple Music API errors"""

    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)

def handle_api_errors(response: requests.Response) -> Dict:
    """
    Comprehensive error handling for Apple Music API responses

    Args:
        response: requests.Response object

    Returns:
        Dict: Parsed response data

    Raises:
        AppleMusicAPIError: For various API error conditions
    """
    try:
        data = response.json()
    except ValueError:
        data = {"error": "Invalid JSON response"}

    # Handle different status codes
    if response.status_code == 200:
        return data

    elif response.status_code == 401:
        raise AppleMusicAPIError(
            "Authentication failed. Check your developer token.",
            status_code=401,
            response_data=data
        )

    elif response.status_code == 403:
        raise AppleMusicAPIError(
            "Access forbidden. Verify your Apple Developer account permissions.",
            status_code=403,
            response_data=data
        )

    elif response.status_code == 404:
        raise AppleMusicAPIError(
            "Resource not found.",
            status_code=404,
            response_data=data
        )

    elif response.status_code == 429:
        # Rate limit exceeded
        retry_after = response.headers.get('Retry-After', '60')
        raise AppleMusicAPIError(
            f"Rate limit exceeded. Retry after {retry_after} seconds.",
            status_code=429,
            response_data=data
        )

    elif response.status_code >= 500:
        raise AppleMusicAPIError(
            "Apple Music API server error. Try again later.",
            status_code=response.status_code,
            response_data=data
        )

    else:
        raise AppleMusicAPIError(
            f"Unexpected API error (Status {response.status_code})",
            status_code=response.status_code,
            response_data=data
        )
```

---

## Rate Limits & Optimization

Apple Music API has specific rate limits that vary by endpoint and account type. Understanding these limits is crucial for building efficient applications that can handle large-scale playlist creation.

### Rate Limit Guidelines
```python
class RateLimitManager:
    """
    Manage Apple Music API rate limits and request throttling
    """

    def __init__(self, requests_per_minute: int = 120):
        self.requests_per_minute = requests_per_minute
        self.request_times = []

    def wait_if_needed(self):
        """Wait if necessary to stay within rate limits"""
        now = time.time()

        # Remove requests older than 1 minute
        self.request_times = [
            req_time for req_time in self.request_times
            if now - req_time < 60
        ]

        # Check if we need to wait
        if len(self.request_times) >= self.requests_per_minute:
            oldest_request = min(self.request_times)
            wait_time = 60 - (now - oldest_request)

            if wait_time > 0:
                print(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)

        # Record this request
        self.request_times.append(now)

# Usage in API client
rate_limiter = RateLimitManager()

def make_throttled_request(self, endpoint: str, params: Dict = None) -> Dict:
    """Make API request with automatic rate limiting"""
    rate_limiter.wait_if_needed()
    return self._make_request(endpoint, params)
```

---

## Integration with Alex Method DJ Platform

### Playlist Configuration Integration
```python
# Example: Apple Music integration with existing playlist configs
def convert_spotify_config_to_apple_music(spotify_config_path: str) -> Dict:
    """
    Convert existing Spotify playlist configuration to Apple Music format

    Args:
        spotify_config_path: Path to existing Spotify playlist config

    Returns:
        Dict: Apple Music compatible configuration
    """

    with open(spotify_config_path, 'r') as f:
        spotify_config = yaml.safe_load(f)

    # Convert search queries to Apple Music format
    apple_music_config = {
        'name': spotify_config.get('name', ''),
        'description': spotify_config.get('description', ''),
        'target_duration_minutes': spotify_config.get('target_duration_minutes', 60),
        'search_queries': [],
        'filters': {
            'explicit_filter': 'clean' if spotify_config.get('exclude_explicit') else None,
            'duration_range': (
                spotify_config.get('min_duration_ms', 120000),
                spotify_config.get('max_duration_ms', 480000)
            )
        }
    }

    # Convert track categories to Apple Music search queries
    for category in spotify_config.get('track_categories', []):
        query = f"{category.get('decade', '')} {category.get('style', '')}"
        apple_music_config['search_queries'].append(query.strip())

    return apple_music_config

# Cross-platform playlist creation
def create_cross_platform_playlist(playlist_config: Dict):
    """
    Create identical playlists across Spotify, YouTube Music, and Apple Music

    Args:
        playlist_config: Universal playlist configuration
    """
    results = {}

    # Apple Music creation
    try:
        apple_music_api = AppleMusicAPI(developer_token=APPLE_MUSIC_TOKEN)
        apple_playlist = create_alex_method_playlist(apple_music_api, playlist_config)
        results['apple_music'] = apple_playlist
        print("✅ Apple Music playlist created successfully")

    except Exception as e:
        results['apple_music'] = {'error': str(e)}
        print(f"❌ Apple Music playlist creation failed: {e}")

    # Additional platform integrations would go here

    return results
```

---

## Summary

This comprehensive Apple Music API documentation provides everything needed to integrate Apple Music into The Alex Method DJ Platform. Key features include:

- **🔐 JWT Authentication**: Secure server-to-server authentication using Apple Developer certificates
- **🎵 Rich Catalog Access**: Search and retrieve from 100+ million songs with comprehensive metadata
- **📝 Playlist Management**: Create, modify, and organize playlists with advanced features
- **👤 User Integration**: Access user libraries, preferences, and listening history
- **📊 Charts & Discovery**: Leverage Apple Music's editorial content and trending data
- **⚡ Performance Optimization**: Built-in rate limiting, caching, and error handling
- **🔄 Cross-Platform Support**: Easy integration with existing Spotify and YouTube Music workflows

The Apple Music API integration enables The Alex Method DJ Platform to provide users with comprehensive multi-platform playlist creation capabilities, ensuring no music lover is left behind regardless of their streaming service preference.

---

## 🚨 FINAL SUMMARY: Apple Music API Limitations

**For Alex Method DJ Platform developers, these restrictions are critical to understand:**

### ❌ **MAJOR LIMITATIONS**
1. **NO Server-Side Playlist Creation** - Cannot create playlists via API
2. **NO Library Write Operations** - Cannot add/remove songs from user libraries
3. **NO Personalized Recommendations** - Limited discovery compared to Spotify
4. **NO Listening History Access** - Cannot analyze user behavior patterns
5. **NO Advanced Audio Features** - Limited track analysis capabilities

### ✅ **AVAILABLE FEATURES (Read-Only)**
1. **Catalog Search** - Full Apple Music catalog search
2. **Metadata Access** - Song, artist, album information
3. **Library Reading** - Access existing user library contents
4. **Playlist Reading** - Access existing playlist contents
5. **Chart Data** - Trending music and editorial content

### 🔧 **RECOMMENDED APPROACH**
- **Use Apple Music API as a METADATA SOURCE ONLY**
- **Export track lists for manual playlist creation**
- **Integrate MusicKit.js for web-based user interactions**
- **Focus on Spotify/YouTube Music for full platform features**

### 🎯 **Implementation Strategy**
```python
# Apple Music should be used ONLY for:
def use_apple_music_for():
    return [
        "Track metadata lookup",
        "Catalog search and discovery",
        "Export generation for manual playlist creation",
        "Cross-platform track matching",
        "Chart and trending data"
    ]

# NOT for:
def do_not_use_apple_music_for():
    return [
        "Automated playlist creation",  # Use Spotify instead
        "Library management",          # Use Spotify instead
        "Personalized recommendations", # Use Spotify instead
        "User behavior analysis",      # Use Spotify instead
        "Complete platform integration" # Use Spotify/YouTube Music
    ]
```

**CONCLUSION**: Apple Music API is **NOT SUITABLE** for full integration with playlist creation platforms. Use it only as a supplementary metadata source while focusing primary features on Spotify and YouTube Music APIs.

---

For technical support and advanced implementation guidance, refer to Apple's official [MusicKit documentation](https://developer.apple.com/documentation/musickit) and the [Apple Music API reference](https://developer.apple.com/documentation/applemusicapi).

**⚠️ CRITICAL LIMITATIONS VERIFIED**: Documentation last updated August 4, 2025, against official Apple Developer documentation confirming playlist creation and library modification restrictions.

---

*Professional DJ music curation tools optimized for Spotify and YouTube Music platforms with Apple Music metadata support.*
