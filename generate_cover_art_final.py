#!/usr/bin/env python3
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
OPTIMIZED_DIR = COVER_ART_DIR / 'optimized'
FONTS_DIR = COVER_ART_DIR / 'fonts'

# Ensure directories exist
COVER_ART_DIR.mkdir(exist_ok=True)
GENERATED_DIR.mkdir(exist_ok=True)
OPTIMIZED_DIR.mkdir(exist_ok=True)
FONTS_DIR.mkdir(exist_ok=True)


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
            print(f"❌ Error parsing playlist config: {e}")
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
    
    def _build_background_prompt(self, visual_theme: Dict[str, Any]) -> str:
        """Build background-focused prompt for DALL-E 3"""
        
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
                    
                    # Remove track list section to reduce prompt length
                    track_list_pattern = re.compile(r'### Track List[^\n]*\n.*?(?=##|\Z)', re.DOTALL)
                    playlist_content = track_list_pattern.sub('', playlist_content)
                    
                    # Also limit the overall length of the playlist content
                    max_content_length = 4000  # Characters, adjust as needed
                    if len(playlist_content) > max_content_length:
                        # Keep metadata and first few sections
                        playlist_content = playlist_content[:max_content_length] + "\n..."
                        print(f"   Note: Playlist content truncated to {max_content_length} characters")
            except Exception as e:
                print(f"Warning: Could not read playlist file: {e}")
        
        # Build the prompt - Keep it simple!
        prompt = f"""Please create a background image for a cover art for this playlist:

{playlist_content}

Requirements:
- Create ONLY the background (no text, no logos)
- Square 1024x1024 composition
- Leave center area clean for text overlay
- Match the theme and mood described in the playlist
- Focus on the emoji {emoji} and playlist theme
- Make the image realistic but artistic

IMPORTANT: Background only - no text, no words."""

        return prompt
    
    def generate_background(self, visual_theme: Dict[str, Any]) -> str:
        """Generate background image using DALL-E 3"""
        
        prompt = self._build_background_prompt(visual_theme)
        print(f"🎨 Generating AI background with prompt:")
        # Print a truncated version of the prompt for clarity
        print(f"   {prompt.split('Requirements:')[0][:200]}...")
        print(f"   Requirements: (artistic, realistic background with clean center for text)")
        
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
            print(f"❌ Error generating background: {e}")
            raise


class CoverArtComposer:
    """Compose final cover art with AI background + Python overlay"""
    
    def __init__(self):
        self.canvas_size = (1024, 1024)
        self.emoji_size = 180
        self.title_size = 72
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
        clean_name = clean_name.strip()
        
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
        
        # No emoji added - removed from overlay
        
        # Center the title text vertically since we don't have an emoji above it
        self._add_text_with_shadow(overlay, clean_name, title_font, (512, 400), max_width=900)
        
        # Add Alex Method branding
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
        """Add text with shadow and background for better readability"""
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
        
        # Create semi-transparent background for better text readability
        # Calculate background rectangle with padding
        padding = 20
        bg_rect = (
            x - padding,
            y - padding,
            x + text_block_width + padding,
            y + text_block_height + padding
        )
        
        # Draw semi-transparent background
        bg_color = (0, 0, 0, 128)  # Black with 50% opacity
        draw.rectangle(bg_rect, fill=bg_color)
        
        # Draw each line of text
        current_y = y
        for i, line in enumerate(lines):
            # Draw shadow
            shadow_x, shadow_y = x + 2, current_y + 2
            draw.text((shadow_x, shadow_y), line, font=font, fill=(0, 0, 0, 180))
            
            # Draw text
            draw.text((x, current_y), line, font=font, fill=(255, 255, 255, 255))
            
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
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)  # Single word too long, add anyway
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _add_alex_method_branding(self, overlay: Image.Image, brand_font: Any, 
                                brand_small_font: Any) -> None:
        """Add Alex Method branding with enhanced readability"""
        draw = ImageDraw.Draw(overlay)
        
        # Main branding at bottom
        brand_text = "ALEX METHOD"
        bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
        text_width = bbox[2] - bbox[0]
        
        # Calculate text dimensions
        bbox_dj = draw.textbbox((0, 0), "DJ", font=brand_small_font)
        dj_width = bbox_dj[2] - bbox_dj[0]
        
        # Create semi-transparent background for branding
        brand_bg_padding = 10
        brand_x = (self.canvas_size[0] - text_width - dj_width - 10) // 2
        brand_y = self.canvas_size[1] - 60
        
        brand_bg_rect = (
            brand_x - brand_bg_padding,
            brand_y - brand_bg_padding,
            brand_x + text_width + dj_width + 10 + (brand_bg_padding * 2),
            brand_y + brand_font.size + (brand_bg_padding * 2)
        )
        
        # Draw semi-transparent background
        bg_color = (0, 0, 0, 128)  # Black with 50% opacity
        draw.rectangle(brand_bg_rect, fill=bg_color)
        
        # Draw shadow for ALEX METHOD
        shadow_offset = 2
        draw.text((brand_x + shadow_offset, brand_y + shadow_offset), 
                brand_text, font=brand_font, fill=(0, 0, 0, 180))
        
        # Draw ALEX METHOD text
        draw.text((brand_x, brand_y), brand_text, font=brand_font, fill=(255, 255, 255, 255))
        
        # Draw DJ
        dj_x = brand_x + text_width + 10
        dj_y = brand_y + 12  # Offset to align with main text
        
        # Draw shadow for DJ
        draw.text((dj_x + shadow_offset, dj_y + shadow_offset), 
                "DJ", font=brand_small_font, fill=(0, 0, 0, 180))
        
        # Draw DJ text
        draw.text((dj_x, dj_y), "DJ", font=brand_small_font, fill=(255, 255, 255, 255))
    
    def compose_cover_art(self, background_url: str, visual_theme: Dict[str, Any], 
                        output_path: Path) -> Tuple[Path, Path, Path]:
        """Compose the final cover art image with AI background and Python overlay"""
        print(f"🎨 Composing cover art with Python overlay...")
        
        # Download background image
        try:
            response = requests.get(background_url)
            response.raise_for_status()
            background = Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"❌ Error downloading background image: {e}")
            raise
        
        # Create overlay with text and branding
        overlay = self._create_overlay(visual_theme)
        
        # Composite background and overlay
        background = background.convert("RGBA")
        result = Image.alpha_composite(background, overlay)
        
        # Save as PNG (with transparency)
        png_path = f"{output_path}.png"
        result.save(png_path)
        print(f"   📁 PNG: {png_path}")
        
        # Save as JPEG (no transparency)
        jpg_path = f"{output_path}.jpg"
        jpg_image = result.convert("RGB")
        jpg_image.save(jpg_path, quality=95)
        print(f"   📁 JPEG: {jpg_path}")
        
        # Save as Base64 for embedding
        base64_path = f"{output_path}_base64.txt"
        buffered = BytesIO()
        jpg_image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        with open(base64_path, 'w') as f:
            f.write(img_str)
        print(f"   📁 Base64: {base64_path}")
        
        print(f"✅ Cover art composed successfully!")
        
        return Path(png_path), Path(jpg_path), Path(base64_path)


