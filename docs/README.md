# Music Platform APIs & SDKs Documentation

*Comprehensive guide to integrating with major music streaming platforms*

## Platform Overview

This comprehensive guide compares major music streaming platforms and their API capabilities for integration with The Alex Method DJ platform. Each platform offers unique features, access levels, and development opportunities.

## Additional Music Services Research

Beyond the main platforms, several specialized music services offer unique capabilities:

### Advanced Platforms

| Platform | Type | API Status | Best For | Developer Access |
|----------|------|------------|----------|------------------|
| **TIDAL** | High-fidelity streaming | Beta (developer.tidal.com) | Audiophile quality, exclusive content | Developer platform with SDK tools |
| **SoundCloud** | Creator platform | Full API (OAuth 2.1) | Independent artists, user-generated content | Open registration with comprehensive docs |
| **Deezer** | International streaming | Simple API available | Global music discovery, flow technology | Open API with plugins and widgets |
| **Sonos** | Smart speaker ecosystem | Control API (OAuth 2.0) | Multi-room audio, home automation | Integration manager with client credentials |

### Specialized Services

| Platform | Type | API Status | Best For | Developer Access |
|----------|------|------------|----------|------------------|
| **Pandora** | Radio/discovery | GraphQL API | Music genome project, personalized radio | Partnership-based approval required |
| **Last.fm** | Music discovery/scrobbling | Full REST/XML-RPC API | Music metadata, listening history, social discovery | Open registration, extensive documentation |

### Integration Recommendations

- **TIDAL**: Consider for high-quality audio projects (beta status - verify access)
- **SoundCloud**: Excellent for independent/emerging artist discovery platforms
- **Deezer**: Strong international coverage, especially Europe
- **Sonos**: Essential for multi-room audio and home automation integration
- **Pandora**: Best for radio-style discovery features (requires partnership)
- **Last.fm**: Essential for music metadata and listening analytics

## Quick Decision Framework

### API Access & Authentication

| Platform | API Access | Authentication | Developer Program | Access Complexity |
|----------|-------------|----------------|-------------------|-------------------|
| **Spotify** | ✅ Open API | OAuth 2.0 (PKCE) | Free registration | Low - Immediate |
| **Apple Music** | ✅ Open API | JWT + MusicKit | Apple Developer ($99/year) | Low - Standard approval |
| **YouTube Music** | ✅ Open API | OAuth 2.0 | Google Cloud project | Medium - Quota management |
| **Amazon Music** | ⚠️ Closed Beta | OAuth 2.0 (LWA) | Business case approval | High - Restricted access |
| **SoundCloud** | ✅ Open API | OAuth 2.1 | Free registration | Low - Immediate |
| **TIDAL** | ⚠️ Beta | Developer platform | Beta registration | Medium - Beta access |
| **Deezer** | ✅ Simple API | API key | Free registration | Low - Immediate |
| **Sonos** | ✅ Control API | OAuth 2.0 | Integration manager | Medium - Client credentials |
| **Last.fm** | ✅ Open API | API key + Auth | Free registration | Low - Immediate |
| **Pandora** | ⚠️ Partnership | GraphQL | Partnership approval | High - Business case |

### Core Features Comparison

| Feature | Spotify | Apple Music | YouTube Music | Amazon Music | SoundCloud | TIDAL | Sonos |
|---------|---------|-------------|---------------|---------------|------------|-------|--------|
| **Search & Discovery** | ✅ Full catalog search | ✅ Comprehensive search | ✅ Full search capabilities | ⚠️ Beta access only | ✅ Track/user search | ⚠️ Beta access | ❌ No content API |
| **Playlist Management** | ✅ Full CRUD operations | ✅ Library management | ✅ Playlist operations | ⚠️ Beta access only | ✅ Playlist creation | ⚠️ Beta access | ✅ Playback control |
| **User Library Access** | ✅ Saved tracks/albums | ✅ Library + purchases | ✅ Liked songs/playlists | ⚠️ Beta access only | ✅ User tracks/likes | ⚠️ Beta access | ✅ Favorites access |
| **Music Playback** | ✅ Web Playback SDK | ✅ MusicKit JS | ❌ No direct playback | ⚠️ Beta access only | ✅ Streaming URLs | ⚠️ Beta access | ✅ Speaker control |
| **Recommendations** | ✅ Personalized playlists | ✅ Recommendations API | ✅ Trending content | ⚠️ Beta access only | ✅ Related tracks | ⚠️ Beta access | ❌ Not applicable |
| **Artist/Album Data** | ✅ Rich metadata | ✅ Comprehensive info | ✅ Detailed metadata | ⚠️ Beta access only | ✅ Track metadata | ⚠️ Beta access | ❌ Control-focused |
| **Real-time Controls** | ✅ Play/pause/skip | ✅ Full playback control | ❌ Limited control | ⚠️ Beta access only | ✅ Basic controls | ⚠️ Beta access | ✅ Full speaker control |

