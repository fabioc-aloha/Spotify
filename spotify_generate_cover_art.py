#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alex Method DJ Platform - AI Cover Art Generator (Modular Version)
Generates high-quality playlist cover art with AI backgrounds and professional branding

Usage:
    python spotify_generate_cover_art.py <playlist_config.md> [options]

Options:
    --force         Force regeneration of cover art even if files exist
    --preview       Open the generated image in the default viewer
    --batch         Process multiple playlists (provide a directory instead of a file)
    --force-ascii   Force ASCII output (disable emojis) for compatibility with older terminals

Examples:
    python spotify_generate_cover_art.py playlist-configs/neural-network-symphony.md
    python spotify_generate_cover_art.py playlist-configs/coffee-shop.md --preview
    python spotify_generate_cover_art.py playlist-configs/space-odyssey.md --force
    python spotify_generate_cover_art.py playlist-configs/ --batch --force

Note: If OpenAI content policy errors occur, edit the playlist .md file directly
"""

import os
import sys
import re
import json
import requests
import time
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
from pathlib import Path
import argparse
from typing import Dict, Any, Optional, Tuple, List
from dotenv import load_dotenv
import subprocess
from datetime import datetime

# Import modular components
from src.smart_print import safe_print, set_force_ascii_mode
from src.config_parser import PlaylistConfigParser

# Load environment variables from .env file
load_dotenv()

# Configuration - TypeScript-safe API key handling
OPENAI_API_KEY_ENV = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY_ENV:
    safe_print("❌ Error: OPENAI_API_KEY not found in environment variables or .env file")
    safe_print("Create a .env file with your OpenAI API key: OPENAI_API_KEY=your-api-key")
    sys.exit(1)

# Now we know it's a string
OPENAI_API_KEY: str = OPENAI_API_KEY_ENV

# API Configuration
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'dall-e-3')
OPENAI_IMAGE_SIZE = os.getenv('OPENAI_IMAGE_SIZE', '1024x1024')
OPENAI_IMAGE_QUALITY = os.getenv('OPENAI_IMAGE_QUALITY', 'hd')
OPENAI_IMAGE_STYLE = os.getenv('OPENAI_IMAGE_STYLE', 'vivid')

# Directory Configuration
COVER_ART_DIR = Path('cover-art')

# Ensure directory exists
COVER_ART_DIR.mkdir(exist_ok=True)


class BackgroundGenerator:
    """Generate AI backgrounds using OpenAI DALL-E"""
    
    def __init__(self, api_key: str, config_path: Optional[str] = None):
        self.api_key = api_key
        self.config_path = config_path
    
    def _build_background_prompt(self, visual_theme: Dict[str, Any]) -> str:
        """Build background-focused prompt for DALL-E 3"""
        
        emoji = visual_theme.get('emoji', '🎵')
        description = visual_theme.get('description', '')
        
        # Extract specific sections from playlist content
        search_queries = ""
        creation_notes = ""
        
        if self.config_path:
            try:
                playlist_file_path = Path(self.config_path)
                if playlist_file_path.exists():
                    content = playlist_file_path.read_text(encoding='utf-8')
                    
                    # Extract Search Queries section
                    search_pattern = re.compile(r'## Search Queries\s*\n(.*?)(?=##|$)', re.DOTALL)
                    search_match = search_pattern.search(content)
                    if search_match:
                        search_queries = search_match.group(1).strip()
                    
                    # Extract Creation Notes section
                    notes_pattern = re.compile(r'## Creation Notes\s*\n(.*?)(?=##|$)', re.DOTALL)
                    notes_match = notes_pattern.search(content)
                    if notes_match:
                        creation_notes = notes_match.group(1).strip()
                        
            except Exception as e:
                safe_print(f"Warning: Could not read playlist file: {e}")
        
        # Simple, direct prompt
        prompt = f"""Create a high-quality background image for a **Spotify playlist cover**.
Playlist Description: {description}
Primary Mood/Concept: {emoji}

Image Guidelines:
- Square format (1024x1024 pixels)
- Realistic but artistic, with strong emotional resonance and clear storytelling
- Must visually convey the mood and theme of the playlist
- Focal elements should avoid the middle-top area to leave space for title overlay
- Avoid placing any key visual elements where Spotify's title or creator name might appear
- No human faces unless specified

IMPORTANT:
- Do not include any typography, characters, numbers, or embedded words of any kind

