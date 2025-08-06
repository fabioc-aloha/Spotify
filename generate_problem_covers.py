#!/usr/bin/env python3
"""
Special script to generate cover art for playlists that failed with the standard generator.
This script uses additional content filtering to ensure the prompts are accepted by the API.
"""

import os
import sys
import re
import json
import base64
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv
import argparse

# Load environment variables from .env file
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("❌ Error: OPENAI_API_KEY not found in environment variables or .env file")
    print("Create a .env file with your OpenAI API key: OPENAI_API_KEY=your-api-key")
    sys.exit(1)
# Ensure it's a string for type checking
OPENAI_API_KEY = str(OPENAI_API_KEY)

# API Configuration
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'dall-e-3')
OPENAI_IMAGE_SIZE = os.getenv('OPENAI_IMAGE_SIZE', '1024x1024')
OPENAI_IMAGE_QUALITY = os.getenv('OPENAI_IMAGE_QUALITY', 'hd')
OPENAI_IMAGE_STYLE = os.getenv('OPENAI_IMAGE_STYLE', 'vivid')

# Directory Configuration
COVER_ART_DIR = Path('cover-art')
GENERATED_DIR = COVER_ART_DIR / 'generated'

# Ensure directories exist
COVER_ART_DIR.mkdir(exist_ok=True)
GENERATED_DIR.mkdir(exist_ok=True)

# List of problematic playlists
PROBLEM_PLAYLISTS = [
    "bpm-energy-curve",
    "brazilian-rock-80s-90s",
    "ketamine-therapy",
    "loud-music-escalation",
]

class SimplifiedCoverGenerator:
    """Generate covers for problematic playlists with simplified prompts"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def generate_cover_for_playlist(self, playlist_name: str) -> bool:
        """Generate cover art for a specific playlist using minimal information"""
        
        print(f"🎨 Processing {playlist_name}...")
        
        # Construct path to the playlist config file
        config_path = Path(f"playlist-configs/{playlist_name}.md")
        if not config_path.exists():
            print(f"❌ Error: Playlist config not found: {config_path}")
            return False
        
        try:
            # Extract basic metadata
            content = config_path.read_text(encoding='utf-8')
            name_match = re.search(r'(?:- )?\*\*Name\*\*:\s*([^\n]+)', content)
            description_match = re.search(r'(?:- )?\*\*Description\*\*:\s*([^\n]+)', content)
            emoji_match = re.search(r'(?:- )?\*\*Emoji\*\*:\s*([^\n]+)', content)
            
            # Create simplified visual theme info
            name = name_match.group(1).strip() if name_match else f"{playlist_name.title()} Playlist"
            description = description_match.group(1).strip() if description_match else "An Alex Method playlist"
            emoji = emoji_match.group(1).strip() if emoji_match else "🎵"
            
            # Clean name and description for safe prompting
            clean_name = re.sub(r'[^\w\s\-\'",.:;!?&()]', '', name)
            clean_description = re.sub(r'[^\w\s\-\'",.:;!?&()]', '', description)
            if len(clean_description) > 100:
                clean_description = clean_description[:100] + "..."
            
            # Create a very simplified prompt
            prompt = self._create_safe_prompt(clean_name, clean_description, emoji)
            
            # Generate background using OpenAI API
            background_url = self._generate_background(prompt)
            
            # Create cover art
            self._create_cover_art(background_url, name, emoji, playlist_name)
            
            print(f"✅ Successfully generated cover art for {playlist_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error processing {playlist_name}: {e}")
            return False
    
    def _create_safe_prompt(self, name: str, description: str, emoji: str) -> str:
        """Create a minimal, safe prompt for OpenAI that avoids policy violations"""
        
        # Extract the primary theme
        words = name.lower().split()
        if "ketamine" in words:
            theme = "therapeutic relaxation"  # Avoid mentioning restricted terms
        elif "bpm" in words:
            theme = "dynamic energy progression"
        elif "brazilian" in words:
            theme = "brazilian music culture"
        elif "loud" in words:
            theme = "powerful audio experience"
        else:
            theme = "music playlist"
        
        # Create a safe prompt focusing just on visual elements
        prompt = f"""Create an abstract artistic background for a music playlist with these themes:
