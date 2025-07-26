#!/usr/bin/env python3
"""
Fix only Python print statements for Windows PowerShell compatibility.
Keep Unicode emojis in the generated Markdown files intact.
"""

import os
import re

def fix_print_statements_in_file(filepath):
    """Replace Unicode emojis ONLY in Python print statements, not in Markdown output."""
    
    print_replacements = {
        # Only for print statements
        'print(f"✅': 'print(f"[OK]',
        'print(f"🔥': 'print(f"[FIRE]',
        'print(f"📊': 'print(f"[INFO]',
        'print(f"⚠️': 'print(f"[WARN]',
        'print("✅': 'print("[OK]',
        'print("🔥': 'print("[FIRE]',
        'print("📊': 'print("[INFO]',
        'print("⚠️': 'print("[WARN]',
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Track changes
        changes_made = False
        original_content = content
        
        # Replace only in print statements
        for unicode_print, ascii_print in print_replacements.items():
            if unicode_print in content:
                content = content.replace(unicode_print, ascii_print)
                changes_made = True
                print(f"  Fixed print statement: {unicode_print} → {ascii_print}")
        
        # Write back if changes were made
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated {filepath}")
        else:
            print(f"- No print statements needed fixing in {filepath}")
            
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")

def restore_markdown_emojis_in_file(filepath):
    """Restore Unicode emojis in Markdown output strings."""
    
    markdown_restorations = {
        # Restore emojis in markdown strings (inside quotes for report content)
        '"[OK]"': '"✅"',
        '"[FIRE]"': '"🔥"', 
        '"[HIGH]"': '"🟢"',
        '"[MED]"': '"🟡"',
        '"[LOW]"': '"🔴"',
        '"[SWORD]"': '"⚔️"',
        '"[BLUE]"': '"🔵"',
        '"[ORANGE]"': '"🔶"',
        '"[WARN]"': '"⚠️"',
        '"[TARGET]"': '"🎯"',
        '"[INFO]"': '"📊"',
        '"[STAR]"': '"🌟"',
        
        # Also restore in f-strings for headers
        '[HIGH]': '🟢',
        '[MED]': '🟡', 
        '[LOW]': '🔴',
        '[BLUE]': '🔵',
        '[ORANGE]': '🔶',
        '[WARN]': '⚠️',
        '[TARGET]': '🎯',
        '[INFO]': '📊',
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Track changes
        changes_made = False
        
        # Restore emojis in markdown content (but NOT in print statements)
        for ascii_md, unicode_emoji in markdown_restorations.items():
            # Only replace if it's NOT in a print statement
            lines = content.split('\n')
            new_lines = []
            
            for line in lines:
                if ascii_md in line and not line.strip().startswith('print('):
                    line = line.replace(ascii_md, unicode_emoji)
                    changes_made = True
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
        
        # Write back if changes were made
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Restored Markdown emojis in {filepath}")
        else:
            print(f"- No Markdown emojis needed restoration in {filepath}")
            
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")

def main():
    """Fix print statements but keep Markdown emojis."""
    
    python_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Files to process
    files_to_fix = [
        "create_stronghold_md.py",
        "create_fortified_md.py", 
        "create_exploited_md.py",
        "create_contested_md.py"
    ]
    
    print("🔧 Fixing ONLY Python print statements for Windows PowerShell...")
    print("📝 Keeping Unicode emojis in Markdown output intact!\n")
    
    for filename in files_to_fix:
        filepath = os.path.join(python_dir, filename)
        if os.path.exists(filepath):
            print(f"Processing {filename}:")
            fix_print_statements_in_file(filepath)
            restore_markdown_emojis_in_file(filepath)
        else:
            print(f"✗ File not found: {filepath}")
        print()
    
    print("✅ Print statement fix complete!")
    print("📝 Markdown emojis preserved for beautiful reports!")

if __name__ == "__main__":
    main()
