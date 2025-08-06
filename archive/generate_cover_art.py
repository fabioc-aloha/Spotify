#!/usr/bin/env python3
"""
Alex Method DJ Platform - AI Cover Art Generator
Proof of Concept for generating playlist cover art using OpenAI DALL-E 3

Usage:
    python generate_cover_art.py playlist-configs/neural-network-symphony.md
    python generate_cover_art.py playlist-configs/digital-consciousness-awakening.md
"""

import os
import sys
import re
import json
import base64
import requests
from PIL import Image
from io import BytesIO
from pathlib import Path
import argparse
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'dall-e-3')
OPENAI_IMAGE_SIZE = os.getenv('OPENAI_IMAGE_SIZE', '1024x1024')
OPENAI_IMAGE_QUALITY = os.getenv('OPENAI_IMAGE_QUALITY', 'hd')
OPENAI_IMAGE_STYLE = os.getenv('OPENAI_IMAGE_STYLE', 'vivid')
COVER_ART_DIR = Path('cover-art')
GENERATED_DIR = COVER_ART_DIR / 'generated'
OPTIMIZED_DIR = COVER_ART_DIR / 'optimized'

# Ensure directories exist
COVER_ART_DIR.mkdir(exist_ok=True)
GENERATED_DIR.mkdir(exist_ok=True)
OPTIMIZED_DIR.mkdir(exist_ok=True)

