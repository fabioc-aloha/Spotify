# YouTube Music API Documentation
**Universal Playlist Creator - YouTube Music Integration**

---

## 🎯 **Overview**

This documentation covers the YouTube Data API v3 integration for creating music playlists through the Universal Playlist Creator. YouTube Music support enables video-based playlist creation with music-focused content curation.

### **Key Features**
- 🎵 **Music Video Discovery**: Search and filter for official music videos
- 🎬 **Content Quality Control**: Filter by views, channel verification, and content type
- ⏱️ **Duration Targeting**: Precise playlist timing with ±10% accuracy
- 🔐 **OAuth2 Authentication**: Secure user authorization for playlist management
- 🎭 **Video Type Filtering**: Music videos, live performances, official audio
- 📊 **Analytics Integration**: View counts, engagement metrics, and popularity

---

## 🚀 **Getting Started**

Getting started with YouTube Music integration requires setting up Google Cloud Console access and configuring OAuth 2.0 authentication. Unlike Spotify's straightforward app registration, YouTube API access involves creating a Google Cloud project, enabling the YouTube Data API v3, and setting up both API keys for search operations and OAuth credentials for playlist management. This section walks you through the complete setup process, from initial project creation to obtaining the necessary credentials for full YouTube Music functionality.

### **1. Google Cloud Console Setup**

#### **Create Project & Enable API**
```bash
# 1. Go to Google Cloud Console
https://console.cloud.google.com/

# 2. Create new project or select existing
# 3. Enable YouTube Data API v3
APIs & Services > Library > "YouTube Data API v3" > Enable
```

#### **Create Credentials**
```bash
# API Key (for search operations)
APIs & Services > Credentials > "Create Credentials" > "API Key"

# OAuth 2.0 Client ID (for playlist management)
APIs & Services > Credentials > "Create Credentials" > "OAuth client ID"
```

#### **OAuth Consent Screen**
```bash
# Configure OAuth consent screen
APIs & Services > OAuth consent screen
- Application name: "Universal Playlist Creator"
- User support email: your-email@example.com
- Scopes: Add YouTube API scopes
- Test users: Add your email for testing
```

### **2. Environment Configuration**

#### **Add to .env file**
```bash
# YouTube Music API Credentials
YOUTUBE_API_KEY=your_youtube_api_key_here
YOUTUBE_CLIENT_ID=your_youtube_client_id_here
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret_here
YOUTUBE_CLIENT_CONFIG=client_secret.json
```

#### **Download OAuth Configuration**
```bash
# Download client_secret.json from Google Cloud Console
# Place in project root directory
# Ensure it's added to .gitignore for security
```

### **3. Install Dependencies**
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

## 🔑 **Authentication**

YouTube API authentication is more complex than Spotify's approach, requiring a dual authentication strategy. For read-only operations like searching for videos, you can use API keys, but for creating and managing playlists, OAuth 2.0 authentication is mandatory. This section covers both authentication methods, including the complete OAuth flow implementation, token management, credential refresh strategies, and proper scope configuration. Understanding this authentication system is crucial for seamless integration with YouTube's services.

### **OAuth 2.0 Flow**

#### **Required Scopes**
```python
SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',  # Full YouTube access
    'https://www.googleapis.com/auth/youtube'            # YouTube access
]
```

#### **Authentication Process**
```python
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def authenticate_youtube():
    """Authenticate with YouTube API using OAuth2."""
    creds = None
    token_file = 'youtube_token.json'

    # Load existing credentials
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # Refresh or obtain new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save credentials for future use
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    return build('youtube', 'v3', credentials=creds)
```

### **API Key Authentication**
```python
from googleapiclient.discovery import build

def build_youtube_service():
    """Build YouTube service with API key."""
    api_key = os.getenv('YOUTUBE_API_KEY')
    return build('youtube', 'v3', developerKey=api_key)
```

---

## 🔍 **Content Search & Discovery**

YouTube's content discovery system offers powerful search capabilities specifically designed for finding music videos, live performances, and official audio content. This section demonstrates how to leverage YouTube's search API with music-specific filters, category targeting, and advanced query parameters. You'll learn to extract detailed video metadata, parse YouTube's unique ISO 8601 duration format, and implement efficient batch operations to minimize API quota usage while maximizing content discovery accuracy.

### **Music Video Search**

