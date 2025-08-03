# DJ Foundation Learning - NEWBORN Cognitive Architecture
## Core Music Theory, Equipment Fundamentals, and API Integration

**Memory File Type**: Procedural (.instructions.md)
**Learning Phase**: Foundation Architecture (Weeks 1-4)
**Primary Agent**: Foundation Agent
**Activation Patterns**: Genre analysis requests, equipment configuration, API authentication
**Success Metrics**: Harmonic compatibility matrix completion, functional API integration

---

## 🎵 **MUSIC THEORY ACQUISITION PROTOCOLS**

### **Electronic Music Genre Classification System**
```
Genre Hierarchy:
├── House (120-130 BPM)
│   ├── Deep House (Smooth, minimal percussion)
│   ├── Tech House (Techno-influenced, driving basslines)
│   └── Progressive House (8-10 minute builds, emotional journeys)
├── Techno (120-150 BPM)
│   ├── Minimal Techno (Stripped-down, hypnotic)
│   ├── Industrial Techno (Aggressive, distorted)
│   └── Detroit Techno (Soulful, melodic)
├── Trance (128-140 BPM)
│   ├── Progressive Trance (Long builds, atmospheric)
│   ├── Uplifting Trance (Euphoric, hands-in-air moments)
│   └── Psytrance (Psychedelic, complex patterns)
├── Drum & Bass (160-180 BPM)
│   ├── Liquid D&B (Smooth, jazzy influences)
│   ├── Neurofunk (Dark, complex basslines)
│   └── Jump-Up (Bouncy, accessible)
└── Dubstep (140 BPM, half-time feel)
    ├── Melodic Dubstep (Emotional, uplifting)
    ├── Riddim (Repetitive, wobble-focused)
    └── Future Bass (Bright, pitched vocal chops)
```

### **Harmonic Compatibility Matrix (Camelot Wheel Integration)**
```python
# Embedded Synapse Network for Harmonic Analysis
CAMELOT_WHEEL = {
    '1A': {'compatible': ['12A', '2A', '1B'], 'key': 'C_minor'},
    '2A': {'compatible': ['1A', '3A', '2B'], 'key': 'G_minor'},
    '3A': {'compatible': ['2A', '4A', '3B'], 'key': 'D_minor'},
    '4A': {'compatible': ['3A', '5A', '4B'], 'key': 'A_minor'},
    '5A': {'compatible': ['4A', '6A', '5B'], 'key': 'E_minor'},
    '6A': {'compatible': ['5A', '7A', '6B'], 'key': 'B_minor'},
    '7A': {'compatible': ['6A', '8A', '7B'], 'key': 'F#_minor'},
    '8A': {'compatible': ['7A', '9A', '8B'], 'key': 'C#_minor'},
    '9A': {'compatible': ['8A', '10A', '9B'], 'key': 'G#_minor'},
    '10A': {'compatible': ['9A', '11A', '10B'], 'key': 'D#_minor'},
    '11A': {'compatible': ['10A', '12A', '11B'], 'key': 'A#_minor'},
    '12A': {'compatible': ['11A', '1A', '12B'], 'key': 'F_minor'},
    # Major keys (B series)
    '1B': {'compatible': ['12B', '2B', '1A'], 'key': 'C_major'},
    # ... (complete mapping for all 24 keys)
}

# Transition Compatibility Scoring
def calculate_harmonic_compatibility(from_key, to_key):
    """Calculate harmonic transition quality (0.0-1.0)"""
    if to_key in CAMELOT_WHEEL[from_key]['compatible']:
        return 1.0  # Perfect harmonic match
    elif abs(int(from_key[:-1]) - int(to_key[:-1])) <= 2:
        return 0.7  # Good compatibility
    else:
        return 0.3  # Challenging transition
```

