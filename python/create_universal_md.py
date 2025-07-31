#!/usr/bin/env python3
"""
Universal system status markdown report generator
Supports: stronghold, fortified, exploited states
Cache-bust: v1.1
"""
import json
import sys
from datetime import datetime
from pathlib import Path

def find_transition_systems(systems, state):
    """Find systems that have exceeded 100% progress and will transition"""
    transition_systems = []
    
    for system in systems:
        progress = system.get('progress_percent', 0)
        if progress > 100.0:
            transition_systems.append({
                'system': system.get('system', 'Unknown'),
                'progress_percent': progress,
                'reinforcement': system.get('reinforcement', 0),
                'undermining': system.get('undermining', 0),
                'net_cp': system.get('net_cp', 0)
            })
    
    # Sort by highest progress
    transition_systems.sort(key=lambda x: x['progress_percent'], reverse=True)
    return transition_systems

def get_next_status(current_state):
    """Determine next status after transition (system gets stronger when exceeding 100%)"""
    transitions = {
        'exploited': 'fortified',
        'fortified': 'stronghold', 
        'stronghold': 'stronghold (already max)'
    }
    return transitions.get(current_state, 'unknown')

def generate_transition_section(systems, state):
    """Generate transition tracking section"""
    transition_systems = find_transition_systems(systems, state)
    next_status = get_next_status(state)
    
    if not transition_systems:
        return f"""
## 🔄 System Status Transitions
*Systems that have exceeded 100% progress*

**No systems found that have exceeded 100% progress.**
"""
    
    section = f"""
## 🔄 System Status Transitions  
*Systems that have exceeded 100% progress and will transition to "{next_status}"*

**⚠️ {len(transition_systems)} system(s) have exceeded 100% progress!**

| System | Progress % | Next State | Net CP | Reinforcement | Undermining | 
|--------|------------|-------------|--------|---------------|-------------|"""

    for system in transition_systems:
        progress_icon = "🚀" if system['progress_percent'] > 120 else "⬆️"
        net_cp_display = f"+{system['net_cp']:,}" if system['net_cp'] > 0 else f"{system['net_cp']:,}"
        
        section += f"""
| {progress_icon} **{system['system']}** | {system['progress_percent']:.1f}% | {next_status} | {net_cp_display} | {system['reinforcement']:,} | {system['undermining']:,} |"""
    section += f"""

### 📈 Transition Details
- **Systems over 100%**: {len(transition_systems)}
- **Highest Progress**: {max(s['progress_percent'] for s in transition_systems):.1f}%
- **Status Change**: {state.title()} → {next_status.title()}

---
"""

    return section

def categorize_by_activity(systems, activity_field='undermining'):
    """Categorize systems by activity level"""
    high = []
    medium = []
    low = []
    
    for system in systems:
        # Use net_cp if available, otherwise check if system dropped due to decay+undermining
        if 'net_cp' in system:
            activity = abs(system.get('net_cp', 0))
        else:
            # For systems without net_cp, check if they dropped from above 25%
            last_cycle = system.get('last_cycle_percent', 0)
            current = system.get('progress_percent', 0)
            if last_cycle >= 25.0 and current < 25.0:
                # System dropped significantly - treat as high activity
                activity = 10000  # Treat as high activity to ensure visibility
            else:
                continue  # Skip systems without meaningful activity
         
        if activity >= 10000:
            high.append(system)
        elif activity >= 5000:
            medium.append(system)
        elif activity >= 1000:
            low.append(system)
    
    return high, medium, low