#### **Basic Search Query**
```python
def search_music_videos(query, max_results=50):
    """Search for music videos on YouTube."""
    search_response = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        videoCategoryId='10',        # Music category
        order='relevance',           # or 'viewCount', 'rating'
        maxResults=min(max_results, 50),
        regionCode='US',             # Optional: target region
        relevanceLanguage='en'       # Optional: language preference
    ).execute()

    return search_response['items']
```

#### **Enhanced Search with Filters**
```python
def enhanced_music_search(query, filters=None):
    """Enhanced search with music-specific filters."""
    search_params = {
        'q': query,
        'part': 'snippet',
        'type': 'video',
        'videoCategoryId': '10',  # Music category
        'order': 'relevance',
        'maxResults': 50
    }

    # Apply optional filters
    if filters:
        if 'duration' in filters:
            search_params['videoDuration'] = filters['duration']  # short, medium, long
        if 'definition' in filters:
            search_params['videoDefinition'] = filters['definition']  # high, standard
        if 'published_after' in filters:
            search_params['publishedAfter'] = filters['published_after']  # RFC 3339

    return youtube.search().list(**search_params).execute()
```

### **Video Details & Metadata**

#### **Get Detailed Video Information**
```python
def get_video_details(video_ids):
    """Get detailed information for videos."""
    videos_response = youtube.videos().list(
        part='snippet,contentDetails,statistics,status',
        id=','.join(video_ids)
    ).execute()

    video_details = []
    for video in videos_response['items']:
        details = {
            'id': video['id'],
            'title': video['snippet']['title'],
            'description': video['snippet']['description'],
            'channel_title': video['snippet']['channelTitle'],
            'channel_id': video['snippet']['channelId'],
            'published_at': video['snippet']['publishedAt'],
            'duration': video['contentDetails']['duration'],
            'view_count': int(video['statistics'].get('viewCount', 0)),
            'like_count': int(video['statistics'].get('likeCount', 0)),
            'comment_count': int(video['statistics'].get('commentCount', 0)),
            'thumbnail_url': video['snippet']['thumbnails']['high']['url']
        }
        video_details.append(details)

    return video_details
```

#### **Parse Video Duration**
```python
import re

def parse_youtube_duration(iso_duration):
    """Parse ISO 8601 duration format (PT4M33S) to minutes."""
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, iso_duration)

    if not match:
        return 0.0

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return hours * 60 + minutes + seconds / 60

# Example usage
duration_iso = "PT4M33S"  # 4 minutes 33 seconds
duration_minutes = parse_youtube_duration(duration_iso)  # 4.55
```

---

## 🎵 **Music-Focused Content Filtering**

YouTube's vast content library requires sophisticated filtering to identify high-quality music content suitable for playlists. This section implements intelligent algorithms to distinguish genuine music videos from tutorials, reactions, and low-quality uploads. You'll learn to analyze video titles, descriptions, and channel metadata to filter for official music videos, live performances, and verified artist content while excluding fan-made compilations, covers, and non-music content that could compromise playlist quality.

### **Content Quality Filters**

#### **Music Content Detection**
```python
def is_music_content(video):
    """Determine if video is music-focused content."""
    snippet = video['snippet']
    title = snippet['title'].lower()
    description = snippet.get('description', '').lower()
    channel = snippet['channelTitle'].lower()

    # Positive indicators
    music_keywords = [
        'official', 'music video', 'official video', 'official audio',
        'live performance', 'acoustic', 'cover', 'remix', 'soundtrack',
        'album', 'single', 'ep', 'live', 'concert', 'session'
    ]

    # Negative indicators
    exclude_keywords = [
        'tutorial', 'lesson', 'how to', 'reaction', 'review', 'analysis',
        'compilation', 'mashup', 'nightcore', 'slowed', 'reverb',
        'gameplay', 'walkthrough', 'trailer', 'interview'
    ]

    # Check for music keywords
    music_score = sum(1 for keyword in music_keywords
                     if keyword in title or keyword in description)

    # Check for exclude keywords
    exclude_score = sum(1 for keyword in exclude_keywords
                       if keyword in title or keyword in description)

    return music_score > 0 and exclude_score == 0
```

