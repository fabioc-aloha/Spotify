#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alex Method DJ Platform - File Utilities Module
Common file operations and path handling utilities

Features:
- Safe file reading/writing with encoding handling
- Path normalization and validation
- Configuration file discovery
- Metadata updating utilities
- Cross-platform path handling

Usage:
    from src.file_utils import safe_read_file, safe_write_file, update_config_metadata
    
    content = safe_read_file('config.md')
    safe_write_file('output.txt', 'content')
    update_config_metadata('config.md', {'key': 'value'})
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from src.smart_print import safe_print


def safe_read_file(file_path: str, encoding: str = 'utf-8') -> str:
    """Read file content safely with proper encoding handling.
    
    Args:
        file_path: Path to the file to read
        encoding: Text encoding to use (default: utf-8)
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If encoding fails
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        return path.read_text(encoding=encoding)
    except UnicodeDecodeError as e:
        safe_print(f"⚠️ Encoding error with {encoding}, trying fallback encodings...")
        
        # Try common fallback encodings
        fallback_encodings = ['utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']
        
        for fallback in fallback_encodings:
            try:
                content = path.read_text(encoding=fallback)
                safe_print(f"✅ Successfully read with {fallback} encoding")
                return content
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, re-raise the original error
        raise e


def safe_write_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
    """Write content to file safely with proper encoding handling.
    
    Args:
        file_path: Path to the file to write
        content: Content to write
        encoding: Text encoding to use (default: utf-8)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(file_path)
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        path.write_text(content, encoding=encoding)
        return True
        
    except Exception as e:
        safe_print(f"❌ Error writing file {file_path}: {e}")
        return False


def normalize_path(file_path: str, relative_to: Optional[str] = None) -> str:
    """Normalize file path for cross-platform compatibility.
    
    Args:
        file_path: Path to normalize
        relative_to: Optional base path for relative calculation
        
    Returns:
        Normalized path string
    """
    path = Path(file_path).resolve()
    
    if relative_to:
        try:
            base = Path(relative_to).resolve()
            relative_path = path.relative_to(base)
            return str(relative_path).replace('\\', '/')
        except ValueError:
            # If path is not relative to base, return absolute path
            pass
    
    return str(path).replace('\\', '/')


def find_config_files(directory: str, pattern: str = "*.md") -> List[Path]:
    """Find configuration files in directory matching pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern to match (default: *.md)
        
    Returns:
        List of matching file paths
    """
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        return []
    
    # Find matching files, excluding common non-config files
    exclude_patterns = ['README.md', 'TEMPLATE*.md', 'template*.md']
    
    matching_files = []
    for file_path in dir_path.glob(pattern):
        # Skip excluded patterns
        if any(file_path.match(exclude) for exclude in exclude_patterns):
            continue
        matching_files.append(file_path)
    
    return sorted(matching_files)


