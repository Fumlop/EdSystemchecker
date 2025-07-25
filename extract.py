#!/usr/bin/env python3
"""
Extract system data from Inara HTML files and convert to JSON
"""
import os
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from html.parser import HTMLParser

def is_current_powerplay_cycle(extracted_at_str: str) -> bool:
    """
    Determine if a system's data is from the current PowerPlay cycle.
    PowerPlay cycles run Thursday to Thursday (settlement on Thursday 7-11 UTC).
    
    Args:
        extracted_at_str: ISO timestamp string when the data was extracted
        
    Returns:
        bool: True if data is from current cycle, False otherwise
    """
    try:
        # Parse the extraction timestamp
        extracted_at = datetime.fromisoformat(extracted_at_str.replace('Z', '+00:00'))
        if extracted_at.tzinfo is None:
            # Assume local time if no timezone info
            extracted_at = extracted_at.replace(tzinfo=None)
        else:
            # Convert to local time for comparison
            extracted_at = extracted_at.replace(tzinfo=None)
        
        # Get current date
        now = datetime.now()
        
        # Find the most recent Thursday (PowerPlay settlement day)
        days_since_thursday = (now.weekday() - 3) % 7  # Thursday is weekday 3
        if days_since_thursday == 0 and now.weekday() == 3:
            # If today is Thursday, consider current cycle start as this Thursday
            cycle_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # Find last Thursday
            cycle_start = now - timedelta(days=days_since_thursday)
            cycle_start = cycle_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Current cycle runs from last Thursday to next Thursday
        cycle_end = cycle_start + timedelta(days=7)
        
        # Check if extraction time is within current cycle
        return cycle_start <= extracted_at < cycle_end
        
    except Exception as e:
        print(f"Error checking PowerPlay cycle for timestamp {extracted_at_str}: {e}")
        return False

def calculate_current_progress_cp(state: str, progress_percent: float) -> int:
    """
    Calculate current progress CP using formulas from Formulas.md
    
    Args:
        state: System state (Stronghold, Fortified, Exploited)
        progress_percent: Progress as percentage (0-100)
        
    Returns:
        int: Current progress CP
    """
    if state == "Stronghold":
        return int(1000000 * (progress_percent / 100.0))
    elif state == "Fortified":
        return int(650000 * (progress_percent / 100.0))
    elif state == "Exploited":
        return int(350000 * (progress_percent / 100.0))
    else:
        return 0

def calculate_natural_decay(state: str, last_cycle_cp_actual: int) -> int:
    """
    Calculate natural decay using formulas from Formulas.md
    
    Args:
        state: System state (Stronghold, Fortified, Exploited)
        last_cycle_cp_actual: Last cycle CP actual value
        
    Returns:
        int: Natural decay amount (multiplied by -1 for correct direction)
    """
    if state == "Stronghold":
        # Normalize CP to 0-1 range first
        normalized_cp = last_cycle_cp_actual / 1000000
        # decay = 1 000 000 × (–0.2087 × normalized_cp + 0.0527)
        return int(1000000 * (-0.2087 * normalized_cp + 0.0527)) * -1
    elif state == "Fortified":
        # Normalize CP to 0-1 range first
        normalized_cp = last_cycle_cp_actual / 650000
        # decay = 650 000 × (–0.1707 × normalized_cp + 0.0425)
        return int(650000 * (-0.1707 * normalized_cp + 0.0425)) * -1
    elif state == "Exploited":
        # Normalize CP to 0-1 range first
        normalized_cp = last_cycle_cp_actual / 350000
        # decay = 350 000 × (–0.0833 × normalized_cp + 0.0207)
        return int(350000 * (-0.0833 * normalized_cp + 0.0207)) * -1
    else:
        return 0