#### **Channel Verification & Quality**
```python
def check_channel_quality(channel_id):
    """Check channel quality indicators."""
    channel_response = youtube.channels().list(
        part='snippet,statistics,status',
        id=channel_id
    ).execute()

    if not channel_response['items']:
        return False

    channel = channel_response['items'][0]
    stats = channel['statistics']

    # Quality thresholds
    min_subscribers = 1000
    min_video_count = 5

    subscriber_count = int(stats.get('subscriberCount', 0))
    video_count = int(stats.get('videoCount', 0))

    # Check verification status (if available)
    is_verified = channel.get('status', {}).get('longUploadsStatus') == 'allowed'

    return (subscriber_count >= min_subscribers and
            video_count >= min_video_count)
```

#### **View Count & Engagement Filters**
```python
def filter_by_engagement(videos, min_views=1000, min_like_ratio=0.01):
    """Filter videos by engagement metrics."""
    filtered_videos = []

    for video in videos:
        stats = video.get('statistics', {})
        view_count = int(stats.get('viewCount', 0))
        like_count = int(stats.get('likeCount', 0))

        # Skip videos with low view counts
        if view_count < min_views:
            continue

        # Calculate like ratio (likes per view)
        like_ratio = like_count / view_count if view_count > 0 else 0

        # Skip videos with poor engagement
        if like_ratio < min_like_ratio:
            continue

        filtered_videos.append(video)

    return filtered_videos
```

### **Duration-Based Filtering**
```python
def filter_by_duration(videos, min_duration=1.0, max_duration=10.0):
    """Filter videos by duration range (in minutes)."""
    filtered_videos = []

    for video in videos:
        duration_iso = video['contentDetails']['duration']
        duration_minutes = parse_youtube_duration(duration_iso)

        # Skip videos outside duration range
        if min_duration <= duration_minutes <= max_duration:
            filtered_videos.append(video)

    return filtered_videos
```

---

## 📋 **Playlist Management**

YouTube playlist management provides comprehensive control over video collections with support for public, private, and unlisted playlists. This section covers the complete playlist lifecycle from creation to analytics, including privacy settings, batch video operations, and playlist metadata management. You'll learn to handle YouTube's specific playlist structure, manage video ordering, and implement robust error handling for content that may become unavailable due to copyright claims or regional restrictions.

### **Create Playlist**

#### **Basic Playlist Creation**
```python
def create_youtube_playlist(title, description, privacy='public'):
    """Create a new YouTube playlist."""
    playlist_response = youtube.playlists().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': title,
                'description': description,
                'defaultLanguage': 'en'
            },
            'status': {
                'privacyStatus': privacy  # 'public', 'private', 'unlisted'
            }
        }
    ).execute()

    playlist_id = playlist_response['id']
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"

    return {
        'id': playlist_id,
        'url': playlist_url,
        'title': title,
        'privacy': privacy
    }
```

#### **Add Videos to Playlist**
```python
def add_videos_to_playlist(playlist_id, video_ids):
    """Add videos to an existing playlist."""
    added_videos = []

    for video_id in video_ids:
        try:
            playlist_item = youtube.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            ).execute()

            added_videos.append({
                'video_id': video_id,
                'playlist_item_id': playlist_item['id'],
                'position': len(added_videos)
            })

        except Exception as e:
            print(f"Failed to add video {video_id}: {str(e)}")

    return added_videos
```

### **Playlist Analytics & Management**

#### **Get Playlist Information**
```python
def get_playlist_details(playlist_id):
    """Get detailed playlist information."""
    playlist_response = youtube.playlists().list(
        part='snippet,status,contentDetails',
        id=playlist_id
    ).execute()

    if not playlist_response['items']:
        return None

    playlist = playlist_response['items'][0]

    return {
        'id': playlist['id'],
        'title': playlist['snippet']['title'],
        'description': playlist['snippet']['description'],
        'published_at': playlist['snippet']['publishedAt'],
        'channel_title': playlist['snippet']['channelTitle'],
        'item_count': playlist['contentDetails']['itemCount'],
        'privacy_status': playlist['status']['privacyStatus']
    }
```

#### **Get Playlist Videos**
```python
def get_playlist_videos(playlist_id, max_results=50):
    """Get all videos in a playlist."""
    videos = []
    next_page_token = None

    while True:
        playlist_items = youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=playlist_id,
            maxResults=min(max_results, 50),
            pageToken=next_page_token
        ).execute()

        for item in playlist_items['items']:
            video_info = {
                'video_id': item['contentDetails']['videoId'],
                'title': item['snippet']['title'],
                'channel_title': item['snippet']['videoOwnerChannelTitle'],
                'position': item['snippet']['position'],
                'added_at': item['snippet']['publishedAt']
            }
            videos.append(video_info)

        next_page_token = playlist_items.get('nextPageToken')
        if not next_page_token or len(videos) >= max_results:
            break

    return videos
```

