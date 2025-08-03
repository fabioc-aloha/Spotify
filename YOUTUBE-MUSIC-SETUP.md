# YouTube Music Integration Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify YouTube Music API
```bash
python -c "from ytmusicapi import YTMusic; print('✅ YouTube Music API ready')"
```

### 3. Test Enhanced Creator
```bash
python src/platforms/enhanced_youtube_music_creator.py
```

## Cross-Platform Transfer Example

### Prerequisites
- Existing Spotify playlist with Cross-Platform Metadata
- Example: `playlist-configs/dj-live-performances.md`

### Test Transfer Workflow
```bash
python test_workflow.py
```

**Expected Output**:
```
✅ Found playlist config: playlist-configs/dj-live-performances.md
✅ Cross-Platform Metadata found - Spotify processing completed
📈 Extracted 82 tracks from Cross-Platform Metadata
✅ Found 19 YouTube Music matches for first track
🎯 Workflow Status: READY - All components functional
```

## Key Features Verified

- ✅ **ytmusicapi Integration**: Proper music track search (not video search)
- ✅ **Cross-Platform Metadata**: Seamless transfer from Spotify playlists
- ✅ **Smart Matching**: Quality-based track selection with similarity scoring
- ✅ **Quota Efficiency**: Conservative API usage with intelligent caching
- ✅ **No Video Complexity**: YouTube Music handles video mapping automatically

## Troubleshooting

### Import Errors
If you see `ytmusicapi not available`, run:
```bash
pip install ytmusicapi>=1.11.0
```

### No Matches Found
Check that your playlist config has Cross-Platform Metadata:
```markdown
## Cross-Platform Metadata
### Track List (for YouTube Music Transfer)
 1. Track Title - Artist Name (3.1m)
```

### API Quota Issues
Monitor usage with:
```python
quota = creator.get_quota_usage()
print(f"Used: {quota['searches_used']}/{quota['searches_remaining']}")
```

---

*For detailed workflow documentation, see CROSS-PLATFORM-WORKFLOW.md*
