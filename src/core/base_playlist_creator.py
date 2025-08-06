#!/usr/bin/env python3
"""
Base Playlist Creator - Alex Method DJ Platform Support

Abstract base class for all music platform integrations.
Part of the Alex Method DJ Platform system
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import re
import os
from pathlib import Path

class BasePlaylistCreator(ABC):
    """Abstract base class for platform-specific playlist creators."""
    
    def __init__(self):
        """Initialize common attributes."""
        self.config: Optional[Dict[str, Any]] = None
        self._raw_config_content = ""
        self.config_file_path: Optional[str] = None
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load and parse playlist configuration from markdown file."""
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        # Store config file path for later use
        self.config_file_path = str(config_path.absolute())
        
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self._raw_config_content = content  # Store raw content for phased playlist parsing
        
        # Initialize config structure
        config = {
            'metadata': {},
            'search_queries': [],
            'track_categories': {},
            'track_filters': {},
            'track_limits': {},
            'content_preferences': {},
            'special_instructions': []
        }
        
        # Parse metadata section
        metadata_match = re.search(r'## Metadata\s*\n(.*?)(?=\n##|\n\n|$)', content, re.DOTALL)
        if metadata_match:
            metadata_lines = metadata_match.group(1).strip().split('\n')
            for line in metadata_lines:
                # Handle both bullet point format (- **Name**:) and direct format (**Name**:)
                if line.startswith('- **'):
                    match = re.match(r'- \*\*(.*?)\*\*:\s*(.*)', line)
                    if match:
                        key = match.group(1).lower().replace(' ', '_')
                        value = match.group(2)
                        config['metadata'][key] = value
                elif line.startswith('**') and ':' in line:
                    match = re.match(r'\*\*(.*?)\*\*:\s*(.*)', line)
                    if match:
                        key = match.group(1).lower().replace(' ', '_')
                        value = match.group(2)
                        config['metadata'][key] = value
        
        # Parse search queries
        queries_match = re.search(r'## Search Queries\s*\n(.*?)(?=\n##|\n\n|$)', content, re.DOTALL)
        if queries_match:
            queries_lines = queries_match.group(1).strip().split('\n')
            for line in queries_lines:
                if line.startswith('- ') and not line.startswith('- **'):
                    # Skip format instruction lines and only get actual query lines
                    query = line[2:].strip()
                    if query and not query.startswith('FORMAT:') and not query.startswith('FOCUS ON:'):
                        config['search_queries'].append(query)
        
        # Parse content preferences (YouTube-specific)
        prefs_match = re.search(r'## Content Preferences\s*\n(.*?)(?=\n##|$)', content, re.DOTALL)
        if prefs_match:
            prefs_lines = prefs_match.group(1).strip().split('\n')
            for line in prefs_lines:
                if line.startswith('- **'):
                    match = re.match(r'- \*\*(.*?)\*\*:\s*(.*)', line)
                    if match:
                        key = match.group(1).lower().replace(' ', '_')
                        value = match.group(2)
                        
                        # Handle array values like [music_video, live_performance]
                        if value.startswith('[') and value.endswith(']'):
                            array_content = value[1:-1]
                            config['content_preferences'][key] = [item.strip() for item in array_content.split(',') if item.strip()]
                        else:
                            config['content_preferences'][key] = value
        
        # Parse track filters
        filters_match = re.search(r'## Track Filters\s*\n(.*?)(?=\n##|$)', content, re.DOTALL)
        if filters_match:
            filters_text = filters_match.group(1)
            
            # Include keywords
            include_match = re.search(r'### Include Keywords\s*\n(.*?)(?=\n###|$)', filters_text, re.DOTALL)
            if include_match:
                include_lines = include_match.group(1).strip().split('\n')
                config['track_filters']['include'] = [line[2:] for line in include_lines if line.startswith('- ')]
            
            # Exclude keywords
            exclude_match = re.search(r'### Exclude Keywords\s*\n(.*?)(?=\n###|$)', filters_text, re.DOTALL)
            if exclude_match:
                exclude_lines = exclude_match.group(1).strip().split('\n')
                config['track_filters']['exclude'] = [line[2:] for line in exclude_lines if line.startswith('- ')]
            
            # Duration preferences
            duration_match = re.search(r'### Duration Preferences\s*\n(.*?)(?=\n###|$)', filters_text, re.DOTALL)
            if duration_match:
                duration_lines = duration_match.group(1).strip().split('\n')
                config['track_filters']['duration'] = {}
                for line in duration_lines:
                    if line.startswith('- **'):
                        match = re.match(r'- \*\*(.*?)\*\*:\s*(.*)', line)
                        if match:
                            key = match.group(1).lower()
                            value = match.group(2)
                            if 'minute' in value:
                                # Extract number from duration
                                num_match = re.search(r'(\d+)', value)
                                if num_match:
                                    config['track_filters']['duration'][key] = int(num_match.group(1))
        
        # Parse track limits
        limits_match = re.search(r'## Track Limits\s*\n(.*?)(?=\n##|$)', content, re.DOTALL)
        if limits_match:
            limits_lines = limits_match.group(1).strip().split('\n')
            for line in limits_lines:
                if line.startswith('- **'):
                    match = re.match(r'- \*\*(.*?)\*\*:\s*(.*)', line)
                    if match:
                        key = match.group(1).lower().replace(' ', '_')
                        value = match.group(2)
                        try:
                            if value.isdigit():
                                config['track_limits'][key] = int(value)
                            elif value.lower() == 'none':
                                config['track_limits'][key] = None
                            else:
                                # Try to extract number from text like "20 (prefer less mainstream)"
                                num_match = re.search(r'(\d+)', value)
                                if num_match:
                                    config['track_limits'][key] = int(num_match.group(1))
                                else:
                                    config['track_limits'][key] = value
                        except:
                            config['track_limits'][key] = value
        
        # Parse special instructions
        instructions_match = re.search(r'## Special Instructions\s*\n(.*?)(?=\n##|$)', content, re.DOTALL)
        if instructions_match:
            instructions_lines = instructions_match.group(1).strip().split('\n')
            config['special_instructions'] = [line[2:] for line in instructions_lines if line.startswith('- ')]
        
        self.config = config
        return config
    
    def parse_target_duration(self, duration_str: str) -> Optional[int]:
        """Parse target duration from string format."""
        if not duration_str:
            return None
        
        # Extract numbers from duration string
        duration_match = re.search(r'(\d+)', duration_str)
        if duration_match:
            return int(duration_match.group(1))
        
        return None
    
    def has_track_categories(self) -> bool:
        """Check if config has Track Categories section for phased playlists."""
        content = getattr(self, '_raw_config_content', '')
        return '## Track Categories' in content
    
    def parse_track_categories(self) -> Dict:
        """Parse Track Categories section into phases with durations and queries."""
        content = getattr(self, '_raw_config_content', '')
        if not content:
            return {}
        
        phases = {}
        categories_match = re.search(r'## Track Categories\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        
        if not categories_match:
            return {}
        
        categories_content = categories_match.group(1)
        
        # Parse each phase: ### Grounding (10 minutes)
        phase_pattern = r'### ([^(]+)\((\d+)\s*minutes?\)'
        query_pattern = r'- Queries?: (.+)'
        
        current_phase = None
        for line in categories_content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check for phase header
            phase_match = re.match(phase_pattern, line)
            if phase_match:
                phase_name = phase_match.group(1).strip()
                duration = int(phase_match.group(2))
                current_phase = phase_name
                phases[current_phase] = {
                    'duration': duration,
                    'queries': []
                }
                continue
            
            # Check for queries line
            if current_phase and line.startswith('- Queries'):
                query_match = re.match(query_pattern, line)
                if query_match:
                    query_text = query_match.group(1)
                    # Split by commas and clean up
                    queries = [q.strip() for q in query_text.split(',') if q.strip()]
                    phases[current_phase]['queries'].extend(queries)
        
        return phases
    
    def apply_duration_targeting(self, content_list: List[Dict], target_minutes: int) -> List[Dict]:
        """Apply duration targeting to content list - shared algorithm."""
        if not content_list or target_minutes <= 0:
            return content_list
        
        target_seconds = target_minutes * 60
        variance_seconds = target_seconds * 0.1  # ±10% variance
        
        target_min = target_seconds - variance_seconds
        target_max = target_seconds + variance_seconds
        
        # Try to find optimal combination
        optimal_content = self.find_optimal_content_combination(content_list, target_min / 60, target_max / 60)
        
        if optimal_content:
            return optimal_content
        
        # Fallback to greedy selection
        return self.greedy_content_selection(content_list, target_min / 60, target_max / 60)
    
    def find_optimal_content_combination(self, content_list: List[Dict], target_min: float, target_max: float) -> List[Dict]:
        """Find optimal content combination using dynamic programming approach."""
        if not content_list:
            return []
        
        # Sort by duration for better optimization
        sorted_content = sorted(content_list, key=lambda x: x.get('duration_minutes', 0))
        
        # For large lists, use sampling to maintain performance
        if len(sorted_content) > 100:
            # Take a diverse sample: shortest, longest, and middle range
            sample_size = 100
            step = len(sorted_content) // sample_size
            sampled_content = sorted_content[::step][:sample_size]
        else:
            sampled_content = sorted_content
        
        best_combination = []
        best_duration = 0
        
        # Try different starting points and build combinations
        for i in range(min(20, len(sampled_content))):  # Limit iterations for performance
            current_combination = []
            current_duration = 0
            available_content = sampled_content.copy()
            
            # Start with the i-th content item
            if i < len(available_content):
                current_combination.append(available_content[i])
                current_duration = available_content[i].get('duration_minutes', 0)
                available_content.remove(available_content[i])
            
            # Greedily add content that brings us closer to target
            while available_content and current_duration < target_max:
                remaining_time = target_max - current_duration
                
                # Find content item that best fits remaining time
                best_fit = None
                best_fit_diff = float('inf')
                
                for content in available_content:
                    content_duration = content.get('duration_minutes', 0)
                    new_total = current_duration + content_duration
                    
                    if new_total <= target_max:
                        # Prefer content that gets us closer to target
                        target_center = (target_min + target_max) / 2
                        diff = abs(new_total - target_center)
                        if diff < best_fit_diff:
                            best_fit = content
                            best_fit_diff = diff
                
                if best_fit:
                    current_combination.append(best_fit)
                    current_duration += best_fit.get('duration_minutes', 0)
                    available_content.remove(best_fit)
                else:
                    break
            
            # Check if this combination is better than our current best
            if (target_min <= current_duration <= target_max and 
                (not best_combination or 
                 abs(current_duration - (target_min + target_max) / 2) < 
                 abs(best_duration - (target_min + target_max) / 2))):
                best_combination = current_combination
                best_duration = current_duration
        
        return best_combination
    
    def greedy_content_selection(self, content_list: List[Dict], target_min: float, target_max: float) -> List[Dict]:
        """Greedy content selection as fallback."""
        if not content_list:
            return []
        
        # Sort by duration (shortest first for greedy approach)
        sorted_content = sorted(content_list, key=lambda x: x.get('duration_minutes', 0))
        
        selected_content = []
        total_duration = 0
        
        for content in sorted_content:
            content_duration = content.get('duration_minutes', 0)
            
            if total_duration + content_duration <= target_max:
                selected_content.append(content)
                total_duration += content_duration
                
                # Stop if we've reached a good duration
                if total_duration >= target_min:
                    break
        
        return selected_content
    
    # Abstract methods that must be implemented by platform-specific classes
    
    @abstractmethod
    def setup_platform_client(self) -> None:
        """Set up platform-specific API client and authentication."""
        pass
    
    @abstractmethod
    def search_content(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for content (tracks/videos) on the platform."""
        pass
    
    @abstractmethod
    def create_playlist(self, name: str, description: str, public: bool = True) -> str:
        """Create a new playlist and return its ID."""
        pass
    
    @abstractmethod
    def add_content_to_playlist(self, playlist_id: str, content_ids: List[str]) -> None:
        """Add content items to a playlist."""
        pass
    
    @abstractmethod
    def extract_content_info(self, item: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Extract standardized information from platform-specific content item."""
        pass
    
    @abstractmethod
    def is_content_suitable(self, item: Dict[str, Any]) -> bool:
        """Determine if content item meets quality and filtering criteria."""
        pass
    
    @abstractmethod
    def find_existing_playlist(self, playlist_name: str) -> Optional[Dict[str, Any]]:
        """Find existing playlist by name."""
        pass
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return the platform name for display purposes."""
        pass
