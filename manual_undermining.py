#!/usr/bin/env python3
"""
Manual undermining data for systems where HTML extraction fails
"""

# Manual undermining data in CP
MANUAL_UNDERMINING = {
    "LHS 317": 21986,
    "Dazbog": 12286,  # Add other known values here
    "LP 726-6": 0,    # Add as needed
    "Andel": 0,
    "Orishpucho": 0
}

def get_undermining_cp(system_name: str, extracted_undermining: int = 0) -> int:
    """
    Get undermining CP for a system, preferring manual data over extracted
    
    Args:
        system_name: Name of the system
        extracted_undermining: Undermining value extracted from HTML
        
    Returns:
        int: Undermining CP value
    """
    # Use manual data if available
    if system_name in MANUAL_UNDERMINING:
        return MANUAL_UNDERMINING[system_name]
    
    # Otherwise use extracted value
    return extracted_undermining
