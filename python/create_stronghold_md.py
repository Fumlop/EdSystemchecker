#!/usr/bin/env python3
"""
Generate stronghold status markdown report from JSON data
"""
import json
from datetime import datetime
from pathlib import Path

def categorize_by_activity(systems, activity_field='undermining'):
    """Categorize systems by activity level"""
    high = []
    medium = []
    low = []
    
    for system in systems:
        activity = abs(system.get('net_cp', 0))
         
        if activity >= 10000:
            high.append(system)
        elif activity >= 5000:
            medium.append(system)
        elif activity >= 1000:
            low.append(system)
    
    return high, medium, low

def generate_stronghold_report():
    """Generate stronghold status report"""
    
    # Load stronghold data
    json_file = Path("json/stronghold_systems.json")
    if not json_file.exists():
        print("❌ stronghold_systems.json not found. Run extract.py first!")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    systems = data['systems']
    systems_with_net_cp = [s for s in systems if 'net_cp' in s]
    
    # Separate by Net CP (positive = reinforcement winning, negative = undermining winning)
    reinforcement_winning = [s for s in systems_with_net_cp if s['net_cp'] > 0]
    undermining_winning = [s for s in systems_with_net_cp if s['net_cp'] < 0]
    
    # Sort: Positive Net CP descending, Negative Net CP ascending (most negative first)
    reinforcement_winning.sort(key=lambda x: x['net_cp'], reverse=True)
    undermining_winning.sort(key=lambda x: x['net_cp'])
    
    # Categorize by activity levels
    reinf_high, reinf_medium, reinf_low = categorize_by_activity(reinforcement_winning)
    under_high, under_medium, under_low = categorize_by_activity(undermining_winning)
    
    # Generate report
    report = f"""# 🏛️ Stronghold Status Report

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Data Source:** {data.get('last_update', 'Unknown')}
**Total Strongholds:** {len(systems)} ({len(systems_with_net_cp)} with decay analysis)

## [INFO] Quick Summary

### Top 5 Most Threatened (Most Negative Net CP)
"""
    
    if undermining_winning:
        for i, system in enumerate(undermining_winning[:5], 1):
            report += f"{i}. **{system['system']}:** {system['net_cp']} CP (U:{system['undermining']:,}, R:{system['reinforcement']:,})\n"
    else:
        report += "*No systems currently losing CP*\n"
    
    report += f"\n### Top 5 Best Protected (Most Positive Net CP)\n"
    if reinforcement_winning:
        for i, system in enumerate(reinforcement_winning[:5], 1):
            report += f"{i}. **{system['system']}:** +{system['net_cp']} CP (U:{system['undermining']:,}, R:{system['reinforcement']:,})\n"
    else:
        report += "*No systems currently gaining CP*\n"

    report += f"""

---

## [BLUE] Active Reinforcement (Positive Net CP)
*Systems where reinforcement is winning against undermining*

### [HIGH] High Activity (≥10,000 CP Reinforcement)
"""
    
    if reinf_high:
        report += """
| Status | System | Reinforcement | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Current CP | Net CP | Activity |
|--------|--------|---------------|-------------|--------------|-----------------|-------------------|------------|--------|----------|
"""
        for system in reinf_high:
            status_icon = "[OK]" if system['progress_percent'] >= 20 else "[FIRE]"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0):.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['reinforcement']:,} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['current_progress_cp']:,} | +{system['net_cp']} | [HIGH] High Reinforcement |\n"
    else:
        report += "\n*No strongholds with high reinforcement activity*\n"
    
    report += f"\n### [MED] Medium Activity (5000-9999 CP Reinforcement)\n"
    
    if reinf_medium:
        report += """
| Status | System | Reinforcement | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Current CP | Net CP | Activity |
|--------|--------|---------------|-------------|--------------|-----------------|-------------------|------------|--------|----------|
"""
        for system in reinf_medium:
            status_icon = "[OK]" if system['progress_percent'] >= 20 else "[FIRE]"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0):.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['reinforcement']:,} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['current_progress_cp']:,} | +{system['net_cp']} | [MED] Medium Reinforcement |\n"
    else:
        report += "\n*No strongholds with medium reinforcement activity*\n"
    
    report += f"\n### [LOW] Low Activity (1000-4999 CP Reinforcement)\n"
    
    if reinf_low:
        report += """
| Status | System | Reinforcement | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Current CP | Net CP | Activity |
|--------|--------|---------------|-------------|--------------|-----------------|-------------------|------------|--------|----------|
"""
        for system in reinf_low:
            status_icon = "[OK]" if system['progress_percent'] >= 20 else "[FIRE]"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0):.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['reinforcement']:,} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['current_progress_cp']:,} | +{system['net_cp']} | [BLUE] Low Reinforcement |\n"
    else:
        report += "\n*No strongholds with low reinforcement activity*\n"

    report += """

---

## [WARN] Active Undermining (Negative Net CP)
*Systems where undermining is winning against reinforcement*

### [WARN] High Activity (≥10,000 CP Undermining)
"""
    
    if under_high:
        report += """
| Status | System | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Reinforcement | Current CP | Net CP | Activity |
|--------|--------|-------------|--------------|-----------------|-------------------|---------------|------------|--------|----------|
"""
        for system in under_high:
            status_icon = "[OK]" if system['progress_percent'] >= 20 else "[FIRE]"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0):.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['reinforcement']:,} | {system['current_progress_cp']:,} | {system['net_cp']} | [WARN] High Undermining |\n"
    else:
        report += "\n*No strongholds with high undermining activity*\n"
    
    report += f"\n### [ORANGE] Medium Activity (5000-9999 CP Undermining)\n"
    
    if under_medium:
        report += """
| Status | System | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Reinforcement | Current CP | Net CP | Activity |
|--------|--------|-------------|--------------|-----------------|-------------------|---------------|------------|--------|----------|
"""
        for system in under_medium:
            status_icon = "[OK]" if system['progress_percent'] >= 20 else "[FIRE]"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0):.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['reinforcement']:,} | {system['current_progress_cp']:,} | {system['net_cp']} | [ORANGE] Medium Undermining |\n"
    else:
        report += "\n*No strongholds with medium undermining activity*\n"
    
    report += f"\n### [MED] Low Activity (1000-4999 CP Undermining)\n"
    
    if under_low:
        report += """
| Status | System | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Reinforcement | Current CP | Net CP | Activity |
|--------|--------|-------------|--------------|-----------------|-------------------|---------------|------------|--------|----------|
"""
        for system in under_low:
            status_icon = "[OK]" if system['progress_percent'] >= 20 else "[FIRE]"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0):.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['reinforcement']:,} | {system['current_progress_cp']:,} | {system['net_cp']} | [MED] Low Undermining |\n"
    else:
        report += "\n*No strongholds with low undermining activity*\n"

    # Write report
    output_file = Path("stronghold_status.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[OK] Stronghold report generated: {output_file}")
    print(f"[INFO] {len(reinforcement_winning)} systems gaining CP, {len(undermining_winning)} systems losing CP")

if __name__ == "__main__":
    generate_stronghold_report()
