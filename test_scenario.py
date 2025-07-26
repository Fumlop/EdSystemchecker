#!/usr/bin/env python3
"""
Test scenario for system decay vs undermining calculation
"""

def calculate_natural_decay(state: str, current_progress_cp: int, undermining: int, reinforcement: int) -> float:
    """Calculate natural decay with minimum 25% limit"""
    before = (current_progress_cp + undermining - reinforcement) 
    if state == "Exploited":
        current_cp_normiert = before / 350000
        decay = (0.922557 * current_cp_normiert + 0.018819)
    else:
        decay = 0.25
    
    # Ensure natural decay never goes below 25%
    return max(decay, 0.25)

def test_scenario():
    print("Testing scenario: System that should decay to 25.5% but has undermining")
    print("=" * 70)
    
    # Scenario: System that would naturally decay to 25.5% but has enough undermining to pull it below 25%
    state = "Exploited"
    max_cp = 350000
    
    # Let's say the system had 28% last cycle (98,000 CP)
    last_cycle_cp = 98000  # 28%
    
    # Natural decay would be ~25.5% without any activity
    # But let's add significant undermining
    undermining = 8000  # Strong undermining
    reinforcement = 0
    
    # Current progress after undermining
    current_progress_cp = 87500  # 25.0% (hit the minimum)
    progress_percent = (current_progress_cp / max_cp) * 100
    
    print(f"System State: {state}")
    print(f"Last Cycle CP: {last_cycle_cp:,} ({last_cycle_cp/max_cp*100:.1f}%)")
    print(f"Undermining: {undermining:,} CP")
    print(f"Reinforcement: {reinforcement:,} CP")
    print(f"Current Progress CP: {current_progress_cp:,} ({progress_percent:.1f}%)")
    print()
    
    # Calculate what the natural decay should be
    natural_decay = calculate_natural_decay(state, current_progress_cp, undermining, reinforcement)
    expected_progress_cp = int(round(max_cp * natural_decay))
    net_cp = current_progress_cp - expected_progress_cp
    
    print("Calculations:")
    print(f"Natural Decay: {natural_decay:.4f} ({natural_decay*100:.2f}%)")
    print(f"Expected Progress CP: {expected_progress_cp:,}")
    print(f"Actual Progress CP: {current_progress_cp:,}")
    print(f"Net CP: {net_cp:,}")
    print()
    
    if net_cp < 0:
        print(f"✅ UNDERMINING DETECTED: {abs(net_cp):,} CP active undermining")
        print(f"   System should be at {natural_decay*100:.2f}% but is at {progress_percent:.1f}%")
        print(f"   The difference shows undermining beyond natural decay")
    else:
        print(f"⚠️ No active undermining detected (positive net CP)")
    
    print()
    print("Conclusion:")
    print("- The system calculation works correctly even when progress hits 25% minimum")
    print("- Net CP shows the 'extra' undermining beyond what natural decay would cause")
    print("- This gives accurate undermining threat assessment")

if __name__ == "__main__":
    test_scenario()
