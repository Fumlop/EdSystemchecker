#!/usr/bin/env python3
"""
Complete PowerPlay System Analysis Generator
Runs the full pipeline: Download → Extract → Generate all MD reports
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_script(script_command, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")
    
    try:
        # Split command into parts for subprocess
        if isinstance(script_command, str):
            command_parts = script_command.split()
        else:
            command_parts = [script_command]
        
        # Prepend python executable
        full_command = [sys.executable] + command_parts
        
        result = subprocess.run(full_command, 
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
        print(f"ERROR: Script {script_command} not found!")
        return False
    except Exception as e:
        print(f"ERROR: Exception running {script_command}: {e}")
        return False
    
    return True

def check_script_exists(script_command):
    """Check if a required script exists"""
    # Extract just the script name from command with arguments
    if isinstance(script_command, str):
        script_name = script_command.split()[0]
    else:
        script_name = script_command
        
    if not Path(script_name).exists():
        print(f"Required script {script_name} not found!")
        return False
    return True

def main():
    """Main generation pipeline"""
    print("Elite Dangerous PowerPlay System Analysis Generator")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if HTML files already exist
    html_dir = Path("html")
    html_files_exist = html_dir.exists() and list(html_dir.glob("*.html"))
    
    # Required scripts - make download optional if HTML files exist
    scripts = []
    
    if not html_files_exist:
        scripts.append(("download.py", "Downloading system data from Inara"))
        print("HTML files not found - will download fresh data")
    else:
        print(f"Found existing HTML files in {html_dir} - skipping download")
    
    scripts.extend([
        ("extract.py", "Extracting and processing system data"), 
        ("python/create_universal_md.py stronghold", "Generating Stronghold status report"),
        ("python/create_universal_md.py exploited", "Generating Exploited status report"),
        ("python/create_universal_md.py fortified", "Generating Fortified status report"),
        ("python/transition_tracker.py stronghold", "Adding transition tracking to Stronghold report"),
        ("python/transition_tracker.py exploited", "Adding transition tracking to Exploited report"),
        ("python/transition_tracker.py fortified", "Adding transition tracking to Fortified report")
    ])
    
    # Check if all required scripts exist
    print("\nChecking required scripts...")
    missing_scripts = []
    for script_command, _ in scripts:
        if not check_script_exists(script_command):
            missing_scripts.append(script_command.split()[0] if isinstance(script_command, str) else script_command)
    
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
            ("stronghold_status.md", "Stronghold Systems Report (with transition tracking)"),
            ("exploited_status.md", "Exploited Systems Report (with transition tracking)"), 
            ("fortified_status.md", "Fortified Systems Report (with transition tracking)")
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
