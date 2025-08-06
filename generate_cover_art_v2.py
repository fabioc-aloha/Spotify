#!/usr/bin/env python3
"""
Alex Method DJ Platform - AI Cover Art Generator v2
Enhanced version with AI background generation + Python overlay branding

Usage:
    python generate_cover_art_v2.py playlist-configs/neural-network-symphony.md
    python generate_cover_art_v2.py playlist-configs/coffee-shop-vibes.md --preview
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
import argparse
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv
import textwrap

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
        """Parse playlist configuration from markdown file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Playlist config not found: {self.config_path}")
        
        content = self.config_path.read_text(encoding='utf-8')
        config = {}
        
        # Extract basic metadata - handle both formats (with and without bullet points)
        name_match = re.search(r'(?:\*\*Name\*\*:|[-\*]\s*\*\*Name\*\*:)\s*(.+)', content)
        description_match = re.search(r'(?:\*\*Description\*\*:|[-\*]\s*\*\*Description\*\*:)\s*(.+)', content)  
        emoji_match = re.search(r'(?:\*\*Emoji\*\*:|[-\*]\s*\*\*Emoji\*\*:)\s*(.+)', content)
        
        config['name'] = name_match.group(1).strip() if name_match else 'Unnamed Playlist'
        config['description'] = description_match.group(1).strip() if description_match else ''
        config['emoji'] = emoji_match.group(1).strip() if emoji_match else '🎵'
        
        # Extract phases
        phases = []
        phase_pattern = r'### Phase (\d+): (.+?) \((\d+) minutes\)\s*\n\s*(.+?)(?=\n###|\n\n|\Z)'
        
        for match in re.finditer(phase_pattern, content, re.DOTALL):
            phase_number = int(match.group(1))
            phase_name = match.group(2).strip()
            phase_duration = int(match.group(3))
            phase_description = match.group(4).strip()
            
            phases.append({
                'number': phase_number,
                'name': phase_name,
                'duration': phase_duration,
                'description': phase_description
            })
        
        config['phases'] = phases
        return config
    
    def get_visual_theme(self) -> Dict[str, Any]:
        """Extract basic visual theme information for AI generation"""
        emoji = self.config_data.get('emoji', '🎵')
        name = self.config_data.get('name', 'Unnamed Playlist')
        description = self.config_data.get('description', '')
        phases = self.config_data.get('phases', [])
        
        # Simple theme info - we'll let the AI interpret the playlist file directly
        return {
            'emoji': emoji,
            'name': name,
            'description': description,
            'phases': phases
        }

class BackgroundGenerator:
    """Generate AI backgrounds using OpenAI DALL-E 3"""
    
    def __init__(self, api_key: str, config_path: Optional[str] = None):
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
        self.config_path = config_path
    
    def generate_background(self, visual_theme: Dict[str, Any]) -> str:
        """Generate background image using DALL-E 3"""
        
        # Build background-focused prompt
        prompt = self._build_background_prompt(visual_theme)
        
        print(f"🎨 Generating AI background with prompt:")
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
            
            print(f"✅ Successfully generated background")
            return image_url
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error generating background: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Response: {e.response.text}")
            raise
    
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

