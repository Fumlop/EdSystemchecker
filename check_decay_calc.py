#!/usr/bin/env python3
"""
Manual verification of natural decay calculations
"""

def calculate_natural_decay(state: str, current_progress_cp: int, undermining: int, reinforcement: int) -> float:
    """Calculate natural decay using the current formula"""
    before = (current_progress_cp + undermining - reinforcement) 
    if state == "Exploited":
        current_cp_normiert = before / 350000
        return (0.965505 * current_cp_normiert + 0.009839)
    return 0

# System 1: Lyncis Sector VE-Q b5-1
print("=== Lyncis Sector VE-Q b5-1 ===")
current_progress_cp = 283150
undermining = 13841
reinforcement = 43384
last_cycle_percent = 84.9

before = current_progress_cp + undermining - reinforcement
print(f"Current Progress CP: {current_progress_cp:,}")
print(f"Undermining: {undermining:,}")
print(f"Reinforcement: {reinforcement:,}")
print(f"Before (CP + U - R): {before:,}")

current_cp_normiert = before / 350000
natural_decay = 0.965505 * current_cp_normiert + 0.009839
print(f"Normalized: {current_cp_normiert:.6f}")
print(f"Natural Decay: {natural_decay:.6f} ({natural_decay*100:.2f}%)")

# System 2: Ogondage
print("\n=== Ogondage ===")
current_progress_cp = 284200
undermining = 17875
reinforcement = 0
last_cycle_percent = 86.3

before = current_progress_cp + undermining - reinforcement
print(f"Current Progress CP: {current_progress_cp:,}")
print(f"Undermining: {undermining:,}")
print(f"Reinforcement: {reinforcement:,}")
print(f"Before (CP + U - R): {before:,}")

current_cp_normiert = before / 350000
natural_decay = 0.965505 * current_cp_normiert + 0.009839
print(f"Normalized: {current_cp_normiert:.6f}")
print(f"Natural Decay: {natural_decay:.6f} ({natural_decay*100:.2f}%)")

print("\n=== Comparison ===")
print("Lyncis: Last Cycle 84.9%, Natural Decay 71.00%")
print("Ogondage: Last Cycle 86.3%, Natural Decay 84.00%")
print("\nNote: Lyncis has high reinforcement (43,384) which reduces the 'before' value")
print("      Ogondage has no reinforcement, so full undermining effect")
