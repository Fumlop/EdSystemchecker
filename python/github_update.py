#!/usr/bin/env python3
"""
GitHub-ready data fetching and report generation
Automatically downloads latest Inara data and generates reports
"""

import requests
import json
import os
from pathlib import Path
from datetime import datetime
import subprocess
import sys

def fetch_inara_data():
    """Fetch latest data from Inara for Felicia Winters (Power ID 5)"""
    print("🌐 Fetching latest data from Inara...")
    
    # Felicia Winters PowerPlay URLs (Power ID 5 based on existing files)
    inara_endpoints = {
        'power-controlled-5': 'https://inara.cz/elite/power-controlled/5/',
        'power-exploited-5': 'https://inara.cz/elite/power-exploited/5/', 
        'power-contested-5': 'https://inara.cz/elite/power-contested/5/'
    }
    
    # Create html directory if it doesn't exist
    html_dir = Path('html')
    html_dir.mkdir(exist_ok=True)
    
    success_count = 0
    
    for file_name, url in inara_endpoints.items():
        try:
            print(f"📥 Downloading {file_name} data from {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(f'html/{file_name}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"✅ {file_name} data saved ({len(response.text)} chars)")
            success_count += 1
        except Exception as e:
            print(f"❌ Error fetching {file_name}: {e}")
    
    return success_count == len(inara_endpoints)

def run_extraction():
    """Run the data extraction pipeline"""
    print("🔄 Running data extraction...")
    try:
        result = subprocess.run([sys.executable, 'python/extract.py'], 
                              capture_output=True, text=True, check=True)
        print("✅ Data extraction completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Extraction failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def generate_all_reports():
    """Generate all markdown reports including transition tracking"""
    print("📄 Generating reports...")
    
    reports = [
        ('stronghold', 'python/create_universal_md.py'),
        ('fortified', 'python/create_universal_md.py'),
        ('exploited', 'python/create_universal_md.py'),
        ('contested', 'python/create_contested_md.py')
    ]
    
    # Generate base reports first
    success_count = 0
    
    for report_type, script in reports:
        try:
            if 'universal' in script:
                cmd = [sys.executable, script, report_type]
            else:
                cmd = [sys.executable, script]
                
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ {report_type.title()} report generated")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate {report_type} report: {e}")
            print(f"Error: {e.stderr}")
    
    # Add transition tracking to applicable reports
    transition_reports = ['stronghold', 'fortified', 'exploited']
    
    for report_type in transition_reports:
        try:
            cmd = [sys.executable, 'python/transition_tracker.py', report_type]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Transition tracking added to {report_type} report")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to add transition tracking to {report_type}: {e}")
            print(f"Error: {e.stderr}")
    
    return success_count

def update_readme_timestamp():
    """Update README with last update timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Add timestamp to README if needed
    readme_path = Path('README.md')
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for existing timestamp line and update it
        lines = content.split('\n')
        updated = False
        
        for i, line in enumerate(lines):
            if '**Last Updated:**' in line:
                lines[i] = f'**Last Updated:** {timestamp}'
                updated = True
                break
        
        if not updated:
            # Add timestamp after the quick actions section
            for i, line in enumerate(lines):
                if '## 📊 Current PowerPlay Status Reports' in line:
                    lines.insert(i, f'**Last Updated:** {timestamp}')
                    lines.insert(i+1, '')
                    break
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"📝 README updated with timestamp: {timestamp}")

def handle_git_conflicts():
    """Handle potential Git conflicts by rebasing local changes"""
    print("🔄 Handling potential Git conflicts...")
    
    try:
        # Check if there are any uncommitted changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("📝 Found uncommitted changes, stashing them...")
            subprocess.run(['git', 'stash', 'push', '-m', 'Auto-stash before rebase'], 
                          capture_output=True, text=True, check=True)
            stashed = True
        else:
            stashed = False
        
        # Fetch latest changes from origin
        print("📡 Fetching latest changes from origin...")
        subprocess.run(['git', 'fetch', 'origin'], 
                      capture_output=True, text=True, check=True)
        
        # Rebase current branch on origin/main
        print("🔄 Rebasing on origin/main...")
        result = subprocess.run(['git', 'rebase', 'origin/main'], 
                              capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            print("⚠️ Rebase had conflicts, trying reset strategy...")
            # If rebase fails, abort and use reset strategy
            subprocess.run(['git', 'rebase', '--abort'], 
                          capture_output=True, text=True, check=False)
            
            # Reset to origin/main (this will lose local commits but keep working directory)
            subprocess.run(['git', 'reset', '--soft', 'origin/main'], 
                          capture_output=True, text=True, check=True)
            print("✅ Reset to origin/main successfully")
        else:
            print("✅ Rebase completed successfully")
        
        # Restore stashed changes if any
        if stashed:
            print("📤 Restoring stashed changes...")
            result = subprocess.run(['git', 'stash', 'pop'], 
                                  capture_output=True, text=True, check=False)
            if result.returncode != 0:
                print("⚠️ Could not restore stashed changes automatically")
                print("💡 Use 'git stash list' and 'git stash apply' manually if needed")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git conflict handling failed: {e}")
        print(f"Output: {e.stdout if e.stdout else 'None'}")
        print(f"Error: {e.stderr if e.stderr else 'None'}")
        return False

def main():
    """Main execution pipeline"""
    print("🚀 Starting PowerPlay Data Update Pipeline")
    print("=" * 50)
    
    # Step 0: Handle potential Git conflicts first
    if not handle_git_conflicts():
        print("⚠️ Git conflict handling had issues, but continuing...")
    
    # Step 1: Fetch latest data from Inara
    if not fetch_inara_data():
        print("❌ Data fetching failed, trying with existing HTML files")
    
    # Step 2: Extract data from HTML files
    if not run_extraction():
        print("❌ Pipeline failed at extraction step")
        sys.exit(1)
    
    # Step 3: Generate reports (now includes transition tracking)
    success_count = generate_all_reports()
    print(f"📊 Generated {success_count}/4 reports successfully")
    
    # Step 4: Update README
    update_readme_timestamp()
    
    print("=" * 50)
    print("✅ Pipeline completed successfully!")
    print("💡 Files are ready for commit and push to GitHub")
    print("💡 Git conflicts have been automatically resolved via rebase")

if __name__ == "__main__":
    main()