Final Output:
- Professional-grade background-only artwork for playlist cover usage, with **zero text or logo content**"""

        # Truncate to 4000 characters to stay within OpenAI's limit
        if len(prompt) > 4000:
            prompt = prompt[:4000]
            safe_print(f"   ⚠️ Prompt truncated to 4000 characters")

        return prompt
    
    def _build_fallback_prompt(self, visual_theme: Dict[str, Any]) -> str:
        """Build simplified prompt using only search queries for content policy fallback"""
        
        emoji = visual_theme.get('emoji', '🎵')
        
        # Extract search queries from the visual theme data if available
        search_queries = ""
        if 'file_content' in visual_theme:
            content = visual_theme['file_content']
            # Extract search queries section
            search_pattern = re.compile(r'## Search Queries\s*\n(.*?)(?=##|$)', re.DOTALL)
            search_match = search_pattern.search(content)
            if search_match:
                search_queries = search_match.group(1).strip()
        
        # Build fallback prompt with search queries only
        fallback_prompt = f"""Create a high-quality background image for a **Spotify playlist cover**.
Playlist Description: {search_queries}
Primary Mood/Concept: {emoji}

Image Guidelines:
- Square format (1024x1024 pixels)
- Realistic but artistic, with strong emotional resonance and clear storytelling
- Must visually convey the mood and theme of the playlist
- Focal elements should avoid the middle-top area to leave space for title overlay
- Avoid placing any key visual elements where Spotify's title or creator name might appear
- No human faces unless specified

IMPORTANT:
- Do not include any typography, characters, numbers, or embedded words of any kind

