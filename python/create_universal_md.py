#!/usr/bin/env python3
"""
Universal system status markdown report generator
Supports: stronghold, fortified, exploited states
"""
import json
import sys
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

def get_state_config(state):
    """Get configuration for each state type"""
    configs = {
        'stronghold': {
            'title': '🏛️ Stronghold Status Report',
            'emoji': '🏛️',
            'json_file': 'json/stronghold_systems.json',
            'output_file': 'stronghold_status.md'
        },
        'fortified': {
            'title': '🛡️ Fortified Status Report',
            'emoji': '🛡️',
            'json_file': 'json/fortified_systems.json',
            'output_file': 'fortified_status.md'
        },
        'exploited': {
            'title': '🌟 Exploited Status Report',
            'emoji': '🌟',
            'json_file': 'json/exploited_systems.json',
            'output_file': 'exploited_status.md'
        }
    }
    return configs.get(state)

def generate_universal_report(state):
    """Generate status report for specified state"""
    
    config = get_state_config(state)
    if not config:
        print(f"[ERROR] Invalid state: {state}. Use: stronghold, fortified, or exploited")
        return
    
    # Load data
    json_file = Path(config['json_file'])
    if not json_file.exists():
        print(f"[ERROR] {config['json_file']} not found. Run extract.py first!")
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
    report = f"""# {config['title']}

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Data Source:** {data.get('last_update', 'Unknown')}
**Total {state.title()}:** {len(systems)} ({len(systems_with_net_cp)} with decay analysis)

## 📊 Quick Summary

### 🟢 **Best Protected Systems**
*Top systems with positive Net CP (reinforcement winning)*

| Status | System | Net CP | Undermining | Reinforcement | Progress |
|--------|--------|--------|-------------|---------------|----------|"""
    
    if reinforcement_winning:
        for system in reinforcement_winning[:5]:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            report += f"\n| {status_icon} | **{system['system']}** | +{system['net_cp']:,} CP | {system['undermining']:,} | {system['reinforcement']:,} | {system['progress_percent']}% |"
    else:
        report += "\n| - | *No systems currently gaining CP* | - | - | - | - |"
    
    report += f"""

### 🔴 **Most Threatened Systems**
*Top systems with negative Net CP (undermining winning)*

| Status | System | Net CP | Undermining | Reinforcement | Progress |
|--------|--------|--------|-------------|---------------|----------|"""
    
    if undermining_winning:
        for system in undermining_winning[:5]:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            report += f"\n| {status_icon} | **{system['system']}** | {system['net_cp']:,} CP | {system['undermining']:,} | {system['reinforcement']:,} | {system['progress_percent']}% |"
    else:
        report += "\n| - | *No systems currently losing CP* | - | - | - | - |"

    # High Activity Summary
    high_activity_systems = []
    if reinf_high:
        high_activity_systems.extend([(s, "Reinforcement", s['reinforcement']) for s in reinf_high])
    if under_high:
        high_activity_systems.extend([(s, "Undermining", s['undermining']) for s in under_high])
    
    high_activity_systems.sort(key=lambda x: abs(x[0]['net_cp']), reverse=True)

    report += f"""

### ⚡ **High Activity Systems**
*Systems with ≥10,000 CP activity (reinforcement or undermining)*

| Status | System | Net CP | Activity Type | CP Amount | Progress |
|--------|--------|--------|---------------|-----------|----------|"""
    
    if high_activity_systems:
        for system, activity_type, cp_amount in high_activity_systems[:5]:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            net_cp_display = f"+{system['net_cp']:,}" if system['net_cp'] > 0 else f"{system['net_cp']:,}"
            activity_icon = "🛡️" if activity_type == "Reinforcement" else "⚠️"
            report += f"\n| {status_icon} | **{system['system']}** | {net_cp_display} CP | {activity_icon} {activity_type} | {cp_amount:,} | {system['progress_percent']}% |"
    else:
        report += "\n| - | *No high activity systems found* | - | - | - | - |"

    report += f"""

---

## 🛡️ Active Reinforcement (Positive Net CP)
*Systems where reinforcement is winning against undermining*

### 🟢 High Activity (≥10,000 CP Reinforcement)
"""
    
    if reinf_high:
        report += """
| Status | System | Reinforcement | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Current CP | Net CP | Activity |
|--------|--------|---------------|-------------|--------------|-----------------|-------------------|------------|--------|----------|
"""
        for system in reinf_high:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0):.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['reinforcement']:,} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['current_progress_cp']:,} | +{system['net_cp']:,} | 🟢 High Reinforcement |\n"
    else:
        report += f"\n*No {state} systems with high reinforcement activity*\n"
    
    report += f"\n### 🟡 Medium Activity (5000-9999 CP Reinforcement)\n"
    
    if reinf_medium:
        report += """
| Status | System | Reinforcement | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Current CP | Net CP | Activity |
|--------|--------|---------------|-------------|--------------|-----------------|-------------------|------------|--------|----------|
"""
        for system in reinf_medium:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0):.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['reinforcement']:,} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['current_progress_cp']:,} | +{system['net_cp']:,} | 🟡 Medium Reinforcement |\n"
    else:
        report += f"\n*No {state} systems with medium reinforcement activity*\n"
    
    report += f"\n### 🔴 Low Activity (1000-4999 CP Reinforcement)\n"
    
    if reinf_low:
        report += """
| Status | System | Reinforcement | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Current CP | Net CP | Activity |
|--------|--------|---------------|-------------|--------------|-----------------|-------------------|------------|--------|----------|
"""
        for system in reinf_low:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0):.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['reinforcement']:,} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['current_progress_cp']:,} | +{system['net_cp']:,} | 🔵 Low Reinforcement |\n"
    else:
        report += f"\n*No {state} systems with low reinforcement activity*\n"

    report += """

---

## ⚠️ Active Undermining (Negative Net CP)
*Systems where undermining is winning against reinforcement*

### ⚠️ High Activity (≥10,000 CP Undermining)
"""
    
    if under_high:
        report += """
| Status | System | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Reinforcement | Current CP | Net CP | Activity |
|--------|--------|-------------|--------------|-----------------|-------------------|---------------|------------|--------|----------|
"""
        for system in under_high:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0):.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['reinforcement']:,} | {system['current_progress_cp']:,} | {system['net_cp']:,} | ⚠️ High Undermining |\n"
    else:
        report += f"\n*No {state} systems with high undermining activity*\n"
    
    report += f"\n### 🔶 Medium Activity (5000-9999 CP Undermining)\n"
    
    if under_medium:
        report += """
| Status | System | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Reinforcement | Current CP | Net CP | Activity |
|--------|--------|-------------|--------------|-----------------|-------------------|---------------|------------|--------|----------|
"""
        for system in under_medium:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0):.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['reinforcement']:,} | {system['current_progress_cp']:,} | {system['net_cp']:,} | 🔶 Medium Undermining |\n"
    else:
        report += f"\n*No {state} systems with medium undermining activity*\n"
    
    report += f"\n### 🟡 Low Activity (1000-4999 CP Undermining)\n"
    
    if under_low:
        report += """
| Status | System | Undermining | Last Cycle % | Natural Decay % | Current Progress % | Reinforcement | Current CP | Net CP | Activity |
|--------|--------|-------------|--------------|-----------------|-------------------|---------------|------------|--------|----------|
"""
        for system in under_low:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            last_cycle_percent = f"{system.get('last_cycle_percent', 0):.1f}%"
            natural_decay = f"{system.get('natural_decay', 0):.2f}%" if 'natural_decay' in system else "N/A"
            current_progress = f"{system['progress_percent']}%"
            report += f"| {status_icon} | {system['system']} | {system['undermining']:,} | {last_cycle_percent} | {natural_decay} | {current_progress} | {system['reinforcement']:,} | {system['current_progress_cp']:,} | {system['net_cp']:,} | 🟡 Low Undermining |\n"
    else:
        report += f"\n*No {state} systems with low undermining activity*\n"

    # Write report
    output_file = Path(config['output_file'])
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[OK] {state.title()} report generated: {output_file}")
    print(f"[INFO] {len(reinforcement_winning)} systems gaining CP, {len(undermining_winning)} systems losing CP")

def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python create_universal_md.py <state>")
        print("States: stronghold, fortified, exploited")
        sys.exit(1)
    
    state = sys.argv[1].lower()
    generate_universal_report(state)

if __name__ == "__main__":
    main()