class PlaylistConfigParser:
    """Parse Alex Method playlist configuration files"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config_data = self._parse_config()
    
    def _parse_config(self) -> Dict[str, Any]:
        """Parse playlist configuration from markdown file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        content = self.config_path.read_text(encoding='utf-8')
        
        # Extract metadata
        config = {}
        
        # Parse Name (includes emoji and duration)
        name_match = re.search(r'\*\*Name\*\*:\s*(.+)', content)
        if name_match:
            full_name = name_match.group(1).strip()
            config['full_name'] = full_name
            
            # Extract emoji, name, and duration
            emoji_match = re.search(r'^([^\w\s]+)\s+(.+?)\s+-\s+Alex Method\s+\((\d+)min\)', full_name)
            if emoji_match:
                config['emoji'] = emoji_match.group(1)
                config['name'] = emoji_match.group(2)
                config['duration'] = emoji_match.group(3)
            else:
                config['name'] = full_name
        
        # Parse Description
        desc_match = re.search(r'\*\*Description\*\*:\s*(.+)', content)
        if desc_match:
            config['description'] = desc_match.group(1).strip()
        
        # Extract phase information
        phases = []
        phase_pattern = r'###\s+(.+?)\s*\((\d+)\s+minutes?\)\s*\n(.+?)(?=\*\*FORMAT|###|\n##|\Z)'
        
        for match in re.finditer(phase_pattern, content, re.DOTALL):
            phase_name = match.group(1).strip()
            phase_duration = match.group(2)
            phase_description = match.group(3).strip()
            
            phases.append({
                'name': phase_name,
                'duration': int(phase_duration),
                'description': phase_description
            })
        
        config['phases'] = phases
        
        return config
    
    def get_visual_theme(self) -> Dict[str, Any]:
        """Extract visual theme information for AI generation"""
        emoji = self.config_data.get('emoji', '🎵')
        name = self.config_data.get('name', 'Unnamed Playlist')
        description = self.config_data.get('description', '')
        phases = self.config_data.get('phases', [])
        
        # Theme mapping based on emoji and content - Enhanced for Alex Method branding
        theme_mappings = {
            '🔮': {
                'colors': 'cosmic deep blue, electric purple, neon cyan, neural network silver',
                'style': 'futuristic DJ interface, AI consciousness-themed, holographic, crystalline',
                'elements': 'neural networks, digital synapses, crystal formations, DJ control panels'
            },
            '⚡': {
                'colors': 'electric neon blue, lightning yellow, digital cyan, chrome silver',
                'style': 'high-energy electronic, consciousness awakening, electric storms, dynamic',
                'elements': 'lightning patterns, digital consciousness waves, electrical flows, sound visualizers'
            },
            '🚀': {
                'colors': 'deep space navy, cosmic purple, starlight silver, quantum blue',
                'style': 'space exploration, quantum mechanics, scientific precision, cosmic DJ',
                'elements': 'quantum particles, space nebulae, scientific instruments, orbital patterns'
            },
            '🌸': {
                'colors': 'soft blossom pink, zen green, healing blue, pearl white',
                'style': 'peaceful meditation, healing frequencies, organic flow, gentle energy',
                'elements': 'cherry blossoms, healing light rays, peaceful geometric patterns, sound waves'
            },
            '🎨': {
                'colors': 'artistic spectrum, creative gradients, painter palette, inspiration gold',
                'style': 'artistic expression, creative flow, sophisticated design, inspired energy',
                'elements': 'paint flow effects, color mixing, artistic brushstrokes, creative energy patterns'
            },
            '⚗️': {
                'colors': 'alchemical gold, mystical purple, transformation copper, wisdom bronze',
                'style': 'mystical alchemy, sound transformation, ancient wisdom meets modern DJ',
                'elements': 'alchemy symbols, transformation spirals, golden ratios, sound alchemy patterns'
            },
            '🧠': {
                'colors': 'neural pink, consciousness blue, synapse silver, intelligence gold',
                'style': 'brain network visualization, cognitive enhancement, neural pathways, intelligence',
                'elements': 'brain networks, neural pathways, synapse connections, consciousness patterns'
            },
            '🌊': {
                'colors': 'ocean deep blue, wave cyan, foam white, tide silver',
                'style': 'flowing water dynamics, wave patterns, oceanic depth, fluid motion',
                'elements': 'wave formations, water flow, oceanic patterns, tidal rhythms'
            },
            '🔥': {
                'colors': 'flame orange, ember red, fire yellow, smoke gray',
                'style': 'intense energy, fire dynamics, passionate heat, burning intensity',
                'elements': 'flame patterns, fire particles, heat waves, burning energy'
            },
            '🌟': {
                'colors': 'stellar gold, cosmic silver, starlight white, galaxy purple',
                'style': 'stellar formation, cosmic energy, star birth, celestial power',
                'elements': 'star formations, cosmic dust, celestial bodies, stellar energy'
            }
        }
        
        # Get theme or use default with Alex Method branding
        theme = theme_mappings.get(emoji, {
            'colors': 'cosmic deep blue, neural network silver, electric cyan, professional gradient',
            'style': 'professional DJ interface, modern electronic, sophisticated tech, premium design',
            'elements': 'DJ control elements, sound waves, geometric patterns, neural connections'
        })
        
        return {
            'emoji': emoji,
            'name': name,
            'description': description,
            'theme': theme,
            'phases': phases
        }

class CoverArtGenerator:
    """Generate AI cover art using OpenAI DALL-E 3"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
    
    def generate_cover_art(self, visual_theme: Dict[str, Any]) -> str:
        """Generate cover art using DALL-E 3"""
        
        # Build comprehensive prompt
        prompt = self._build_prompt(visual_theme)
        
        print(f"🎨 Generating cover art with prompt:")
        print(f"   {prompt}")
        
        # Call OpenAI API
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': OPENAI_MODEL,
            'prompt': prompt,
            'n': 1,
            'size': OPENAI_IMAGE_SIZE,
            'quality': OPENAI_IMAGE_QUALITY,
            'style': OPENAI_IMAGE_STYLE
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/images/generations",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            image_url = result['data'][0]['url']
            
            print(f"✅ Successfully generated cover art")
            return image_url
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error generating cover art: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Response: {e.response.text}")
            raise
    
    def _build_prompt(self, visual_theme: Dict[str, Any]) -> str:
        """Build detailed prompt for DALL-E 3 with Alex Method branding"""
        
        emoji = visual_theme['emoji']
        name = visual_theme['name']
        description = visual_theme['description']
        theme = visual_theme['theme']
        
        # Extract mood from first phase if available
        phase_moods = []
        for phase in visual_theme.get('phases', []):
            phase_desc = phase.get('description', '')
            if phase_desc:
                phase_moods.append(phase_desc.split(' - ')[0] if ' - ' in phase_desc else phase_desc[:50])
        
        mood_context = ', '.join(phase_moods[:2]) if phase_moods else description[:100]
        
        prompt = f"""Professional DJ playlist cover art for "{name}" - Alex Method style