class InaraHTMLParser(HTMLParser):
    """Custom HTML parser for Inara system data"""
    
    def __init__(self):
        super().__init__()
        self.systems = []
        self.current_row = []
        self.current_cell = ""
        self.in_table = False
        self.in_row = False
        self.in_cell = False
    
    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
        elif tag == 'tr' and self.in_table:
            self.in_row = True
            self.current_row = []
        elif tag in ['td', 'th'] and self.in_row:
            self.in_cell = True
            self.current_cell = ""
    
    def handle_endtag(self, tag):
        if tag == 'table':
            self.in_table = False
        elif tag == 'tr' and self.in_row:
            self.in_row = False
            if len(self.current_row) >= 3:  # Process rows with enough data
                system_data = self.extract_system_from_row(self.current_row)
                if system_data:
                    self.systems.append(system_data)
        elif tag in ['td', 'th'] and self.in_cell:
            self.in_cell = False
            self.current_row.append(self.current_cell.strip())
    
    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data
    
    def extract_system_from_row(self, cells):
        """Extract system data from table row cells"""
        try:
            if not cells or len(cells) < 6:  # Need at least 6 columns
                return None
            
            # First cell: System name - clean Unicode characters
            system_name = cells[0].strip()
            system_name = system_name.replace("\ue81d", "").replace("︎", "").strip()
            system_name = re.sub(r'<[^>]+>', '', system_name)
            
            # Skip header rows
            if not system_name or system_name.lower() in ['system', 'name', 'star system']:
                return None
            
            # Second cell: State
            state = "Unknown"
            state_cell = cells[1].lower()
            if 'stronghold' in state_cell:
                state = 'Stronghold'
            elif 'fortified' in state_cell:
                state = 'Fortified' 
            elif 'exploited' in state_cell:
                state = 'Exploited'
            
            # Fourth cell: Undermining
            undermining = 0
            if len(cells) > 3:
                under_cell = cells[3]
                number_match = re.search(r'(\d+(?:,\d+)*)', under_cell)
                if number_match:
                    undermining = int(number_match.group(1).replace(',', ''))
            
            # Fifth cell: Reinforcement
            reinforcement = 0
            if len(cells) > 4:
                reinf_cell = cells[4]
                number_match = re.search(r'(\d+(?:,\d+)*)', reinf_cell)
                if number_match:
                    reinforcement = int(number_match.group(1).replace(',', ''))
            
            # Sixth cell: Progress
            progress_percent = 0.0
            if len(cells) > 5:
                progress_cell = cells[5]
                percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%', progress_cell)
                if percent_match:
                    progress_percent = float(percent_match.group(1))
            
            # Calculate current progress CP using formulas from Formulas.md
            current_progress_cp = calculate_current_progress_cp(state, progress_percent)
            
            # Calculate last_cycle_cp_actual using formula from Formulas.md
            last_cycle_cp_actual = current_progress_cp + undermining
            
            # Get extraction timestamp
            extracted_at = datetime.now().isoformat()
            
            # Calculate natural decay only for systems with > 25% progress
            system_data = {
                "system": system_name,
                "state": state,
                "undermining": undermining,
                "reinforcement": reinforcement,
                "progress_percent": progress_percent,
                "current_progress_cp": current_progress_cp,
                "last_cycle_cp_actual": last_cycle_cp_actual,
                "extracted_at": extracted_at,
                "current_cycle_refresh": is_current_powerplay_cycle(extracted_at)
            }
            
            # Only add natural_decay, expected_progress_cp and net_cp for systems with > 25% progress
            if progress_percent > 25.0:
                natural_decay = calculate_natural_decay(state, last_cycle_cp_actual)
                expected_progress_cp = last_cycle_cp_actual - natural_decay
                net_cp = expected_progress_cp - current_progress_cp
                system_data["natural_decay"] = natural_decay
                system_data["expected_progress_cp"] = expected_progress_cp
                system_data["net_cp"] = net_cp
            
            return system_data
            
        except Exception as e:
            print(f"Error extracting system data: {e}")
            return None

def parse_html_file(file_path: str) -> list:
    """Parse HTML file and extract system data"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = InaraHTMLParser()
        parser.feed(content)
        return parser.systems
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def save_systems_by_state(systems: list, output_dir: str = "json"):
    """Save systems grouped by state to separate JSON files"""
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Group systems by state
    systems_by_state = {}
    for system in systems:
        state = system.get('state', 'Unknown')
        if state not in systems_by_state:
            systems_by_state[state] = []
        systems_by_state[state].append(system)
    
    # Save each state to separate JSON file
    for state, state_systems in systems_by_state.items():
        filename = f"{state.lower()}_systems.json"
        output_path = Path(output_dir) / filename
        
        data = {
            "state": state,
            "system_count": len(state_systems),
            "last_update": datetime.now().isoformat(),
            "systems": state_systems
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {len(state_systems)} {state} systems to {output_path}")

def main():
    """Main extraction function"""
    html_dir = Path("html")
    
    if not html_dir.exists():
        print("❌ HTML directory not found. Run download.py first!")
        return
    
    print(f"Starting extraction at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    all_systems = []
    
    # Process HTML files
    html_files = list(html_dir.glob("*.html"))
    
    if not html_files:
        print("❌ No HTML files found in html/ directory")
        return
    
    for html_file in html_files:
        print(f"Processing: {html_file}")
        systems = parse_html_file(str(html_file))
        all_systems.extend(systems)
        print(f"  → Extracted {len(systems)} systems")
    
    print("-" * 60)
    print(f"Total systems extracted: {len(all_systems)}")
    
    if all_systems:
        # Save systems grouped by state
        save_systems_by_state(all_systems)
        
        # Print summary by state
        states = {}
        for system in all_systems:
            state = system.get('state', 'Unknown')
            states[state] = states.get(state, 0) + 1
        
        print("\n📊 Summary by state:")
        for state, count in sorted(states.items()):
            print(f"  {state}: {count} systems")
        
        print(f"\n✅ Extraction complete! JSON files saved in /json/")
    else:
        print("⚠ No systems extracted. Check HTML file structure.")

if __name__ == "__main__":
    main()
