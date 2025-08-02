#!/usr/bin/env python3
"""
Test YouTube Music Enhanced Content Filtering
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from platforms.youtube_creator import YouTubePlaylistCreator

def test_music_filtering():
    """Test the enhanced music content filtering."""
    print("🎵 Testing YouTube Music Enhanced Content Filtering")
    print("=" * 50)
    
    try:
        # Initialize YouTube creator
        creator = YouTubePlaylistCreator()
        
        # Test with a small search for coffee shop music
        print("🔍 Searching for coffee shop music content...")
        results = creator.search_content("coffee shop jazz music", max_results=10)
        
        print(f"✅ Found {len(results)} music-filtered results")
        
        # Display results
        for i, video in enumerate(results[:5]):
            snippet = video['snippet']
            title = snippet['title']
            channel = snippet['channelTitle']
            duration = video.get('contentDetails', {}).get('duration', 'Unknown')
            
            print(f"  {i+1}. {title}")
            print(f"     Channel: {channel}")
            print(f"     Duration: {duration}")
            print()
        
        print("🎉 Enhanced music filtering test completed!")
        
    except Exception as e:
        print(f"❌ Error testing music filtering: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_music_filtering()
