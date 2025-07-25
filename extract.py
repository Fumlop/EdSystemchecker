#!/usr/bin/env python3
"""
Extract system data from Inara HTML files and convert to JSON
"""
import os
import json
import re
from pathlib import Path
from datetime import datetime
from html.parser import HTMLParser

# Formula constants from Formulas.md - ORIGINAL VERSION
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

def calculate_cp_progress(state: str, progress_percent: float) -> int:
    """
    Calculate CP (Control Points) based on state and progress percentage
    
    Args:
        state: System state (Stronghold, Fortified, Exploited)
        progress_percent: Progress as percentage (0-100)
        
    Returns:
        int: Calculated CP value
    """
    if state not in FORMULAS:
        return 0
    
    formula = FORMULAS[state]
    cp_max = formula["cp_100_percent"]
    
    # Convert percentage to CP
    cp_value = int((progress_percent / 100.0) * cp_max)
    return cp_value

def calculate_last_cycle_cp(state: str, current_progress: float) -> int:
    """
    Calculate what the progress was in the previous cycle using reverse formula
    
    Args:
        state: System state (Stronghold, Fortified, Exploited)
        current_progress: Current progress as percentage (0-100)
        
    Returns:
        int: Previous cycle CP value
    """
    if state not in FORMULAS:
        # Fallback to current CP
        return calculate_cp_progress(state, current_progress)
    
    formula = FORMULAS[state]
    
    # Convert percentage to decimal (0-1)
    current_inf = current_progress / 100.0
    
    # Reverse formula: last_inf = (current_inf - constant) / coefficient
    last_inf = (current_inf - formula["constant"]) / formula["coefficient"]
    
    # Convert to CP
    last_cycle_cp = int(last_inf * formula["cp_100_percent"])
    
    return last_cycle_cp

