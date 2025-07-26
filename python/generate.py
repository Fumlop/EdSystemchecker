#!/usr/bin/env python3
"""
Complete PowerPlay System Analysis Generator
Runs the full pipeline: Download → Extract → Generate all MD reports
"""
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              cwd=Path.cwd(),
                              encoding='utf-8',
                              errors='replace')
        
        if result.returncode == 0:
            print(f"SUCCESS: {description} completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"ERROR: {description} failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error details: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return False
            
    except FileNotFoundError:
        print(f"ERROR: Script {script_name} not found!")
        return False
    except Exception as e:
        print(f"ERROR: Exception running {script_name}: {e}")
        return False
    
    return True

def check_script_exists(script_name):
    """Check if a required script exists"""
    if not Path(script_name).exists():
        print(f"Required script {script_name} not found!")
        return False
    return True

def main():
    """Main generation pipeline"""
    print("Elite Dangerous PowerPlay System Analysis Generator")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Change to parent directory (main project folder)
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"Working directory: {project_root}")
    
    # Check if HTML files already exist
    html_dir = Path("html")
    html_files_exist = html_dir.exists() and list(html_dir.glob("*.html"))
    
    # Required scripts - make download optional if HTML files exist
    scripts = []
    
    if not html_files_exist:
        scripts.append(("python/download.py", "Downloading system data from Inara"))
        print("HTML files not found - will download fresh data")
    else:
        print(f"Found existing HTML files in {html_dir} - skipping download")
    
    scripts.extend([
        ("python/extract.py", "Extracting and processing system data"), 
        ("python/create_stronghold_md.py", "Generating Stronghold status report"),
        ("python/create_exploited_md.py", "Generating Exploited status report"),
        ("python/create_fortified_md.py", "Generating Fortified status report"),
        ("python/create_contested_md.py", "Generating Contested systems report"),
        ("python/genreadme.py", "Generating README from template")
    ])
    
    # Check if all required scripts exist
    print("\nChecking required scripts...")
    missing_scripts = []
    for script_name, _ in scripts:
        if not check_script_exists(script_name):
            missing_scripts.append(script_name)
    
    if missing_scripts:
        print(f"\nMissing scripts: {', '.join(missing_scripts)}")
        print("Please ensure all required scripts are present before running generate.py")
        sys.exit(1)
    
    print("All required scripts found")
    
    # Run the complete pipeline
    success_count = 0
    total_scripts = len(scripts)
    
    for script_name, description in scripts:
        if run_script(script_name, description):
            success_count += 1
        else:
            print(f"\n💥 Pipeline stopped due to error in {script_name}")
            break
    
    # Final summary
    print(f"\n{'='*60}")
    print("PIPELINE SUMMARY")
    print(f"{'='*60}")
    
    if success_count == total_scripts:
        print("COMPLETE SUCCESS!")
        print(f"All {total_scripts} steps completed successfully")
        
        # List generated files
        print("\nGenerated Reports:")
        reports = [
            ("stronghold_status.md", "Stronghold Systems Report"),
            ("exploited_status.md", "Exploited Systems Report"), 
            ("fortified_status.md", "Fortified Systems Report")
        ]
        
        for filename, description in reports:
            if Path(filename).exists():
                print(f"  SUCCESS: {description}: {filename}")
            else:
                print(f"  ERROR: {description}: {filename} (not found)")
        
        print("\nJSON Data Files:")
        json_files = [
            ("json/stronghold_systems.json", "Stronghold Systems Data"),
            ("json/exploited_systems.json", "Exploited Systems Data"),
            ("json/fortified_systems.json", "Fortified Systems Data")
        ]
        
        for filepath, description in json_files:
            if Path(filepath).exists():
                print(f"  SUCCESS: {description}: {filepath}")
            else:
                print(f"  ERROR: {description}: {filepath} (not found)")
                
    else:
        print(f"PARTIAL SUCCESS: {success_count}/{total_scripts} steps completed")
        print("Some steps failed - check error messages above")
    
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nNext steps:")
    print("  - Review the generated markdown reports")
    print("  - Check the README.md for links to all reports")
    print("  - Use the JSON files for further analysis if needed")

if __name__ == "__main__":
    main()
