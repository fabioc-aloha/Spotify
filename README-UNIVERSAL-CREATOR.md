# Universal Spotify Playlist Creator - Alex Method

A standardized playlist creation system that uses markdown configuration files to create custom Spotify playlists with sophisticated filtering, categorization, and curation capabilities.

## 🚀 Quick Start

```bash
# Create a playlist using a configuration file
python universal_playlist_creator.py coffee-shop.md

# Or with full path
python universal_playlist_creator.py playlist-configs/ketamine-therapy.md
```

## 📁 Project Structure

```
📦 Spotify Playlist Creator
├── 🎵 universal_playlist_creator.py    # Main standardized creator
├── 📋 playlist-configs/                 # Configuration files
│   ├── coffee-shop.md                   # ☕ Coffee shop vibes
│   ├── ketamine-therapy.md              # 🧘 Therapeutic sessions
│   └── dj-live-performances.md          # 🎧 Live DJ sets
├── 🧪 test_universal_creator.py         # Test script
├── 📚 Legacy creators/                  # Original specific creators
│   ├── coffee_shop_playlist.py
│   ├── ketamine_therapy_playlist.py
│   └── dj_live_performances_playlist.py
└── 📖 README-UNIVERSAL-CREATOR.md       # This file
```

## 🎯 Configuration File Format

Each playlist is defined by a markdown file with structured sections:

### Basic Structure

```markdown
# Playlist Name Configuration

## Metadata
- **Name**: Your Playlist Name
- **Description**: Playlist description for Spotify
- **Duration Target**: 90 minutes
- **Privacy**: Public/Private
- **Emoji**: 🎵

## Search Queries
- acoustic coffee shop
- chill indie folk
- lo-fi coffee

## Track Filters
### Include Keywords
- acoustic
- indie
- chill

### Exclude Keywords
- remix
- electronic
- metal

### Duration Preferences
- **Minimum**: 2 minutes
- **Maximum**: 6 minutes
- **Preferred**: 3-4 minutes

## Track Limits
- **Per Query**: 10
- **Total Tracks**: 40
- **Popularity Threshold**: 20

## Special Instructions
- Focus on organic instruments
- Avoid jarring tempo changes
- Create relaxed atmosphere
```

### Advanced: Categories with Time Targets

For complex playlists like therapeutic sessions:

```markdown
## Track Categories
### Foundation (45 minutes)
- Deep ambient start
- Queries: ambient drone, deep soundscapes

### Processing (30 minutes)
- Emotional work
- Queries: neoclassical piano, therapeutic classical
```

## 🎵 Available Configurations

### ☕ Coffee Shop (`coffee-shop.md`)
- **Duration**: 90 minutes
- **Style**: Acoustic, indie folk, jazz
- **Mood**: Relaxed, conversational
- **Perfect for**: Work, study, cafe visits

### 🧘 Ketamine Therapy (`ketamine-therapy.md`)
- **Duration**: 180 minutes (3 hours)
- **Style**: Ambient, therapeutic, healing
- **Categories**: Foundation → Grounding → Processing → Transcendence → Integration
- **Perfect for**: Medical therapeutic sessions (supervised)

### 🎧 DJ Live Performances (`dj-live-performances.md`)
- **Duration**: 120 minutes
- **Style**: Electronic, house, techno, trance
- **Focus**: Live recordings, festival sets
- **Perfect for**: Electronic music enthusiasts

## 🛠️ Creating Your Own Configuration

1. **Copy a template**: Start with an existing config file
2. **Modify metadata**: Change name, description, duration
3. **Update search queries**: Add your preferred search terms
4. **Adjust filters**: Set include/exclude keywords
5. **Set limits**: Control track count and popularity
6. **Add special instructions**: Describe the desired atmosphere

### Example: Gaming Playlist

