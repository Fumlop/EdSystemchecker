#!/usr/bin/env python3
"""
Generate contested status report from contested systems JSON data
"""
import json
from datetime import datetime
from pathlib import Path

def load_accquise_systems():
    """Load priority acquisition systems from accquise.conf"""
    config_path = Path("accquise.conf")
    if not config_path.exists():
        print("WARNING: accquise.conf not found!")
        return []
    
    systems = []
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                systems.append(line)
    
    print(f"Loaded {len(systems)} priority acquisition systems from accquise.conf")
    return systems

def load_contested_systems():
    """Load contested systems from JSON file"""
    json_path = Path("json/contested_systems.json")
    if not json_path.exists():
        print("ERROR: contested_systems.json not found. Run extract.py first!")
        return []
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_opposing_powers(opposing_powers):
    """Format opposing powers list for display"""
    if not opposing_powers:
        return "None"
    
    power_strings = []
    for power in opposing_powers:
        name = power.get('name', 'Unknown')
        percent = power.get('progress_percent', 0.0)
        power_strings.append(f"{name} ({percent:.1f}%)")
    
    return ", ".join(power_strings)

def get_progress_icon(winters_progress, total_opposition):
    """Get progress icon based on Winters progress and opposition levels"""
    if total_opposition > 100:
        return "🔥"  # Brennender Ofen wenn Opposition > 100%
    elif winters_progress > 100:
        return "�"  # Stern wenn Winters Progress > 100%
    else:
        return "⚔"  # Schwert wenn noch keiner 100% hat

def format_progress_vs_opposition(winters_progress, total_opposition):
    """Format progress vs opposition with color coding"""
    winters_formatted = f"**{winters_progress:.1f}%**" if winters_progress > total_opposition else f"{winters_progress:.1f}%"
    opposition_formatted = f"**{total_opposition:.1f}%**" if total_opposition > winters_progress else f"{total_opposition:.1f}%"
    
    # Color coding
    if winters_progress > total_opposition:
        winters_formatted = f"🟢 {winters_formatted}"
    else:
        opposition_formatted = f"🔴 {opposition_formatted}"
    
    return winters_formatted, opposition_formatted

def get_status_emoji(contested, progress_percent):
    """Get status emoji based on contested status and progress"""
    if not contested:
        return "🔵"  # Expansion
    
    if progress_percent >= 80:
        return "🟢"  # High progress
    elif progress_percent >= 50:
        return "🟡"  # Medium progress
    elif progress_percent >= 25:
        return "🟠"  # Low-medium progress
    else:
        return "🔴"  # Low progress