def get_existing_cover_art(config_name: str) -> List[Path]:
    """Check if cover art already exists for this config"""
    config_name = Path(config_name).stem
    existing_files = []
    
    # Check for PNG
    png_path = GENERATED_DIR / f"{config_name}.png"
    if png_path.exists():
        existing_files.append(png_path)
    
    # Check for JPEG
    jpg_path = GENERATED_DIR / f"{config_name}.jpg"
    if jpg_path.exists():
        existing_files.append(jpg_path)
    
    # Check for Base64
    base64_path = GENERATED_DIR / f"{config_name}_base64.txt"
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
            print(f"⚠️ {config_name} is a known problematic playlist.")
            print(f"   Please use generate_problem_covers.py instead:")
            print(f"   python generate_problem_covers.py --playlist {config_name}")
            return False
        
        # Parse the playlist config
        print(f"📋 Parsing playlist config: {config_file}")
        parser = PlaylistConfigParser(config_file)
        playlist_info = parser.get_info()
        visual_theme = parser.get_visual_theme()
        
        # Show basic info
        name = playlist_info.get('name', 'Unknown Playlist')
        description = playlist_info.get('description', 'No description')
        if len(description) > 70:
            description = description[:67] + "..."
        emoji = playlist_info.get('emoji', '🎵')
        
        print(f"🎵 Playlist: {name}")
        print(f"   Emoji: {emoji}")
        print(f"   Description: {description}")
        
        # Check if cover art already exists
        config_name = Path(config_file).stem
        existing_files = get_existing_cover_art(config_name)
        existing_count = len(existing_files)
        
        if existing_count > 0 and not force:
            print(f"📁 Found {existing_count} existing cover art files:")
            for path in existing_files:
                format_name = path.suffix[1:].lower()
                if "base64" in path.name:
                    format_name = "BASE64"
                if path:
                    print(f"   ✅ {format_name.upper()}: {path}")
            print("\nUse --force to regenerate the cover art.")
            return False
        elif existing_count > 0 and force:
            print(f"📁 Found {existing_count} existing cover art files, but --force flag is set.")
            print("   Will regenerate cover art...")
        else:
            print("📁 No existing cover art found - will generate new files")
        
        # Generate AI background
        generator = BackgroundGenerator(OPENAI_API_KEY, config_file)
        background_url = generator.generate_background(visual_theme)
        
        # Compose final cover art
        output_path = GENERATED_DIR / config_name
        
        composer = CoverArtComposer()
        png_path, jpg_path, _ = composer.compose_cover_art(background_url, visual_theme, output_path)
        
        # Preview the image if requested
        if preview:
            if sys.platform == 'win32':
                os.startfile(png_path)
            elif sys.platform == 'darwin':
                subprocess.call(['open', png_path])
            else:
                subprocess.call(['xdg-open', png_path])
            print(f"🔍 Opening preview of {png_path}")
        
        print(f"🎵 Ready for use with Alex Method DJ Platform!")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {config_file}: {e}")
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
                print(f"❌ Error processing {md_file}: {e}")
                failure_count += 1
        
        print(f"\n✅ Batch processing complete: {success_count} successful, {failure_count} failed")
    
    else:
        # Single file processing
        process_single_playlist(args.config_file, args.force, args.preview)


if __name__ == "__main__":
    main()
