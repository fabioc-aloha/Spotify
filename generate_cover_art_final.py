#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alex Method DJ Platform - AI Cover Art Generator (Final Version)
Generates high-quality playlist cover art with AI backgrounds and professional branding

Usage:
    python generate_cover_art_final.py <playlist_config.md> [options]

Options:
    --force       Force regeneration of cover art even if files exist
    --preview     Open the generated image in the default viewer
    --batch       Process multiple playlists (provide a directory instead of a file)

Examples:
    python generate_cover_art_final.py playlist-configs/neural-network-symphony.md
    python generate_cover_art_final.py playlist-configs/coffee-shop.md --preview
    python generate_cover_art_final.py playlist-configs/space-odyssey.md --force
    python generate_cover_art_final.py playlist-configs/ --batch --force

Note: For playlists that consistently fail with API errors, use generate_problem_covers.py
"""

import os
import sys

# Safe print function for Windows console encoding issues
def safe_print(text):
    """Print text safely, handling Windows console encoding issues"""
    try:
        # Replace common emoji patterns with text alternatives
        import re
        
        # Replace specific emojis with text equivalents
        text = re.sub(r'📋', '[INFO]', text)
        text = re.sub(r'🎵', '[MUSIC]', text)
        text = re.sub(r'❌', '[ERROR]', text)
        text = re.sub(r'⚠️', '[WARNING]', text)
        text = re.sub(r'✅', '[SUCCESS]', text)
        text = re.sub(r'📁', '[FOLDER]', text)
        text = re.sub(r'🎨', '[ART]', text)
        
        # Remove any remaining emoji characters
        emoji_pattern = re.compile("["
                                  u"\U0001F600-\U0001F64F"  # emoticons
                                  u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                  u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                  u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                  u"\U00002702-\U000027B0"  # dingbats
                                  u"\U000024C2-\U0001F251"
                                  "]+", flags=re.UNICODE)
        text = emoji_pattern.sub('[EMOJI]', text)
        
        print(text)
    except UnicodeEncodeError:
        # Fallback: remove all non-ASCII characters
        ascii_text = text.encode('ascii', 'ignore').decode('ascii')
        print(ascii_text)
import re
import json
import base64
import requests
import time
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
from pathlib import Path
import argparse
from typing import Dict, Any, Optional, Tuple, List
from dotenv import load_dotenv
import textwrap
import subprocess
import glob
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    safe_print("❌ Error: OPENAI_API_KEY not found in environment variables or .env file")
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

# Ensure directory exists
COVER_ART_DIR.mkdir(exist_ok=True)


class PlaylistConfigParser:
    """Parse Alex Method playlist configuration files"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config_data = self._parse_config()
    
    def _parse_config(self) -> Dict[str, Any]:
        """Parse the playlist configuration file and extract metadata"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Playlist config not found: {self.config_path}")
            
            content = self.config_path.read_text(encoding='utf-8')
            
            # Extract basic metadata
            name_match = re.search(r'(?:- )?\*\*Name\*\*:\s*([^\n]+)', content)
            description_match = re.search(r'(?:- )?\*\*Description\*\*:\s*([^\n]+)', content)
            emoji_match = re.search(r'(?:- )?\*\*Emoji\*\*:\s*([^\n]+)', content)
            
            # Basic metadata
            metadata = {
                'name': name_match.group(1).strip() if name_match else f"{self.config_path.stem.title()} Playlist",
                'description': description_match.group(1).strip() if description_match else "An Alex Method playlist",
                'emoji': emoji_match.group(1).strip() if emoji_match else "🎵",
                'file_content': content  # Store full content for prompt generation
            }
            
            return metadata
            
        except Exception as e:
            safe_print(f"❌ Error parsing playlist config: {e}")
            raise
    
    def get_visual_theme(self) -> Dict[str, Any]:
        """Extract visual theming information from the config"""
        return {
            'name': self.config_data.get('name', ''),
            'description': self.config_data.get('description', ''),
            'emoji': self.config_data.get('emoji', '🎵'),
            'file_content': self.config_data.get('file_content', '')
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Get basic playlist information"""
        return self.config_data