def get_net_cp_display(system):
    """Get Net CP display string, handling systems without net_cp"""
    if 'net_cp' in system:
        return f"{system['net_cp']:,}"
    else:
        # For systems that dropped from above 25%, show as decay indication
        drop = system.get('last_cycle_percent', 0) - system.get('progress_percent', 0)
        return f"Decay+Under. (-{drop:.1f}%)"

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
    
    # ONLY include systems with current cycle data - filter by current_cycle_refresh
    systems = [s for s in systems if s.get('current_cycle_refresh', True)]
    
    # Include systems with net_cp OR systems that dropped from above 25% (decay+undermining)
    systems_with_analysis = []
    for s in systems:
        if 'net_cp' in s:
            systems_with_analysis.append(s)
        elif s.get('last_cycle_percent', 0) >= 25.0 and s.get('progress_percent', 0) < 25.0:
            # System dropped from above 25% - likely decay+undermining
            systems_with_analysis.append(s)
    
    # Separate by Net CP (positive = reinforcement winning, negative = undermining winning)
    reinforcement_winning = [s for s in systems_with_analysis if s.get('net_cp', 0) > 0]
    undermining_winning = [s for s in systems_with_analysis if s.get('net_cp', 0) < 0]
    
    # Add systems that dropped from above 25% to undermining_winning if they don't have net_cp
    for s in systems_with_analysis:
        if 'net_cp' not in s and s.get('last_cycle_percent', 0) >= 25.0 and s.get('progress_percent', 0) < 25.0:
            undermining_winning.append(s)
    
    # Sort: Positive Net CP descending, Negative Net CP ascending (most negative first)
    # For systems without net_cp, sort by progress drop (last_cycle - current)
    reinforcement_winning.sort(key=lambda x: x.get('net_cp', 0), reverse=True)
    undermining_winning.sort(key=lambda x: x.get('net_cp', 
        -(x.get('last_cycle_percent', 0) - x.get('progress_percent', 0)) * 1000))
    
    # Categorize by activity levels
    reinf_high, reinf_medium, reinf_low = categorize_by_activity(reinforcement_winning)
    under_high, under_medium, under_low = categorize_by_activity(undermining_winning)
    
    # Generate report
    report = f"""# {config['title']}

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Data Source:** {data.get('last_update', 'Unknown')}
**Total {state.title()}:** {len(systems)} ({len(systems_with_analysis)} with decay analysis)

## 📊 Quick Summary

### 🟢 **Best Protected Systems**
*Top systems with positive Net CP (reinforcement winning)*

| Status | System | Net CP | Undermining | Reinforcement | Progress |
|--------|--------|--------|-------------|---------------|----------|"""
    
    if reinforcement_winning:
        for system in reinforcement_winning[:5]:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            net_cp_display = f"+{system.get('net_cp', 0):,}"
            report += f"\n| {status_icon} | **{system['system']}** | {net_cp_display} CP | {system['undermining']:,} | {system['reinforcement']:,} | {system['progress_percent']}% |"
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
            net_cp_display = get_net_cp_display(system)
            report += f"\n| {status_icon} | **{system['system']}** | {net_cp_display} CP | {system['undermining']:,} | {system['reinforcement']:,} | {system['progress_percent']}% |"
    else:
        report += "\n| - | *No systems currently losing CP* | - | - | - | - |"

    # High Progress and Low Progress Systems
    high_progress_systems = [s for s in systems_with_analysis if s.get('progress_percent', 0) >= 70]
    low_progress_systems = [s for s in systems_with_analysis if s.get('progress_percent', 0) < 25]
    
    # Sort by progress (highest first for high progress, lowest first for low progress)
    high_progress_systems.sort(key=lambda x: x.get('progress_percent', 0), reverse=True)
    low_progress_systems.sort(key=lambda x: x.get('progress_percent', 0))

    report += f"""

### 🟢 **High Progress Systems (>=70%)**
*Systems with strong progress that are close to completion*

| Status | System | Net CP | Progress | Undermining | Reinforcement |
|--------|--------|--------|----------|-------------|---------------|"""
    
    if high_progress_systems:
        for system in high_progress_systems:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            net_cp_display = f"+{system.get('net_cp', 0):,}" if system.get('net_cp', 0) >= 0 else f"{system.get('net_cp', 0):,}"
            report += f"\n| {status_icon} | **{system['system']}** | {net_cp_display} CP | {system['progress_percent']}% | {system['undermining']:,} | {system['reinforcement']:,} |"
    else:
        report += "\n| - | *No systems with >=70% progress found* | - | - | - | - |"

    report += f"""

### 🔴 **Low Progress Systems (<25%)**
*Systems with low progress that need attention*

| Status | System | Net CP | Progress | Undermining | Reinforcement |
|--------|--------|--------|----------|-------------|---------------|"""
    
    if low_progress_systems:
        for system in low_progress_systems:
            status_icon = "✅" if system['progress_percent'] >= 20 else "🔥"
            net_cp_display = f"+{system.get('net_cp', 0):,}" if system.get('net_cp', 0) >= 0 else f"{system.get('net_cp', 0):,}"
            report += f"\n| {status_icon} | **{system['system']}** | {net_cp_display} CP | {system['progress_percent']}% | {system['undermining']:,} | {system['reinforcement']:,} |"
    else:
        report += "\n| - | *No systems with <25% progress found* | - | - | - | - |"

    # Add Transition Tracking Section
    transition_section = generate_transition_section(systems, state)
    report += transition_section

    report += f"""
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
