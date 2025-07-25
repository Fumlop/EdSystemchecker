#!/usr/bin/env python3
"""
Analyze system data to find actively undermined systems
"""
import json
import os
from pathlib import Path
from datetime import datetime

# Formula constants from Formulas.md
FORMULAS = {
    "Stronghold": {
        "cp_100_percent": 1000000,
        "coefficient": 0.852137,
        "constant": 0.018411
    },
    "Fortified": {
        "cp_100_percent": 650000,
        "coefficient": 0.814443,
        "constant": 0.011009
    },
    "Exploited": {
        "cp_100_percent": 350000,
        "coefficient": 0.965505,
        "constant": 0.009839
    }
}

def calculate_previous_cycle_progress(state: str, current_progress: float) -> float:
    """
    Calculate what the progress was in the previous cycle (reverse formula)
    
    Args:
        state: System state (Stronghold, Fortified, Exploited)
        current_progress: Current progress as percentage (0-100)
        
    Returns:
        float: Previous cycle progress percentage
    """
    if state not in FORMULAS:
        return current_progress
    
    formula = FORMULAS[state]
    
    # Convert percentage to decimal (0-1)
    new_inf = current_progress / 100.0
    
    # Reverse formula: old_inf = (new_inf - constant) / coefficient
    # new_inf = coefficient × old_inf + constant
    # old_inf = (new_inf - constant) / coefficient
    old_inf = (new_inf - formula["constant"]) / formula["coefficient"]
    
    # Convert back to percentage
    return old_inf * 100.0

def calculate_expected_current_progress(state: str, previous_progress: float) -> float:
    """
    Calculate expected current progress from previous cycle using new_inf formula
    
    Args:
        state: System state (Stronghold, Fortified, Exploited)
        previous_progress: Previous cycle progress as percentage (0-100)
        
    Returns:
        float: Expected current progress percentage
    """
    if state not in FORMULAS:
        return previous_progress
    
    formula = FORMULAS[state]
    
    # Convert percentage to decimal (0-1)
    old_inf = previous_progress / 100.0
    
    # Apply formula: new_inf = coefficient × old_inf + constant
    new_inf = formula["coefficient"] * old_inf + formula["constant"]
    
    # Convert back to percentage
    return new_inf * 100.0

def calculate_cp_from_percentage(state: str, percentage: float) -> int:
    """Calculate CP value from percentage"""
    if state not in FORMULAS:
        return 0
    
    cp_max = FORMULAS[state]["cp_100_percent"]
    return int((percentage / 100.0) * cp_max)

def analyze_undermined_systems(threshold_cp: int = 5000, min_progress: float = 25.0) -> list:
    """
    Analyze systems to find actively undermined ones
    
    Args:
        threshold_cp: CP threshold for "active undermining" (default: 5000)
        min_progress: Minimum progress percentage to consider (default: 25%)
        
    Returns:
        list: List of undermined system data
    """
    json_dir = Path("json")
    undermined_systems = []
    
    if not json_dir.exists():
        print("❌ JSON directory not found. Run extract.py first!")
        return []
    
    # Process all JSON files
    for json_file in json_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            state = data.get("state", "Unknown")
            systems = data.get("systems", [])
            
            print(f"Analyzing {len(systems)} {state} systems...")
            
            for system in systems:
                current_progress = system.get("progress_percent", 0.0)
                undermining = system.get("undermining", 0)
                actual_cp = system.get("cp_progress", 0)
                last_cycle_cp = system.get("last_cycle_cp", 0)
                
                # Skip if progress is below minimum threshold
                if current_progress < min_progress:
                    continue
                
                # Calculate expected current progress from last cycle using natural decay
                if last_cycle_cp > 0:
                    # Convert last cycle CP to percentage
                    cp_max = FORMULAS[state]["cp_100_percent"]
                    last_cycle_percent = (last_cycle_cp / cp_max) * 100.0
                    
                    # Apply natural decay formula
                    expected_current_percent = calculate_expected_current_progress(state, last_cycle_percent)
                    expected_cp = calculate_cp_from_percentage(state, expected_current_percent)
                else:
                    # Fallback to reverse calculation if last_cycle_cp is missing
                    previous_progress = calculate_previous_cycle_progress(state, current_progress)
                    expected_current_percent = calculate_expected_current_progress(state, previous_progress)
                    expected_cp = calculate_cp_from_percentage(state, expected_current_percent)
                
                # Calculate CP difference (actual vs expected with natural decay only)
                cp_difference = actual_cp - expected_cp
                
                # Debug output for specific systems
                system_name = system.get("system", "Unknown")
                if system_name in ["LHS 317", "Dazbog", "LP 726-6", "Andel", "Orishpucho"]:
                    print(f"\n🔍 DEBUG: {system_name} ({state})")
                    print(f"  Current Progress: {current_progress:.1f}% = {actual_cp:,} CP")
                    print(f"  Last Cycle CP: {last_cycle_cp:,}")
                    if last_cycle_cp > 0:
                        last_cycle_percent = (last_cycle_cp / FORMULAS[state]["cp_100_percent"]) * 100.0
                        print(f"  Last Cycle %: {last_cycle_percent:.1f}%")
                        expected_current_percent = calculate_expected_current_progress(state, last_cycle_percent)
                        print(f"  Expected Current: {expected_current_percent:.1f}% = {expected_cp:,} CP")
                    print(f"  CP Difference: {cp_difference:,} CP")
                    print(f"  Undermining field: {undermining:,}")
                
                # Check if system shows undermining activity
                if cp_difference >= threshold_cp:
                    undermined_systems.append({
                        "system": system.get("system", "Unknown"),
                        "state": state,
                        "current_progress": current_progress,
                        "last_cycle_cp": last_cycle_cp,
                        "expected_cp": expected_cp,
                        "actual_cp": actual_cp,
                        "cp_difference": cp_difference,
                        "undermining": undermining,
                        "analysis_date": datetime.now().isoformat()
                    })
        
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    # Sort by CP difference (highest first)
    undermined_systems.sort(key=lambda x: x["cp_difference"], reverse=True)
    
    return undermined_systems

