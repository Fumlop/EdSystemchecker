#!/usr/bin/env python3
"""
Generate README.md from README.tpl template
Replaces $norefresh$ with a table of systems without current Inara data
"""
import json
from datetime import datetime
from pathlib import Path

def load_all_systems():
    """Load all systems from JSON files"""
    all_systems = []
    json_dir = Path("json")
    
    # Load systems from all JSON files
    for json_file in ["stronghold_systems.json", "exploited_systems.json", "fortified_systems.json"]:
        file_path = json_dir / json_file
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    systems = data.get('systems', [])
                    all_systems.extend(systems)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
    
    return all_systems

def get_systems_without_current_data(systems):
    """Get systems that don't have current cycle refresh"""
    no_refresh_systems = []
    
    for system in systems:
        # Check if system has current_cycle_refresh field and it's False
        if not system.get('current_cycle_refresh', True):
            no_refresh_systems.append(system)
    
    # Sort by extracted_at timestamp (oldest first)
    no_refresh_systems.sort(key=lambda x: x.get('extracted_at', ''))
    
    return no_refresh_systems

def format_refresh_table(systems):
    """Format systems without current data as markdown table"""
    if not systems:
        return "*All systems up to date!*"
    
    table = """| System | State | Last Update | Progress % | Undermining | Reinforcement |
|--------|-------|-------------|------------|-------------|---------------|
"""
    
    for system in systems:
        # Format the extracted_at timestamp
        try:
            extracted_at = system.get('extracted_at', '')
            if extracted_at:
                dt = datetime.fromisoformat(extracted_at.replace('Z', '+00:00'))
                formatted_date = dt.strftime('%Y-%m-%d %H:%M')
            else:
                formatted_date = 'Unknown'
        except:
            formatted_date = 'Invalid'
        
        system_name = system.get('system', 'Unknown')
        state = system.get('state', 'Unknown')
        progress = f"{system.get('progress_percent', 0)}%"
        undermining = f"{system.get('undermining', 0):,}"
        reinforcement = f"{system.get('reinforcement', 0):,}"
        
        table += f"| {system_name} | {state} | {formatted_date} | {progress} | {undermining} | {reinforcement} |\n"
    
    return table

def generate_readme():
    """Generate README.md from template"""
    template_path = Path("README.tpl")
    output_path = Path("README.md")
    
    if not template_path.exists():
        print("ERROR: README.tpl template not found!")
        return False
    
    # Load template content
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except Exception as e:
        print(f"Error reading template: {e}")
        return False
    
    # Load all systems and find those without current data
    all_systems = load_all_systems()
    no_refresh_systems = get_systems_without_current_data(all_systems)
    
    # Format the table
    refresh_table = format_refresh_table(no_refresh_systems)
    
    # Replace placeholder
    final_content = template_content.replace('_norefresh_', refresh_table)
    
    # Write final README.md
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"SUCCESS: README.md generated with {len(no_refresh_systems)} systems without current data")
        return True
        
    except Exception as e:
        print(f"Error writing README.md: {e}")
        return False

def main():
    """Main function"""
    print("Elite Dangerous PowerPlay README Generator")
    print("=" * 50)
    
    if generate_readme():
        print("README.md generation completed successfully!")
    else:
        print("README.md generation failed!")

if __name__ == "__main__":
    main()