def calculate_expected_undermining_decay(state: str, last_cycle_cp: int, current_progress_percent: float) -> int:
    """
    Calculate expected current CP from last cycle CP using forward decay formula
    
    This represents what we would expect the system to have naturally decayed to
    without any undermining activity. For systems ≤25%, no natural decay occurs.
    
    Args:
        state: System state (Stronghold, Fortified, Exploited)
        last_cycle_cp: Last cycle CP value
        current_progress_percent: Current progress percentage (to check 25% threshold)
        
    Returns:
        int: Expected current CP value after natural decay (or current CP if ≤25%)
    """
    if state not in FORMULAS:
        return last_cycle_cp
    
    formula = FORMULAS[state]
    cp_max = formula["cp_100_percent"]
    
    # For systems ≤25%, no natural decay occurs
    if current_progress_percent <= 25.0:
        return int((current_progress_percent / 100.0) * cp_max)
    
    # Apply natural decay formula for systems >25%
    # Convert CP to inf (0-1)
    last_inf = last_cycle_cp / cp_max
    
    # Apply formula: current_inf = coefficient × last_inf + constant
    current_inf = formula["coefficient"] * last_inf + formula["constant"]
    
    # Convert back to CP
    expected_undermining_decay = int(current_inf * cp_max)
    
    return expected_undermining_decay

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
            if not cells or len(cells) < 6:  # Need at least 6 columns: System, State, Opposing, Under, Reinf, Progress
                return None
            
            # First cell is usually system name - clean Unicode characters
            system_name = cells[0].strip()
            # Remove unwanted Unicode characters and HTML artifacts
            system_name = system_name.replace("\ue81d", "").replace("︎", "").strip()
            # Remove any remaining HTML tags
            import re
            system_name = re.sub(r'<[^>]+>', '', system_name)
            
            # Skip header rows
            if not system_name or system_name.lower() in ['system', 'name', 'star system']:
                return None
            
            # Extract state from second cell
            state = "Unknown"
            state_cell = cells[1].lower()
            if 'stronghold' in state_cell:
                state = 'Stronghold'
            elif 'fortified' in state_cell:
                state = 'Fortified' 
            elif 'exploited' in state_cell:
                state = 'Exploited'
            
            # Extract undermining from 4th cell (index 3)
            undermining = 0
            if len(cells) > 3:
                under_cell = cells[3]
                # Look for numbers in undermining cell
                number_match = re.search(r'(\d+(?:,\d+)*)', under_cell)
                if number_match:
                    undermining = int(number_match.group(1).replace(',', ''))
            
            # Extract reinforcement from 5th cell (index 4)
            reinforcement = 0
            if len(cells) > 4:
                reinf_cell = cells[4]
                # Look for numbers in reinforcement cell
                number_match = re.search(r'(\d+(?:,\d+)*)', reinf_cell)
                if number_match:
                    reinforcement = int(number_match.group(1).replace(',', ''))
            
            # Extract progress from 6th cell (index 5)
            progress_percent = 0.0
            if len(cells) > 5:
                progress_cell = cells[5]
                # Look for percentage
                percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%', progress_cell)
                if percent_match:
                    progress_percent = float(percent_match.group(1))
            
            # Calculate CP
            curr_progress_cp = calculate_cp_progress(state, progress_percent)
            
            # Calculate THEORETICAL last cycle CP using REVERSE FORMULA
            # This represents what the system would have needed to be to reach current progress through natural decay
            last_cycle_cp_formula = calculate_last_cycle_cp(state, progress_percent)
            
            # Calculate ACTUAL last cycle CP: current + undermining  
            # This is what the system actually had (if we assume curr_progress_cp + undermining logic)
            last_cycle_cp_actual = curr_progress_cp + undermining
            
            # Use the ACTUAL last cycle CP for decay analysis
            # Apply forward formula: current_inf = coefficient × last_inf + constant
            expected_undermining_decay = calculate_expected_undermining_decay(state, last_cycle_cp_actual, progress_percent)
            
            # Calculate real undermining: difference between actual and expected
            # Only meaningful for systems >25% progress (natural decay zone)
            if progress_percent > 25.0:
                real_undermining = curr_progress_cp - expected_undermining_decay
            else:
                real_undermining = 0  # No natural decay for systems ≤25%
            
            # Check for possible state change from last cycle
            # If undermining + curr_progress_cp exceeds the max CP for current state,
            # the system was likely in a higher state last cycle
            formula = FORMULAS.get(state, {"cp_100_percent": 0})
            cp_max_current = formula["cp_100_percent"]
            possible_state_change = (undermining + curr_progress_cp) > cp_max_current
            
            # Calculate NET value: reinforcement - undermining 
            # Negative = more undermining than reinforcement (bad)
            # Positive = more reinforcement than undermining (good)
            net_activity = reinforcement - real_undermining
            
            return {
                "system": system_name,
                "state": state,
                "undermining": undermining,
                "real_reinforcement": reinforcement,
                "curr_progress": progress_percent,
                "curr_progress_cp": curr_progress_cp,
                "last_cycle_cp_formula": last_cycle_cp_formula,
                "last_cycle_cp_actual": last_cycle_cp_actual,
                "expected_undermining_decay": expected_undermining_decay,
                "real_undermining": real_undermining,
                "net_activity": net_activity,
                "possible_state_change": possible_state_change,
                "extracted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting system data: {e}")
            return None

def parse_html_file(file_path: str) -> list:
    """
    Parse HTML file and extract system data
    
    Args:
        file_path: Path to HTML file
        
    Returns:
        list: List of system dictionaries
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = InaraHTMLParser()
        parser.feed(content)
        return parser.systems
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def extract_state_from_text(text: str) -> str:
    """Extract state from text"""
    text_lower = text.lower()
    if 'stronghold' in text_lower:
        return 'Stronghold'
    elif 'fortified' in text_lower:
        return 'Fortified'
    elif 'exploited' in text_lower:
        return 'Exploited'
    return 'Unknown'

def save_systems_by_state(systems: list, output_dir: str = "json"):
    """
    Save systems grouped by state to separate JSON files
    
    Args:
        systems: List of system dictionaries
        output_dir: Output directory for JSON files
    """
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
            "extracted_at": datetime.now().isoformat(),
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