Final Output:
- Professional-grade background-only artwork for playlist cover usage, with **zero text or logo content**"""

        return fallback_prompt
    
    def generate_background(self, visual_theme: Dict[str, Any]) -> str:
        """Generate background image using DALL-E 3 with content policy fallback"""
        
        prompt = self._build_background_prompt(visual_theme)
        
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
            safe_print("✅ Successfully generated background")
            return image_url
            
        except requests.exceptions.HTTPError as e:
            # Check if it's a content policy error (400 status with policy violation)
            if e.response.status_code == 400:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', '').lower()
                    
                    # Only trigger fallback for specific content policy keywords
                    content_policy_keywords = ['content policy', 'safety', 'violates', 'policy', 'unsafe', 'inappropriate']
                    
                    is_policy_error = any(keyword in error_message for keyword in content_policy_keywords)
                    
                    if is_policy_error:
                        safe_print(f"⚠️ Content policy violation detected: {error_message}")
                        safe_print(f"⚠️ Trying fallback prompt with search queries only...")
                        return self._generate_with_fallback(visual_theme, headers)
                    else:
                        # For other 400 errors, just raise the exception
                        safe_print(f"❌ Bad request error (non-policy): {error_message}")
                        raise
                except ValueError:
                    # If we can't parse the JSON response, it's probably not a content policy issue
                    safe_print(f"❌ 400 error with unparseable response: {e}")
                    raise
            
            safe_print(f"❌ Error generating background: {e}")
            raise
            
        except Exception as e:
            safe_print(f"❌ Error generating background: {e}")
            raise
    
    def _generate_with_fallback(self, visual_theme: Dict[str, Any], headers: dict) -> str:
        """Generate background using fallback prompt with search queries only"""
        
        fallback_prompt = self._build_fallback_prompt(visual_theme)
        safe_print(f"🔄 Using fallback prompt with search queries only:")
        safe_print(f"   {fallback_prompt.split('Requirements:')[0][:200]}...")
        
        data = {
            "model": OPENAI_MODEL,
            "prompt": fallback_prompt,
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
            safe_print("✅ Successfully generated background with fallback prompt")
            return image_url
            
        except Exception as e:
            safe_print(f"❌ Fallback prompt also failed: {e}")
            raise


class CoverArtComposer:
    """Compose final cover art with AI background + Python overlay"""
    
    def __init__(self):
        self.canvas_size = (1024, 1024)  # Keep high resolution for quality
        self.emoji_size = 180
        self.title_size = 160  # Increased for more prominent display
        self.brand_size = 48   # Consistent branding size
        self.brand_small_size = 32  # Consistent DJ text size
    
    def _analyze_background_colors(self, background: Image.Image) -> Tuple[Tuple[int, int, int, int], Tuple[int, int, int, int]]:
        """Analyze background image to choose optimal text colors"""
        # Convert to RGB if needed
        if background.mode != 'RGB':
            background = background.convert('RGB')
        
        # Sample the top area where title will be placed (top 30% of image)
        title_area = background.crop((0, 0, background.width, background.height // 3))
        
        # Get dominant colors in the title area
        title_area = title_area.resize((50, 50))  # Reduce for faster processing
        title_pixels = list(title_area.getdata())
        
        # Calculate average brightness in title area
        avg_brightness = sum(sum(pixel) for pixel in title_pixels) / (len(title_pixels) * 3)
        
        # Choose text color based on background brightness
        if avg_brightness > 128:  # Bright background
            text_color = (0, 0, 0, 255)      # Black text
            outline_color = (255, 255, 255, 200)  # White outline
        else:  # Dark background
            text_color = (255, 255, 255, 255)  # White text
            outline_color = (0, 0, 0, 200)    # Black outline
        
        return text_color, outline_color

    def _create_overlay_with_background(self, visual_theme: Dict[str, Any], background: Image.Image) -> Image.Image:
        """Create text and branding overlay with background-aware colors"""
        
        # Analyze background colors for optimal text contrast
        text_color, outline_color = self._analyze_background_colors(background)
        
        # Create transparent overlay
        overlay = Image.new('RGBA', self.canvas_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        name = visual_theme['name']
        
        # Clean up playlist name - remove emoji and Alex Method suffix since it's in the branding
        clean_name = re.sub(r'[^\w\s\-\'",.:;!?&()]', '', name)
        clean_name = re.sub(r'\s*-\s*Alex Method.*$', '', clean_name, flags=re.IGNORECASE)
        clean_name = re.sub(r'\s+', ' ', clean_name.strip())
        
        # Load fonts with better hierarchy
        try:
            # Try modern fonts first - Segoe UI is clean and modern
            title_font = ImageFont.truetype("seguibl.ttf", self.title_size)  # Segoe UI Bold
            brand_font = ImageFont.truetype("seguisb.ttf", self.brand_size)  # Segoe UI Semibold
            brand_small_font = ImageFont.truetype("segoeui.ttf", self.brand_small_size)  # Segoe UI Regular
        except:
            try:
                # Fallback to Arial Bold for clean look
                title_font = ImageFont.truetype("arialbd.ttf", self.title_size)
                brand_font = ImageFont.truetype("arialbd.ttf", self.brand_size)
                brand_small_font = ImageFont.truetype("arial.ttf", self.brand_small_size)
            except:
                try:
                    # Second fallback to regular Arial
                    title_font = ImageFont.truetype("arial.ttf", self.title_size)
                    brand_font = ImageFont.truetype("arial.ttf", self.brand_size)
                    brand_small_font = ImageFont.truetype("arial.ttf", self.brand_small_size)
                except:
                    title_font = ImageFont.load_default()
                    brand_font = ImageFont.load_default()
                    brand_small_font = ImageFont.load_default()
        
        # Position the title text higher up and more prominently with dynamic colors
        self._add_title_text(overlay, clean_name, title_font, (512, 140), max_width=900, 
                           text_color=text_color, outline_color=outline_color)
        
        # Add Alex Method branding at the bottom with dynamic colors
        self._add_alex_method_branding(overlay, brand_font, brand_small_font,
                                     text_color=text_color, outline_color=outline_color)
        
        # Add subtle overlay effects
        overlay = self._add_subtle_effects(overlay)
        
        return overlay
    
    def _add_subtle_effects(self, overlay: Image.Image) -> Image.Image:
        """Add subtle effects to make overlay stand out"""
        # The overlay is already good as is
        return overlay
    
    def _draw_text_with_outline(self, draw, text: str, font: Any, 
                               position: Tuple[int, int], text_color: Tuple[int, int, int, int],
                               outline_color: Tuple[int, int, int, int], outline_thickness: int = 2) -> None:
        """Draw text with outline and shadow effects using dynamic colors"""
        x, y = position
        shadow_color = (0, 0, 0, 120)   # Semi-transparent shadow
        
        # Draw outline in 8 directions (smaller outline for cleaner look)
        for dx in [-outline_thickness, 0, outline_thickness]:
            for dy in [-outline_thickness, 0, outline_thickness]:
                if dx != 0 or dy != 0:  # Skip center position
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        
        # Draw subtle shadow
        shadow_offset = 2
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)
    
    def _add_title_text(self, overlay: Image.Image, text: str, font: Any, 
                       position: Tuple[int, int], max_width: int = 900,
                       text_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                       outline_color: Tuple[int, int, int, int] = (0, 0, 0, 200)) -> None:
        """Add wrapped title text with outline effects and dynamic colors"""
        draw = ImageDraw.Draw(overlay)
        lines = self._wrap_text(text, font, max_width)
        
        # Calculate text block height for centering
        line_heights = [draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] 
                       for line in lines]
        text_block_height = sum(line_heights)
        
        # Start from top of text block
        current_y = position[1] - (text_block_height // 2)
        
        for i, line in enumerate(lines):
            line = line.strip()
            # Center each line
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_x = position[0] - (line_width // 2)
            
            self._draw_text_with_outline(draw, line, font, (int(line_x), int(current_y)), 
                                        text_color, outline_color, 2)
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
                                brand_small_font: Any,
                                text_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                                outline_color: Tuple[int, int, int, int] = (0, 0, 0, 200)) -> None:
        """Add Alex Method branding with dynamic colors"""
        draw = ImageDraw.Draw(overlay)
        center_x = self.canvas_size[0] // 2
        
        # Calculate positions
        brand_text = "ALEX METHOD"
        dj_text = "DJ"
        
        brand_bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
        brand_width = brand_bbox[2] - brand_bbox[0]
        brand_height = brand_bbox[3] - brand_bbox[1]
        
        dj_bbox = draw.textbbox((0, 0), dj_text, font=brand_small_font)
        dj_width = dj_bbox[2] - dj_bbox[0]
        
        # Positions
        brand_x = center_x - (brand_width // 2)
        brand_y = self.canvas_size[1] - 120  # Moved up from 80px to 120px from bottom
        
        dj_x = center_x - (dj_width // 2)
        dj_y = brand_y + brand_height + 8  # 8px spacing
        
        # Draw both texts using the DRY method with dynamic colors
        self._draw_text_with_outline(draw, brand_text, brand_font, (int(brand_x), int(brand_y)), 
                                    text_color, outline_color, 2)
        self._draw_text_with_outline(draw, dj_text, brand_small_font, (int(dj_x), int(dj_y)), 
                                    text_color, outline_color, 2)
    
    def compose_cover_art(self, background_url: str, visual_theme: Dict[str, Any], 
                        output_path: Path) -> Tuple[Path, Path]:
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
        
        # Ensure background is the right size first
        if background.size != self.canvas_size:
            background = background.resize(self.canvas_size, Image.Resampling.LANCZOS)
            safe_print(f"   🔧 Resized background from {background.size} to {self.canvas_size}")
        
        # Create overlay with text and branding using background-aware colors
        overlay = self._create_overlay_with_background(visual_theme, background)
        
        # Composite background and overlay
        background = background.convert("RGBA")
        result = Image.alpha_composite(background, overlay)
        
        # Save full-size PNG (1024x1024) - keep high quality
        png_path = f"{output_path}.png"
        result.save(png_path)
        safe_print(f"   📁 PNG (1024x1024): {png_path}")
        
        # Create 512x512 version for JPEG and Base64 (Spotify optimization)
        result_512 = result.resize((512, 512), Image.Resampling.LANCZOS)
        
        # Save as JPEG (512x512 for smaller file size)
        jpg_path = f"{output_path}.jpg"
        jpg_image = result_512.convert("RGB")
        jpg_image.save(jpg_path, quality=95)
        safe_print(f"   📁 JPEG (512x512): {jpg_path}")
        
        safe_print(f"✅ Cover art composed successfully!")
        
        return Path(png_path), Path(jpg_path)


def update_playlist_metadata_with_cover_art(config_file: str, cover_art_paths: Tuple[Path, Path]) -> bool:
    """Update playlist config file with generated cover art paths - simplified"""
    try:
        config_path = Path(config_file)
        if not config_path.exists():
            safe_print(f"❌ Config file not found: {config_file}")
            return False
        
        content = config_path.read_text(encoding='utf-8')
        png_path, jpg_path = cover_art_paths
        
        # Ensure paths are absolute for proper relative calculation
        png_abs = png_path.resolve()
        jpg_abs = jpg_path.resolve()
        working_dir = Path.cwd().resolve()
        
        # Convert paths to forward slashes for cross-platform compatibility
        png_rel = str(png_abs.relative_to(working_dir)).replace('\\', '/')
        jpg_rel = str(jpg_abs.relative_to(working_dir)).replace('\\', '/')
        
        # Create cover art metadata section
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cover_art_section = f"""## Cover Art
- **PNG**: {png_rel}
- **JPEG**: {jpg_rel}
- **Generated**: {timestamp}