---

## ⚡ **API Quotas & Rate Limiting**

YouTube API operates on a strict quota system with a default limit of 10,000 units per day, making efficient quota management essential for production applications. Each API operation consumes different amounts of quota units, with search operations being particularly expensive at 100 units per request. This section provides comprehensive strategies for quota tracking, batch operations optimization, and implementing intelligent caching to maximize the value of your daily quota allocation while maintaining responsive application performance.

### **Understanding YouTube API Quotas**

#### **Daily Quota Limits**
```python
# YouTube Data API v3 Default Quotas (per day)
DEFAULT_QUOTA = 10000  # units per day

# Operation Costs (in quota units)
QUOTA_COSTS = {
    'search': 100,           # per search request
    'videos.list': 1,        # per video requested
    'playlists.insert': 50,  # create playlist
    'playlistItems.insert': 50,  # add video to playlist
    'playlists.list': 1,     # get playlist info
    'playlistItems.list': 1, # get playlist videos
    'channels.list': 1       # get channel info
}
```

#### **Quota Management Strategy**
```python
class QuotaManager:
    """Manage YouTube API quota usage."""

    def __init__(self, daily_limit=10000):
        self.daily_limit = daily_limit
        self.used_quota = 0
        self.reset_time = None

    def check_quota(self, operation, count=1):
        """Check if operation can be performed within quota."""
        cost = QUOTA_COSTS.get(operation, 1) * count
        return (self.used_quota + cost) <= self.daily_limit

    def use_quota(self, operation, count=1):
        """Record quota usage for operation."""
        cost = QUOTA_COSTS.get(operation, 1) * count
        self.used_quota += cost
        return cost

    def get_remaining_quota(self):
        """Get remaining quota for the day."""
        return max(0, self.daily_limit - self.used_quota)
```

#### **Efficient Batch Operations**
```python
def batch_video_lookup(video_ids, batch_size=50):
    """Efficiently lookup video details in batches."""
    all_videos = []

    # Process videos in batches to minimize API calls
    for i in range(0, len(video_ids), batch_size):
        batch = video_ids[i:i + batch_size]

        videos_response = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=','.join(batch)
        ).execute()

        all_videos.extend(videos_response['items'])

        # Track quota usage
        quota_manager.use_quota('videos.list', len(batch))

    return all_videos
```

---

## 🛡️ **Error Handling & Best Practices**

YouTube API integration requires robust error handling due to the dynamic nature of video content, regional restrictions, and quota limitations. Videos can become unavailable, private, or geo-blocked at any time, and quota exhaustion can interrupt operations unexpectedly. This section implements comprehensive error handling strategies, retry mechanisms with exponential backoff, and content validation protocols to ensure your application gracefully handles the various failure scenarios unique to YouTube's platform while maintaining a smooth user experience.

### **Common API Errors**

#### **Error Types & Solutions**
```python
from googleapiclient.errors import HttpError
import time
import random

def handle_youtube_api_error(error):
    """Handle common YouTube API errors."""
    error_details = error.resp.get('content-type', '')

    if error.resp.status == 403:
        # Quota exceeded or forbidden
        if 'quotaExceeded' in str(error):
            print("❌ YouTube API quota exceeded. Try again tomorrow.")
            return 'quota_exceeded'
        else:
            print("❌ Access forbidden. Check your API credentials.")
            return 'forbidden'

    elif error.resp.status == 404:
        print("❌ Resource not found (video may be deleted or private).")
        return 'not_found'

    elif error.resp.status == 400:
        print("❌ Bad request. Check your request parameters.")
        return 'bad_request'

    elif error.resp.status >= 500:
        print("❌ YouTube API server error. Retrying...")
        return 'server_error'

    else:
        print(f"❌ Unknown error: {error}")
        return 'unknown_error'
```

#### **Retry Strategy with Exponential Backoff**
```python
def youtube_api_call_with_retry(api_call, max_retries=3):
    """Execute YouTube API call with retry logic."""
    for attempt in range(max_retries):
        try:
            return api_call()

        except HttpError as e:
            error_type = handle_youtube_api_error(e)

            if error_type in ['quota_exceeded', 'forbidden']:
                # Don't retry quota or permission errors
                raise e

            elif error_type == 'server_error' and attempt < max_retries - 1:
                # Retry server errors with exponential backoff
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying in {wait_time:.1f} seconds...")
                time.sleep(wait_time)

            else:
                # Last attempt or non-retryable error
                raise e

    raise Exception("Max retries exceeded")
```