```markdown
# Gaming Focus Playlist Configuration

## Metadata
- **Name**: 🎮 Epic Gaming Focus - Alex Method
- **Description**: High-energy instrumental tracks for gaming sessions
- **Duration Target**: 120 minutes
- **Privacy**: Public
- **Emoji**: 🎮

## Search Queries
- epic instrumental gaming
- cinematic orchestral
- electronic gaming music
- synthwave retro gaming
- epic trailer music

## Track Filters
### Include Keywords
- instrumental
- epic
- cinematic
- gaming
- electronic

### Exclude Keywords
- vocal
- ballad
- slow
- sad

### Duration Preferences
- **Minimum**: 2 minutes
- **Maximum**: 8 minutes
- **Preferred**: 3-5 minutes

## Track Limits
- **Per Query**: 12
- **Total Tracks**: 50
- **Popularity Threshold**: 25

## Special Instructions
- High energy for focus
- No vocals to avoid distraction
- Epic crescendos and drops
- Consistent tempo for gaming flow
```

## 🔧 Technical Features

### Smart Filtering
- **Keyword filtering**: Include/exclude based on track/artist names
- **Duration control**: Set minimum/maximum track lengths
- **Popularity thresholds**: Control mainstream vs. underground balance
- **Duplicate prevention**: Automatic removal of duplicate tracks

### Advanced Categorization
- **Time-based categories**: Organize tracks into phases with time targets
- **Progressive organization**: Tracks sorted by category and duration
- **Cross-category balancing**: Ensure representation across all categories

### Robust Error Handling
- **Connection issues**: Graceful handling of network problems
- **Missing credentials**: Clear error messages for setup issues
- **Invalid configs**: Helpful feedback for configuration errors
- **Search failures**: Continue processing even if some queries fail

## 🚀 Usage Examples

### Basic Usage
```bash
# Use a pre-made configuration
python universal_playlist_creator.py coffee-shop.md
```

### Testing
```bash
# Test the system
python test_universal_creator.py
```

### Custom Configuration
```bash
# Create your own config and use it
python universal_playlist_creator.py my-custom-playlist.md
```

## 🎯 Migration from Legacy Creators

The universal creator replaces individual playlist scripts:

| Legacy Script | New Configuration | Benefits |
|---------------|-------------------|----------|
| `coffee_shop_playlist.py` | `coffee-shop.md` | No code changes needed |
| `ketamine_therapy_playlist.py` | `ketamine-therapy.md` | Better categorization |
| `dj_live_performances_playlist.py` | `dj-live-performances.md` | Easier customization |

### Benefits of Universal System
- **No coding required**: Just edit markdown files
- **Consistent behavior**: Same filtering and creation logic
- **Easy customization**: Change any aspect without code
- **Version control friendly**: Text-based configurations
- **Shareable**: Send config files to others easily

## 🔮 Advanced Tips

### Optimizing Search Queries
- **Be specific**: "acoustic indie coffee" vs. "music"
- **Use genres**: Include specific genre terms
- **Mix broad/narrow**: Combine general and specific queries
- **Test and iterate**: Run with small limits first

### Fine-tuning Filters
- **Start permissive**: Begin with loose filters, then tighten
- **Monitor results**: Check what gets included/excluded
- **Balance quality**: Don't over-filter and lose good tracks
- **Consider popularity**: Lower thresholds find hidden gems

### Category Design
- **Progressive flow**: Design emotional/energy progression
- **Time targets**: Match category lengths to use case
- **Clear descriptions**: Document what each category represents
- **Flexible queries**: Allow categories to overlap slightly

## 🎵 The Alex Method Philosophy

This system embodies the Alex Method approach to music curation:

- **Intention-driven**: Every playlist serves a specific purpose
- **Quality over quantity**: Careful curation beats random selection
- **User-centric design**: Easy to use, modify, and understand
- **Comprehensive coverage**: From therapeutic to high-energy use cases
- **Professional presentation**: Beautiful metadata and descriptions

---

*Created with ❤️ using The Alex Method for music technology*