class CoverArtComposer:
    """Compose final cover art with AI background + Python overlay"""
    
    def __init__(self):
        self.canvas_size = (1024, 1024)
        self.emoji_size = 180
        self.title_size = 72
        self.brand_size = 36
        self.brand_small_size = 24
    
    def compose_cover_art(self, background_url: str, visual_theme: Dict[str, Any], output_path: Path) -> None:
        """Compose final cover art with background + overlay"""
        
        print(f"🎨 Composing cover art with Python overlay...")
        
        # Download and load background
        background = self._download_image(background_url)
        background = background.resize(self.canvas_size, Image.Resampling.LANCZOS)
        
        # Create overlay
        overlay = self._create_overlay(visual_theme)
        
        # Composite final image
        final_image = Image.alpha_composite(background.convert('RGBA'), overlay)
        
        # Save in multiple formats
        self._save_final_image(final_image, output_path)
        
        print(f"✅ Cover art composed successfully!")
    
    def _download_image(self, url: str) -> Image.Image:
        """Download image from URL"""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    
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
        self._add_overlay_effects(overlay)
        
        return overlay
    
    def _add_emoji_with_glow(self, overlay: Image.Image, emoji: str, position: Tuple[int, int]) -> None:
        """Add emoji with enhanced glow effect for better visibility"""
        draw = ImageDraw.Draw(overlay)
        
        # Try to use a larger font for emoji to make it more prominent
        emoji_size = self.emoji_size + 20  # Increased size
        
        try:
            emoji_font = ImageFont.truetype("seguiemj.ttf", emoji_size)
        except:
            try:
                emoji_font = ImageFont.truetype("arial.ttf", emoji_size)
            except:
                emoji_font = ImageFont.load_default()
        
        # Get text size for centering
        bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = position[0] - text_width // 2
        y = position[1] - text_height // 2
        
        # Add stronger glow effect with multiple layers
        # Outer glow (more transparent)
        glow_color_outer = (255, 255, 255, 60)
        for offset in range(6, 3, -1):
            for dx in [-offset, 0, offset]:
                for dy in [-offset, 0, offset]:
                    if dx == 0 and dy == 0:
                        continue
                    draw.text((x + dx, y + dy), emoji, font=emoji_font, fill=glow_color_outer)
        
        # Inner glow (more opaque)
        glow_color_inner = (255, 255, 255, 120)
        for offset in range(3, 0, -1):
            for dx in [-offset, 0, offset]:
                for dy in [-offset, 0, offset]:
                    if dx == 0 and dy == 0:
                        continue
                    draw.text((x + dx, y + dy), emoji, font=emoji_font, fill=glow_color_inner)
        
        # Add main emoji with full opacity
        draw.text((x, y), emoji, font=emoji_font, fill=(255, 255, 255, 255))
    
    def _add_text_with_shadow(self, overlay: Image.Image, text: str, font: Any, 
                            position: Tuple[int, int], max_width: int = 800) -> None:
        """Add text with enhanced shadow effect and word wrapping for better readability"""
        draw = ImageDraw.Draw(overlay)
        
        # Wrap text if too long
        wrapped_lines = self._wrap_text(text, font, max_width)
        
        # Calculate total height for centering
        line_height = 80
        total_height = len(wrapped_lines) * line_height
        start_y = position[1] - total_height // 2
        
        # Add a semi-transparent background behind all text for better readability
        if wrapped_lines:
            # Calculate background dimensions
            padding = 30  # Padding around text
            max_line_width = 0
            
            for line in wrapped_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                max_line_width = max(max_line_width, line_width)
            
            bg_width = max_line_width + padding * 2
            bg_height = total_height + padding * 2
            bg_x = position[0] - bg_width // 2
            bg_y = start_y - padding
            
            # Draw rounded semi-transparent background
            background_color = (0, 0, 0, 100)  # Semi-transparent black
            draw.rounded_rectangle(
                [bg_x, bg_y, bg_x + bg_width, bg_y + bg_height],
                radius=20,
                fill=background_color
            )
        
        for i, line in enumerate(wrapped_lines):
            # Get text size for centering
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            
            x = position[0] - text_width // 2
            y = start_y + i * line_height
            
            # Add stronger shadow with multiple layers for better contrast and readability
            shadow_color = (0, 0, 0, 180)
            
            # Multiple shadow layers for depth
            for offset in range(1, 5):
                draw.text((x + offset, y + offset), line, font=font, fill=shadow_color)
                
            # Add subtle outline for better readability against any background
            outline_color = (0, 0, 0, 220)
            for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                draw.text((x + dx, y + dy), line, font=font, fill=outline_color)
            
            # Add main text with full opacity
            text_color = (255, 255, 255, 255)
            draw.text((x, y), line, font=font, fill=text_color)
    
    def _wrap_text(self, text: str, font: Any, max_width: int) -> list:
        """Wrap text to fit within max_width"""
        draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
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
        dj_height = bbox_dj[3] - bbox_dj[1]
        
        x = 512 - text_width // 2
        y = 920
        
        # Create semi-transparent background for branding area
        padding = 15
        bg_width = max(text_width, dj_width) + padding * 2
        bg_height = 45 + dj_height + padding * 2
        bg_x = 512 - bg_width // 2
        bg_y = y - padding
        
        # Draw rounded semi-transparent background
        background_color = (0, 0, 0, 120)  # Semi-transparent black
        draw.rounded_rectangle(
            [bg_x, bg_y, bg_x + bg_width, bg_y + bg_height],
            radius=15,
            fill=background_color
        )
        
        # Add stronger brand shadow with multiple layers
        shadow_color = (0, 0, 0, 180)
        for offset in range(1, 4):
            draw.text((x + offset, y + offset), brand_text, font=brand_font, fill=shadow_color)
            
        # Add subtle outline for better readability against any background
        outline_color = (0, 0, 0, 220)
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            draw.text((x + dx, y + dy), brand_text, font=brand_font, fill=outline_color)
        
        # Add main brand text with brighter color for better visibility
        draw.text((x, y), brand_text, font=brand_font, fill=(225, 225, 255, 255))
        
        # Add "DJ" subtitle with enhanced readability
        dj_text = "DJ"
        dj_x = 512 - dj_width // 2
        dj_y = y + 45
        
        # Add shadow and outline to DJ text
        for offset in range(1, 3):
            draw.text((dj_x + offset, dj_y + offset), dj_text, font=brand_small_font, fill=shadow_color)
            
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            draw.text((dj_x + dx, dj_y + dy), dj_text, font=brand_small_font, fill=outline_color)
            
        # Add main DJ text with brighter color
        draw.text((dj_x, dj_y), dj_text, font=brand_small_font, fill=(180, 180, 230, 255))
    
    def _add_overlay_effects(self, overlay: Image.Image) -> None:
        """Add subtle overlay effects"""
        # Create a subtle vignette effect
        vignette = Image.new('RGBA', self.canvas_size, (0, 0, 0, 0))
        vignette_draw = ImageDraw.Draw(vignette)
        
        # Darken edges slightly for better text contrast
        center = (512, 512)
        for radius in range(700, 800, 10):
            alpha = min(30, (radius - 700) * 3)
            vignette_draw.ellipse(
                [center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius],
                fill=(0, 0, 0, alpha)
            )
        
        overlay = Image.alpha_composite(overlay, vignette)
    
    def _save_final_image(self, image: Image.Image, output_path: Path) -> None:
        """Save final image in multiple formats"""
        
        # Convert to RGB for JPEG
        rgb_image = Image.new('RGB', image.size, (0, 0, 0))
        rgb_image.paste(image, mask=image.split()[-1])
        
        # Save JPEG version
        jpeg_path = output_path.with_suffix('.jpg')
        rgb_image.save(jpeg_path, 'JPEG', quality=95, optimize=True)
        print(f"   📁 JPEG: {jpeg_path}")
        
        # Save PNG version
        png_path = output_path.with_suffix('.png')
        image.save(png_path, 'PNG', optimize=True)
        print(f"   📁 PNG: {png_path}")
        
        # Create base64 version for Spotify API
        buffer = BytesIO()
        rgb_image.save(buffer, format='JPEG', quality=85)
        base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        base64_path = output_path.parent / f"{output_path.stem}_base64.txt"
        base64_path.write_text(base64_data)
        print(f"   📁 Base64: {base64_path}")