"""
        
        # Simple replacement logic
        cover_art_pattern = re.compile(r'^## Cover Art\n.*?(?=^##|\Z)', re.MULTILINE | re.DOTALL)
        
        if cover_art_pattern.search(content):
            content = cover_art_pattern.sub(cover_art_section.rstrip() + '\n\n', content)
            safe_print("   📝 Updated existing Cover Art metadata")
        else:
            # Insert after Metadata section or at beginning
            metadata_pattern = re.compile(r'(^## Metadata\n.*?(?=^##))', re.MULTILINE | re.DOTALL)
            metadata_match = metadata_pattern.search(content)
            
            if metadata_match:
                insert_pos = metadata_match.end()
                content = content[:insert_pos] + '\n' + cover_art_section + content[insert_pos:]
            else:
                content = cover_art_section + content
            safe_print("   📝 Added Cover Art metadata")
        
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
        # Parse the playlist config using modular parser
        safe_print(f"📋 Parsing playlist config: {config_file}")
        parser = PlaylistConfigParser(config_file)
        playlist_info = parser.get_metadata()
        visual_theme = parser.get_visual_theme()
        
        # Show basic info
        name = playlist_info.get('name', 'Unknown Playlist')
        description = playlist_info.get('description', 'No description')
        emoji = playlist_info.get('emoji', '🎵')
        
        safe_print(f"🎵 Playlist: {name}")
        safe_print(f"   Emoji: {emoji}")
        safe_print(f"   Description: {description[:100]}{'...' if len(description) > 100 else ''}")
        
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
            safe_print("   Regenerating cover art...")
        else:
            safe_print("📁 No existing cover art found - generating new files")
        
        # Generate AI background
        generator = BackgroundGenerator(OPENAI_API_KEY, config_file)
        background_url = generator.generate_background(visual_theme)
        
        # Compose final cover art
        output_path = COVER_ART_DIR / config_name
        
        composer = CoverArtComposer()
        png_path, jpg_path = composer.compose_cover_art(background_url, visual_theme, output_path)
        
        # Update playlist metadata with cover art paths (no longer including base64)
        cover_art_paths = (png_path, jpg_path)
        metadata_updated = update_playlist_metadata_with_cover_art(config_file, cover_art_paths)
        
        if not metadata_updated:
            safe_print("⚠️ Warning: Failed to update playlist metadata, but cover art was generated successfully")
        
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
    parser.add_argument(
        "--force-ascii", 
        action="store_true", 
        help="Force ASCII output (disable emojis) for compatibility with older terminals"
    )
    args = parser.parse_args()
    
    # Set global ASCII mode using the smart print module
    set_force_ascii_mode(args.force_ascii)
    
    # Check if OpenAI API key is available
    if not OPENAI_API_KEY:
        safe_print("❌ Error: OPENAI_API_KEY environment variable not set")
        safe_print("Create a .env file with your OpenAI API key or set the environment variable")
        sys.exit(1)
    
    # Process in batch mode or single file mode
    if args.batch:
        # Batch processing
        config_path = Path(args.config_file)
        if not config_path.is_dir():
            safe_print(f"❌ Error: For batch processing, {args.config_file} must be a directory")
            sys.exit(1)
        
        # Get all .md files in the directory
        md_files = list(config_path.glob("*.md"))
        if not md_files:
            safe_print(f"❌ Error: No .md files found in {args.config_file}")
            sys.exit(1)
        
        safe_print(f"🔍 Found {len(md_files)} playlist configuration files")
        safe_print("Starting batch processing...")
        
        # Track successes and failures
        success_count = 0
        failure_count = 0
        
        for i, md_file in enumerate(md_files):
            if md_file.name == "README.md" or md_file.name.startswith("TEMPLATE"):
                continue  # Skip README and template files
                
            safe_print(f"\n[{i+1}/{len(md_files)}] Processing {md_file.name}...")
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
        
        safe_print(f"\n✅ Batch processing complete: {success_count} successful, {failure_count} failed")
    
    else:
        # Single file processing
        process_single_playlist(args.config_file, args.force, args.preview)


if __name__ == "__main__":
    main()
