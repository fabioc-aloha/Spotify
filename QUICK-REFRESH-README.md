# Quick Refresh Script

Simple, fast script to refresh all Alex Method DJ playlists with minimal output. Perfect for scheduled tasks or daily routine updates.

## 🚀 Usage

### **Basic Commands**
```powershell
# Refresh all playlists on Spotify (default)
.\quick-refresh.ps1

# Refresh all playlists on YouTube Music
.\quick-refresh.ps1 -Platform youtube-music
```

## ✨ Features

- ✅ **Auto-Discovery** - Finds all 19 playlist configs automatically
- ✅ **Clean Output** - Minimal progress indicators: `🔄 playlist-name... ✅`
- ✅ **Cross-Platform** - Supports both Spotify and YouTube Music
- ✅ **Error Handling** - Proper exit codes and failure reporting
- ✅ **API-Friendly** - 1-second pauses between requests
- ✅ **Fast & Reliable** - No complex features, just works

## 📊 Example Output

```
🎵 Alex Method DJ - Quick Refresh (spotify)
📁 Found 19 playlists to refresh
🔄 adhd-focus-protocol... ✅
🔄 anxiety-relief... ✅
🔄 billboard-decades-hits... ✅
🔄 coffee-shop... ✅
...
🔄 trauma-recovery... ✅

🎉 Completed in 23:18
✅ Success: 19 | ❌ Failed: 0
```

## 🎯 Perfect For

- **Daily Routine**: Quick playlist updates without detailed logging
- **Scheduled Tasks**: Automated playlist maintenance
- **Simple Workflows**: When you just want your playlists refreshed
- **Cross-Platform Sync**: Easy Spotify → YouTube Music migration

## 📝 Script Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `-Platform` | Target music platform | `spotify` | `-Platform youtube-music` |

## 🔧 Technical Details

- **Auto-excludes**: Templates (`TEMPLATE-*`), README files, example folders
- **Processing Order**: Alphabetical by config filename
- **Exit Codes**: 0 = success, 1 = failure(s) occurred
- **Error Reporting**: Suggests detailed diagnostics when failures occur
- **Unicode Support**: Full emoji display on Windows PowerShell

---

*Part of the Alex Method DJ Platform - Simple, reliable playlist management*