def check_existing_cover_art(config_file: str) -> Dict[str, Optional[Path]]:
    """Check if cover art already exists for a playlist config"""
    config_name = Path(config_file).stem
    
    existing_files: Dict[str, Optional[Path]] = {
        'jpeg': None,
        'png': None,
        'base64': None
    }
    
    # Check in generated directory
    jpeg_path = GENERATED_DIR / f"{config_name}.jpg"
    png_path = GENERATED_DIR / f"{config_name}.png"
    base64_path = GENERATED_DIR / f"{config_name}_base64.txt"
    
    if jpeg_path.exists():
        existing_files['jpeg'] = jpeg_path
    if png_path.exists():
        existing_files['png'] = png_path
    if base64_path.exists():
        existing_files['base64'] = base64_path
    
    return existing_files

def get_cover_art_path(config_file: str, format: str = 'jpeg') -> Optional[Path]:
    """Get the cover art path for a playlist config file"""
    config_name = Path(config_file).stem
    
    if format == 'jpeg':
        path = GENERATED_DIR / f"{config_name}.jpg"
    elif format == 'png':
        path = GENERATED_DIR / f"{config_name}.png"
    elif format == 'base64':
        path = GENERATED_DIR / f"{config_name}_base64.txt"
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    return path if path.exists() else None

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Generate AI cover art with Python overlay')
    parser.add_argument('config_file', help='Path to playlist configuration file')
    parser.add_argument('--preview', action='store_true', help='Save preview version only')
    parser.add_argument('--format', choices=['jpeg', 'png', 'both'], default='both', 
                       help='Output format')
    parser.add_argument('--force', action='store_true', help='Force regeneration of cover art even if it exists')
    
    args = parser.parse_args()
    
    # Validate API key
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Please check your .env file configuration:")
        print("   1. Copy .env.template to .env")
        print("   2. Get your OpenAI API key from https://platform.openai.com/api-keys")
        print("   3. Add: OPENAI_API_KEY=your-api-key-here")
        sys.exit(1)
    
    try:
        # Parse playlist config
        print(f"📋 Parsing playlist config: {args.config_file}")
        parser = PlaylistConfigParser(args.config_file)
        visual_theme = parser.get_visual_theme()
        
        print(f"🎵 Playlist: {visual_theme['name']}")
        print(f"   Emoji: {visual_theme['emoji']}")
        print(f"   Description: {visual_theme['description'][:100]}...")
        
        # Check for existing cover art
        existing_art = check_existing_cover_art(args.config_file)
        existing_count = sum(1 for path in existing_art.values() if path is not None)
        
        if existing_count > 0 and not args.force:
            print(f"📁 Found {existing_count} existing cover art files:")
            for format_name, path in existing_art.items():
                if path:
                    print(f"   ✅ {format_name.upper()}: {path}")
            print("\nUse --force to regenerate the cover art.")
            return
        elif existing_count > 0 and args.force:
            print(f"📁 Found {existing_count} existing cover art files, but --force flag is set.")
            print("   Will regenerate cover art...")
        else:
            print("📁 No existing cover art found - will generate new files")
        
        # Generate AI background
        generator = BackgroundGenerator(OPENAI_API_KEY, args.config_file)
        background_url = generator.generate_background(visual_theme)
        
        # Compose final cover art
        config_name = Path(args.config_file).stem
        output_path = GENERATED_DIR / config_name  # Remove -v2 suffix for consistency
        
        composer = CoverArtComposer()
        composer.compose_cover_art(background_url, visual_theme, output_path)
        
        print(f"🎵 Ready for use with Alex Method DJ Platform!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
