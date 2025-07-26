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

def get_max_cp(state: str) -> int:
    """
    Get maximum CP for a system state
    
    Args:
        state: System state (Stronghold, Fortified, Exploited)
        
    Returns:
        int: Maximum CP for the state
    """
    if state == "Stronghold":
        return 1000000
    elif state == "Fortified":
        return 650000
    elif state == "Exploited":
        return 350000
    else:
        return 1

def calculate_last_cycle_percent(last_cycle_cp_actual: int, state: str) -> float:
    """
    Calculate last cycle percentage from last_cycle_cp_actual
    
    Args:
        last_cycle_cp_actual: Last cycle CP actual value
        state: System state (Stronghold, Fortified, Exploited)
        
    Returns:
        float: Last cycle percentage (0-100)
    """
    max_cp = get_max_cp(state)
    return round((last_cycle_cp_actual / max_cp) * 100.0, 1)

def calculate_natural_decay(state: str, current_progress_cp: int, undermining: int, reinforcement: int) -> float:
    """
    Calculate natural decay using formulas from Formulas.md
    
    Args:
        state: System state (Stronghold, Fortified, Exploited)
        current_progress_cp: Current progress CP value
        undermining: Undermining value (not used in calculation, kept for compatibility)
        
    Returns:
        float: Natural decay amount as decimal (0.25 = 25%), minimum 0.25
    """
    before = (current_progress_cp + undermining - reinforcement) 
    if state == "Stronghold":
        current_cp_normiert = before/ 1000000
        decay = (0.799384 * current_cp_normiert + 0.049691)
    elif state == "Fortified":
        current_cp_normiert = before / 650000
        decay = (0.827635  * current_cp_normiert + 0.04388)
    elif state == "Exploited":
        current_cp_normiert = before / 350000
        decay = (0.922557 * current_cp_normiert + 0.018819)
    else:
        decay = 0.25
    
    # Ensure natural decay never goes below 25%
    return max(decay, 0.25)

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
            # Calculate last cycle percentage
            last_cycle_percent = calculate_last_cycle_percent(last_cycle_cp_actual, state)
            
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
                "last_cycle_percent": last_cycle_percent,
                "extracted_at": extracted_at,
                "current_cycle_refresh": is_current_powerplay_cycle(extracted_at)
            }
            
            # Add natural_decay, expected_progress_cp and net_cp calculations
            # Calculate decay for systems that were above 25% last cycle OR are currently >= 25%
            if progress_percent >= 25.0 or last_cycle_percent >= 25.0:
                natural_decay = calculate_natural_decay(state, current_progress_cp,undermining, reinforcement)
                if (state == "Stronghold"):
                    expected_progress_cp = int(round(1000000 * natural_decay))
                if (state == "Fortified"):
                    expected_progress_cp = int(round(650000 * natural_decay))
                if (state == "Exploited"):
                    expected_progress_cp = int(round(350000 * natural_decay))
                net_cp = int(round(current_progress_cp - expected_progress_cp ))
                system_data["natural_decay"] = round(natural_decay * 100, 2)  # Store as percentage
                system_data["expected_progress_cp"] = expected_progress_cp
                system_data["net_cp"] = net_cp
            
            return system_data
            
        except Exception as e:
            print(f"Error extracting system data: {e}")
            return None

