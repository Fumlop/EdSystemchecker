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
    Analyze systems for undermining activity
    
    Args:
        systems_data: Dictionary with system data by state
        threshold_cp: CP threshold for considering undermining (default: 1000)
        
    Returns:
        dict: Analysis results separated by progress threshold
    """
    results = {
        "above_25": [],  # Systems with >25% progress
        "below_25": []   # Systems with <=25% progress
    }
    
    for state, data in systems_data.items():
        systems = data["systems"]
        
        for system in systems:
            curr_progress = system.get("curr_progress", 0.0)
            curr_progress_cp = system.get("curr_progress_cp", 0)
            expected_undermining_decay = system.get("expected_undermining_decay", 0)
            undermining = system.get("undermining", 0)
            
            # Calculate CP difference (actual vs expected)
            cp_difference = curr_progress_cp - expected_undermining_decay
            
            # Prepare system data
            system_data = {
                "system": system.get("system", "Unknown"),
                "state": state,
                "curr_progress": curr_progress,
                "curr_progress_cp": curr_progress_cp,
                "expected_undermining_decay": expected_undermining_decay,
                "cp_difference": cp_difference,
                "undermining": undermining
            }
            
            # Categorize by progress threshold
            if curr_progress > 25.0:
                # For systems >25%, check if CP difference exceeds threshold
                if abs(cp_difference) >= threshold_cp:
                    results["above_25"].append(system_data)
            else:
                # For systems <=25%, any difference indicates activity
                if abs(cp_difference) >= threshold_cp:
                    results["below_25"].append(system_data)
    
    # Sort by CP difference (highest absolute difference first)
    results["above_25"].sort(key=lambda x: abs(x["cp_difference"]), reverse=True)
    results["below_25"].sort(key=lambda x: abs(x["cp_difference"]), reverse=True)
    
    return results

def generate_markdown_report(analysis_results: dict, systems_data: dict, output_file: str = "active_undermining.md"):
    """
    Generate markdown report for active undermining
    
    Args:
        analysis_results: Analysis results from analyze_undermining
        systems_data: Original system data for metadata
        output_file: Output file name
    """
    above_25 = analysis_results["above_25"]
    below_25 = analysis_results["below_25"]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Active Undermining Analysis Report\n\n")
        f.write(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Analysis Threshold:** Systems with CP difference ≥ 1\n\n")
        
        # Data sources section
        f.write("## Data Sources\n\n")
        for state, data in systems_data.items():
            last_update = data.get("last_update", "Unknown")
            try:
                dt = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                formatted_time = last_update
            f.write(f"- **{state}**: {len(data['systems'])} systems (updated: {formatted_time})\n")
        f.write("\n")
        
        # Summary
        f.write("## Summary\n\n")
        f.write(f"- **Systems >25% Progress:** {len(above_25)} systems showing undermining activity\n")
        f.write(f"- **Systems ≤25% Progress:** {len(below_25)} systems showing activity\n")
        f.write(f"- **Total Systems Analyzed:** {sum(len(data['systems']) for data in systems_data.values())}\n\n")
        
        # Explanation
        f.write("## Analysis Method\n\n")
        f.write("### Systems >25% Progress\n")
        f.write("- **Natural Decay Applied:** These systems experience natural influence decay\n")
        f.write("- **CP Difference:** Actual CP minus Expected CP (after natural decay)\n")
        f.write("- **Positive Difference:** More CP than expected = Active undermining/fortification\n")
        f.write("- **Negative Difference:** Less CP than expected = Possible preparation activity\n\n")
        
        f.write("### Systems ≤25% Progress\n")
        f.write("- **No Natural Decay:** These systems maintain their progress\n")
        f.write("- **Expected = Actual:** Under normal circumstances\n")
        f.write("- **Any Difference:** Indicates recent activity (undermining/fortification)\n\n")
        
        # Systems >25% Progress Table
        f.write("## Systems >25% Progress (Natural Decay Applied)\n\n")
        
        if not above_25:
            f.write("**No systems >25% showing significant undermining activity**\n\n")
        else:
            f.write(f"**{len(above_25)} systems showing activity:**\n\n")
            
            # Group by state
            above_25_by_state = {}
            for system in above_25:
                state = system["state"]
                if state not in above_25_by_state:
                    above_25_by_state[state] = []
                above_25_by_state[state].append(system)
            
            for state, systems in above_25_by_state.items():
                f.write(f"### {state} Systems ({len(systems)} systems)\n\n")
                f.write("| System | Progress | Current CP | Expected CP | CP Difference | Reported Undermining |\n")
                f.write("|--------|----------|------------|-------------|---------------|----------------------|\n")
                
                for system in systems:
                    diff_sign = "+" if system["cp_difference"] >= 0 else ""
                    f.write(f"| **{system['system']}** | ")
                    f.write(f"{system['curr_progress']:.1f}% | ")
                    f.write(f"{system['curr_progress_cp']:,} | ")
                    f.write(f"{system['expected_undermining_decay']:,} | ")
                    f.write(f"**{diff_sign}{system['cp_difference']:,}** | ")
                    f.write(f"{system['undermining']:,} |\n")
                
                f.write("\n")
        
        # Systems ≤25% Progress Table
        f.write("## Systems ≤25% Progress (No Natural Decay)\n\n")
        
        if not below_25:
            f.write("**No systems ≤25% showing significant activity**\n\n")
        else:
            f.write(f"**{len(below_25)} systems showing activity:**\n\n")
            
            # Group by state
            below_25_by_state = {}
            for system in below_25:
                state = system["state"]
                if state not in below_25_by_state:
                    below_25_by_state[state] = []
                below_25_by_state[state].append(system)
            
            for state, systems in below_25_by_state.items():
                f.write(f"### {state} Systems ({len(systems)} systems)\n\n")
                f.write("| System | Progress | Current CP | Expected CP | CP Difference | Reported Undermining |\n")
                f.write("|--------|----------|------------|-------------|---------------|----------------------|\n")
                
                for system in systems:
                    diff_sign = "+" if system["cp_difference"] >= 0 else ""
                    f.write(f"| **{system['system']}** | ")
                    f.write(f"{system['curr_progress']:.1f}% | ")
                    f.write(f"{system['curr_progress_cp']:,} | ")
                    f.write(f"{system['expected_undermining_decay']:,} | ")
                    f.write(f"**{diff_sign}{system['cp_difference']:,}** | ")
                    f.write(f"{system['undermining']:,} |\n")
                
                f.write("\n")
        
        # Top 10 overall
        all_systems = above_25 + below_25
        if all_systems:
            f.write("## Top 10 Systems by Activity\n\n")
            f.write("| Rank | System | State | Progress | CP Difference | Category |\n")
            f.write("|------|--------|-------|----------|---------------|----------|\n")
            
            top_10 = sorted(all_systems, key=lambda x: abs(x["cp_difference"]), reverse=True)[:10]
            
            for i, system in enumerate(top_10, 1):
                category = ">25%" if system["curr_progress"] > 25.0 else "≤25%"
                diff_sign = "+" if system["cp_difference"] >= 0 else ""
                f.write(f"| {i} | **{system['system']}** | ")
                f.write(f"{system['state']} | ")
                f.write(f"{system['curr_progress']:.1f}% | ")
                f.write(f"**{diff_sign}{system['cp_difference']:,}** | ")
                f.write(f"{category} |\n")
        
        f.write("\n---\n")
        f.write(f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} using PowerPlay data from Inara.cz*\n")

def main():
    """Main function"""
    print("🔍 Analyzing systems for active undermining...")
    print("-" * 60)
    
    # Load system data
    systems_data = load_system_data()
    
    if not systems_data:
        print("❌ No system data found!")
        return
    
    # Analyze for undermining
    analysis_results = analyze_undermining(systems_data, threshold_cp=1)
    
    above_25_count = len(analysis_results["above_25"])
    below_25_count = len(analysis_results["below_25"])
    
    print(f"\n📊 Analysis Results:")
    print(f"- Systems >25% with activity: {above_25_count}")
    print(f"- Systems ≤25% with activity: {below_25_count}")
    print(f"- Total systems with activity: {above_25_count + below_25_count}")
    
    # Generate report
    generate_markdown_report(analysis_results, systems_data)
    print(f"\n✅ Report generated: active_undermining.md")
    
    # Show top 5 for each category
    if analysis_results["above_25"]:
        print(f"\n🔥 Top 5 Systems >25%:")
        for i, system in enumerate(analysis_results["above_25"][:5], 1):
            print(f"  {i}. {system['system']} ({system['state']}): {system['cp_difference']:+,} CP")
    
    if analysis_results["below_25"]:
        print(f"\n⚡ Top 5 Systems ≤25%:")
        for i, system in enumerate(analysis_results["below_25"][:5], 1):
            print(f"  {i}. {system['system']} ({system['state']}): {system['cp_difference']:+,} CP")

if __name__ == "__main__":
    main()