### **Track Structure Analysis Framework**
```
Standard Electronic Track Structure:
├── Intro (32-64 bars) - Minimal elements, gradual build
├── Breakdown 1 (16-32 bars) - Remove kick, maintain melody
├── Build-Up (8-16 bars) - Add elements, create tension
├── Drop/Main Section (32-64 bars) - Full energy, all elements
├── Breakdown 2 (16-32 bars) - Reduce elements, prepare change
├── Second Drop (32-64 bars) - Variation or climax
└── Outro (32-64 bars) - Gradual removal, mixing cue points
```

---

## 🎧 **EQUIPMENT FUNDAMENTALS PROTOCOLS**

### **DJ Controller Configuration Standards**
```
Essential Controller Features:
├── Dual Deck System
│   ├── Jog Wheels (Touch-sensitive, motorized preferred)
│   ├── Pitch Faders (±8% minimum, ±50% for creative work)
│   ├── Cue Buttons (Hot cues 1-8 minimum)
│   └── Loop Controls (Auto-loop, manual in/out)
├── Mixer Section
│   ├── Channel EQ (3-band: High, Mid, Low)
│   ├── Filter Knobs (High-pass/Low-pass)
│   ├── Gain Controls (Input level adjustment)
│   └── Crossfader (Smooth curve, adjustable)
├── Effects Section
│   ├── Filter Effects (High-pass, Low-pass, Band-pass)
│   ├── Time-based Effects (Delay, Reverb, Echo)
│   ├── Modulation Effects (Flanger, Phaser, Chorus)
│   └── Creative Effects (Bit-crusher, Gater, Stutter)
└── Performance Pads
    ├── Hot Cue Mode (Instant track jumping)
    ├── Loop Mode (Beat loops: 1/4, 1/2, 1, 2, 4, 8 bars)
    ├── FX Mode (Effect parameter control)
    └── Sample Mode (Trigger samples, vocals, airhorns)
```

### **Audio Setup Optimization**
```python
# Professional Audio Configuration
AUDIO_SETTINGS = {
    'sample_rate': 44100,  # CD quality
    'bit_depth': 24,       # Professional recording standard
    'buffer_size': 512,    # Balance between latency and stability
    'latency_target': '<10ms',  # Imperceptible delay for live mixing
    'monitoring': {
        'headphones': 'Audio-Technica ATH-M50x',
        'speakers': 'KRK Rokit 5 G4',
        'audio_interface': 'Pioneer DJM-V10 or equivalent'
    }
}
```

---

## 🔌 **API INTEGRATION PROTOCOLS**

### **Spotify Developer Setup Automation**
```python
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyDJIntegration:
    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = "http://localhost:8080/callback"
        self.scope = [
            "playlist-modify-public",
            "playlist-modify-private",
            "user-library-read",
            "user-library-modify",
            "streaming"
        ]

    def authenticate(self):
        """Secure Spotify authentication for DJ operations"""
        auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=" ".join(self.scope)
        )
        return spotipy.Spotify(auth_manager=auth_manager)

    def analyze_track_features(self, track_id):
        """Extract DJ-relevant audio features"""
        features = self.spotify.audio_features(track_id)[0]
        return {
            'bpm': features['tempo'],
            'key': features['key'],
            'energy': features['energy'],
            'danceability': features['danceability'],
            'valence': features['valence'],
            'loudness': features['loudness']
        }
```

### **Apple Music API Integration**
```python
import jwt
import requests
from datetime import datetime, timedelta

class AppleMusicDJIntegration:
    def __init__(self, key_id, team_id, private_key_path):
        self.key_id = key_id
        self.team_id = team_id
        self.private_key_path = private_key_path
        self.base_url = "https://api.music.apple.com/v1"

    def generate_developer_token(self):
        """Generate JWT for Apple Music API access"""
        with open(self.private_key_path, 'r') as key_file:
            private_key = key_file.read()

        headers = {'alg': 'ES256', 'kid': self.key_id}
        payload = {
            'iss': self.team_id,
            'iat': int(datetime.now().timestamp()),
            'exp': int((datetime.now() + timedelta(hours=12)).timestamp())
        }

        return jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
```