### SDK & Client-Side Support

| Platform | Web SDK | iOS SDK | Android SDK | Cross-Platform |
|----------|---------|---------|-------------|----------------|
| **Spotify** | ✅ Web Playback SDK | ✅ iOS SDK | ✅ Android SDK | ✅ React Native |
| **Apple Music** | ✅ MusicKit JS | ✅ MusicKit (Swift) | ❌ Not available | ❌ iOS/Web only |
| **YouTube Music** | ❌ No official SDK | ❌ YouTube Data API | ❌ YouTube Data API | ⚠️ API-based only |
| **Amazon Music** | ❌ No public SDK | ❌ Not available | ❌ Not available | ❌ Beta API only |
| **SoundCloud** | ✅ JavaScript SDK | ❌ API-based | ❌ API-based | ⚠️ Web SDK only |
| **TIDAL** | ⚠️ Beta SDK tools | ⚠️ Beta access | ⚠️ Beta access | ⚠️ Beta platform |
| **Sonos** | ❌ Control API only | ❌ Control API only | ❌ Control API only | ✅ REST API |
| **Last.fm** | ❌ No official SDK | ❌ API-based | ❌ API-based | ✅ REST/XML-RPC |

### Rate Limits & Quotas

| Platform | Rate Limits | Quota Management | Commercial Use |
|----------|-------------|------------------|----------------|
| **Spotify** | 100 requests/minute | Automatic scaling | ✅ Allowed |
| **Apple Music** | 3,000 requests/hour | Token-based limits | ✅ Allowed |
| **YouTube Music** | 10,000 units/day | Complex quota system | ✅ Allowed |
| **Amazon Music** | TPS limits enforced | Custom approval | ⚠️ Approval required |
| **SoundCloud** | 15,000 requests/hour | Rate limiting | ✅ Allowed |
| **TIDAL** | Beta rate limits | Beta program limits | ⚠️ Beta restrictions |
| **Deezer** | Standard API limits | Basic rate limiting | ✅ Allowed |
| **Sonos** | Standard OAuth limits | 24-hour token expiry | ✅ Allowed |
| **Last.fm** | Reasonable usage | Community guidelines | ✅ Allowed (contact for commercial) |
| **Pandora** | Partnership-defined | Custom agreements | ⚠️ Partnership required |

### Integration Capabilities

| Capability | Spotify | Apple Music | YouTube Music | Amazon Music | SoundCloud | Sonos | Last.fm |
|------------|---------|-------------|---------------|---------------|------------|--------|---------|
| **Streaming Integration** | ✅ Full web playback | ✅ Native integration | ❌ External links only | ⚠️ Beta access | ✅ Direct streaming | ✅ Speaker control | ❌ Metadata only |
| **Offline Sync** | ❌ Premium feature | ✅ Downloaded music | ❌ Not supported | ⚠️ Unknown | ❌ Stream-based | ❌ Hardware dependent | ❌ Not applicable |
| **Social Features** | ✅ Following/sharing | ✅ Friend activity | ✅ Public playlists | ⚠️ Beta access | ✅ User interaction | ❌ Control-focused | ✅ Scrobbling/social |
| **Analytics** | ✅ Play history | ✅ Library insights | ✅ View statistics | ⚠️ Unknown | ✅ Track statistics | ❌ Control-focused | ✅ Listening analytics |
| **Voice Control** | ✅ Connect API | ✅ SiriKit | ✅ Assistant actions | ✅ Alexa Skills | ❌ Not supported | ✅ Voice commands | ❌ Not supported |
| **Multi-room Audio** | ✅ Connect devices | ❌ Single device | ❌ Single device | ⚠️ Echo ecosystem | ❌ Single stream | ✅ Native feature | ❌ Not applicable |

## Platform-Specific Strengths

### 🎵 Spotify
**Best for**: Web applications, comprehensive playlist management, social music features
- **Strengths**: Mature API, excellent documentation, rich SDK ecosystem
- **Ideal use cases**: Music discovery apps, playlist managers, social music platforms
- **Developer experience**: ⭐⭐⭐⭐⭐ Excellent