class BackgroundGenerator:
    """Generate AI backgrounds using OpenAI DALL-E"""
    
    def __init__(self, api_key: str, config_path: Optional[str] = None):
        self.api_key = api_key
        self.config_path = config_path
    
    def _sanitize_content_for_ai(self, content: str) -> str:
        """Sanitize content to avoid OpenAI content policy violations"""
        import re
        
        # Remove or replace problematic terms that might trigger content policy
        problematic_terms = {
            # Mystical/spiritual terms
            'alchemical': 'transformative',
            'alchemy': 'transformation',
            'mystical': 'mysterious',
            'spiritual': 'inspirational', 
            'sacred': 'special',
            'enlightened': 'elevated',
            'transcendent': 'uplifting',
            'transmutation': 'transformation',
            'purification': 'refinement',
            'consciousness': 'awareness',
            'awakening': 'discovery',
            
            # Medical/therapeutic terms
            'therapy': 'relaxation',
            'therapeutic': 'calming',
            'amygdala': 'mind',
            'neuroscience': 'science',
            'trauma': 'healing',
            'depression': 'mood',
            'anxiety': 'calm',
            'ketamine': 'ambient',
            
            # Potentially problematic descriptors
            'intense alchemical work': 'deep musical transformation',
            'fundamental change occurs': 'musical evolution happens',
            'purification process': 'refinement journey',
            'golden achievement': 'perfect harmony',
        }
        
        sanitized = content
        for problematic, safe in problematic_terms.items():
            sanitized = re.sub(re.escape(problematic), safe, sanitized, flags=re.IGNORECASE)
        
        return sanitized

    def _build_background_prompt(self, visual_theme: Dict[str, Any]) -> str:
        """Build background-focused prompt for DALL-E 3 with structured field injection"""
        
        emoji = visual_theme.get('emoji', '🎵')
        name = visual_theme.get('name', '')
        
        # Get the original playlist configuration file content
        playlist_content = ""
        
        if self.config_path:
            # Read the playlist configuration file if available
            try:
                playlist_file_path = Path(self.config_path)
                if playlist_file_path.exists():
                    playlist_content = playlist_file_path.read_text(encoding='utf-8')
                    
                    # Sanitize content to avoid content policy violations
                    playlist_content = self._sanitize_content_for_ai(playlist_content)
                    
                    # Remove track list section to reduce prompt length
                    track_list_pattern = re.compile(r'### Track List[^\n]*\n.*?(?=##|\Z)', re.DOTALL)
                    playlist_content = track_list_pattern.sub('', playlist_content)
                    
                    # Also limit the overall length of the playlist content
                    max_content_length = 3500  # Reduced to leave room for structured prompt
                    if len(playlist_content) > max_content_length:
                        # Keep metadata and first few sections
                        playlist_content = playlist_content[:max_content_length] + "\n..."
                        print(f"   Note: Playlist content truncated to {max_content_length} characters")
            except Exception as e:
                print(f"Warning: Could not read playlist file: {e}")
        
        # Build the structured prompt with field injection
        prompt = f"""Please create a background image for a **Spotify playlist cover**.

Playlist Theme: {playlist_content}
Primary Mood/Concept: {emoji}

Image Requirements:
- Square composition (1024x1024)
- Realistic yet artistic — aim for emotional impact and visual clarity
- No text, no logos, no faces, no branding
- Must visually represent the theme and mood of the playlist
- Central area or upper-center should be visually calm or low-detail to allow for **title overlay** (Spotify places text prominently in this area)
- Important: Treat this as a Spotify playlist cover where the **title and creator name will be placed over the image**
- Focal elements should avoid the middle-top region to prevent clashing with text
- Visual storytelling should be preserved even when text is overlaid

Final Output:
- Background-only artwork suitable for professional cover usage"""

        return prompt
    
    def generate_background(self, visual_theme: Dict[str, Any]) -> str:
        """Generate background image using DALL-E 3"""
        
        prompt = self._build_background_prompt(visual_theme)
        safe_print(f"🎨 Generating AI background with prompt:")
        # Print a truncated version of the prompt for clarity
        safe_print(f"   {prompt.split('Requirements:')[0][:200]}...")
        safe_print(f"   Requirements: (artistic, realistic background with clean center for text)")
        
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
            response.raise_for_status()  # Raise exception for non-2xx responses
            
            image_url = response.json()["data"][0]["url"]
            print("✅ Successfully generated background")
            return image_url
        except Exception as e:
            safe_print(f"❌ Error generating background: {e}")
            raise


