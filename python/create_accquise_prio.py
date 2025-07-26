#!/usr/bin/env python3
"""
Extract priority acquisition systems from accquise.conf and add to reports
"""
from pathlib import Path
from datetime import datetime

def extract_accquise_systems():
    """Extract system names from accquise.conf"""
    # Look for accquise.conf in parent directory (project root)
    script_dir = Path(__file__).parent
    conf_path = script_dir.parent / "accquise.conf"
    
    if not conf_path.exists():
        print(f"WARNING: accquise.conf not found at {conf_path}")
        return []
    
    systems = []
    with open(conf_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract system name (everything before the first colon)
                if ':' in line:
                    system_name = line.split(':')[0].strip()
                    if system_name:
                        systems.append({
                            'system': system_name,
                            'description': line.split(':', 1)[1].strip() if ':' in line else '',
                            'line_number': line_num
                        })
    
    return systems

def generate_accquise_report():
    """Generate priority acquisition systems report"""
    systems = extract_accquise_systems()
    
    if not systems:
        print("No acquisition systems found in accquise.conf")
        return
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Start building the report
    report = []
    report.append("# 🎯 Priority Acquisition Systems")
    report.append("")
    report.append(f"**Report Generated:** {timestamp}")
    report.append(f"**Source:** accquise.conf")
    report.append(f"**Total Systems:** {len(systems)}")
    report.append("")
    
    # Quick list
    report.append("## 📋 System List")
    report.append("")
    for i, system in enumerate(systems, 1):
        report.append(f"{i}. **{system['system']}**")
    report.append("")
    
    # Detailed table
    report.append("## 📊 Detailed Information")
    report.append("")
    report.append("| # | System | Description |")
    report.append("|---|--------|-------------|")
    
    for i, system in enumerate(systems, 1):
        description = system['description'].replace('|', '\\|')  # Escape pipes for markdown
        report.append(f"| {i} | {system['system']} | {description} |")
    
    report.append("")
    report.append("---")
    report.append("")
    report.append("*Generated from accquise.conf configuration file*")
    
    # Write report to file
    output_path = Path("accquise_prio.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Priority acquisition report generated: {output_path}")
    print(f"📊 {len(systems)} systems extracted from accquise.conf")
    
    # Print extracted systems for verification
    print("\n🎯 Extracted systems:")
    for system in systems:
        print(f"  - {system['system']}")
    
    return systems

if __name__ == "__main__":
    generate_accquise_report()
