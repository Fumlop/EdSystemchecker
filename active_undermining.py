#!/usr/bin/env python3
"""
Generate active undermining report with separate tables for >25% and <25% systems
"""
import json
import os
from pathlib import Path
from datetime import datetime
from manual_undermining import get_undermining_cp

def load_system_data(json_dir: str = "json") -> dict:
    """
    Load all system data from JSON files
    
    Args:
        json_dir: Directory containing JSON files
        
    Returns:
        dict: Dictionary with state as key and systems list as value
    """
    systems_data = {}
    json_path = Path(json_dir)
    
    if not json_path.exists():
        print("❌ JSON directory not found. Run extract.py first!")
        return {}
    
    for json_file in json_path.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            state = data.get("state", "Unknown")
            systems = data.get("systems", [])
            last_update = data.get("last_update", "Unknown")
            
            systems_data[state] = {
                "systems": systems,
                "last_update": last_update
            }
            
            print(f"Loaded {len(systems)} {state} systems")
            
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    
    return systems_data

def analyze_undermining(systems_data: dict, threshold_cp: int = 1) -> dict:
    """
    Analyze systems for real undermining activity (positive real_undermining only)
    
    Args:
        systems_data: Dictionary with system data by state
        threshold_cp: CP threshold for considering undermining (default: 1)
        
    Returns:
        dict: Analysis results by state with only real undermining
    """
    results = {}
    
    for state, data in systems_data.items():
        systems = data["systems"]
        state_systems = []
        
        for system in systems:
            curr_progress = system.get("curr_progress", 0.0)
            real_undermining = system.get("real_undermining", 0)
            
            # Only include systems with positive real_undermining (actual undermining)
            if real_undermining > threshold_cp:
                system_data = {
                    "system": system.get("system", "Unknown"),
                    "state": state,
                    "curr_progress": curr_progress,
                    "curr_progress_cp": system.get("curr_progress_cp", 0),
                    "expected_undermining_decay": system.get("expected_undermining_decay", 0),
                    "real_undermining": real_undermining,
                    "undermining": system.get("undermining", 0),
                    "real_reinforcement": system.get("real_reinforcement", 0),
                    "net_activity": system.get("net_activity", 0)
                }
                state_systems.append(system_data)
        
        if state_systems:
            # Sort by real_undermining (highest first)
            state_systems.sort(key=lambda x: x["real_undermining"], reverse=True)
            results[state] = state_systems
    
    return results

def generate_markdown_report(analysis_results: dict, systems_data: dict, output_file: str = "undermining.md"):
    """
    Generate markdown report for real undermining activities
    
    Args:
        analysis_results: Analysis results from analyze_undermining (by state)
        systems_data: Original system data for metadata
        output_file: Output file name
    """
    total_systems = sum(len(systems) for systems in analysis_results.values())
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Real Undermining Activity Report\n\n")
        f.write(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Systems with Real Undermining:** {total_systems}\n\n")
        
        # Data sources section
        f.write("## Data Sources\n\n")
        for state, data in systems_data.items():
            last_update = data.get("last_update", "Unknown")
            try:
                dt = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                formatted_time = last_update
            f.write(f"- **{state}**: {len(data['systems'])} systems total (updated: {formatted_time})\n")
        f.write("\n")
        
        # Summary by state
        f.write("## Summary by State\n\n")
        f.write("| State | Systems with Real Undermining | Total Systems | Percentage |\n")
        f.write("|-------|--------------------------------|---------------|------------|\n")
        
        for state, data in systems_data.items():
            state_undermining = len(analysis_results.get(state, []))
            total_state = len(data['systems'])
            percentage = (state_undermining / total_state * 100) if total_state > 0 else 0
            f.write(f"| **{state}** | {state_undermining} | {total_state} | {percentage:.1f}% |\n")
        f.write("\n")
        
        # Explanation
        f.write("## Analysis Method\n\n")
        f.write("- **Real Undermining:** Positive values indicating actual player undermining activity\n")
        f.write("- **Expected Decay:** What the system should have after natural influence decay\n")
        f.write("- **Net Activity:** Real Reinforcement - Real Undermining (positive = more fortification)\n")
        f.write("- **Only systems with confirmed undermining activity are shown**\n\n")
        
        # Systems by state
        for state in ["Stronghold", "Fortified", "Exploited"]:
            if state in analysis_results:
                systems = analysis_results[state]
                f.write(f"## {state} Systems ({len(systems)} systems)\n\n")
                
                f.write("| System | Progress | Current CP | Expected CP | Real Undermining | Real Reinforcement | Net Activity |\n")
                f.write("|--------|----------|------------|-------------|------------------|--------------------|--------------|\n")
                
                for system in systems:
                    net_sign = "+" if system["net_activity"] >= 0 else ""
                    f.write(f"| **{system['system']}** | ")
                    f.write(f"{system['curr_progress']:.1f}% | ")
                    f.write(f"{system['curr_progress_cp']:,} | ")
                    f.write(f"{system['expected_undermining_decay']:,} | ")
                    f.write(f"**{system['real_undermining']:,}** | ")
                    f.write(f"{system['real_reinforcement']:,} | ")
                    f.write(f"**{net_sign}{system['net_activity']:,}** |\n")
                
                f.write("\n")
        
        # Top 10 overall
        all_systems = []
        for systems in analysis_results.values():
            all_systems.extend(systems)
        
        if all_systems:
            f.write("## Top 10 Systems by Undermining Activity\n\n")
            f.write("| Rank | System | State | Progress | Real Undermining | Net Activity |\n")
            f.write("|------|--------|-------|----------|------------------|---------------|\n")
            
            top_10 = sorted(all_systems, key=lambda x: x["real_undermining"], reverse=True)[:10]
            
            for i, system in enumerate(top_10, 1):
                net_sign = "+" if system["net_activity"] >= 0 else ""
                f.write(f"| {i} | **{system['system']}** | ")
                f.write(f"{system['state']} | ")
                f.write(f"{system['curr_progress']:.1f}% | ")
                f.write(f"**{system['real_undermining']:,}** | ")
                f.write(f"**{net_sign}{system['net_activity']:,}** |\n")
        
        f.write("\n---\n")
        f.write(f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} using PowerPlay data from Inara.cz*\n")

def main():
    """Main function"""
    print("🔍 Analyzing systems for real undermining activity...")
    print("-" * 60)
    
    # Load system data
    systems_data = load_system_data()
    
    if not systems_data:
        print("❌ No system data found!")
        return
    
    # Analyze for real undermining
    analysis_results = analyze_undermining(systems_data, threshold_cp=1)
    
    total_undermining = sum(len(systems) for systems in analysis_results.values())
    
    print(f"\n📊 Analysis Results:")
    for state, systems in analysis_results.items():
        print(f"- {state}: {len(systems)} systems with real undermining")
    print(f"- Total systems with real undermining: {total_undermining}")
    
    # Generate report
    generate_markdown_report(analysis_results, systems_data)
    print(f"\n✅ Report generated: undermining.md")
    
    # Show top 5 overall
    all_systems = []
    for systems in analysis_results.values():
        all_systems.extend(systems)
    
    if all_systems:
        top_5 = sorted(all_systems, key=lambda x: x["real_undermining"], reverse=True)[:5]
        print(f"\n🔥 Top 5 Systems with Real Undermining:")
        for i, system in enumerate(top_5, 1):
            print(f"  {i}. {system['system']} ({system['state']}): {system['real_undermining']:,} CP")

if __name__ == "__main__":
    main()