class InaraContestedHTMLParser(HTMLParser):
    """Custom HTML parser for Inara contested system data"""
    
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
            if len(self.current_row) >= 4:  # Process rows with enough data
                system_data = self.extract_contested_system_from_row(self.current_row)
                if system_data:
                    self.systems.append(system_data)
        elif tag in ['td', 'th'] and self.in_cell:
            self.in_cell = False
            self.current_row.append(self.current_cell.strip())
    
    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data
    
    def extract_contested_system_from_row(self, cells):
        """Extract contested system data from table row cells"""
        try:
            if not cells or len(cells) < 4:  # Need at least 4 columns
                return None
            
            # Skip header rows
            if cells[0].lower().strip() in ['star system', '']:
                return None
            
            # Extract system name (remove HTML tags and extra text)
            system_name = cells[0]
            
            # Remove common HTML artifacts
            if 'staricon' in system_name:
                # Extract system name after staricon
                parts = system_name.split('staricon')
                if len(parts) > 1:
                    system_name = parts[1].split('Copied!')[0].strip()
                    # Remove remaining HTML artifacts
                    system_name = system_name.replace('>', '').replace('<', '').strip()
            
            # Simple fix: remove the last character (usually a Unicode artifact)
            if system_name:
                # Remove multiple possible Unicode artifacts from the end
                import re
                system_name = re.sub(r'[\ue81d︎\u200b\u200c\u200d\ufeff]+$', '', system_name).strip()
            
            if "102" in system_name:
                print(f"DEBUG: Cleaned system name: '{system_name}'")
            
            # Extract state (Contested, Expansion, etc.)
            state = cells[1].replace('Contested', 'Contested')
            contested = 'Contested' in state
            
            # Extract opposing powers (can be multiple)
            opposing_powers = []
            opposing_text = cells[2]
            if opposing_text and opposing_text.strip():
                # Parse multiple powers with percentages
                # Format: "PowerName 1.5% PowerName2 0.0%"
                # Split by power class identifiers or common patterns
                import re
                power_pattern = r'([^<>]+?)(\d+\.\d+)%'
                matches = re.findall(power_pattern, opposing_text)
                for match in matches:
                    power_name = match[0].strip()
                    power_percentage = float(match[1])
                    # Clean up power name
                    power_name = re.sub(r'[<>\/]', '', power_name).strip()
                    if power_name and not any(x in power_name.lower() for x in ['class', 'href', 'span']):
                        opposing_powers.append({
                            'name': power_name,
                            'progress_percent': power_percentage
                        })
            
            # Extract progress percentage
            progress_text = cells[3].replace('%', '').strip()
            try:
                progress_percent = float(progress_text) if progress_text and progress_text != '-' else 0.0
            except ValueError:
                progress_percent = 0.0
            
            # Skip rows with invalid data
            if not system_name or system_name.lower() in ['star system', '']:
                return None
            
            extracted_at = datetime.now().isoformat()
            
            system_data = {
                "system": system_name,
                "contested": contested,
                "state": state,
                "opposing_powers": opposing_powers,
                "progress_percent": progress_percent,
                "extracted_at": extracted_at,
                "current_cycle_refresh": is_current_powerplay_cycle(extracted_at)
            }
            
            return system_data
            
        except Exception as e:
            print(f"Error extracting contested system data: {e}")
            return None

def parse_html_file(file_path: str) -> list:
    """Parse HTML file and extract system data"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use contested parser for contested systems file
        if 'contested' in file_path.lower():
            parser = InaraContestedHTMLParser()
        else:
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
        
        print(f"* Saved {len(state_systems)} {state} systems to {output_path}")

def main():
    """Main extraction function"""
    html_dir = Path("html")
    
    if not html_dir.exists():
        print("ERROR: HTML directory not found. Run download.py first!")
        return
    
    print(f"Starting extraction at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    all_systems = []
    contested_systems = []
    
    # Process HTML files
    html_files = list(html_dir.glob("*.html"))
    
    if not html_files:
        print("ERROR: No HTML files found in html/ directory")
        return
    
    for html_file in html_files:
        print(f"Processing: {html_file}")
        systems = parse_html_file(str(html_file))
        
        # Separate contested systems from regular systems
        if 'contested' in html_file.name.lower():
            contested_systems.extend(systems)
            print(f"  > Extracted {len(systems)} contested systems")
        else:
            all_systems.extend(systems)
            print(f"  > Extracted {len(systems)} systems")
    
    print("-" * 60)
    print(f"Total regular systems extracted: {len(all_systems)}")
    print(f"Total contested systems extracted: {len(contested_systems)}")
    
    # Save regular systems grouped by state
    if all_systems:
        save_systems_by_state(all_systems)
        
        # Print summary by state
        states = {}
        for system in all_systems:
            state = system.get('state', 'Unknown')
            states[state] = states.get(state, 0) + 1
        
        print("\nRegular systems summary by state:")
        for state, count in sorted(states.items()):
            print(f"  {state}: {count} systems")
    
    # Save contested systems
    if contested_systems:
        json_dir = Path("json")
        json_dir.mkdir(exist_ok=True)
        
        output_path = json_dir / "contested_systems.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(contested_systems, f, indent=2, ensure_ascii=False)
        
        print(f"\n* Saved {len(contested_systems)} contested systems to {output_path}")
        
        # Print contested systems summary
        contested_states = {}
        for system in contested_systems:
            state = system.get('state', 'Unknown')
            contested_states[state] = contested_states.get(state, 0) + 1
        
        print("\nContested systems summary by state:")
        for state, count in sorted(contested_states.items()):
            print(f"  {state}: {count} systems")
    
    if all_systems or contested_systems:
        print(f"\nSUCCESS: Extraction complete! JSON files saved in /json/")
    else:
        print("WARNING: No systems extracted. Check HTML file structure.")

if __name__ == "__main__":
    main()
