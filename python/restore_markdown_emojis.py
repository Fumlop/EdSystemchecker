#!/usr/bin/env python3
"""
Restore beautiful Unicode emojis in Markdown output while keeping print statements ASCII-compatible
"""

import os
import re

def restore_markdown_emojis(filepath):
    """Restore Unicode emojis in Markdown content but keep print statements ASCII-compatible."""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Keep track of changes
        changes_made = False
        original_content = content
        
        # ASCII to Unicode replacements for Markdown content
        emoji_restorations = {
            # Status icons in tables and headers
            "[OK]": "✅",
            "[FIRE]": "🔥", 
            "[HIGH]": "🟢",
            "[MED]": "🟡",
            "[LOW]": "🔴",
            "[SWORD]": "⚔️",
            "[BLUE]": "🔵",
            "[ORANGE]": "🔶", 
            "[WARN]": "⚠️",
            "[TARGET]": "🎯",
            "[INFO]": "📊",
            "[STAR]": "🌟",
        }
        
        # Process line by line to avoid affecting print statements
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            original_line = line
            
            # Only restore emojis if this is NOT a print statement
            if not (line.strip().startswith('print(') or 'print(f"' in line):
                for ascii_icon, unicode_emoji in emoji_restorations.items():
                    if ascii_icon in line:
                        line = line.replace(ascii_icon, unicode_emoji)
                        if line != original_line:
                            changes_made = True
            
            new_lines.append(line)
        
        # Write back if changes were made
        if changes_made:
            restored_content = '\n'.join(new_lines)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(restored_content)
            print(f"✅ Restored beautiful emojis in {os.path.basename(filepath)}")
        else:
            print(f"- No emoji restoration needed in {os.path.basename(filepath)}")
            
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")

def main():
    """Restore beautiful emojis in all Markdown generation scripts."""
    
    python_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Files to restore emojis in
    files_to_restore = [
        "create_contested_md.py",
        "create_fortified_md.py", 
        "create_exploited_md.py",
        # stronghold already restored manually
    ]
    
    print("🎨 Restoring beautiful Unicode emojis in Markdown output...")
    print("🔧 Keeping print statements ASCII-compatible for Windows PowerShell!\n")
    
    for filename in files_to_restore:
        filepath = os.path.join(python_dir, filename)
        if os.path.exists(filepath):
            print(f"Processing {filename}:")
            restore_markdown_emojis(filepath)
        else:
            print(f"❌ File not found: {filepath}")
        print()
    
    print("🎉 Emoji restoration complete!")
    print("📝 Your Markdown reports will have beautiful icons!")
    print("🖥️ Python print statements remain Windows PowerShell compatible!")

if __name__ == "__main__":
    main()
