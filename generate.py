#!/usr/bin/env python3
"""
Complete PowerPlay System Analysis Generator
Runs the full pipeline: Download → Extract → Generate all MD reports
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              cwd=Path.cwd())
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return False
            
    except FileNotFoundError:
        print(f"❌ Script {script_name} not found!")
        return False
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False
    
    return True

def check_script_exists(script_name):
    """Check if a required script exists"""
    if not Path(script_name).exists():
        print(f"❌ Required script {script_name} not found!")
        return False
    return True

def main():
    """Main generation pipeline"""
    print("🚀 Elite Dangerous PowerPlay System Analysis Generator")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Required scripts
    scripts = [
        ("download.py", "Downloading system data from Inara"),
        ("extract.py", "Extracting and processing system data"), 
        ("create_stronghold_md.py", "Generating Stronghold status report"),
        ("create_exploited_md.py", "Generating Exploited status report"),
        ("create_fortified_md.py", "Generating Fortified status report")
    ]
    
    # Check if all required scripts exist
    print("\n🔍 Checking required scripts...")
    missing_scripts = []
    for script_name, _ in scripts:
        if not check_script_exists(script_name):
            missing_scripts.append(script_name)
    
    if missing_scripts:
        print(f"\n❌ Missing scripts: {', '.join(missing_scripts)}")
        print("Please ensure all required scripts are present before running generate.py")
        sys.exit(1)
    
    print("✅ All required scripts found")
    
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
    print("📊 PIPELINE SUMMARY")
    print(f"{'='*60}")
    
    if success_count == total_scripts:
        print("🎉 COMPLETE SUCCESS!")
        print(f"✅ All {total_scripts} steps completed successfully")
        
        # List generated files
        print("\n📂 Generated Reports:")
        reports = [
            ("stronghold_status.md", "🏛️ Stronghold Systems Report"),
            ("exploited_status.md", "🏭 Exploited Systems Report"), 
            ("fortified_status.md", "🛡️ Fortified Systems Report")
        ]
        
        for filename, description in reports:
            if Path(filename).exists():
                print(f"  ✅ {description}: {filename}")
            else:
                print(f"  ❌ {description}: {filename} (not found)")
        
        print("\n📁 JSON Data Files:")
        json_files = [
            ("json/stronghold_systems.json", "Stronghold Systems Data"),
            ("json/exploited_systems.json", "Exploited Systems Data"),
            ("json/fortified_systems.json", "Fortified Systems Data")
        ]
        
        for filepath, description in json_files:
            if Path(filepath).exists():
                print(f"  ✅ {description}: {filepath}")
            else:
                print(f"  ❌ {description}: {filepath} (not found)")
                
    else:
        print(f"💥 PARTIAL SUCCESS: {success_count}/{total_scripts} steps completed")
        print("Some steps failed - check error messages above")
    
    print(f"\n⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🔗 Next steps:")
    print("  - Review the generated markdown reports")
    print("  - Check the README.md for links to all reports")
    print("  - Use the JSON files for further analysis if needed")

if __name__ == "__main__":
    main()
