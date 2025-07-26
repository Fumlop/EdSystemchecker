#!/usr/bin/env python3
"""
Generate priority acquisition report from accquise.conf and system data
"""
import json
from datetime import datetime
from pathlib import Path

def load_accquise_systems():
    """Load priority acquisition systems from accquise.conf"""
    config_path = Path("../accquise.conf")
    if not config_path.exists():
        # Try in current directory
        config_path = Path("accquise.conf")
        if not config_path.exists():
            print("ERROR: accquise.conf not found!")
            return []
    
    systems = []
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                systems.append(line)
    
    print(f"Loaded {len(systems)} priority acquisition systems from {config_path}")
    return systems

def load_system_data():
    """Load system data from JSON files"""
    data = {}
    
    # Load different system types
    json_files = [
        ("json/stronghold_systems.json", "stronghold"),
        ("json/exploited_systems.json", "exploited"), 
        ("json/fortified_systems.json", "fortified"),
        ("json/contested_systems.json", "contested")
    ]
    
    for json_path, system_type in json_files:
        file_path = Path(json_path)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                
                # Handle different JSON structures
                if system_type == "contested":
                    # contested_systems.json is a direct array
                    systems = json_data if isinstance(json_data, list) else []
                else:
                    # Other files have a 'systems' key
                    systems = json_data.get('systems', [])
                
                for system in systems:
                    system_name = system.get('system', '')
                    if system_name:
                        data[system_name] = {
                            'type': system_type,
                            'data': system
                        }
    
    return data

def get_status_emoji(system_type, progress_percent=0):
    """Get status emoji based on system type and progress"""
    if system_type == "stronghold":
        return "🏰"
    elif system_type == "exploited":
        return "⚡"
    elif system_type == "fortified":
        return "🛡️"
    elif system_type == "contested":
        if progress_percent >= 80:
            return "🟢"
        elif progress_percent >= 50:
            return "🟡"
        elif progress_percent >= 25:
            return "🟠"
        else:
            return "🔴"
    else:
        return "❓"  # Unknown system

def generate_accquise_report():
    """Generate priority acquisition status report"""
    accquise_systems = load_accquise_systems()
    if not accquise_systems:
        return
    
    system_data = load_system_data()
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Start building the report
    report = []
    report.append("# 🎯 Priority Acquisition Report")
    report.append("")
    report.append(f"**Report Generated:** {timestamp}")
    report.append(f"**Total Priority Systems:** {len(accquise_systems)}")
    report.append("")
    
    # Analyze systems
    found_systems = []
    not_found_systems = []
    
    for system_name in accquise_systems:
        if system_name in system_data:
            found_systems.append((system_name, system_data[system_name]))
        else:
            not_found_systems.append(system_name)
    
    # Quick summary
    report.append("## 📊 Quick Summary")
    report.append("")
    report.append(f"- **Systems in PowerPlay:** {len(found_systems)}")
    report.append(f"- **Systems not found:** {len(not_found_systems)}")
    report.append("")
    
    # Group by type
    by_type = {}
    for system_name, system_info in found_systems:
        system_type = system_info['type']
        if system_type not in by_type:
            by_type[system_type] = []
        by_type[system_type].append((system_name, system_info))
    
    for system_type, count in [(t, len(by_type.get(t, []))) for t in ['stronghold', 'exploited', 'fortified', 'contested']]:
        if count > 0:
            emoji = get_status_emoji(system_type)
            report.append(f"- **{emoji} {system_type.title()}:** {count}")
    
    report.append("")
    report.append("---")
    report.append("")
    
    # Detailed status table
    if found_systems:
        report.append("## 🎯 Priority Systems Status")
        report.append("")
        report.append("| Status | System | Type | Progress % | Additional Info |")
        report.append("|--------|--------|------|------------|----------------|")
        
        for system_name, system_info in found_systems:
            system_type = system_info['type']
            system_data_obj = system_info['data']
            
            status = get_status_emoji(system_type, system_data_obj.get('progress_percent', 0))
            progress = system_data_obj.get('progress_percent', 0)
            
            # Additional info based on type
            additional_info = ""
            if system_type == "contested":
                opposing_powers = system_data_obj.get('opposing_powers', [])
                if opposing_powers:
                    power_strings = []
                    for power in opposing_powers[:2]:  # Show max 2 opposing powers
                        power_strings.append(f"{power.get('name', 'Unknown')} ({power.get('progress_percent', 0)}%)")
                    additional_info = f"vs {', '.join(power_strings)}"
                    if len(opposing_powers) > 2:
                        additional_info += f" (+{len(opposing_powers)-2} more)"
            elif system_type == "fortified":
                triggers = system_data_obj.get('triggers', 0)
                if triggers:
                    additional_info = f"{triggers} triggers"
            elif system_type == "exploited":
                income = system_data_obj.get('income', 0)
                if income:
                    additional_info = f"{income} CC income"
            
            report.append(f"| {status} | {system_name} | {system_type.title()} | {progress}% | {additional_info} |")
        
        report.append("")
        report.append("---")
        report.append("")
    
    # Systems not found
    if not_found_systems:
        report.append("## ❓ Systems Not Found in PowerPlay")
        report.append("*These systems are not currently in any PowerPlay category*")
        report.append("")
        
        for system_name in not_found_systems:
            report.append(f"- {system_name}")
        
        report.append("")
    
    # Write report to file
    output_path = Path("accquise_status.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Priority acquisition report generated: {output_path}")
    print(f"🎯 {len(found_systems)} systems found, {len(not_found_systems)} not found")

if __name__ == "__main__":
    generate_accquise_report()
