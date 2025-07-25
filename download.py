#!/usr/bin/env python3
"""
Download HTML files from Inara power pages
"""
import os
import requests
from pathlib import Path
from datetime import datetime

def download_html(url: str, filename: str, output_dir: str = "html") -> bool:
    """
    Download HTML content from URL and save to file
    
    Args:
        url: URL to download from
        filename: Name of the output file
        output_dir: Directory to save files (default: "html")
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(exist_ok=True)
        
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        print(f"Downloading: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Save to file
        output_path = Path(output_dir) / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✓ Saved: {output_path} ({len(response.text):,} chars)")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error downloading {url}: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def main():
    """Main function to download both Inara pages"""
    # URLs to download
    urls = [
        {
            'url': 'https://inara.cz/elite/power-controlled/5/',
            'filename': 'power-controlled-5.html'
        },
        {
            'url': 'https://inara.cz/elite/power-exploited/5/',
            'filename': 'power-exploited-5.html'
        }
    ]
    
    print(f"Starting download at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    success_count = 0
    for item in urls:
        if download_html(item['url'], item['filename']):
            success_count += 1
    
    print("-" * 50)
    print(f"Download complete: {success_count}/{len(urls)} files successful")
    
    if success_count == len(urls):
        print("✓ All downloads completed successfully!")
    else:
        print("⚠ Some downloads failed!")

if __name__ == "__main__":
    main()