### 🍎 Apple Music
**Best for**: iOS/macOS applications, high-quality streaming, purchased music integration
- **Strengths**: Native iOS integration, high-quality audio, seamless ecosystem
- **Ideal use cases**: iOS music apps, Apple ecosystem integration, premium experiences
- **Developer experience**: ⭐⭐⭐⭐ Very Good (iOS-focused)

### 📺 YouTube Music
**Best for**: Video music content, YouTube integration, global music discovery
- **Strengths**: Massive catalog, video content, global reach
- **Ideal use cases**: Music discovery, video-first experiences, international apps
- **Developer experience**: ⭐⭐⭐ Good (complex quota system)

### 📦 Amazon Music
**Best for**: Enterprise partnerships, Alexa integration, voice-controlled experiences
- **Strengths**: Alexa ecosystem, enterprise focus, voice control
- **Ideal use cases**: Alexa Skills, enterprise music solutions, voice-first apps
- **Developer experience**: ⭐⭐ Limited (closed beta access)

## Quick Start Recommendations

### For New Projects
```javascript
// Recommended platform priority for most use cases
const platformPriority = {
    webApp: ['spotify', 'apple', 'youtube'],
    mobileApp: ['spotify', 'apple'],
    iosApp: ['apple', 'spotify'],
    voiceApp: ['amazon_alexa', 'spotify'],
    enterprise: ['spotify', 'amazon_approval_process']
};
```

### Platform Selection Decision Tree

1. **Need immediate access?**
   - ✅ Yes → Spotify, Apple Music, YouTube Music
   - ❌ No → Consider Amazon Music if you can wait for approval

2. **Target platform?**
   - 🌐 Web → Spotify (best SDK) or Apple Music
   - 📱 iOS → Apple Music (native) or Spotify
   - 🤖 Android → Spotify or YouTube Music
   - 🗣️ Voice → Amazon Music (Alexa) or Spotify Connect

3. **Required features?**
   - 🎵 Streaming → Spotify or Apple Music
   - 📹 Video content → YouTube Music
   - 🎧 High-quality audio → Apple Music
   - 🗣️ Voice control → Amazon Music (Alexa)

## Documentation Index

### Platform-Specific Guides
- [**Spotify API Documentation**](./SPOTIFY-API-DOCUMENTATION.md) - Complete REST API integration
- [**Spotify Client SDK Documentation**](./SPOTIFY-CLIENT-SDK-DOCUMENTATION.md) - Web Playback SDK, iOS/Android SDKs
- [**Apple Music API Documentation**](./APPLE-MUSIC-API-DOCUMENTATION.md) - MusicKit and API integration
- [**YouTube Music API Documentation**](./YOUTUBE-MUSIC-API-DOCUMENTATION.md) - YouTube Data API for music
- [**Amazon Music API Documentation**](../AMAZON-MUSIC-API-DOCUMENTATION.md) - Closed beta access and Alexa integration

### Setup & Configuration Guides
- [**Spotify Playlist Guide**](./SPOTIFY-PLAYLIST-GUIDE.md) - Playlist management best practices
- [**YouTube Music Setup**](./YOUTUBE-MUSIC-SETUP.md) - API configuration and authentication
- [**Cross-Platform Workflow**](./CROSS-PLATFORM-WORKFLOW.md) - Multi-platform integration strategies

## Authentication Quick Reference

### Spotify (OAuth 2.0 + PKCE)
```javascript
const authUrl = 'https://accounts.spotify.com/authorize?' +
  'client_id=your_client_id&' +
  'response_type=code&' +
  'redirect_uri=your_redirect&' +
  'code_challenge_method=S256&' +
  'code_challenge=your_challenge&' +
  'scope=user-read-private%20playlist-modify-public';
```

### Apple Music (JWT)
```javascript
const token = MusicKit.getInstance().developerToken;
const userToken = await MusicKit.getInstance().authorize();
```

### YouTube Music (OAuth 2.0)
```javascript
const auth = new google.auth.OAuth2(
  'your_client_id',
  'your_client_secret',
  'your_redirect_uri'
);
```

### Amazon Music (Login with Amazon)
```javascript
amazon.Login.authorize({
  scope: 'profile'
}, function(response) {
  // Handle authentication
});
```

### Sonos (OAuth 2.0)
```javascript
const authUrl = 'https://api.sonos.com/login/v3/oauth?' +
  'client_id=your_client_id&' +
  'response_type=code&' +
  'state=your_state&' +
  'scope=playback-control-all&' +
  'redirect_uri=https%3A%2F%2Fyour.domain%2Fcallback';
```