BRAND IDENTITY & LAYOUT:
- Modern DJ interface aesthetic with subtle tech elements
- "Alex Method" branding in elegant, readable typography
- Clean geometric patterns and neural network inspiration
- Professional music streaming platform design
- Square 1024x1024 composition with centered focal point

VISUAL ELEMENTS:
- Central {emoji} symbol as primary focal point
- Cosmic/space background with starfield effects
- Geometric sacred geometry patterns (subtle)
- Neural network connections and nodes
- DJ interface elements (waveforms, equalizers, control panels)
- Holographic/neon accent lighting in blues and purples
- Modern glass/crystal effects with depth

COLOR PALETTE:
- Deep space blues and cosmic purples as base
- Bright cyan/electric blue accents and highlights
- Subtle pink/magenta neural connection points
- Clean white/silver for text and geometric elements
- Professional gradient overlays
- {theme['colors']} mood integration

TECHNICAL STYLE:
- {theme['style']} with DJ/electronic music aesthetic
- High-contrast design for thumbnail readability
- Premium album cover quality with commercial polish
- Sophisticated lighting effects and depth
- Clean, modern typography hierarchy
- {theme['elements']} seamlessly integrated

MOOD & ATMOSPHERE:
- {mood_context}
- Professional DJ brand identity
- Futuristic yet accessible design
- High-energy electronic music vibe
- Sophisticated and premium feel"""

        return prompt

class ImageOptimizer:
    """Optimize images for Spotify API requirements"""
    
    @staticmethod
    def download_and_save(image_url: str, output_path: Path, format_type: str = 'JPEG') -> Path:
        """Download image and save in specified format"""
        
        print(f"📥 Downloading image from URL...")
        
        # Download original image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Open with PIL
        img = Image.open(BytesIO(response.content))
        
        # Ensure square format
        if img.size != (1024, 1024):
            img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
        
        # Handle different formats
        if format_type.upper() == 'JPEG':
            # Ensure RGB mode for JPEG
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(output_path, format='JPEG', quality=95, optimize=True)
        elif format_type.upper() == 'PNG':
            # Keep transparency if present
            if img.mode == 'RGB':
                img = img.convert('RGBA')
            img.save(output_path, format='PNG', optimize=True)
        elif format_type.upper() == 'WEBP':
            img.save(output_path, format='WEBP', quality=95, optimize=True)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        file_size = output_path.stat().st_size
        print(f"✅ Image saved: {file_size/1024:.1f} KB ({format_type})")
        
        return output_path
    
    @staticmethod
    def optimize_for_spotify(image_path: Path, output_path: Path) -> Path:
        """Optimize existing image for Spotify (<256KB JPEG)"""
        
        print(f"🔧 Optimizing for Spotify API...")
        
        # Open existing image
        img = Image.open(image_path)
        
        # Ensure RGB mode for JPEG
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Ensure square format
        if img.size != (1024, 1024):
            img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
        
        # Optimize for Spotify's 256KB limit
        quality = 95
        
        while quality >= 50:
            # Save with current quality
            img.save(output_path, format='JPEG', quality=quality, optimize=True)
            
            # Check file size
            file_size = output_path.stat().st_size
            print(f"   Quality {quality}: {file_size/1024:.1f} KB")
            
            if file_size < 256000:  # Less than 256KB
                break
            
            quality -= 5
        
        final_size = output_path.stat().st_size
        print(f"✅ Spotify-optimized image saved: {final_size/1024:.1f} KB")
        
        return output_path
    
    @staticmethod
    def to_base64_spotify(image_path: Path) -> str:
        """Convert optimized image to base64 for Spotify API"""
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            base64_data = base64.b64encode(img_data).decode('utf-8')
        
        print(f"🔄 Converted to base64: {len(base64_data)} characters")
        return base64_data

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Generate AI cover art for Alex Method playlists')
    parser.add_argument('config_file', help='Path to playlist configuration .md file')
    parser.add_argument('--format', choices=['JPEG', 'PNG', 'WEBP'], default='JPEG', 
                       help='Image format for generated cover art (default: JPEG)')
    parser.add_argument('--spotify-optimize', action='store_true', 
                       help='Generate Spotify-optimized version (<256KB JPEG)')
    parser.add_argument('--base64', action='store_true', 
                       help='Generate base64 encoded version for Spotify API')
    
    args = parser.parse_args()
    
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Please check your .env file configuration:")
        print("   1. Copy .env.template to .env")
        print("   2. Get your OpenAI API key from https://platform.openai.com/api-keys")
        print("   3. Add: OPENAI_API_KEY=your-api-key-here")
        sys.exit(1)
    
    try:
        # Parse playlist configuration
        print(f"📋 Parsing playlist config: {args.config_file}")
        config_parser = PlaylistConfigParser(args.config_file)
        visual_theme = config_parser.get_visual_theme()
        
        playlist_name = visual_theme['name'].lower().replace(' ', '-')
        
        print(f"🎵 Playlist: {visual_theme['name']}")
        print(f"   Emoji: {visual_theme['emoji']}")
        print(f"   Description: {visual_theme['description'][:100]}...")
        
        # Generate cover art
        generator = CoverArtGenerator(OPENAI_API_KEY)
        image_url = generator.generate_cover_art(visual_theme)
        
        # Define file paths
        format_ext = args.format.lower()
        if format_ext == 'jpeg':
            format_ext = 'jpg'
        
        original_filename = f"{playlist_name}-original.{format_ext}"
        cover_filename = f"{playlist_name}-cover.{format_ext}"
        spotify_filename = f"{playlist_name}-spotify.jpg"
        
        original_path = GENERATED_DIR / original_filename
        cover_path = GENERATED_DIR / cover_filename
        spotify_path = OPTIMIZED_DIR / spotify_filename
        
        # Step 1: Download and save in requested format
        print(f"💾 Saving original in {args.format} format...")
        ImageOptimizer.download_and_save(image_url, original_path, args.format)
        
        # Step 2: Create clean version for visual inspection
        print(f"🎨 Creating clean cover version...")
        ImageOptimizer.download_and_save(image_url, cover_path, args.format)
        
        print(f"\n✅ Cover art generated successfully!")
        print(f"   Original: {original_path}")
        print(f"   Cover: {cover_path}")
        print(f"\n👀 You can now view the generated cover art to verify quality.")
        
        # Step 3: Spotify optimization (optional)
        if args.spotify_optimize:
            print(f"\n🔧 Creating Spotify-optimized version...")
            ImageOptimizer.optimize_for_spotify(cover_path, spotify_path)
            print(f"   Spotify-optimized: {spotify_path}")
        
        # Step 4: Base64 conversion (optional)
        if args.base64:
            if args.spotify_optimize:
                base64_source = spotify_path
                print(f"\n📝 Converting Spotify-optimized version to base64...")
            else:
                # Need to create JPEG version for Spotify API
                temp_jpeg = OPTIMIZED_DIR / f"{playlist_name}-temp.jpg"
                ImageOptimizer.optimize_for_spotify(cover_path, temp_jpeg)
                base64_source = temp_jpeg
                print(f"\n📝 Converting to base64 (creating JPEG version for Spotify API)...")
            
            base64_data = ImageOptimizer.to_base64_spotify(base64_source)
            base64_path = OPTIMIZED_DIR / f"{playlist_name}-base64.txt"
            base64_path.write_text(base64_data)
            print(f"   Base64 data saved to: {base64_path}")
        
        print(f"\n🎵 Ready for use with Alex Method DJ Platform!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
