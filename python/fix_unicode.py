#!/usr/bin/env python3
"""
Fix Unicode characters in all create_*_md.py files for Windows PowerShell compatibility
"""

import os
import re

def fix_unicode_in_file(filepath):
    """Replace Unicode emojis with ASCII equivalents in a file."""
    
    unicode_replacements = {
        # Status icons
        "✅": "[OK]",
        "🔥": "[FIRE]", 
        "⚠️": "[WARN]",
        
        # Activity levels
        "🟢": "[HIGH]",
        "🟡": "[MED]", 
        "🔴": "[LOW]",
        
        # Combat states
        "🌟": "[STAR]",
        "⚔️": "[SWORD]",
        
        # Other icons
        "🔵": "[BLUE]",
        "🔶": "[ORANGE]",
        "📊": "[INFO]",
        "⭐": "[STAR]",
        "💀": "[SKULL]",
        "🎯": "[TARGET]",
        "📈": "[CHART]"
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Track changes
        changes_made = False
        original_content = content
        
        # Replace each Unicode character
        for unicode_char, ascii_replacement in unicode_replacements.items():
            if unicode_char in content:
                content = content.replace(unicode_char, ascii_replacement)
                changes_made = True
                print(f"  Replaced '{unicode_char}' with '{ascii_replacement}'")
        
        # Write back if changes were made
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated {filepath}")
        else:
            print(f"- No changes needed for {filepath}")
            
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")

def main():
    """Fix Unicode in all create_*_md.py files."""
    
    python_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Files to process
    files_to_fix = [
        "create_stronghold_md.py",
        "create_fortified_md.py", 
        "create_exploited_md.py",
        "create_contested_md.py"
    ]
    
    print("🔧 Fixing Unicode characters for Windows PowerShell compatibility...\n")
    
    for filename in files_to_fix:
        filepath = os.path.join(python_dir, filename)
        if os.path.exists(filepath):
            print(f"Processing {filename}:")
            fix_unicode_in_file(filepath)
        else:
            print(f"✗ File not found: {filepath}")
        print()
    
    print("✅ Unicode fix complete!")

if __name__ == "__main__":
    main()
