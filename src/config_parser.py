#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alex Method DJ Platform - Configuration Parser Module
Universal markdown configuration file parser for playlists

Features:
- Parse Alex Method playlist configuration files (.md format)
- Extract metadata, search queries, track categories, and filters
- Support for both standard and phased playlist configurations
- Robust regex-based parsing with fallback defaults
- Cross-platform file handling

Usage:
    from src.config_parser import PlaylistConfigParser
    
    parser = PlaylistConfigParser('playlist-configs/coffee-shop.md')
    config = parser.get_config()
    visual_theme = parser.get_visual_theme()
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from src.smart_print import safe_print


class PlaylistConfigParser:
    """Parse Alex Method playlist configuration files.
    
    This class handles the parsing of markdown-based playlist configuration
    files used by the Alex Method DJ platform. It extracts all relevant
    metadata, search queries, track categories, and filtering rules.
    """
    
    def __init__(self, config_path: str):
        """Initialize parser with configuration file path.
        
        Args:
            config_path: Path to the playlist configuration file
        """
        self.config_path = Path(config_path)
        self.config_data = self._parse_config()
    
    def _parse_config(self) -> Dict[str, Any]:
        """Parse the playlist configuration file and extract all data.
        
        Returns:
            Dictionary containing all parsed configuration data
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            Exception: If there's an error parsing the file
        """
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Playlist config not found: {self.config_path}")
            
            content = self.config_path.read_text(encoding='utf-8')
            
            # Parse all sections
            metadata = self._parse_metadata(content)
            search_queries = self._parse_search_queries(content)
            track_categories = self._parse_track_categories(content)
            filters = self._parse_filters(content)
            
            # Store everything
            config_data = {
                'metadata': metadata,
                'search_queries': search_queries,
                'track_categories': track_categories,
                'filters': filters,
                'file_content': content,
                'file_path': str(self.config_path)
            }
            
            return config_data
            
        except Exception as e:
            safe_print(f"❌ Error parsing playlist config: {e}")
            raise
    
    def _parse_metadata(self, content: str) -> Dict[str, Any]:
        """Parse metadata section from configuration content.
        
        Args:
            content: Raw configuration file content
            
        Returns:
            Dictionary containing parsed metadata with defaults
        """
        metadata = {}
        
        # Extract basic fields using regex patterns
        patterns = {
            'name': r'(?:- )?\*\*Name\*\*:\s*([^\n]+)',
            'description': r'(?:- )?\*\*Description\*\*:\s*([^\n]+)',
            'emoji': r'(?:- )?\*\*Emoji\*\*:\s*([^\n]+)',
            'duration_target': r'(?:- )?\*\*Duration Target\*\*:\s*([^\n]+)',
            'privacy': r'(?:- )?\*\*Privacy\*\*:\s*([^\n]+)',
            'randomize_selection': r'(?:- )?\*\*Randomize Selection\*\*:\s*([^\n]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                metadata[key] = match.group(1).strip()
        
        # Set sensible defaults
        metadata.setdefault('name', f"{self.config_path.stem.title()} Playlist")
        metadata.setdefault('description', 'Created with Alex Method DJ')
        metadata.setdefault('emoji', '🎵')
        metadata.setdefault('privacy', 'public')
        metadata.setdefault('randomize_selection', 'false')
        
        return metadata
    
    def _parse_search_queries(self, content: str) -> List[str]:
        """Parse search queries from configuration content.
        
        Args:
            content: Raw configuration file content
            
        Returns:
            List of search query strings
        """
        queries = []
        
        # Look for Search Queries section
        search_section = re.search(
            r'## Search Queries\s*\n(.*?)(?=\n##|\Z)', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        if search_section:
            for line in search_section.group(1).strip().split('\n'):
                line = line.strip()
                if line and line.startswith('- '):
                    query = line[2:].strip()
                    if query:
                        queries.append(query)
        
        return queries
    
    def _parse_track_categories(self, content: str) -> Dict[str, Any]:
        """Parse track categories for phased playlists.
        
        Args:
            content: Raw configuration file content
            
        Returns:
            Dictionary mapping category names to their configuration
        """
        categories = {}
        
        # Look for Track Categories section
        categories_section = re.search(
            r'## Track Categories\s*\n(.*?)(?=\n##|\Z)', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        if not categories_section:
            return categories
        
        current_category = None
        current_duration = 30  # Default duration
        current_queries = []
        
        for line in categories_section.group(1).strip().split('\n'):
            line = line.strip()
            
            # Category header (### Category Name (duration))
            category_match = re.match(r'###\s+(.+?)\s*\((\d+)\s*minutes?\)', line)
            if category_match:
                # Save previous category
                if current_category and current_queries:
                    categories[current_category] = {
                        'duration': current_duration,
                        'queries': current_queries.copy()
                    }
                
                # Start new category
                current_category = category_match.group(1).strip()
                current_duration = int(category_match.group(2))
                current_queries = []
                continue
            
            # Queries line
            if line.startswith('- Queries: '):
                query = line[11:].strip()  # Remove "- Queries: "
                if query:
                    current_queries.append(query)
        
        # Save last category
        if current_category and current_queries:
            categories[current_category] = {
                'duration': current_duration,
                'queries': current_queries
            }
        
        return categories
    
    def _parse_filters(self, content: str) -> Dict[str, List[str]]:
        """Parse include/exclude filters from configuration content.
        
        Args:
            content: Raw configuration file content
            
        Returns:
            Dictionary with 'include' and 'exclude' filter lists
        """
        filters = {'include': [], 'exclude': []}
        
        # Look for Track Filters section
        filters_section = re.search(
            r'## Track Filters\s*\n(.*?)(?=\n##|\Z)', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        if not filters_section:
            return filters
        
        current_filter_type = None
        
        for line in filters_section.group(1).strip().split('\n'):
            line = line.strip()
            
            # Filter type headers
            if line.startswith('### Include Keywords'):
                current_filter_type = 'include'
                continue
            elif line.startswith('### Exclude Keywords'):
                current_filter_type = 'exclude'
                continue
            
            # Filter items
            if current_filter_type and line.startswith('- '):
                keyword = line[2:].strip()
                if keyword:
                    filters[current_filter_type].append(keyword.lower())
        
        return filters
    
    def get_config(self) -> Dict[str, Any]:
        """Get the complete parsed configuration.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config_data
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get just the metadata section.
        
        Returns:
            Metadata dictionary
        """
        return self.config_data.get('metadata', {})
    
    def get_visual_theme(self) -> Dict[str, Any]:
        """Extract visual theming information for cover art generation.
        
        Returns:
            Dictionary containing visual theme data
        """
        metadata = self.get_metadata()
        return {
            'name': metadata.get('name', ''),
            'description': metadata.get('description', ''),
            'emoji': metadata.get('emoji', '🎵'),
            'file_content': self.config_data.get('file_content', '')
        }
    
    def get_search_queries(self) -> List[str]:
        """Get the search queries list.
        
        Returns:
            List of search query strings
        """
        return self.config_data.get('search_queries', [])
    
    def get_track_categories(self) -> Dict[str, Any]:
        """Get track categories for phased playlists.
        
        Returns:
            Dictionary of track categories
        """
        return self.config_data.get('track_categories', {})
    
    def get_filters(self) -> Dict[str, List[str]]:
        """Get include/exclude filters.
        
        Returns:
            Dictionary with filter lists
        """
        return self.config_data.get('filters', {'include': [], 'exclude': []})
    
    def is_phased_playlist(self) -> bool:
        """Check if this is a phased playlist configuration.
        
        Returns:
            True if playlist has track categories (phased), False otherwise
        """
        return bool(self.get_track_categories())
    
    def get_total_target_duration(self) -> Optional[int]:
        """Calculate total target duration for phased playlists.
        
        Returns:
            Total duration in minutes, or None if not a phased playlist
        """
        categories = self.get_track_categories()
        if not categories:
            # Try to parse from metadata duration_target
            duration_target = self.get_metadata().get('duration_target', '')
            if duration_target:
                numbers = re.findall(r'\d+', duration_target)
                if numbers:
                    return int(numbers[0])
            return None
        
        return sum(cat['duration'] for cat in categories.values())
    
    def validate_config(self) -> List[str]:
        """Validate the configuration and return any issues found.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        issues = []
        
        metadata = self.get_metadata()
        search_queries = self.get_search_queries()
        track_categories = self.get_track_categories()
        
        # Check for required fields
        if not metadata.get('name'):
            issues.append("Missing playlist name")
        
        if not search_queries and not track_categories:
            issues.append("No search queries or track categories defined")
        
        # Validate phased playlist structure
        if track_categories:
            for cat_name, cat_info in track_categories.items():
                if not cat_info.get('queries'):
                    issues.append(f"Category '{cat_name}' has no queries")
                if cat_info.get('duration', 0) <= 0:
                    issues.append(f"Category '{cat_name}' has invalid duration")
        
        return issues


# Test function for module validation
def test_config_parser() -> None:
    """Test the configuration parser with a sample configuration."""
    safe_print("Testing Configuration Parser Module...")
    
    # Create a sample config for testing
    sample_config = """# Test Playlist

## Metadata
- **Name**: Test Playlist - Alex Method
- **Description**: A test playlist for validation
- **Emoji**: 🎵
- **Duration Target**: 60 minutes
- **Privacy**: public

## Search Queries
- chill electronic
- ambient music
- downtempo

## Track Categories
### Intro (10 minutes)
- Queries: ambient intro music

### Main (40 minutes)  
- Queries: electronic chill
- Queries: downtempo beats

### Outro (10 minutes)
- Queries: ambient outro

## Track Filters
### Exclude Keywords
- explicit
- remix
"""
    
    # Write sample config to temporary file
    test_file = Path("test_config.md")
    test_file.write_text(sample_config, encoding='utf-8')
    
    try:
        # Test parsing
        parser = PlaylistConfigParser("test_config.md")
        config = parser.get_config()
        
        safe_print(f"✅ Parsed configuration successfully")
        safe_print(f"   Name: {parser.get_metadata()['name']}")
        safe_print(f"   Search Queries: {len(parser.get_search_queries())}")
        safe_print(f"   Is Phased: {parser.is_phased_playlist()}")
        safe_print(f"   Total Duration: {parser.get_total_target_duration()} minutes")
        
        # Test validation
        issues = parser.validate_config()
        if issues:
            safe_print(f"❌ Validation issues: {issues}")
        else:
            safe_print("✅ Configuration validation passed")
            
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()
    
    safe_print("Configuration Parser Module test complete!")


if __name__ == "__main__":
    test_config_parser()
