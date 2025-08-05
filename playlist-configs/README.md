# Playlist Configuration Templates

## Universal Template

Use `TEMPLATE-universal.md` as the base for all new playlists.

### Template Features
- **Single Phase**: Use one "Main Phase" for simple playlists
- **Multi Phase**: Create progression phases for complex playlists (e.g., warm-up → main → cool-down)
- **Duration Control**: Each phase has specific duration targeting
- **Advanced Search**: Phase-specific search queries for better results

### CRITICAL FORMATTING REQUIREMENTS

**All sections must use bullet points (- ) format:**

#### ✅ CORRECT Format:
```markdown
## Search Queries
- calm music
- relaxing instrumental
- peaceful sounds

### Phase 1: Name (10 minutes)
Description here
- Queries: search term one
- Queries: search term two

## Track Filters
### Exclude Keywords
- loud
- aggressive
- fast

### Include Keywords (Prioritize)
- calm
- peaceful
- gentle

### Duration Preferences
- **Min Duration**: 2 minutes
- **Max Duration**: 6 minutes

## Track Limits
- **Per Query**: 20
- **Total Tracks**: 100

## Content Preferences
- **Content Types**: [music_video, live_performance]
- **Quality**: high_quality

## Special Instructions
- Prioritize original versions over covers
- Focus on high-quality audio
```

#### ❌ WRONG Format:
```markdown
## Search Queries
calm music, relaxing instrumental, peaceful sounds

### Exclude Keywords
loud, aggressive, fast, intense
```

### Complete Section Reference

**REQUIRED SECTIONS:**
- `## Metadata` - Playlist name, description, duration, privacy
- `## Search Queries` - Basic search terms (bullet points)
- `## Track Categories` - Phases with durations and specific queries
- `## Track Filters` - Include/exclude keywords (bullet points)

**OPTIONAL SECTIONS:**
- `### Duration Preferences` - Min/max/preferred track lengths
- `## Track Limits` - Per query, total tracks, popularity thresholds
- `## Content Preferences` - YouTube-specific content type preferences
- `## Special Instructions` - Additional creation guidelines
- `## Creation Notes` - Documentation and notes (free text)

**AUTO-GENERATED:**
- `## Cross-Platform Metadata` - Added automatically after playlist creation

### Examples
- **Single Phase**: `coffee-shop.md` - One "Coffeehouse Vibes" phase
- **Multi Phase**: `study-focus.md` - Four phases (Gentle Start → Deep Focus → Active Concentration → Wind Down)
- **Therapeutic**: `anxiety-relief.md` - Journey phases for therapy sessions

### Why Universal Template?
- Works for both simple and complex playlists
- Better duration control and content targeting
- Consistent format across all configurations
- Enhanced search capabilities with phase-specific queries
- **Proper filtering requires bullet-point format**
- Supports all advanced features (limits, preferences, instructions)

The universal template automatically detects single vs. multi-phase configurations and optimizes accordingly.