class CoverArtComposer:
    """Compose final cover art with AI background + Python overlay"""
    
    def __init__(self):
        self.canvas_size = (1024, 1024)
        self.emoji_size = 180
        self.title_size = 84  # Increased from 72 for better small thumbnail readability
        self.brand_size = 36
        self.brand_small_size = 24
    
    def _create_overlay(self, visual_theme: Dict[str, Any]) -> Image.Image:
        """Create text and branding overlay"""
        
        # Create transparent overlay
        overlay = Image.new('RGBA', self.canvas_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        name = visual_theme['name']
        
        # Clean up playlist name - remove emoji and Alex Method suffix since it's in the branding
        # Remove all emoji characters from anywhere in the title
        clean_name = re.sub(r'[^\w\s\-\'",.:;!?&()]', '', name)
        # Then remove Alex Method suffix
        clean_name = re.sub(r'\s*-\s*Alex Method.*$', '', clean_name, flags=re.IGNORECASE)
        # Trim all whitespace from both ends and normalize internal spacing
        clean_name = re.sub(r'\s+', ' ', clean_name.strip())
        
        # Load fonts (fallback to default if custom fonts not available)
        try:
            # Try to use Arial Bold for stronger text
            title_font = ImageFont.truetype("arialbd.ttf", self.title_size)
            brand_font = ImageFont.truetype("arialbd.ttf", self.brand_size)
            brand_small_font = ImageFont.truetype("arialbd.ttf", self.brand_small_size)
        except:
            try:
                # Fallback to regular Arial but with larger size for stronger presence
                title_font = ImageFont.truetype("arial.ttf", self.title_size + 10)
                brand_font = ImageFont.truetype("arial.ttf", self.brand_size + 4)
                brand_small_font = ImageFont.truetype("arial.ttf", self.brand_small_size + 2)
            except:
                title_font = ImageFont.load_default()
                brand_font = ImageFont.load_default()
                brand_small_font = ImageFont.load_default()
        
        # Position the title text at the top of the image (centered horizontally)
        self._add_text_with_shadow(overlay, clean_name, title_font, (512, 180), max_width=900)
        
        # Add Alex Method branding at the bottom
        self._add_alex_method_branding(overlay, brand_font, brand_small_font)
        
        # Add subtle overlay effects
        overlay = self._add_subtle_effects(overlay)
        
        return overlay
    
    def _add_subtle_effects(self, overlay: Image.Image) -> Image.Image:
        """Add subtle effects to make overlay stand out"""
        # The overlay is already good as is
        return overlay
    
    def _add_text_with_shadow(self, overlay: Image.Image, text: str, font: Any, 
                            position: Tuple[int, int], max_width: int = 800) -> None:
        """Add text with strong outline and shadow for better readability without background box"""
        draw = ImageDraw.Draw(overlay)
        
        # Wrap text to fit width
        lines = self._wrap_text(text, font, max_width)
        
        # Calculate text block dimensions
        line_heights = []
        line_widths = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_heights.append(bbox[3] - bbox[1])
            line_widths.append(bbox[2] - bbox[0])
        
        text_block_height = sum(line_heights)
        text_block_width = max(line_widths)
        
        # Calculate starting position
        x, y = position
        x = x - (text_block_width // 2)  # Center horizontally
        y = y - (text_block_height // 2)  # Center vertically
        
        # Draw each line of text with enhanced effects
        current_y = y
        for i, line in enumerate(lines):
            # Trim each line and recalculate centering for perfect alignment
            line = line.strip()
            
            # Calculate precise centering for this line
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_x = position[0] - (line_width // 2)  # Center this specific line
            
            # Create strong outline effect by drawing text in multiple directions
            outline_thickness = 3
            outline_color = (0, 0, 0, 255)  # Solid black outline
            
            # Draw outline in 8 directions for thick border effect
            for dx in [-outline_thickness, 0, outline_thickness]:
                for dy in [-outline_thickness, 0, outline_thickness]:
                    if dx != 0 or dy != 0:  # Skip center position
                        draw.text((line_x + dx, current_y + dy), line, font=font, fill=outline_color)
            
            # Draw additional shadow for depth
            shadow_offset = 4
            shadow_color = (0, 0, 0, 180)
            draw.text((line_x + shadow_offset, current_y + shadow_offset), line, font=font, fill=shadow_color)
            
            # Draw main text in white
            draw.text((line_x, current_y), line, font=font, fill=(255, 255, 255, 255))
            
            current_y += line_heights[i]
    
    def _wrap_text(self, text: str, font: Any, max_width: int) -> List[str]:
        """Wrap text to fit within max_width pixels"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Try adding this word to the current line
            test_line = ' '.join(current_line + [word])
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                # Line would be too long with this word
                if current_line:
                    lines.append(' '.join(current_line).strip())  # Trim each line
                    current_line = [word]
                else:
                    lines.append(word.strip())  # Single word too long, add anyway but trimmed
        
        if current_line:
            lines.append(' '.join(current_line).strip())  # Trim final line
        
        return lines
    
    def _add_alex_method_branding(self, overlay: Image.Image, brand_font: Any, 
                                brand_small_font: Any) -> None:
        """Add Alex Method branding with enhanced readability - centered at bottom with strong outline effects"""
        draw = ImageDraw.Draw(overlay)
        
        # Two-line branding at the bottom
        brand_text = "ALEX METHOD"
        dj_text = "DJ"
        
        # Calculate text dimensions for centering
        bbox_brand = draw.textbbox((0, 0), brand_text, font=brand_font)
        brand_width = bbox_brand[2] - bbox_brand[0]
        brand_height = bbox_brand[3] - bbox_brand[1]
        
        bbox_dj = draw.textbbox((0, 0), dj_text, font=brand_small_font)
        dj_width = bbox_dj[2] - bbox_dj[0]
        dj_height = bbox_dj[3] - bbox_dj[1]
        
        # Center horizontally, position at bottom
        center_x = self.canvas_size[0] // 2
        
        # Position "ALEX METHOD" line at bottom with margin
        brand_x = center_x - (brand_width // 2)
        brand_y = self.canvas_size[1] - 80  # 80px from bottom
        
        # Position "DJ" line below "ALEX METHOD"
        dj_x = center_x - (dj_width // 2)
        dj_y = brand_y + brand_height + 8  # 8px spacing between lines
        
        # Enhanced text effects for "ALEX METHOD" without background box
        outline_thickness = 2
        outline_color = (0, 0, 0, 255)  # Solid black outline
        
        # Draw outline in 8 directions for "ALEX METHOD"
        for dx in [-outline_thickness, 0, outline_thickness]:
            for dy in [-outline_thickness, 0, outline_thickness]:
                if dx != 0 or dy != 0:  # Skip center position
                    draw.text((brand_x + dx, brand_y + dy), brand_text, font=brand_font, fill=outline_color)
        
        # Draw shadow for "ALEX METHOD"
        shadow_offset = 3
        draw.text((brand_x + shadow_offset, brand_y + shadow_offset), 
                brand_text, font=brand_font, fill=(0, 0, 0, 180))
        
        # Draw main "ALEX METHOD" text
        draw.text((brand_x, brand_y), brand_text, font=brand_font, fill=(255, 255, 255, 255))
        
        # Enhanced text effects for "DJ"
        outline_thickness_small = 2
        
        # Draw outline in 8 directions for "DJ"
        for dx in [-outline_thickness_small, 0, outline_thickness_small]:
            for dy in [-outline_thickness_small, 0, outline_thickness_small]:
                if dx != 0 or dy != 0:  # Skip center position
                    draw.text((dj_x + dx, dj_y + dy), dj_text, font=brand_small_font, fill=outline_color)
        
        # Draw shadow for "DJ"
        draw.text((dj_x + shadow_offset, dj_y + shadow_offset), 
                dj_text, font=brand_small_font, fill=(0, 0, 0, 180))
        
        # Draw main "DJ" text
        draw.text((dj_x, dj_y), dj_text, font=brand_small_font, fill=(255, 255, 255, 255))
    
    def compose_cover_art(self, background_url: str, visual_theme: Dict[str, Any], 
                        output_path: Path) -> Tuple[Path, Path, Path]:
        """Compose the final cover art image with AI background and Python overlay"""
        safe_print(f"🎨 Composing cover art with Python overlay...")
        
        # Download background image
        try:
            response = requests.get(background_url)
            response.raise_for_status()
            background = Image.open(BytesIO(response.content))
        except Exception as e:
            safe_print(f"❌ Error downloading background image: {e}")
            raise
        
        # Create overlay with text and branding
        overlay = self._create_overlay(visual_theme)
        
        # Composite background and overlay
        background = background.convert("RGBA")
        result = Image.alpha_composite(background, overlay)
        
        # Save as PNG (with transparency)
        png_path = f"{output_path}.png"
        result.save(png_path)
        safe_print(f"   📁 PNG: {png_path}")
        
        # Save as JPEG (no transparency)
        jpg_path = f"{output_path}.jpg"
        jpg_image = result.convert("RGB")
        jpg_image.save(jpg_path, quality=95)
        safe_print(f"   📁 JPEG: {jpg_path}")
        
        # Save as Base64 for embedding
        base64_path = f"{output_path}_base64.txt"
        buffered = BytesIO()
        jpg_image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        with open(base64_path, 'w') as f:
            f.write(img_str)
        safe_print(f"   📁 Base64: {base64_path}")
        
        safe_print(f"✅ Cover art composed successfully!")
        
        return Path(png_path), Path(jpg_path), Path(base64_path)


def update_playlist_metadata_with_cover_art(config_file: str, cover_art_paths: Tuple[Path, Path, Path]) -> bool:
    """Update playlist config file with generated cover art paths"""
    try:
        config_path = Path(config_file)
        if not config_path.exists():
            safe_print(f"❌ Config file not found: {config_file}")
            return False
        
        # Read the current config content
        content = config_path.read_text(encoding='utf-8')
        
        png_path, jpg_path, base64_path = cover_art_paths
        
        # Get relative paths for cleaner metadata
        try:
            png_rel = png_path.relative_to(Path.cwd())
            jpg_rel = jpg_path.relative_to(Path.cwd())
            base64_rel = base64_path.relative_to(Path.cwd())
        except ValueError:
            # If relative path fails, use absolute paths
            png_rel = png_path
            jpg_rel = jpg_path
            base64_rel = base64_path
        
        # Create cover art metadata section
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cover_art_section = f"""## Cover Art
- **PNG**: {png_rel}
- **JPEG**: {jpg_rel}
- **Base64**: {base64_rel}
- **Generated**: {timestamp}

"""
        
        # Check if Cover Art section already exists
        cover_art_pattern = re.compile(r'^## Cover Art\n.*?(?=^##|\Z)', re.MULTILINE | re.DOTALL)
        
        if cover_art_pattern.search(content):
            # Replace existing Cover Art section
            content = cover_art_pattern.sub(cover_art_section.rstrip() + '\n\n', content)
            print("   📝 Updated existing Cover Art metadata")
        else:
            # Add Cover Art section after Metadata section
            metadata_pattern = re.compile(r'(^## Metadata\n.*?(?=^##))', re.MULTILINE | re.DOTALL)
            metadata_match = metadata_pattern.search(content)
            
            if metadata_match:
                # Insert after Metadata section
                insert_pos = metadata_match.end()
                content = content[:insert_pos] + '\n' + cover_art_section + content[insert_pos:]
                print("   📝 Added Cover Art metadata after Metadata section")
            else:
                # Fallback: add at the beginning after title
                title_pattern = re.compile(r'^# [^\n]+\n', re.MULTILINE)
                title_match = title_pattern.search(content)
                
                if title_match:
                    insert_pos = title_match.end()
                    content = content[:insert_pos] + '\n' + cover_art_section + content[insert_pos:]
                    print("   📝 Added Cover Art metadata after title")
                else:
                    # Last resort: add at the very beginning
                    content = cover_art_section + content
                    print("   📝 Added Cover Art metadata at beginning")
        
        # Write back to file
        config_path.write_text(content, encoding='utf-8')
        safe_print(f"✅ Updated playlist metadata: {config_file}")
        return True
        
    except Exception as e:
        safe_print(f"❌ Error updating metadata: {e}")
        return False


def get_existing_cover_art(config_name: str) -> List[Path]:
    """Check if cover art already exists for this config"""
    config_name = Path(config_name).stem
    existing_files = []
    
    # Check for PNG
    png_path = COVER_ART_DIR / f"{config_name}.png"
    if png_path.exists():
        existing_files.append(png_path)
    
    # Check for JPEG
    jpg_path = COVER_ART_DIR / f"{config_name}.jpg"
    if jpg_path.exists():
        existing_files.append(jpg_path)
    
    # Check for Base64
    base64_path = COVER_ART_DIR / f"{config_name}_base64.txt"
    if base64_path.exists():
        existing_files.append(base64_path)
    
    return existing_files


def process_single_playlist(config_file: str, force: bool = False, preview: bool = False) -> bool:
    """Process a single playlist configuration file"""
    try:
        # Check if this is a known problematic playlist
        config_name = Path(config_file).stem
        PROBLEM_PLAYLISTS = [
            "bpm-energy-curve",
            "brazilian-rock-80s-90s",
            "ketamine-therapy",
            "loud-music-escalation",
        ]
        
        if config_name in PROBLEM_PLAYLISTS:
            safe_print(f"⚠️ {config_name} is a known problematic playlist.")
            safe_print(f"   Please use generate_problem_covers.py instead:")
            safe_print(f"   python generate_problem_covers.py --playlist {config_name}")
            return False
        
        # Parse the playlist config
        safe_print(f"📋 Parsing playlist config: {config_file}")
        parser = PlaylistConfigParser(config_file)
        playlist_info = parser.get_info()
        visual_theme = parser.get_visual_theme()
        
        # Show basic info
        name = playlist_info.get('name', 'Unknown Playlist')
        description = playlist_info.get('description', 'No description')
        if len(description) > 70:
            description = description[:67] + "..."
        emoji = playlist_info.get('emoji', '🎵')
        
        safe_print(f"🎵 Playlist: {name}")
        safe_print(f"   Emoji: {emoji}")
        safe_print(f"   Description: {description}")
        
        # Check if cover art already exists
        config_name = Path(config_file).stem
        existing_files = get_existing_cover_art(config_name)
        existing_count = len(existing_files)
        
        if existing_count > 0 and not force:
            safe_print(f"📁 Found {existing_count} existing cover art files:")
            for path in existing_files:
                format_name = path.suffix[1:].lower()
                if "base64" in path.name:
                    format_name = "BASE64"
                if path:
                    safe_print(f"   ✅ {format_name.upper()}: {path}")
            safe_print("\nUse --force to regenerate the cover art.")
            return False
        elif existing_count > 0 and force:
            safe_print(f"📁 Found {existing_count} existing cover art files, but --force flag is set.")
            safe_print("   Will regenerate cover art...")
        else:
            safe_print("📁 No existing cover art found - will generate new files")
        
        # Generate AI background
        generator = BackgroundGenerator(OPENAI_API_KEY, config_file)
        background_url = generator.generate_background(visual_theme)
        
        # Compose final cover art
        output_path = COVER_ART_DIR / config_name
        
        composer = CoverArtComposer()
        png_path, jpg_path, base64_path = composer.compose_cover_art(background_url, visual_theme, output_path)
        
        # Update playlist metadata with cover art paths
        cover_art_paths = (png_path, jpg_path, base64_path)
        metadata_updated = update_playlist_metadata_with_cover_art(config_file, cover_art_paths)
        
        if not metadata_updated:
            print("⚠️ Warning: Failed to update playlist metadata, but cover art was generated successfully")
        
        # Preview the image if requested
        if preview:
            if sys.platform == 'win32':
                os.startfile(png_path)
            elif sys.platform == 'darwin':
                subprocess.call(['open', png_path])
            else:
                subprocess.call(['xdg-open', png_path])
            safe_print(f"🔍 Opening preview of {png_path}")
        
        safe_print(f"🎵 Ready for use with Alex Method DJ Platform!")
        return True
        
    except Exception as e:
        safe_print(f"❌ Error processing {config_file}: {e}")
        return False


def main():
    """Main entry point for the cover art generator"""
    parser = argparse.ArgumentParser(
        description="Alex Method DJ Platform - AI Cover Art Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "config_file", 
        help="Path to playlist config file or directory (for batch mode)"
    )
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force regeneration even if cover art exists"
    )
    parser.add_argument(
        "--preview", 
        action="store_true", 
        help="Open the generated image for preview"
    )
    parser.add_argument(
        "--batch", 
        action="store_true", 
        help="Process multiple playlists (provide directory instead of file)"
    )
    args = parser.parse_args()
    
    # Check if OpenAI API key is available
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Create a .env file with your OpenAI API key or set the environment variable")
        sys.exit(1)
    
    # Process in batch mode or single file mode
    if args.batch:
        # Batch processing
        config_path = Path(args.config_file)
        if not config_path.is_dir():
            print(f"❌ Error: For batch processing, {args.config_file} must be a directory")
            sys.exit(1)
        
        # Get all .md files in the directory
        md_files = list(config_path.glob("*.md"))
        if not md_files:
            print(f"❌ Error: No .md files found in {args.config_file}")
            sys.exit(1)
        
        print(f"🔍 Found {len(md_files)} playlist configuration files")
        print("Starting batch processing...")
        
        # Track successes and failures
        success_count = 0
        failure_count = 0
        
        for i, md_file in enumerate(md_files):
            if md_file.name == "README.md" or md_file.name.startswith("TEMPLATE"):
                continue  # Skip README and template files
                
            print(f"\n[{i+1}/{len(md_files)}] Processing {md_file.name}...")
            try:
                result = process_single_playlist(str(md_file), args.force, False)  # No preview in batch mode
                if result:
                    success_count += 1
                else:
                    failure_count += 1
                # Add a small delay between API calls to avoid rate limits
                if i < len(md_files) - 1:
                    time.sleep(1)
            except Exception as e:
                safe_print(f"❌ Error processing {md_file}: {e}")
                failure_count += 1
        
        print(f"\n✅ Batch processing complete: {success_count} successful, {failure_count} failed")
    
    else:
        # Single file processing
        process_single_playlist(args.config_file, args.force, args.preview)


if __name__ == "__main__":
    main()
