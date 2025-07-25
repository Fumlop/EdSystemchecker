##Generel
last_cycle_cp_actual = curr_progress_cp + undermining - reinforcement

##Stronghold:
current_progress_cp = 1000000 * progress_percent
decay = 1 000 000 × (–0.2087 × last_cycle_cp_actual + 0.0527)
##Fortified:
current_progress_cp = 650000 * progress_percent
decay = 650 000 × (–0.1707 × last_cycle_cp_actual + 0.0425)

##Exploited:
current_progress_cp = 350000 * progress_percent
decay = 350 000 × (–0.0833 × last_cycle_cp_actual + 0.0207)

