#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Safe print utility for handling Unicode encoding issues on Windows
"""

import sys
import os

# Set UTF-8 encoding for Windows console to handle emoji characters
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def safe_print(message):
    """Print function that safely handles Unicode characters on Windows."""
    try:
        print(message)
    except UnicodeEncodeError:
        # Replace emoji with text equivalents if encoding fails
        safe_message = message.replace('🎵', '[MUSIC]').replace('❌', '[ERROR]').replace('📁', '[FOLDER]')
        safe_message = safe_message.replace('✅', '[SUCCESS]').replace('⚡', '[ENERGY]').replace('🎧', '[HEADPHONES]')
        safe_message = safe_message.replace('🎯', '[TARGET]').replace('🎪', '[PARTY]').replace('🧘', '[MEDITATION]')
        safe_message = safe_message.replace('🧠', '[BRAIN]').replace('🎭', '[THEATER]').replace('🔍', '[SEARCH]')
        safe_message = safe_message.replace('🆕', '[NEW]').replace('🎉', '[CELEBRATION]').replace('📱', '[PHONE]')
        safe_message = safe_message.replace('⏱️', '[TIMER]').replace('🔗', '[LINK]').replace('💾', '[SAVE]')
        safe_message = safe_message.replace('🔄', '[REFRESH]').replace('📝', '[MEMO]').replace('📋', '[CLIPBOARD]')
        safe_message = safe_message.replace('📊', '[CHART]').replace('☕', '[COFFEE]').replace('🔀', '[SHUFFLE]')
        safe_message = safe_message.replace('⚠️', '[WARNING]').replace('🎲', '[DICE]')
        print(safe_message)