### **Content Validation**

#### **Video Availability Check**
```python
def validate_video_availability(video_id):
    """Check if video is available and accessible."""
    try:
        video_response = youtube.videos().list(
            part='status,contentDetails',
            id=video_id
        ).execute()

        if not video_response['items']:
            return False, "Video not found"

        video = video_response['items'][0]
        status = video['status']

        # Check various availability factors
        if not status.get('uploadStatus') == 'processed':
            return False, "Video not fully processed"

        if status.get('privacyStatus') == 'private':
            return False, "Video is private"

        if status.get('embeddable') == False:
            return False, "Video not embeddable"

        return True, "Video available"

    except HttpError as e:
        return False, f"API error: {str(e)}"
```

---

## 📊 **Analytics & Reporting**

YouTube's rich analytics ecosystem provides detailed insights into playlist performance, video engagement, and content quality metrics. This section demonstrates how to leverage YouTube's analytics data to assess playlist success, analyze viewer engagement patterns, and generate comprehensive reports on content quality. You'll learn to track key performance indicators like view counts, like ratios, and duration metrics to optimize playlist creation and understand which content resonates most with audiences.

### **Playlist Performance Metrics**

#### **Get Playlist Analytics**
```python
def analyze_playlist_performance(playlist_id):
    """Analyze playlist performance metrics."""
    videos = get_playlist_videos(playlist_id)

    if not videos:
        return None

    # Get detailed video information
    video_ids = [v['video_id'] for v in videos]
    detailed_videos = batch_video_lookup(video_ids)

    # Calculate metrics
    total_views = sum(int(v['statistics'].get('viewCount', 0))
                     for v in detailed_videos)
    total_likes = sum(int(v['statistics'].get('likeCount', 0))
                     for v in detailed_videos)
    total_duration = sum(parse_youtube_duration(v['contentDetails']['duration'])
                        for v in detailed_videos)

    avg_views = total_views / len(detailed_videos) if detailed_videos else 0
    avg_likes = total_likes / len(detailed_videos) if detailed_videos else 0

    return {
        'video_count': len(videos),
        'total_duration_minutes': total_duration,
        'total_views': total_views,
        'total_likes': total_likes,
        'average_views_per_video': avg_views,
        'average_likes_per_video': avg_likes,
        'engagement_rate': (total_likes / total_views * 100) if total_views > 0 else 0
    }
```

### **Content Quality Report**
```python
def generate_content_quality_report(video_ids):
    """Generate quality report for video selection."""
    videos = batch_video_lookup(video_ids)

    quality_metrics = {
        'total_videos': len(videos),
        'music_content_ratio': 0,
        'average_view_count': 0,
        'average_duration': 0,
        'verified_channels': 0,
        'high_quality_videos': 0
    }

    music_videos = 0
    total_views = 0
    total_duration = 0
    verified_count = 0
    high_quality_count = 0

    for video in videos:
        # Check if music content
        if is_music_content(video):
            music_videos += 1

        # Accumulate metrics
        view_count = int(video['statistics'].get('viewCount', 0))
        total_views += view_count

        duration = parse_youtube_duration(video['contentDetails']['duration'])
        total_duration += duration

        # Check channel quality
        channel_id = video['snippet']['channelId']
        if check_channel_quality(channel_id):
            verified_count += 1

        # High quality threshold (example: >10k views, >3 minutes)
        if view_count > 10000 and duration > 3:
            high_quality_count += 1

    # Calculate ratios
    if videos:
        quality_metrics.update({
            'music_content_ratio': music_videos / len(videos),
            'average_view_count': total_views / len(videos),
            'average_duration': total_duration / len(videos),
            'verified_channels': verified_count,
            'high_quality_videos': high_quality_count
        })

    return quality_metrics
```

---

## 🎯 **Configuration Examples**

YouTube Music playlist configuration extends beyond basic search queries to include sophisticated content filtering, channel verification preferences, and video quality thresholds. This section provides practical examples of configuration files optimized for YouTube's unique content ecosystem, demonstrating how to specify video types, exclude unwanted content categories, set engagement thresholds, and configure duration filters to create high-quality, music-focused playlists that leverage YouTube's vast catalog effectively.