def update_config_metadata(config_file: str, metadata: Dict[str, Any], 
                          section_name: str = "Spotify Playlist Metadata") -> bool:
    """Update or add metadata section to configuration file.
    
    Args:
        config_file: Path to configuration file
        metadata: Dictionary of metadata to add
        section_name: Name of the metadata section
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read current content
        content = safe_read_file(config_file)
        
        # Generate metadata section
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata_lines = [f"## {section_name}"]
        
        # Add timestamp if not provided
        if 'last_updated' not in metadata:
            metadata['last_updated'] = timestamp
        
        # Convert metadata to markdown format
        for key, value in metadata.items():
            # Format key as title case with spaces
            display_key = key.replace('_', ' ').title()
            metadata_lines.append(f"- **{display_key}**: {value}")
        
        metadata_section = '\n'.join(metadata_lines) + '\n\n'
        
        # Pattern to match existing metadata section
        section_pattern = re.compile(
            f'^## {re.escape(section_name)}\\n.*?(?=^##|\\Z)', 
            re.MULTILINE | re.DOTALL
        )
        
        if section_pattern.search(content):
            # Replace existing section
            content = section_pattern.sub(metadata_section.rstrip() + '\n\n', content)
            safe_print(f"   📝 Updated existing {section_name}")
        else:
            # Add new section after main metadata or at beginning
            main_metadata_pattern = re.compile(
                r'(^## Metadata\n.*?(?=^##))', 
                re.MULTILINE | re.DOTALL
            )
            match = main_metadata_pattern.search(content)
            
            if match:
                insert_pos = match.end()
                content = content[:insert_pos] + '\n' + metadata_section + content[insert_pos:]
            else:
                content = metadata_section + content
            
            safe_print(f"   📝 Added {section_name}")
        
        # Write updated content
        return safe_write_file(config_file, content)
        
    except Exception as e:
        safe_print(f"❌ Error updating metadata: {e}")
        return False


def append_track_list(config_file: str, tracks: List[Dict[str, Any]]) -> bool:
    """Append track list to configuration file.
    
    Args:
        config_file: Path to configuration file
        tracks: List of track dictionaries
        
    Returns:
        True if successful, False otherwise
    """
    try:
        content = safe_read_file(config_file)
        
        # Remove any existing track list at the end
        content = re.sub(r'\n### Track List\n.*$', '', content, flags=re.DOTALL)
        
        # Create track list section
        track_list_lines = ["\n### Track List"]
        for i, track in enumerate(tracks, 1):
            duration = track.get('duration_min', 0)
            track_line = f"{i:2d}. {track['name']} - {track['artist']} ({duration:.1f}m)"
            track_list_lines.append(track_line)
        
        track_list_section = '\n'.join(track_list_lines) + '\n'
        
        # Append to content
        updated_content = content.rstrip() + track_list_section
        
        return safe_write_file(config_file, updated_content)
        
    except Exception as e:
        safe_print(f"❌ Error appending track list: {e}")
        return False


def backup_file(file_path: str, backup_suffix: str = ".backup") -> Optional[str]:
    """Create a backup copy of a file.
    
    Args:
        file_path: Path to file to backup
        backup_suffix: Suffix to add to backup filename
        
    Returns:
        Path to backup file if successful, None otherwise
    """
    try:
        source = Path(file_path)
        if not source.exists():
            return None
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{source.stem}_{timestamp}{backup_suffix}{source.suffix}"
        backup_path = source.parent / backup_name
        
        # Copy file content
        content = safe_read_file(str(source))
        if safe_write_file(str(backup_path), content):
            return str(backup_path)
        
        return None
        
    except Exception as e:
        safe_print(f"❌ Error creating backup: {e}")
        return None


def validate_file_path(file_path: str, must_exist: bool = True) -> bool:
    """Validate file path and check existence if required.
    
    Args:
        file_path: Path to validate
        must_exist: Whether file must exist (default: True)
        
    Returns:
        True if path is valid, False otherwise
    """
    try:
        path = Path(file_path)
        
        # Check if path is valid
        if not str(path).strip():
            return False
        
        # Check existence if required
        if must_exist and not path.exists():
            return False
        
        # Check if parent directory exists (for new files)
        if not must_exist and not path.parent.exists():
            return False
        
        return True
        
    except Exception:
        return False


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get detailed information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    path = Path(file_path)
    
    info = {
        'path': str(path),
        'name': path.name,
        'stem': path.stem,
        'suffix': path.suffix,
        'exists': path.exists(),
        'is_file': path.is_file() if path.exists() else None,
        'is_dir': path.is_dir() if path.exists() else None,
        'parent': str(path.parent),
        'absolute_path': str(path.resolve())
    }
    
    if path.exists() and path.is_file():
        stat = path.stat()
        info.update({
            'size_bytes': stat.st_size,
            'size_kb': round(stat.st_size / 1024, 2),
            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat()
        })
    
    return info


# Test function for module validation
def test_file_utils() -> None:
    """Test the file utilities module."""
    print("Testing File Utils Module...")
    
    # Test file operations
    test_content = "# Test File\n\nThis is a test configuration file.\n"
    test_file = "test_file_utils.md"
    
    try:
        # Test writing
        if safe_write_file(test_file, test_content):
            print("✅ File writing successful")
        
        # Test reading
        read_content = safe_read_file(test_file)
        if read_content == test_content:
            print("✅ File reading successful")
        
        # Test file info
        info = get_file_info(test_file)
        print(f"✅ File info: {info['name']} ({info['size_bytes']} bytes)")
        
        # Test metadata update
        metadata = {
            'test_key': 'test_value',
            'track_count': 10,
            'duration': '45.5 minutes'
        }
        
        if update_config_metadata(test_file, metadata, "Test Metadata"):
            print("✅ Metadata update successful")
        
        # Test path normalization
        normalized = normalize_path(test_file)
        print(f"✅ Path normalization: {normalized}")
        
        # Test validation
        if validate_file_path(test_file):
            print("✅ File path validation successful")
        
    finally:
        # Clean up
        test_path = Path(test_file)
        if test_path.exists():
            test_path.unlink()
    
    print("File Utils Module test complete!")


if __name__ == "__main__":
    test_file_utils()
