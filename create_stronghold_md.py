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

---

## 🔵 Active Reinforcement (Positive Net CP)
*Systems where reinforcement is winning against undermining*

### 🔵 High Activity (≥1,000 CP Reinforcement)
"""
    
    if reinf_high:
        report += """
| Status | System | Reinforcement | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Current CP | Net CP | Activity |
|--------|--------|---------------|-------------|--------------|-----------------|-------------------|------------|--------|----------|
"""
        for system in reinf_high:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0) * 100:.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['reinforcement']:,} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['current_progress_cp']:,} | +{system['net_cp']} | 🔵 High Reinforcement |\n"
    else:
        report += "\n*No strongholds with high reinforcement activity*\n"
    
    report += f"\n### 🔵 Medium Activity (500-999 CP Reinforcement)\n"
    
    if reinf_medium:
        report += """
| Status | System | Reinforcement | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Current CP | Net CP | Activity |
|--------|--------|---------------|-------------|--------------|-----------------|-------------------|------------|--------|----------|
"""
        for system in reinf_medium:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0) * 100:.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['reinforcement']:,} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['current_progress_cp']:,} | +{system['net_cp']} | 🔵 Medium Reinforcement |\n"
    else:
        report += "\n*No strongholds with medium reinforcement activity*\n"
    
    report += f"\n### 🔵 Low Activity (100-499 CP Reinforcement)\n"
    
    if reinf_low:
        report += """
| Status | System | Reinforcement | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Current CP | Net CP | Activity |
|--------|--------|---------------|-------------|--------------|-----------------|-------------------|------------|--------|----------|
"""
        for system in reinf_low:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0) * 100:.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['reinforcement']:,} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['current_progress_cp']:,} | +{system['net_cp']} | 🔵 Low Reinforcement |\n"
    else:
        report += "\n*No strongholds with low reinforcement activity*\n"

    report += """

---

## ⚠️ Active Undermining (Negative Net CP)
*Systems where undermining is winning against reinforcement*

### ⚠️ High Activity (≥1,000 CP Undermining)
"""
    
    if under_high:
        report += """
| Status | System | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Reinforcement | Current CP | Net CP | Activity |
|--------|--------|-------------|--------------|-----------------|-------------------|---------------|------------|--------|----------|
"""
        for system in under_high:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0) * 100:.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['reinforcement']:,} | {system['current_progress_cp']:,} | {system['net_cp']} | ⚠️ High Undermining |\n"
    else:
        report += "\n*No strongholds with high undermining activity*\n"
    
    report += f"\n### 🔶 Medium Activity (500-999 CP Undermining)\n"
    
    if under_medium:
        report += """
| Status | System | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Reinforcement | Current CP | Net CP | Activity |
|--------|--------|-------------|--------------|-----------------|-------------------|---------------|------------|--------|----------|
"""
        for system in under_medium:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0) * 100:.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['reinforcement']:,} | {system['current_progress_cp']:,} | {system['net_cp']} | 🔶 Medium Undermining |\n"
    else:
        report += "\n*No strongholds with medium undermining activity*\n"
    
    report += f"\n### 🟡 Low Activity (100-499 CP Undermining)\n"
    
    if under_low:
        report += """
| Status | System | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Reinforcement | Current CP | Net CP | Activity |
|--------|--------|-------------|--------------|-----------------|-------------------|---------------|------------|--------|----------|
"""
        for system in under_low:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0) * 100:.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['reinforcement']:,} | {system['current_progress_cp']:,} | {system['net_cp']} | 🟡 Low Undermining |\n"
    else:
        report += "\n*No strongholds with low undermining activity*\n"

    # Quick summary
    report += f"""

---

## 📊 Quick Summary

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

    # Write report
    output_file = Path("stronghold_status.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Stronghold report generated: {output_file}")
    print(f"📊 {len(reinforcement_winning)} systems gaining CP, {len(undermining_winning)} systems losing CP")

if __name__ == "__main__":
    generate_stronghold_report()