def generate_undermined_report(undermined_systems: list, output_file: str = "undermined.md"):
    """
    Generate markdown report of undermined systems
    
    Args:
        undermined_systems: List of undermined system data
        output_file: Output markdown file name
    """
    # Get data update times from JSON files
    json_dir = Path("json")
    update_times = {}
    
    if json_dir.exists():
        for json_file in json_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                state = data.get("state", "Unknown")
                last_update = data.get("last_update", data.get("extracted_at", "Unknown"))
                update_times[state] = last_update
            except:
                pass
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Actively Undermined Systems Report\n\n")
        f.write(f"**Analysis Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Threshold:** Systems with >5000 CP difference and >25% progress\n")
        f.write(f"**Total Systems:** {len(undermined_systems)}\n\n")
        
        # Show data update times
        if update_times:
            f.write("## Data Sources\n\n")
            for state, update_time in update_times.items():
                try:
                    # Format the ISO timestamp
                    dt = datetime.fromisoformat(update_time.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_time = update_time
                f.write(f"- **{state}**: Last updated {formatted_time}\n")
            f.write("\n")
        
        if not undermined_systems:
            f.write("## No actively undermined systems found\n\n")
            f.write("All systems appear to be following expected decay patterns.\n")
            return
        
        f.write("## Analysis Summary\n\n")
        f.write("Systems showing significant undermining activity (deviation from expected natural decay):\n\n")
        
        # Group by state
        by_state = {}
        for system in undermined_systems:
            state = system["state"]
            if state not in by_state:
                by_state[state] = []
            by_state[state].append(system)
        
        for state, systems in by_state.items():
            f.write(f"### {state} Systems ({len(systems)} systems)\n\n")
            f.write("| System | Current % | Expected % | CP Difference | Undermining |\n")
            f.write("|--------|-----------|------------|---------------|-------------|\n")
            
            for system in systems:
                f.write(f"| **{system['system']}** | ")
                f.write(f"{system['current_progress']:.1f}% | ")
                f.write(f"{system['expected_current']:.1f}% | ")
                f.write(f"**{system['cp_difference']:,} CP** | ")
                f.write(f"{system['undermining']:,} |\n")
            
            f.write("\n")
        
        f.write("## Detailed Analysis\n\n")
        f.write("### Formula Used\n")
        f.write("The analysis uses the following decay formulas:\n\n")
        
        for state, formula in FORMULAS.items():
            f.write(f"**{state}:**\n")
            f.write(f"- CP 100% = {formula['cp_100_percent']:,}\n")
            f.write(f"- new_inf = {formula['coefficient']} × old_inf + {formula['constant']}\n\n")
        
        f.write("### Interpretation\n\n")
        f.write("- **CP Difference**: How much more CP the system has compared to expected natural decay\n")
        f.write("- **Current %**: Actual current progress from Inara\n")
        f.write("- **Expected %**: What progress should be based on natural decay formula\n")
        f.write("- **Threshold**: Systems with >5000 CP difference are considered actively undermined\n")
        f.write("- **Progress >25%**: Only systems above 25% are analyzed (below 25% natural decay is minimal)\n\n")
        
        f.write("### Analysis Method\n\n")
        f.write("1. **Reverse Calculate**: Determine previous cycle progress from current values\n")
        f.write("2. **Apply Formula**: Calculate expected current progress using decay formula\n")
        f.write("3. **Compare**: Find difference between actual vs expected current progress\n")
        f.write("4. **Identify**: Systems with significant positive difference are actively undermined\n\n")
        
        f.write("### Top Undermined Systems\n\n")
        
        top_10 = undermined_systems[:10]
        for i, system in enumerate(top_10, 1):
            f.write(f"**{i}. {system['system']} ({system['state']})**\n")
            f.write(f"- Current Progress: {system['current_progress']:.1f}%\n")
            f.write(f"- Expected Current: {system['expected_current']:.1f}%\n")
            f.write(f"- Previous Cycle: {system['previous_progress']:.1f}%\n")
            f.write(f"- CP Difference: **{system['cp_difference']:,} CP**\n")
            f.write(f"- Reported Undermining: {system['undermining']:,}\n\n")

def main():
    """Main analysis function"""
    print("🔍 Analyzing systems for active undermining...")
    print("-" * 50)
    
    # Analyze systems
    undermined_systems = analyze_undermined_systems(threshold_cp=5000, min_progress=25.0)
    
    print(f"\n📊 Analysis Results:")
    print(f"- Found {len(undermined_systems)} actively undermined systems")
    
    if undermined_systems:
        # Group by state for summary
        by_state = {}
        for system in undermined_systems:
            state = system["state"]
            by_state[state] = by_state.get(state, 0) + 1
        
        print("- Breakdown by state:")
        for state, count in by_state.items():
            print(f"  - {state}: {count} systems")
        
        print(f"\n🔥 Top 5 most undermined:")
        for i, system in enumerate(undermined_systems[:5], 1):
            print(f"  {i}. {system['system']} ({system['state']}): {system['cp_difference']:,} CP difference")
    
    # Generate report
    generate_undermined_report(undermined_systems)
    print(f"\n✅ Report generated: undermined.md")

if __name__ == "__main__":
    main()
