#!/usr/bin/env python3
"""
System Status Transition Tracker
Zeigt Systeme die 100% Progress überschritten haben und in den nächsten Status wechseln
"""
import json
import sys
from datetime import datetime
from pathlib import Path

def find_transition_systems(state):
    """Finde Systeme die 100% Progress überschritten haben"""
    
    # State zu JSON-Datei mapping
    json_files = {
        'stronghold': 'json/stronghold_systems.json',
        'fortified': 'json/fortified_systems.json', 
        'exploited': 'json/exploited_systems.json'
    }
    
    json_file = json_files.get(state)
    if not json_file:
        return []
    
    json_path = Path(json_file)
    if not json_path.exists():
        print(f"[WARNING] {json_file} not found")
        return []
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    systems = data.get('systems', [])
    
    # Finde Systeme mit progress_percent > 100
    transition_systems = []
    for system in systems:
        progress = system.get('progress_percent', 0)
        if progress > 100.0:
            transition_systems.append({
                'system': system.get('system', 'Unknown'),
                'progress_percent': progress,
                'current_progress_cp': system.get('current_progress_cp', 0),
                'reinforcement': system.get('reinforcement', 0),
                'undermining': system.get('undermining', 0),
                'net_cp': system.get('net_cp', 0),
                'last_cycle_percent': system.get('last_cycle_percent', 0)
            })
    
    # Sortiere nach höchstem Progress
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

def generate_transition_section(state):
    """Generate Transition section for MD file"""
    
    transition_systems = find_transition_systems(state)
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

| System | Progress % | Next Status | Net CP | Reinforcement | Undermining | 
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
"""

    return section

def add_transition_to_md_file(state):
    """Füge Transition-Sektion zu existierender MD-Datei hinzu"""
    
    md_files = {
        'stronghold': 'stronghold_status.md',
        'fortified': 'fortified_status.md',
        'exploited': 'exploited_status.md'
    }
    
    md_file = md_files.get(state)
    if not md_file:
        print(f"[ERROR] Unbekannter State: {state}")
        return False
    
    md_path = Path(md_file)
    if not md_path.exists():
        print(f"[ERROR] {md_file} not found")
        return False
    
    # Lade existierende MD-Datei
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Transition section already exists
    if "## 🔄 System Status Transitions" in content:
        print(f"[INFO] Transition section already exists in {md_file} - overwriting...")
        # Remove old section
        lines = content.split('\n')
        new_lines = []
        skip_section = False
        
        for line in lines:
            if line.startswith("## 🔄 System Status Transitions"):
                skip_section = True
                continue
            elif line.startswith("## ") and skip_section:
                skip_section = False
                new_lines.append(line)
            elif not skip_section:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
    
    # Generate new Transition section
    transition_section = generate_transition_section(state)
    
    # Add section after Quick Summary
    if "## 📊 Quick Summary" in content:
        # Find end of Quick Summary section
        lines = content.split('\n')
        new_lines = []
        quick_summary_found = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            if line.startswith("## 📊 Quick Summary"):
                quick_summary_found = True
            elif quick_summary_found and (line.startswith("---") or (line.startswith("## ") and "Quick Summary" not in line)):
                # Add Transition section before next section
                new_lines.extend(transition_section.split('\n'))
                quick_summary_found = False
        
        # If Quick Summary was at the end, add section
        if quick_summary_found:
            new_lines.extend(transition_section.split('\n'))
        
        content = '\n'.join(new_lines)
    else:
        # Fallback: Add at the end
        content += transition_section
    
    # Write back
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Transition section added to {md_file}")
    return True

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python transition_tracker.py <state>")
        print("States: stronghold, fortified, exploited")
        return
    
    state = sys.argv[1].lower()
    valid_states = ['stronghold', 'fortified', 'exploited']
    
    if state not in valid_states:
        print(f"[ERROR] Invalid state: {state}")
        print(f"Available states: {', '.join(valid_states)}")
        return
    
    print(f"🔍 Searching for transition systems in {state.title()}...")
    
    # Find systems over 100%
    transition_systems = find_transition_systems(state)
    
    if transition_systems:
        print(f"🚀 {len(transition_systems)} system(s) found that exceeded 100%:")
        for system in transition_systems[:5]:  # Show Top 5
            print(f"  - {system['system']}: {system['progress_percent']:.1f}%")
    else:
        print(f"ℹ️ No systems found that exceeded 100% progress")
    
    # Add to MD file
    success = add_transition_to_md_file(state)
    
    if success:
        print(f"\n✅ Transition tracking successfully added to {state}_status.md!")
    else:
        print(f"\n❌ Error adding transition section")

if __name__ == "__main__":
    main()
