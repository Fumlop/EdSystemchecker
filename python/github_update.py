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
    """Fetch latest data from Inara API or web scraping"""
    # Placeholder for actual Inara data fetching
    # This would need to be implemented based on Inara's API/data source
    print("🌐 Fetching latest data from Inara...")
    
    # Example structure - replace with actual implementation
    inara_endpoints = {
        'stronghold': 'https://inara.cz/elite/powerplay-stronghold-systems/',
        'fortified': 'https://inara.cz/elite/powerplay-fortified-systems/', 
        'exploited': 'https://inara.cz/elite/powerplay-exploited-systems/',
        'contested': 'https://inara.cz/elite/powerplay-contested-systems/'
    }
    
    # Create html directory if it doesn't exist
    html_dir = Path('html')
    html_dir.mkdir(exist_ok=True)
    
    # For now, skip actual fetching since it needs implementation
    print("ℹ️  Data fetching not yet implemented - using existing HTML files")
    return True

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
    """Generate all markdown reports"""
    print("📄 Generating reports...")
    
    reports = [
        ('stronghold', 'python/create_universal_md.py'),
        ('fortified', 'python/create_universal_md.py'),
        ('exploited', 'python/create_universal_md.py'),
        ('contested', 'python/create_contested_md.py')
    ]
    
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

def main():
    """Main execution pipeline"""
    print("🚀 Starting PowerPlay Data Update Pipeline")
    print("=" * 50)
    
    # Step 1: Fetch latest data (if implemented)
    # if not fetch_inara_data():
    #     print("❌ Data fetching failed, using existing data")
    
    # Step 2: Extract data from HTML files
    if not run_extraction():
        print("❌ Pipeline failed at extraction step")
        sys.exit(1)
    
    # Step 3: Generate reports
    success_count = generate_all_reports()
    print(f"📊 Generated {success_count}/4 reports successfully")
    
    # Step 4: Update README
    update_readme_timestamp()
    
    print("=" * 50)
    print("✅ Pipeline completed successfully!")
    print("💡 Commit and push changes to update GitHub repository")

if __name__ == "__main__":
    main()
