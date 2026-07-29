"""
Fix encoding issues in Python files
Run this script to remove problematic characters
"""

import os
import re
from pathlib import Path

def clean_file(filepath):
    """Remove problematic characters from a file"""
    try:
        # Read file with utf-8
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace emojis with text equivalents
        replacements = {
            '✅': '[DONE]',
            '❌': '[X]',
            '⚠️': '[WARN]',
            '🔍': '[SEARCH]',
            '📊': '[CHART]',
            '📈': '[TREND]',
            '📉': '[DOWN]',
            '🔧': '[FIX]',
            '🚀': '[LAUNCH]',
            '🎯': '[TARGET]',
            '💡': '[IDEA]',
            '📋': '[LIST]',
            '📁': '[FOLDER]',
            '📄': '[FILE]',
            '🔄': '[REFRESH]',
            '💰': '[MONEY]',
            '🏆': '[TROPHY]',
            '🌟': '[STAR]',
            '⭐': '[STAR]',
            '🔥': '[FIRE]',
            '🎉': '[PARTY]',
            '🚨': '[ALERT]',
            '🛒': '[CART]',
            '👥': '[USERS]',
            '🧪': '[TEST]',
            '🛡️': '[SHIELD]',
            '📖': '[BOOK]',
            '🔗': '[LINK]',
            '🗂️': '[FOLDER]',
            '📝': '[NOTE]',
            '⚙️': '[GEAR]',
            '🎯': '[TARGET]',
            '📱': '[PHONE]',
            '💎': '[DIAMOND]',
            '🌟': '[STAR]',
            '✨': '[SPARKLE]',
            '🌧️': '[RAIN]',
            '☀️': '[SUN]',
            '❄️': '[SNOW]',
        }
        
        for emoji, text in replacements.items():
            content = content.replace(emoji, text)
        
        # Remove other non-ASCII characters (keep only ASCII)
        content = content.encode('ascii', 'ignore').decode('ascii')
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error cleaning {filepath}: {e}")
        return False

# Clean all Python files in pages directory
pages_dir = Path('pages')
if pages_dir.exists():
    for py_file in pages_dir.glob('*.py'):
        print(f"Cleaning {py_file}...")
        clean_file(py_file)

# Also clean utils
utils_dir = Path('utils')
if utils_dir.exists():
    for py_file in utils_dir.glob('*.py'):
        print(f"Cleaning {py_file}...")
        clean_file(py_file)

# Clean app.py
print("Cleaning app.py...")
clean_file(Path('app.py'))

print("✅ All files cleaned!")