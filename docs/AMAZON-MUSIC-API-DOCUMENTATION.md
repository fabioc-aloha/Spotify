# Amazon Music API Documentation

*Current status and available integration options for Amazon Music development*

## Table of Contents

1. [Overview](#overview)
2. [Current API Status](#current-api-status)
3. [Available Integration Options](#available-integration-options)
4. [Alexa Music Skill Kit](#alexa-music-skill-kit)
5. [Login with Amazon](#login-with-amazon)
6. [Alternative Solutions](#alternative-solutions)
7. [Community Projects](#community-projects)
8. [Best Practices](#best-practices)
9. [Future Considerations](#future-considerations)

---

## Overview

**Important Update**: As of August 2025, Amazon Music **does have a REST API**, but it's currently in **closed beta** with very limited access. Unlike Spotify, Apple Music, or YouTube Music which offer open public APIs, Amazon Music requires pre-approval and restricts access to select developers only.

### What This Means for Developers

- **Limited API access** - Amazon Music Web API exists but is in closed beta
- **Pre-approval required** - Must request access and be approved by Amazon Music team
- **Full functionality when approved** - Includes streaming, playlist management, search, and user data
- **Restrictive access model** - Unlike other platforms' open developer programs

---

## Current API Status

### ⚠️ Available (Closed Beta Only)

| Feature | Status | Notes |
|---------|---------|-------|
| **REST API** | ⚠️ Closed Beta | `https://api.music.amazon.dev/v1/` - Requires approval |
| **Web SDK** | ❌ Not available | No JavaScript SDK |
| **Mobile SDKs** | ❌ Not available | No iOS/Android SDKs |
| **Streaming API** | ⚠️ Closed Beta | Playback endpoints available for approved developers |
| **Search API** | ⚠️ Closed Beta | Catalog search available for approved developers |
| **User Data API** | ⚠️ Closed Beta | Playlist and library access for approved developers |

### ⚠️ Amazon's Position

Amazon has **launched the Amazon Music Web API** but keeps it in closed beta with restricted access. The company's strategy focuses on:

1. **Controlled partner ecosystem** - Only approved developers get API access
2. **Quality control** - Applications must meet Amazon Music's requirements
3. **Alexa integration** for voice-controlled music experiences
4. **Amazon ecosystem** integration (Prime, Echo devices)
5. **Selective partnerships** rather than open platform approach

---

## Available Integration Options

While a direct API is available in closed beta, there are limited integration paths for most developers:

### 1. Amazon Music Web API (Closed Beta)

**Purpose**: Full REST API access to Amazon Music functionality

#### Capabilities (For Approved Developers Only)
- Full catalog search and metadata access
- User playlist creation and management
- User library access (with permission)
- Streaming and playback control
- Artist, album, track, and podcast data
- Views and Browse APIs for rich UI applications

#### Authentication
- **OAuth 2.0** via Login with Amazon (LWA)
- **API Key required** - Security Profile ID from LWA
- **Scope**: Profile scope for user authentication

#### Base URL
```
https://api.music.amazon.dev/v1/
```

#### Example Request (For Approved Developers)
```javascript
// Get album information
const response = await fetch('https://api.music.amazon.dev/v1/albums/?ids=B0064UPU4G,B091BHTFTZ', {
    headers: {
        'x-api-key': 'amzn1.application.xxxxxxxxxx', // Your Security Profile ID
        'Authorization': 'Bearer ' + accessToken // OAuth token from LWA
    }
});

const albumData = await response.json();
```

#### Access Requirements
- **Application approval** by Amazon Music team
- **Compliance verification** with Amazon Developer Services Agreement
- **Security Profile enablement** by Amazon Music Service
- **Business justification** for integration

#### How to Request Access
1. **Contact Amazon Music** via [developer support](https://developer.amazon.com/support/contact-us)
2. **Submit business case** explaining your integration needs
3. **Provide application details** and expected usage
4. **Wait for approval** (no guaranteed timeline)

#### Limitations
- **Closed beta access only** - No public availability
- **Approval required** - Must be vetted by Amazon
- **Rate limiting** enforced via TPS limits
- **Compliance requirements** must be met

### 2. Alexa Music Skill Kit

**Purpose**: Create voice-controlled music experiences for Alexa devices

#### Capabilities
- Voice-activated music playback
- Integration with custom music services
- Alexa Skills for music discovery
- Audio streaming through Alexa

#### Limitations
- Requires Alexa ecosystem
- Voice-only interaction
- Limited to custom music services (not Amazon Music directly)

#### Implementation Example

```javascript
// Alexa Skill Handler
const LaunchRequestHandler = {
    canHandle(handlerInput) {
        return handlerInput.requestEnvelope.request.type === 'LaunchRequest';
    },
    handle(handlerInput) {
        const speechText = 'Welcome to your music skill!';

        return handlerInput.responseBuilder
            .speak(speechText)
            .reprompt(speechText)
            .getResponse();
    }
};

// Music Intent Handler
const PlayMusicIntentHandler = {
    canHandle(handlerInput) {
        return handlerInput.requestEnvelope.request.type === 'IntentRequest'
            && handlerInput.requestEnvelope.request.intent.name === 'PlayMusicIntent';
    },
    handle(handlerInput) {
        // Note: This would connect to YOUR music service, not Amazon Music
        const audioUrl = 'https://your-music-service.com/stream/song.mp3';

        return handlerInput.responseBuilder
            .addAudioPlayerPlayDirective('REPLACE_ALL', audioUrl, 'token', 0)
            .getResponse();
    }
};
```

#### Getting Started

1. **Create an Alexa Developer Account**
```bash
# Install ASK CLI
npm install -g ask-cli

# Configure ASK CLI
ask configure
```

2. **Create a Music Skill**
```bash
# Initialize new skill
ask new

# Choose "Custom" skill type
# Select music-related templates
```

3. **Define Interaction Model**
```json
{
    "interactionModel": {
        "languageModel": {
            "invocationName": "my music player",
            "intents": [
                {
                    "name": "PlayMusicIntent",
                    "slots": [
                        {
                            "name": "songName",
                            "type": "AMAZON.MusicCreativeWork"
                        },
                        {
                            "name": "artistName",
                            "type": "AMAZON.Artist"
                        }
                    ],
                    "samples": [
                        "play {songName}",
                        "play {songName} by {artistName}",
                        "I want to hear {songName}"
                    ]
                }
            ]
        }
    }
}
```

### 3. Login with Amazon

**Purpose**: Authenticate users with their Amazon accounts

#### Use Cases
- User authentication in music applications
- Access to Amazon account information
- Single sign-on functionality

#### Implementation

```javascript
// Frontend Implementation
window.onAmazonLoginReady = function() {
    amazon.Login.setClientId('your-client-id');
};

// Login Function
function loginWithAmazon() {
    amazon.Login.authorize({
        scope: 'profile',
        popup: false
    }, function(response) {
        if (response.error) {
            console.error('Login failed:', response.error);
            return;
        }

        // Use access token to get user profile
        amazon.Login.retrieveProfile(response.access_token, function(profile) {
            console.log('User profile:', profile);
            // Profile contains: user_id, name, email
        });
    });
}
```

```html
<!-- Include Amazon Login SDK -->
<script type="text/javascript">
    window.onAmazonLoginReady = function() {
        amazon.Login.setClientId('amzn1.application-oa2-client.your-client-id');
    };
    (function(d) {
        var a = d.createElement('script'); a.type = 'text/javascript';
        a.async = true; a.id = 'amazon-login-sdk';
        a.src = 'https://assets.loginwithamazon.com/sdk/na/login1.js';
        d.getElementById('amazon-root').appendChild(a);
    })(document);
</script>

<div id="amazon-root"></div>
<a href="#" id="LoginWithAmazon" onclick="loginWithAmazon()">
    <img border="0" alt="Login with Amazon"
         src="https://images-na.ssl-images-amazon.com/images/G/01/lwa/btnLWA_gold_156x32.png"
         width="156" height="32" />
</a>
```

#### Available Scopes

| Scope | Description | Data Returned |
|-------|-------------|---------------|
| `profile` | Basic profile information | name, email, user_id |
| `postal_code` | User's postal code | postal_code |

#### Limitations
- **No music data access** - Only basic profile information
- **No Amazon Music integration** - Cannot access user's music library
- **General authentication only** - Not specific to music services

---

## Alternative Solutions

### 1. Web Scraping (Not Recommended)

⚠️ **Warning**: Web scraping Amazon Music violates their Terms of Service and is not recommended.

**Risks**:
- Legal issues and Terms of Service violations
- IP blocking and rate limiting
- Unreliable due to frequent UI changes
- No guarantee of continued functionality

### 2. Browser Automation (Not Recommended)

⚠️ **Warning**: Automated browser interaction with Amazon Music is against their Terms of Service.

**Example of what NOT to do**:
```javascript
// DON'T DO THIS - Violates ToS
const puppeteer = require('puppeteer');

async function getAmazonMusicData() {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    // This violates Amazon's Terms of Service
    await page.goto('https://music.amazon.com');
    // ... automation code

    await browser.close();
}
```

### 3. Reverse Engineering (Not Recommended)

⚠️ **Warning**: Reverse engineering Amazon Music's internal APIs violates their Terms of Service.

**Why this is problematic**:
- Violates Terms of Service
- APIs can change without notice
- May trigger security measures
- Legal implications

---

## Community Projects

### Unofficial Libraries

**Disclaimer**: These are community-maintained projects and are not officially supported by Amazon. Use at your own risk.

#### 1. amazon-music (Python)
```bash
pip install amazon-music-api
```

```python
# Example usage (unofficial)
from amazon_music import AmazonMusic

# Note: This is an unofficial library
client = AmazonMusic()
# This may violate Amazon's ToS
```

#### 2. Amazon Music Scraper Projects

Several GitHub projects attempt to extract data from Amazon Music:
- `AmineSoukara/amazon-music` - Python-based scraper
- `gratajik/AmazonMusic` - C# album art extractor
- `nltvator/AmazonMusicAPI` - Information extraction tool

**Important**: These projects often violate Amazon's Terms of Service and may stop working at any time.

### Limitations of Community Projects

1. **Terms of Service violations**
2. **Unreliable functionality** due to Amazon's anti-scraping measures
3. **No official support** or documentation
4. **Legal risks** for commercial use
5. **Rate limiting** and IP blocking risks

---

## Best Practices

### For Music Application Developers

#### 1. Use Official APIs Instead

If you need music integration, consider these official alternatives:

```javascript
// Spotify Web API (Recommended)
const spotifyApi = new SpotifyApi({
    clientId: 'your-client-id',
    clientSecret: 'your-client-secret'
});

// Apple Music API (Recommended)
const musicKit = MusicKit.configure({
    developerToken: 'your-developer-token',
    app: {
        name: 'Your App Name',
        build: '1.0.0'
    }
});
```

#### 2. Multi-Platform Support

```javascript
// Support multiple music services
class MusicService {
    constructor() {
        this.providers = {
            spotify: new SpotifyProvider(),
            apple: new AppleMusicProvider(),
            youtube: new YouTubeMusicProvider()
            // Note: Amazon Music not available
        };
    }

    async search(query, provider = 'spotify') {
        if (!this.providers[provider]) {
            throw new Error(`Provider ${provider} not supported`);
        }

        return await this.providers[provider].search(query);
    }
}
```

#### 3. User Choice Implementation

```javascript
// Let users choose their preferred service
const MusicPlatformSelector = () => {
    const [selectedPlatform, setSelectedPlatform] = useState('spotify');

    const platforms = [
        { id: 'spotify', name: 'Spotify', available: true },
        { id: 'apple', name: 'Apple Music', available: true },
        { id: 'youtube', name: 'YouTube Music', available: true },
        { id: 'amazon', name: 'Amazon Music', available: false, reason: 'No API available' }
    ];

    return (
        <div>
            <h3>Choose your music platform:</h3>
            {platforms.map(platform => (
                <button
                    key={platform.id}
                    disabled={!platform.available}
                    onClick={() => setSelectedPlatform(platform.id)}
                >
                    {platform.name}
                    {!platform.available && ` (${platform.reason})`}
                </button>
            ))}
        </div>
    );
};
```

### For Enterprise Integration

#### 1. Focus on Available Ecosystems

```yaml
# Recommended integration strategy
integration_strategy:
  primary:
    - spotify_web_api
    - apple_music_api
    - youtube_data_api

  voice_control:
    - alexa_skills_kit  # For voice music experiences
    - google_assistant   # Alternative voice platform

  authentication:
    - login_with_amazon  # For Amazon account integration
    - oauth2_providers   # For other services

  amazon_integration:
    - alexa_skills       # Voice-controlled music
    - amazon_appstore    # Mobile app distribution
    - aws_services       # Backend infrastructure
```

#### 2. Compliance and Legal Considerations

```javascript
// Terms of Service compliance checker
class ComplianceChecker {
    static checkAmazonMusicAccess(method) {
        const violations = {
            'web_scraping': 'Violates Amazon ToS - unauthorized data extraction',
            'reverse_engineering': 'Violates Amazon ToS - API reverse engineering',
            'automation': 'Violates Amazon ToS - automated browser interaction'
        };

        if (violations[method]) {
            throw new Error(`Compliance Issue: ${violations[method]}`);
        }

        return true;
    }
}
```

---

## Future Considerations

### Potential Developments

#### 1. Amazon Music API Announcement
While no official API exists currently, developers should monitor:

- **Amazon Developer Blog** for announcements
- **AWS re:Invent** conference presentations
- **Amazon Music developer forums** (if they emerge)
- **Third-party integrations** that Amazon might allow

#### 2. Alternative Integration Paths

Amazon might explore:
- **Partner API programs** for select developers
- **Enterprise integrations** for business customers
- **Alexa-based music platform** expansions
- **AWS-hosted music services** integration

### Monitoring for Updates

```javascript
// Check for API availability (conceptual)
class AmazonMusicApiChecker {
    static async checkApiAvailability() {
        const endpoints = [
            'https://api.music.amazon.com',
            'https://music.amazon.com/api',
            'https://developer.amazon.com/music-api'
        ];

        for (const endpoint of endpoints) {
            try {
                const response = await fetch(endpoint);
                if (response.status !== 404) {
                    console.log(`Potential API endpoint found: ${endpoint}`);
                    return endpoint;
                }
            } catch (error) {
                // Endpoint not available yet
            }
        }

        return null;
    }
}

// Check quarterly for API updates
setInterval(AmazonMusicApiChecker.checkApiAvailability, 3 * 30 * 24 * 60 * 60 * 1000);
```

### Recommended Architecture for Future Compatibility

```javascript
// Build with future API support in mind
class FutureProofMusicPlatform {
    constructor() {
        this.adapters = new Map();
        this.initializeAdapters();
    }

    initializeAdapters() {
        // Current available APIs
        this.adapters.set('spotify', new SpotifyAdapter());
        this.adapters.set('apple', new AppleMusicAdapter());
        this.adapters.set('youtube', new YouTubeMusicAdapter());

        // Placeholder for future Amazon Music API
        this.adapters.set('amazon', new PlaceholderAdapter({
            message: 'Amazon Music API not yet available',
            checkForUpdates: true,
            fallbackProvider: 'spotify'
        }));
    }

    async getService(provider) {
        const adapter = this.adapters.get(provider);

        if (adapter instanceof PlaceholderAdapter) {
            // Check if real API is now available
            const realAdapter = await adapter.checkForRealImplementation();
            if (realAdapter) {
                this.adapters.set(provider, realAdapter);
                return realAdapter;
            }
        }

        return adapter;
    }
}
```

---

## Summary and Recommendations

## Current Reality and Recommendations

### Current Reality (August 2025)

1. **Amazon Music Web API exists** but is in closed beta
2. **Access is highly restricted** - requires approval and business justification
3. **Full functionality available** for approved developers (streaming, playlists, search, etc.)
4. **No timeline for public release** - Amazon maintains closed ecosystem approach
5. **Alternative integration options** remain limited to Alexa Skills and basic authentication

### Recommended Approach

#### For New Projects
```javascript
// Recommended multi-platform strategy with Amazon Music consideration
const musicPlatforms = {
    primary: ['spotify', 'apple', 'youtube'], // Open APIs available
    restricted: ['amazon'], // Closed beta API - requires approval
    voice: ['alexa'], // For voice-controlled experiences
    authentication: ['amazon_login'] // For Amazon account integration
};

// Handle Amazon Music API access attempts
async function requestAmazonMusicAccess() {
    // This would require manual approval process
    const businessCase = {
        appName: 'Your Music App',
        useCase: 'Playlist management and streaming',
        expectedUsers: 10000,
        timeline: 'Q4 2025'
    };

    // Contact Amazon Music developer support with business case
    // https://developer.amazon.com/support/contact-us
    return 'manual-approval-required';
}
```

#### For Existing Amazon Music Users
1. **Apply for API access** if you have a strong business case
2. **Inform users** about the approval-required integration process
3. **Offer alternative platforms** with immediate API access
4. **Implement Alexa Skills** for voice-controlled experiences
5. **Use Login with Amazon** for basic account integration

### Requesting Amazon Music API Access

#### Business Case Requirements
- **Clear integration purpose** and expected user benefits
- **Estimated user volume** and usage patterns
- **Compliance commitment** with Amazon's program requirements
- **Development timeline** and launch plans

#### Application Process
1. **Contact Amazon Music Support**
   - Use [developer contact form](https://developer.amazon.com/support/contact-us)
   - Subject: "Amazon Music Web API Access Request"

2. **Provide Documentation**
   - Application mockups or prototypes
   - Integration architecture plans
   - User experience flows
   - Expected API usage patterns

3. **Legal Compliance**
   - Agree to [Amazon Developer Services Agreement](https://developer.amazon.com/support/legal/da)
   - Review [Amazon Music Program Requirements](https://developer.amazon.com/docs/music/requ_AM-Program-Requirements.html)

4. **Wait for Review**
   - No guaranteed approval timeline
   - Amazon evaluates business case and technical merit
   - May require additional documentation or modifications

### Developer Resources

#### Official Documentation
- [Amazon Music Developer Portal](https://developer.amazon.com/docs/music/landing_home.html)
- [Amazon Music Web API Overview](https://developer.amazon.com/docs/music/API_web_overview.html)
- [Amazon Music Developer Forum](https://community.amazondeveloper.com/c/amazon-music/22)
- [Alexa Skills Kit Documentation](https://developer.amazon.com/docs/alexa/ask-overviews/what-is-the-alexa-skills-kit.html)
- [Login with Amazon Guide](https://developer.amazon.com/docs/login-with-amazon/documentation-overview.html)
- [Amazon Developer Portal](https://developer.amazon.com/)

#### Alternative Music APIs
- [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api)
- [Apple Music API Documentation](https://developer.apple.com/documentation/applemusicapi)
- [YouTube Data API v3](https://developers.google.com/youtube/v3)

#### Legal and Compliance
- [Amazon Developer Terms](https://developer.amazon.com/terms-and-agreements)
- [Amazon Music Terms of Use](https://music.amazon.com/terms)

---

**Last Updated**: August 4, 2025
**Status**: Closed Beta API available with approval required
**Recommendation**: Apply for access if you have a strong business case, otherwise use alternative music platforms with open APIs

*This documentation reflects the current state of Amazon Music's closed beta API program. Information will be updated as Amazon's API access policies evolve.*