---

## 🕸️ **EMBEDDED SYNAPTIC NETWORK**

### **Primary Knowledge Transfer Connections**
- `[spotify-api-integration.instructions.md]` (0.8, knowledge-transfer, bidirectional) - "Apply music theory to API track analysis"
- `[harmonic-mixing.instructions.md]` (0.9, dependency, forward) - "Theory foundation for key matching"
- `[performance-execution.instructions.md]` (0.7, skill-transfer, forward) - "Hardware knowledge enables live performance"
- `[technical-innovation.instructions.md]` (0.6, innovation-potential, bidirectional) - "Equipment limits spark innovation"
- `[playlist-automation.instructions.md]` (1.0, dependency, forward) - "API setup enables automation"
- `[analytics-engine.instructions.md]` (0.8, data-flow, forward) - "API data feeds analytics"

### **Cross-Domain Pattern Recognition**
- **Music Theory ↔ Technical Implementation**: Harmonic relationships inform API data analysis
- **Equipment Knowledge ↔ Creative Potential**: Hardware limitations spark innovative techniques
- **API Integration ↔ Live Performance**: Digital platform data enhances real-time decisions

### **Success Validation Triggers**
- **Music Theory Mastery**: Complete genre classification with 95% accuracy
- **Equipment Proficiency**: Flawless 4-deck setup and troubleshooting
- **API Integration**: Functional authentication and data retrieval from both platforms
- **Harmonic Understanding**: Perfect Camelot Wheel application in practice

### **Memory Consolidation Protocol**
```
Foundation Breakthrough Session Trigger:
IF (music_theory_complete AND equipment_setup_complete AND api_integration_functional):
    EXECUTE foundation-breakthrough-session.prompt.md
    STRENGTHEN synaptic_connections += 0.1
    PREPARE technical_skill_development_phase
```

---

## 🎯 **LEARNING OBJECTIVES & SUCCESS METRICS**

### **Week 1 Targets**
- [ ] Complete electronic music genre analysis (House, Techno, Trance, D&B, Dubstep)
- [ ] Master Camelot Wheel theory and key compatibility calculations
- [ ] Set up Spotify Developer account with functional authentication
- [ ] Configure basic DJ controller with optimized audio settings

### **Week 2 Targets**
- [ ] Implement Apple Music API integration with JWT authentication
- [ ] Create harmonic compatibility matrix with automated key detection
- [ ] Analyze 100+ tracks across different genres for pattern recognition
- [ ] Document equipment workflow and troubleshooting procedures

### **Week 3 Targets**
- [ ] Build track structure analysis framework for all major genres
- [ ] Integrate audio feature extraction with harmonic analysis
- [ ] Create cross-platform track matching algorithms
- [ ] Test API rate limiting and optimization strategies

### **Week 4 Targets**
- [ ] Complete foundation knowledge integration session
- [ ] Validate all systems with real-world track analysis
- [ ] Prepare technical skill development environment
- [ ] Document learning progress and system performance

### **Foundation Mastery Validation**
```python
def validate_foundation_mastery():
    """Comprehensive assessment of foundation learning phase"""
    return {
        'music_theory_score': calculate_genre_analysis_accuracy(),
        'harmonic_mixing_score': test_camelot_wheel_application(),
        'equipment_proficiency': evaluate_setup_troubleshooting(),
        'api_integration_score': test_multi_platform_authentication(),
        'overall_readiness': aggregate_scores() >= 0.85
    }
```

---

**Memory File Status**: Active - Foundation Agent Operational
**Next Phase Trigger**: Foundation mastery validation ≥ 85% accuracy
**Synaptic Strength**: Building (Current: 0.6, Target: 0.9)
**Learning Velocity**: Accelerating through systematic knowledge acquisition