def generate_contested_report():
    """Generate contested systems status report"""
    systems = load_contested_systems()
    accquise_systems = load_accquise_systems()
    
    if not systems:
        print("No contested systems data found!")
        return
    
    # Create a dict for faster lookup
    system_dict = {s['system']: s for s in systems}
    
    # Find priority acquisition systems that are contested
    accquise_contested = []
    for system_name in accquise_systems:
        if system_name in system_dict:
            accquise_contested.append(system_dict[system_name])
    
    # Separate contested and expansion systems
    contested_systems = [s for s in systems if s.get('contested', False)]
    expansion_systems = [s for s in systems if not s.get('contested', False)]
    
    # Sort contested systems by progress (highest first)
    contested_systems.sort(key=lambda x: x.get('progress_percent', 0), reverse=True)
    expansion_systems.sort(key=lambda x: x.get('progress_percent', 0), reverse=True)
    
    # Get high progress systems (>=70% instead of 80%)
    high_progress_contested = [s for s in contested_systems if s.get('progress_percent', 0) >= 70]
    high_progress_expansion = [s for s in expansion_systems if s.get('progress_percent', 0) >= 70]
    
    # Get systems where opposition > progress (difficult situations)
    def calculate_total_opposition(system):
        """Calculate total opposition percentage"""
        opposing_powers = system.get('opposing_powers', [])
        return sum(power.get('progress_percent', 0) for power in opposing_powers)
    
    difficult_contested = []
    for system in contested_systems:
        total_opposition = calculate_total_opposition(system)
        progress = system.get('progress_percent', 0)
        if total_opposition > progress:
            system['total_opposition'] = total_opposition
            difficult_contested.append(system)
    
    # Sort difficult systems by opposition strength (highest first)  
    difficult_contested.sort(key=lambda x: x.get('total_opposition', 0), reverse=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    extraction_time = systems[0].get('extracted_at', 'Unknown') if systems else 'Unknown'
    
    # Start building the report
    report = []
    report.append("# 🏛️ Contested Systems Status Report")
    report.append("")
    report.append(f"**Report Generated:** {timestamp}")
    report.append(f"**Data Source:** {extraction_time}")
    report.append(f"**Total Contested:** {len(contested_systems)} systems")
    report.append(f"**Total Expansion:** {len(expansion_systems)} systems")
    if accquise_systems:
        report.append(f"**Priority Acquisition Targets:** {len(accquise_contested)} of {len(accquise_systems)} systems are contested")
    report.append("")
    report.append(f"**Total Expansion:** {len(expansion_systems)} systems")
    report.append("")
    
    # Quick summary
    report.append("## 📊 Quick Summary")
    report.append("")
    
    # Top 5 High Progress Contested Systems Table (>=70%)
    if high_progress_contested:
        report.append("### 🟢 Top 5 High Progress Contested Systems (>=70%)")
        report.append("")
        report.append("| Status | System | Winters Progress | Opposition |")
        report.append("|--------|--------|------------------|------------|")
        
        top_5_high_contested = high_progress_contested[:5]
        for system in top_5_high_contested:
            progress = system.get('progress_percent', 0)
            total_opposition = calculate_total_opposition(system)
            
            status_icon = get_progress_icon(progress, total_opposition)
            winters_formatted, opposition_formatted = format_progress_vs_opposition(progress, total_opposition)
            
            report.append(f"| {status_icon} | {system['system']} | {winters_formatted} | {opposition_formatted} |")
        
        report.append("")
    
    # Top 5 Difficult Contested Systems Table (Opposition > Progress)
    if difficult_contested:
        report.append("### 🔴 Top 5 Difficult Contested Systems (Opposition > Progress)")
        report.append("")
        report.append("| Status | System | Winters Progress | Opposition |")
        report.append("|--------|--------|------------------|------------|")
        
        top_5_difficult = difficult_contested[:5]
        for system in top_5_difficult:
            progress = system.get('progress_percent', 0)
            total_opposition = system.get('total_opposition', 0)
            
            status_icon = get_progress_icon(progress, total_opposition)
            winters_formatted, opposition_formatted = format_progress_vs_opposition(progress, total_opposition)
            
            report.append(f"| {status_icon} | {system['system']} | {winters_formatted} | {opposition_formatted} |")
        
        report.append("")
    
    # FAT Target Systems Table
    if accquise_contested:
        report.append("### 🎯 FAT Target")
        report.append("")
        report.append("| Status | System | Winters Progress | Opposition |")
        report.append("|--------|--------|------------------|------------|")
        
        for system in accquise_contested:
            progress = system.get('progress_percent', 0)
            total_opposition = calculate_total_opposition(system)
            
            status_icon = get_progress_icon(progress, total_opposition)
            winters_formatted, opposition_formatted = format_progress_vs_opposition(progress, total_opposition)
            
            report.append(f"| {status_icon} | {system['system']} | {winters_formatted} | {opposition_formatted} |")
        
        report.append("")
    
    # Top 5 Expansion Systems Table (>=70% Progress)
    if high_progress_expansion:
        report.append("### 🔵 Top 5 Expansion Systems (>=70% Progress)")
        report.append("")
        report.append("| Status | System | Winters Progress |")
        report.append("|--------|--------|------------------|")
        
        top_5_expansion = high_progress_expansion[:5]
        for system in top_5_expansion:
            progress = system.get('progress_percent', 0)
            
            status_icon = get_progress_icon(progress, 0)  # No opposition for expansion
            winters_formatted = f"🟢 **{progress:.1f}%**"  # Always green/bold for expansion
            
            report.append(f"| {status_icon} | {system['system']} | {winters_formatted} |")
        
        report.append("")
    
    report.append("---")
    report.append("")
    
    # High Progress Contested Systems Table
    if high_progress_contested:
        report.append("## 🟢 High Progress Contested Systems (>=70%)")
        report.append("*Systems where Felicia Winters has strong progress but faces opposition*")
        report.append("")
        report.append("| Status | System | Progress % | Opposing Powers | State |")
        report.append("|--------|--------|------------|----------------|-------|")
        
        for system in high_progress_contested:
            status = get_status_emoji(system.get('contested', False), system.get('progress_percent', 0))
            opposing = format_opposing_powers(system.get('opposing_powers', []))
            state = system.get('state', 'Unknown')
            progress = system.get('progress_percent', 0)
            
            report.append(f"| {status} | {system['system']} | {progress:.1f}% | {opposing} | {state} |")
        
        report.append("")
        report.append("---")
        report.append("")
    
    # FAT Target Systems Table
    if accquise_contested:
        report.append("## 🎯 FAT Target")
        report.append("*High priority systems from accquise.conf that are currently contested*")
        report.append("")
        report.append("| Status | System | Progress % | Total Opposition % | Opposing Powers | State |")
        report.append("|--------|--------|------------|-------------------|----------------|-------|")
        
        for system in accquise_contested:
            status = get_status_emoji(system.get('contested', False), system.get('progress_percent', 0))
            opposing = format_opposing_powers(system.get('opposing_powers', []))
            state = system.get('state', 'Unknown')
            progress = system.get('progress_percent', 0)
            total_opposition = calculate_total_opposition(system)
            
            report.append(f"| {status} | {system['system']} | {progress:.1f}% | {total_opposition:.1f}% | {opposing} | {state} |")
        
        report.append("")
        report.append("---")
        report.append("")
    
    # Difficult Contested Systems Table
    if difficult_contested:
        report.append("## 🔴 Difficult Contested Systems (Opposition > Progress)")
        report.append("*Systems where opposition is stronger than our progress*")
        report.append("")
        report.append("| Status | System | Our Progress % | Total Opposition % | Opposing Powers | State |")
        report.append("|--------|--------|----------------|-------------------|----------------|-------|")
        
        for system in difficult_contested:
            status = get_status_emoji(system.get('contested', False), system.get('progress_percent', 0))
            opposing = format_opposing_powers(system.get('opposing_powers', []))
            state = system.get('state', 'Unknown')
            progress = system.get('progress_percent', 0)
            total_opposition = system.get('total_opposition', 0)
            
            report.append(f"| {status} | {system['system']} | {progress:.1f}% | {total_opposition:.1f}% | {opposing} | {state} |")
        
        report.append("")
        report.append("---")
        report.append("")
    
    # All Contested Systems Table
    report.append("## ⚔ All Contested Systems")
    report.append("*Systems under contest by opposing powers*")
    report.append("")
    report.append("| Status | System | Progress % | Opposing Powers |")
    report.append("|--------|--------|------------|----------------|")
    
    for system in contested_systems:
        status = get_status_emoji(system.get('contested', False), system.get('progress_percent', 0))
        opposing = format_opposing_powers(system.get('opposing_powers', []))
        progress = system.get('progress_percent', 0)
        
        report.append(f"| {status} | {system['system']} | {progress:.1f}% | {opposing} |")
    
    report.append("")
    report.append("---")
    report.append("")
    
    # All Expansion Systems Table
    report.append("## 🔵 All Expansion Systems")
    report.append("*Systems being expanded by Felicia Winters without opposition*")
    report.append("")
    report.append("| Status | System | Progress % |")
    report.append("|--------|--------|------------|")
    
    for system in expansion_systems:
        status = get_status_emoji(system.get('contested', False), system.get('progress_percent', 0))
        progress = system.get('progress_percent', 0)
        
        report.append(f"| {status} | {system['system']} | {progress:.1f}% |")
    
    # Write report to file
    output_path = Path("contested_status.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"[OK] Contested status report generated: {output_path}")
    print(f"[INFO] {len(contested_systems)} contested systems, {len(expansion_systems)} expansion systems")
    if high_progress_contested:
        print(f"[HIGH] {len(high_progress_contested)} high progress contested systems (>=70%)")
    if difficult_contested:
        print(f"[LOW] {len(difficult_contested)} difficult contested systems (opposition > progress)")
    if high_progress_expansion:
        print(f"[BLUE] {len(high_progress_expansion)} high progress expansion systems (>=70%)")

if __name__ == "__main__":
    generate_contested_report()
