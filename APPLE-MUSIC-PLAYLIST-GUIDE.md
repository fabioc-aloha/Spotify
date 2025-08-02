# Apple Music Playlist Creation Guide - Alex Method

A comprehensive tutorial for creating Apple Music playlists programmatically using the Apple Music API (MusicKit), with user approval workflow.

## 🍎 Overview

This guide teaches you how to create Apple Music playlists using the same systematic approach as Spotify, but adapted for Apple's ecosystem. **Important**: Apple Music API requires Apple Developer Program membership ($99/year) and more complex authentication.

## 📋 Prerequisites

### Apple Developer Requirements
1. **Apple Developer Program Membership** ($99/year)
   - Required for Apple Music API access
   - Sign up at: https://developer.apple.com

2. **MusicKit Credentials**
   - Team ID (from Apple Developer account)
   - Key ID (from created MusicKit key)
   - Private Key (.p8 file download)

3. **Python Dependencies**
```bash
pip install requests PyJWT cryptography
```

## 🚀 Quick Start

### Step 1: Get Apple Music API Credentials

1. **Join Apple Developer Program**
   - Go to https://developer.apple.com
   - Enroll in the program ($99/year)
   - Wait for approval (usually 24-48 hours)

2. **Create MusicKit Key**
   - Go to https://developer.apple.com/account/resources/authkeys/list
   - Click "Create a key"
   - Enable "MusicKit" service
   - Download the .p8 private key file
   - Note your Key ID and Team ID

3. **Set Up Credentials**
```python
TEAM_ID = "ABC123DEF4"  # Your 10-character Team ID
KEY_ID = "XYZ789"       # Your Key ID from the created key
PRIVATE_KEY_PATH = "path/to/AuthKey_XYZ789.p8"  # Downloaded .p8 file
```

### Step 2: Basic Usage with Approval Workflow

```python
from apple_music_playlist_tutorial import AppleMusicPlaylistCreator

# Initialize creator
creator = AppleMusicPlaylistCreator(TEAM_ID, KEY_ID, PRIVATE_KEY_PATH)

# Note: User authentication required for playlist creation
# user_token = get_user_music_token()  # Implement user auth
# creator.set_user_token(user_token)

# Create playlist with approval workflow
workout_tracks = [
    "Eminem - Till I Collapse",
    "The Prodigy - Spitfire",
    "Skrillex - Bangarang"
]

# This will preview tracks and ask for approval before creating
playlist = creator.create_playlist_with_approval("High Energy Workout", workout_tracks)
```

## 🎵 Core Features

### 1. Preview Before Creation
```python
# Preview what tracks will be found
found_tracks, not_found = creator.preview_playlist_content(track_list)

# Shows:
# ✅ Found tracks with artist, song, album, duration
# ❌ Tracks not found in Apple Music catalog
# 📊 Summary statistics
```

### 2. User Approval Workflow
```python
# All playlist creation requires explicit user approval:
# 1. Preview tracks found/not found
# 2. Ask "Create playlist with X tracks? (yes/no)"
# 3. Only create if user types 'yes'
# 4. Confirm successful creation
```

### 3. Smart Themed Playlists
```python
# Pre-curated playlists by theme with approval
themes = ['workout', 'chill', 'focus', 'party']
playlist = creator.generate_smart_playlist("workout")
```

## 🔑 Authentication Challenge

**Major Difference from Spotify**: Apple Music requires more complex user authentication.

### User Token Requirements
Apple Music API needs two tokens:
1. **Developer JWT Token** (handled automatically)
2. **User Music Token** (requires user login)

```python
# You need to implement user authentication
# Options:
# 1. MusicKit JS (web-based)
# 2. StoreKit (iOS/macOS native)
# 3. Third-party auth services

# Example placeholder:
def get_user_music_token():
    # Implement user authentication flow
    # Return user's music token
    pass

user_token = get_user_music_token()
creator.set_user_token(user_token)
```

## 📊 API Capabilities Comparison

| Feature | Apple Music API | Spotify API |
|---------|----------------|-------------|
| **Authentication** | Complex (2 tokens) | Simple OAuth |
| **Cost** | $99/year Developer Program | Free developer account |
| **Audio Analysis** | Limited | Comprehensive (energy, tempo, etc.) |
| **Catalog Access** | Full Apple Music catalog | Full Spotify catalog |
| **Playlist Creation** | Full control | Full control |
| **User Data** | Requires explicit user auth | OAuth handles it |

## 🎯 Available Playlist Themes

### High-Energy Workout
- **Focus**: Intense, motivating tracks
- **BPM Range**: 120-180
- **Examples**: Eminem, Rage Against The Machine, Skrillex

### Chill Vibes
- **Focus**: Relaxed, atmospheric music
- **BPM Range**: 60-100
- **Examples**: Bonobo, Massive Attack, Tycho

