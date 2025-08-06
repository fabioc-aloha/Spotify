#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alex Method DJ Platform - Smart Print Module
Intelligent cross-platform emoji handling with environment detection

Features:
- Smart environment detection (Windows Terminal, VS Code, CI/CD, etc.)
- Global ASCII mode control via FORCE_ASCII_MODE variable
- Comprehensive emoji-to-text conversion
- Graceful Unicode encoding fallbacks
- Cross-platform terminal capability analysis

Usage:
    from src.smart_print import safe_print, set_force_ascii_mode
    
    # Set global ASCII mode (optional)
    set_force_ascii_mode(True)
    
    # Use intelligent printing
    safe_print("🎵 This will display appropriately for the environment!")
"""

import os
import sys
import re
from typing import Optional

# Global flag for ASCII mode - can be set by applications
_FORCE_ASCII_MODE = False


def set_force_ascii_mode(enabled: bool) -> None:
    """Set global ASCII mode for all safe_print calls.
    
    Args:
        enabled: True to force ASCII conversion, False for smart detection
    """
    global _FORCE_ASCII_MODE
    _FORCE_ASCII_MODE = enabled


def get_force_ascii_mode() -> bool:
    """Get current ASCII mode setting.
    
    Returns:
        Current ASCII mode setting
    """
    return _FORCE_ASCII_MODE


def safe_print(text: str) -> None:
    """Print text safely with intelligent emoji handling.
    
    This function automatically detects the environment capabilities and either
    preserves emojis (modern terminals) or converts them to text alternatives
    (legacy terminals, CI/CD environments).
    
    Args:
        text: The text to print
    """
    # Use global ASCII mode flag
    should_force_ascii = _FORCE_ASCII_MODE
    
    # Determine if we should preserve emojis based on environment
    should_preserve_emojis = _should_preserve_emojis() and not should_force_ascii
    
    if not should_preserve_emojis:
        # Convert emojis to text alternatives
        text = _convert_emojis_to_text(text)
    
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: convert emojis and try again
        if should_preserve_emojis:
            # If we were trying to preserve emojis but failed, convert them
            text = _convert_emojis_to_text(text)
            try:
                print(text)
            except UnicodeEncodeError:
                # Last resort: remove all non-ASCII characters
                ascii_text = text.encode('ascii', 'ignore').decode('ascii')
                print(ascii_text)
        else:
            # Last resort: remove all non-ASCII characters
            ascii_text = text.encode('ascii', 'ignore').decode('ascii')
            print(ascii_text)


def _should_preserve_emojis() -> bool:
    """Determine if the current environment supports emoji display.
    
    This function analyzes the execution environment to determine whether
    emojis should be displayed natively or converted to text alternatives.
    
    Returns:
        True if emojis should be preserved, False if they should be converted
    """
    # Check for automated/CI environments where emojis should be avoided
    ci_indicators = ['CI', 'CONTINUOUS_INTEGRATION', 'GITHUB_ACTIONS', 'JENKINS_URL', 'TRAVIS']
    if any(os.getenv(var) for var in ci_indicators):
        return False
    
    # Check for log file redirection
    if not sys.stdout.isatty():
        return False
    
    # Check Windows terminal capabilities
    if sys.platform == 'win32':
        # Check for modern Windows terminals that support emojis
        term_program = os.getenv('TERM_PROGRAM', '').lower()
        wt_session = os.getenv('WT_SESSION')  # Windows Terminal
        vscode_term = os.getenv('VSCODE_PID')  # VS Code integrated terminal
        
        # Modern terminals that support emojis well
        if any([
            term_program in ['vscode', 'windows terminal'],
            wt_session,  # Windows Terminal
            vscode_term,  # VS Code integrated terminal
            os.getenv('PYCHARM_HOSTED'),  # PyCharm terminal
        ]):
            return True
        
        # Check PowerShell version (PowerShell 7+ has better Unicode support)
        if 'pwsh' in os.getenv('PSModulePath', '').lower():
            return True
        
        # Legacy cmd.exe or old PowerShell - avoid emojis
        return False
    
    # Unix-like systems generally have good Unicode support
    return True


def _convert_emojis_to_text(text: str) -> str:
    """Convert emojis to text equivalents.
    
    This function provides a comprehensive mapping of common emojis to
    text alternatives that are suitable for legacy terminals and CI/CD
    environments.
    
    Args:
        text: Text containing emojis to convert
        
    Returns:
        Text with emojis converted to text alternatives
    """
    # Replace specific emojis with text equivalents
    emoji_replacements = {
        r'🎵': '[MUSIC]',
        r'❌': '[ERROR]',
        r'⚠️': '[WARNING]', 
        r'✅': '[SUCCESS]',
        r'📁': '[FOLDER]',
        r'🎨': '[ART]',
        r'🔍': '[SEARCH]',
        r'🔄': '[REFRESH]',
        r'🔧': '[TOOL]',
        r'📝': '[NOTE]',
        r'🔗': '[LINK]',
        r'⭐': '[STAR]',
        r'🚀': '[ROCKET]',
        r'💡': '[IDEA]',
        r'🎯': '[TARGET]',
        r'📊': '[CHART]',
        r'🔥': '[FIRE]',
        r'💎': '[GEM]',
        r'🌟': '[SPARKLE]',
        r'🎭': '[THEATER]',
        r'📋': '[CLIPBOARD]',
        r'🆕': '[NEW]',
        r'📱': '[MOBILE]',
        r'⏱️': '[TIMER]',
        r'🎉': '[PARTY]',
        r'💻': '[COMPUTER]',
        r'📄': '[DOCUMENT]',
        r'⚡': '[LIGHTNING]',
        r'🌈': '[RAINBOW]',
        r'🔊': '[SPEAKER]',
        r'🎧': '[HEADPHONES]',
        r'🔒': '[LOCK]',
        r'🔓': '[UNLOCK]',
        r'📈': '[TRENDING_UP]',
        r'📉': '[TRENDING_DOWN]',
        r'🏆': '[TROPHY]',
        r'⭐': '[STAR]',
        r'💫': '[DIZZY]',
        r'🌙': '[MOON]',
        r'☀️': '[SUN]',
        r'🔮': '[CRYSTAL_BALL]',
        r'🎪': '[CIRCUS]',
        r'🎨': '[PALETTE]',
        r'📸': '[CAMERA]',
        r'🎬': '[CLAPPER]',
        r'📹': '[VIDEO_CAMERA]',
        r'🎤': '[MICROPHONE]',
        r'🥁': '[DRUM]',
        r'🎸': '[GUITAR]',
        r'🎹': '[KEYBOARD]',
        r'🎺': '[TRUMPET]',
        r'🎷': '[SAXOPHONE]',
        r'🎻': '[VIOLIN]',
    }
    
    for emoji, replacement in emoji_replacements.items():
        text = re.sub(emoji, replacement, text)
    
    # Remove any remaining emoji characters using Unicode ranges
    emoji_pattern = re.compile("["
                              u"\U0001F600-\U0001F64F"  # emoticons
                              u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                              u"\U0001F680-\U0001F6FF"  # transport & map symbols
                              u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                              u"\U00002702-\U000027B0"  # dingbats
                              u"\U000024C2-\U0001F251"
                              "]+", flags=re.UNICODE)
    text = emoji_pattern.sub('[EMOJI]', text)
    
    return text


def print_environment_info() -> None:
    """Print detailed information about the current environment.
    
    This is useful for debugging emoji display issues and understanding
    why certain environments are detected as legacy or modern.
    """
    safe_print("\n=== Smart Print Environment Analysis ===")
    safe_print(f"Platform: {sys.platform}")
    safe_print(f"Force ASCII Mode: {_FORCE_ASCII_MODE}")
    safe_print(f"Should Preserve Emojis: {_should_preserve_emojis()}")
    safe_print(f"stdout.isatty(): {sys.stdout.isatty()}")
    
    safe_print("\nEnvironment Variables:")
    env_vars = [
        'TERM_PROGRAM', 'WT_SESSION', 'VSCODE_PID', 'PYCHARM_HOSTED',
        'CI', 'CONTINUOUS_INTEGRATION', 'GITHUB_ACTIONS', 'JENKINS_URL', 'TRAVIS'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            safe_print(f"  {var}: {value}")
    
    safe_print("\nTest Emojis:")
    test_emojis = "🎵 ✅ ❌ ⚠️ 📁 🎨 🔍"
    safe_print(f"  Original: {test_emojis}")
    safe_print(f"  Converted: {_convert_emojis_to_text(test_emojis)}")
    safe_print("=" * 45)


# Test function for module validation
def test_smart_print() -> None:
    """Test the smart print functionality with various scenarios."""
    print("Testing Smart Print Module...")
    
    # Test basic functionality
    safe_print("🎵 Testing basic emoji handling")
    
    # Test with ASCII mode
    original_mode = _FORCE_ASCII_MODE
    set_force_ascii_mode(True)
    safe_print("🎵 Testing with ASCII mode enabled")
    set_force_ascii_mode(original_mode)
    
    # Test environment info
    print_environment_info()
    
    print("Smart Print Module test complete!")


if __name__ == "__main__":
    test_smart_print()