### SoundCloud (OAuth 2.1)
```javascript
const authUrl = 'https://secure.soundcloud.com/authorize?' +
  'client_id=your_client_id&' +
  'redirect_uri=your_redirect_uri&' +
  'response_type=code&' +
  'code_challenge=your_code_challenge&' +
  'code_challenge_method=S256';
```

### Last.fm (API Key + Session)
```javascript
const apiKey = 'your_api_key';
const sessionKey = await getSessionKey(); // After user authorization
const apiSig = md5(`api_key${apiKey}method${method}sk${sessionKey}${secret}`);
```

## Rate Limit Best Practices

| Platform | Strategy | Implementation |
|----------|----------|----------------|
| **Spotify** | Exponential backoff | Retry with 1s, 2s, 4s delays |
| **Apple Music** | Token management | Refresh tokens before expiry |
| **YouTube Music** | Quota optimization | Batch requests, cache responses |
| **Amazon Music** | TPS management | Implement request queuing |
| **Sonos** | OAuth token lifecycle | 24-hour access token expiry, use refresh tokens |

## Error Handling Standards

```javascript
// Universal error handling pattern
async function handleMusicAPICall(platform, apiCall) {
  try {
    const response = await apiCall();
    return { success: true, data: response };
  } catch (error) {
    if (error.status === 429) {
      // Rate limit - implement backoff
      await delay(getBackoffTime(platform));
      return handleMusicAPICall(platform, apiCall);
    }

    if (error.status === 401) {
      // Auth issue - refresh token
      await refreshToken(platform);
      return handleMusicAPICall(platform, apiCall);
    }

    return { success: false, error: error.message };
  }
}
```

## Verification Notes

*Research conducted August 2025 - API status verified through official developer documentation*

### Fact-Checking Summary
- **Amazon Music**: Confirmed closed beta API program requiring business case approval
- **TIDAL**: Developer platform available in beta with SDK tools and documentation
- **SoundCloud**: Full OAuth 2.1 API with comprehensive documentation and open registration
- **Deezer**: Simple API available with plugins and widgets for developers
- **Sonos**: Control API available with OAuth 2.0 through integration manager and client credentials
- **Pandora**: GraphQL API available through partnership approval process
- **Last.fm**: Complete REST/XML-RPC API with extensive documentation and open access

> **Important**: Always verify current API status and access requirements before integration, as online services frequently update their developer programs and access policies.

## Getting Started

### Next Steps for Developers

1. **Choose Your Primary Platform**: Review the comparison tables above to select the best fit for your use case
2. **Verify Current Access**: Check the official developer documentation for the most up-to-date access requirements
3. **Start with Open APIs**: Begin development with Spotify, Apple Music, or YouTube Music for immediate access
4. **Plan for Approval-Based APIs**: If using Amazon Music or Pandora, prepare business cases and partnership applications
5. **Consider Hybrid Approaches**: Combine multiple APIs for comprehensive music platform coverage

### Platform-Specific Getting Started

- **Spotify**: Visit [Spotify for Developers](https://developer.spotify.com) for immediate API access
- **Apple Music**: Review [Apple Music API Documentation](https://developer.apple.com/documentation/applemusicapi/)
- **YouTube Music**: Access through [YouTube Data API v3](https://developers.google.com/youtube/v3)
- **Amazon Music**: Apply for closed beta at [Amazon Music API](https://developer.amazon.com/en-US/docs/alexa/device-apis/alexa-remotevideoplayer.html)
- **SoundCloud**: Register at [SoundCloud for Developers](https://developers.soundcloud.com)
- **Sonos**: Create integration at [Sonos Integration Manager](https://integration.sonos.com/integrations)
- **Last.fm**: Get API account at [Last.fm API](https://www.last.fm/api/account/create)

## Development

### Before You Begin
- [ ] Choose primary platform based on target audience
- [ ] Review rate limits and pricing for expected usage
- [ ] Set up developer accounts for chosen platforms
- [ ] Design authentication flow for your application
- [ ] Plan for multi-platform support if needed

### Development Setup
- [ ] Configure API credentials and redirect URIs
- [ ] Implement OAuth flows for chosen platforms
- [ ] Set up error handling and rate limiting
- [ ] Create fallback strategies for unavailable platforms
- [ ] Test authentication and basic API calls

### Production Readiness
- [ ] Implement proper token storage and refresh
- [ ] Add comprehensive error handling
- [ ] Set up monitoring for API usage and errors
- [ ] Document your integration for future maintenance
- [ ] Plan for platform API changes and versioning

---

**Last Updated**: August 4, 2025
**Maintained by**: Alex Method DJ Platform Team
**Status**: All documentation current and fact-checked

*For the most up-to-date information, always refer to the official platform documentation and developer portals.*