### Focus & Concentration
- **Focus**: Instrumental, minimal distraction
- **BPM Range**: 80-120
- **Examples**: Max Richter, Nils Frahm, Jon Hopkins

### Party Mix
- **Focus**: Upbeat, danceable tracks
- **BPM Range**: 110-130
- **Examples**: Dua Lipa, Calvin Harris, Bruno Mars

## 🛠️ Interactive Mode

```python
# Run the interactive playlist creator
interactive_apple_music_creator()

# Features:
# • Menu-driven theme selection
# • Preview all tracks before creation
# • User approval for each playlist
# • Automatic error handling
```

## 📝 Complete Example

```python
#!/usr/bin/env python3
from apple_music_playlist_tutorial import AppleMusicPlaylistCreator

# Your Apple Music credentials
TEAM_ID = "your_team_id_here"
KEY_ID = "your_key_id_here"
PRIVATE_KEY_PATH = "path/to/AuthKey_KEY_ID.p8"

try:
    # Initialize Apple Music creator
    creator = AppleMusicPlaylistCreator(TEAM_ID, KEY_ID, PRIVATE_KEY_PATH)

    # Note: Implement user authentication
    # user_token = get_user_music_token()
    # creator.set_user_token(user_token)

    # Create themed playlist with approval
    chill_playlist = creator.generate_smart_playlist("chill")

    if chill_playlist:
        print(f"✅ Created: {chill_playlist['attributes']['name']}")

        # Show user's playlists
        creator.get_user_playlists()

except Exception as e:
    print(f"❌ Error: {e}")
```

## 🚧 Implementation Steps

### 1. Developer Setup
- [ ] Join Apple Developer Program ($99/year)
- [ ] Create MusicKit key with proper permissions
- [ ] Download .p8 private key file
- [ ] Get Team ID and Key ID

### 2. Authentication Implementation
- [ ] Choose authentication method (MusicKit JS recommended)
- [ ] Implement user login flow
- [ ] Handle user music token securely
- [ ] Test authentication with Apple Music

### 3. Playlist Creation
- [ ] Test track search functionality
- [ ] Implement preview system
- [ ] Add user approval workflow
- [ ] Test playlist creation and validation

### 4. Advanced Features
- [ ] Add harmonic mixing (limited by API)
- [ ] Implement cross-platform sync
- [ ] Add user preference learning
- [ ] Integrate with Alex's DJ mastery system

## 🎚️ Alex's Advanced Techniques (Adapted)

### Energy Flow Management
```python
# Limited compared to Spotify, but basic analysis possible
features = creator.analyze_track_features(track_ids)

# Apple Music provides:
# • Basic track information
# • Limited audio characteristics
# • Recommendation: Use iTunes/Music app for detailed analysis
```

### Cross-Platform Integration
```python
# Combine with Spotify data for comprehensive analysis
spotify_features = spotify_creator.analyze_playlist_energy(playlist_id)
apple_playlist = apple_creator.create_playlist_with_approval(theme, tracks)

# Best of both worlds:
# • Spotify: Detailed audio analysis
# • Apple Music: Different catalog, integration with Apple ecosystem
```

## ⚠️ Important Limitations

### 1. Cost Barrier
- Apple Developer Program: $99/year (vs. Spotify's free)
- Additional complexity for hobby projects

### 2. Authentication Complexity
- Requires two-token system
- User authentication more complex than Spotify OAuth
- Need to implement user login flow

### 3. API Limitations
- Limited audio analysis features
- No detailed energy/tempo/valence data like Spotify
- Fewer programmatic customization options

### 4. Development Overhead
- More setup required than Spotify
- Platform-specific considerations
- Requires ongoing Developer Program membership

## 🎵 When to Choose Apple Music API

**Choose Apple Music when:**
- Target audience primarily uses Apple devices
- Need integration with Apple ecosystem
- Want access to Apple Music exclusive content
- Building commercial iOS/macOS applications

**Choose Spotify when:**
- Need detailed audio analysis features
- Want simpler authentication flow
- Building cross-platform applications
- Prototype or learning projects

## 🔄 Migration Between Platforms

Both tutorials use the same track list format and approval workflow, making it easy to support both platforms:

```python
# Same track lists work for both
tracks = ["Artist - Song", "Another - Track"]

# Same approval workflow
spotify_playlist = spotify_creator.create_playlist_with_approval(theme, tracks)
apple_playlist = apple_creator.create_playlist_with_approval(theme, tracks)
```

## 📚 Next Steps

1. **Start with Spotify** for learning (easier setup)
2. **Add Apple Music** when you need Apple ecosystem integration
3. **Combine both** for maximum reach and feature completeness
4. **Integrate with Alex's DJ system** for advanced harmonic mixing

---

*Created with the Alex Method - Systematic learning through practical application with user-controlled approval workflows*