### **Playlist Configuration for YouTube Music**

#### **Enhanced Markdown Configuration**
```markdown
# Douglas Gaming - YouTube Music Edition

**Description**: Epic gaming music with official videos and live performances
**Target Duration**: 60 minutes
**Platform**: youtube
**Privacy**: public

## YouTube Specific Settings
- **Video Types**: [music_video, live_performance, official_audio]
- **Exclude Types**: [tutorial, reaction, compilation, fan_made]
- **Min Views**: 10000
- **Max Duration**: 8 minutes
- **Channel Types**: [verified, official_artist, music_label]
- **Upload Recency**: last_3_years

## Search Queries

### Retro Gaming Soundtracks
1. **Undertale soundtrack official**
   - *Search*: "Undertale soundtrack official Toby Fox"

2. **Megalovania official video**
   - *Search*: "Megalovania official music video"

3. **Nintendo music orchestra**
   - *Search*: "Nintendo music live orchestra concert"

4. **Zelda symphony**
   - *Search*: "Legend of Zelda symphony official"

### Chiptune & 8-bit
5. **FEZ soundtrack official**
   - *Search*: "FEZ soundtrack Disasterpeace official"

6. **Shovel Knight music**
   - *Search*: "Shovel Knight soundtrack official Jake Kaufman"
```

### **Python Integration Example**
```python
def create_youtube_music_playlist(config_file):
    """Create YouTube Music playlist from configuration."""

    # Load configuration
    config = load_playlist_config(config_file)

    # Initialize YouTube Music creator
    creator = YouTubeMusicPlaylistCreator()

    # Create playlist with enhanced settings
    playlist_id = creator.create_playlist(
        name=config['metadata']['name'],
        description=config['metadata']['description'],
        privacy=config['metadata'].get('privacy', 'public')
    )

    # Search and filter videos
    videos = []
    for query in config['search_queries']:
        search_results = creator.search_content(query, limit=20)
        filtered_videos = creator.filter_music_content(search_results)
        videos.extend(filtered_videos)

    # Apply duration targeting
    target_duration = creator.parse_target_duration(
        config['metadata']['target_duration']
    )

    final_videos = creator.apply_duration_targeting(videos, target_duration)

    # Add videos to playlist
    video_ids = [video['id'] for video in final_videos]
    creator.add_videos_to_playlist(playlist_id, video_ids)

    return {
        'playlist_id': playlist_id,
        'video_count': len(final_videos),
        'total_duration': sum(video['duration'] for video in final_videos),
        'playlist_url': f"https://www.youtube.com/playlist?list={playlist_id}"
    }
```

---

## 🚨 **Important Considerations**

### **API Limitations**
- **Daily Quota**: 10,000 units per day (monitor usage carefully)
- **Search Results**: Maximum 50 results per search request
- **Batch Operations**: Maximum 50 items per batch request
- **Rate Limiting**: Respect API rate limits to avoid throttling

### **Content Availability**
- **Regional Restrictions**: Videos may not be available in all regions
- **Copyright Claims**: Music videos may be blocked or restricted
- **Privacy Settings**: Private/unlisted videos won't appear in search
- **Age Restrictions**: Some content may require age verification

### **Best Practices**
- **Quota Management**: Implement efficient batching and caching
- **Error Handling**: Graceful handling of unavailable content
- **Content Validation**: Verify video availability before adding to playlists
- **User Experience**: Provide clear feedback during playlist creation
- **Security**: Protect API credentials and user OAuth tokens

---

## 📚 **Additional Resources**

### **Official Documentation**
- [YouTube Data API v3 Reference](https://developers.google.com/youtube/v3/docs)
- [YouTube API Client Libraries](https://developers.google.com/youtube/v3/libraries)
- [OAuth 2.0 for YouTube](https://developers.google.com/youtube/v3/guides/auth/installed-apps)

### **Useful Tools**
- [YouTube API Explorer](https://developers.google.com/youtube/v3/docs/search/list)
- [Google Cloud Console](https://console.cloud.google.com/)
- [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)

### **Community Resources**
- [YouTube Data API Stack Overflow](https://stackoverflow.com/questions/tagged/youtube-data-api)
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)

---

**Documentation Version**: 1.0
**Last Updated**: August 2, 2025
**Universal Playlist Creator**: YouTube Music Integration Complete