- {theme}
- {emoji} visual elements
- Professional music cover art style
- Appropriate for all audiences

Requirements:
- Create ONLY the background image (no text)
- Square 1024x1024 composition
- Leave center area clean for text overlay
- Make the image realistic but artistic
- Focus on shapes, colors, and textures related to the theme
- Avoid any text, logos, or offensive imagery
- Use a professional color palette suitable for a music playlist

IMPORTANT: Background only - no text, no words."""

        print(f"Using safe prompt for {name}:")
        print(f"Theme: {theme}, Emoji: {emoji}")
        return prompt
    
    def _generate_background(self, prompt: str) -> str:
        """Generate background image using DALL-E 3"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": OPENAI_MODEL,
            "prompt": prompt,
            "size": OPENAI_IMAGE_SIZE,
            "quality": OPENAI_IMAGE_QUALITY,
            "style": OPENAI_IMAGE_STYLE,
            "n": 1
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            image_url = response.json()["data"][0]["url"]
            return image_url
        except Exception as e:
            print(f"❌ Error generating background: {e}")
            raise
    
    def _create_cover_art(self, background_url: str, name: str, emoji: str, playlist_name: str) -> None:
        """Create cover art with text overlay"""
        
        try:
            # Download background image
            response = requests.get(background_url)
            response.raise_for_status()
            background = Image.open(BytesIO(response.content)).convert("RGBA")
            
            # Create overlay
            overlay = Image.new('RGBA', background.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Clean name - remove emoji and "Alex Method" suffix
            clean_name = re.sub(r'[^\w\s\-\'",.:;!?&()]', '', name)
            clean_name = re.sub(r'\s*-\s*Alex Method.*$', '', clean_name, flags=re.IGNORECASE)
            clean_name = clean_name.strip()
            
            # Try to use Arial Bold for stronger text
            try:
                title_font = ImageFont.truetype("arialbd.ttf", 72)
                brand_font = ImageFont.truetype("arialbd.ttf", 36)
                brand_small_font = ImageFont.truetype("arialbd.ttf", 24)
            except:
                try:
                    # Fallback to regular Arial
                    title_font = ImageFont.truetype("arial.ttf", 82)
                    brand_font = ImageFont.truetype("arial.ttf", 40)
                    brand_small_font = ImageFont.truetype("arial.ttf", 26)
                except:
                    title_font = ImageFont.load_default()
                    brand_font = ImageFont.load_default()
                    brand_small_font = ImageFont.load_default()
            
            # Add text with shadow
            # Add semi-transparent background for text
            title_bbox = draw.textbbox((0, 0), clean_name, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
            
            # Calculate text position (centered)
            text_x = (background.width - title_width) // 2
            text_y = (background.height - title_height) // 2
            
            # Semi-transparent background
            padding = 20
            bg_rect = (
                text_x - padding,
                text_y - padding,
                text_x + title_width + padding,
                text_y + title_height + padding
            )
            draw.rectangle(bg_rect, fill=(0, 0, 0, 128))
            
            # Shadow
            draw.text((text_x + 2, text_y + 2), clean_name, font=title_font, fill=(0, 0, 0, 180))
            
            # Main text
            draw.text((text_x, text_y), clean_name, font=title_font, fill=(255, 255, 255, 255))
            
            # Add Alex Method branding
            brand_text = "ALEX METHOD"
            brand_bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
            brand_width = brand_bbox[2] - brand_bbox[0]
            
            # Calculate text dimensions for "DJ"
            dj_bbox = draw.textbbox((0, 0), "DJ", font=brand_small_font)
            dj_width = dj_bbox[2] - dj_bbox[0]
            
            # Create semi-transparent background for branding
            brand_bg_padding = 10
            brand_x = (background.width - brand_width - dj_width - 10) // 2
            brand_y = background.height - 60
            
            # Get approximate font height
            font_height = 36  # Use the same size we specified when creating the font
            
            brand_bg_rect = (
                brand_x - brand_bg_padding,
                brand_y - brand_bg_padding,
                brand_x + brand_width + dj_width + 10 + (brand_bg_padding * 2),
                brand_y + font_height + (brand_bg_padding * 2)
            )
            
            # Draw semi-transparent background
            draw.rectangle(brand_bg_rect, fill=(0, 0, 0, 128))
            
            # Shadow for ALEX METHOD
            shadow_offset = 2
            draw.text((brand_x + shadow_offset, brand_y + shadow_offset), 
                    brand_text, font=brand_font, fill=(0, 0, 0, 180))
            
            # ALEX METHOD text
            draw.text((brand_x, brand_y), brand_text, font=brand_font, fill=(255, 255, 255, 255))
            
            # Draw DJ
            dj_x = brand_x + brand_width + 10
            dj_y = brand_y + 12
            
            # Shadow for DJ
            draw.text((dj_x + shadow_offset, dj_y + shadow_offset), 
                    "DJ", font=brand_small_font, fill=(0, 0, 0, 180))
            
            # DJ text
            draw.text((dj_x, dj_y), "DJ", font=brand_small_font, fill=(255, 255, 255, 255))
            
            # Composite background and overlay
            result = Image.alpha_composite(background, overlay)
            
            # Save as PNG
            png_path = GENERATED_DIR / f"{playlist_name}.png"
            result.save(png_path)
            print(f"   📁 PNG: {png_path}")
            
            # Save as JPEG (no transparency)
            jpg_path = GENERATED_DIR / f"{playlist_name}.jpg"
            jpg_image = result.convert("RGB")
            jpg_image.save(jpg_path, quality=95)
            print(f"   📁 JPEG: {jpg_path}")
            
            # Save as Base64 for embedding
            base64_path = GENERATED_DIR / f"{playlist_name}_base64.txt"
            buffered = BytesIO()
            jpg_image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            with open(base64_path, 'w') as f:
                f.write(img_str)
            print(f"   📁 Base64: {base64_path}")
            
        except Exception as e:
            print(f"❌ Error creating cover art: {e}")
            raise


def main():
    """Generate covers for problematic playlists"""
    
    parser = argparse.ArgumentParser(
        description="Generate covers for playlists that failed with the standard generator"
    )
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force regeneration even if cover art exists"
    )
    parser.add_argument(
        "--playlist", 
        help="Generate for a specific playlist only"
    )
    args = parser.parse_args()
    
    generator = SimplifiedCoverGenerator(OPENAI_API_KEY)
    success_count = 0
    failure_count = 0
    
    # Process a specific playlist or all problem playlists
    playlists_to_process = [args.playlist] if args.playlist else PROBLEM_PLAYLISTS
    
    for playlist_name in playlists_to_process:
        print(f"\n🎵 Processing {playlist_name}...")
        
        # Check if cover art exists already
        if not args.force:
            existing_files = []
            for ext in ['.png', '.jpg']:
                file_path = GENERATED_DIR / f"{playlist_name}{ext}"
                if file_path.exists():
                    existing_files.append(file_path)
            
            if existing_files:
                print(f"📁 Found {len(existing_files)} existing cover art files:")
                for path in existing_files:
                    print(f"   ✅ {path.suffix[1:].upper()}: {path}")
                print("Use --force to regenerate the cover art.")
                continue
        
        # Generate cover art
        result = generator.generate_cover_for_playlist(playlist_name)
        if result:
            success_count += 1
        else:
            failure_count += 1
    
    print(f"\n✅ Processing complete: {success_count} successful, {failure_count} failed")


if __name__ == "__main__":
    main()
