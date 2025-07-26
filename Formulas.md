##Generel
last_cycle_cp_actual = curr_progress_cp + undermining - reinforcement

##Stronghold:
current_progress_cp = 1000000 * progress_percent
decay = (0.799384 * current_cp_normiert + 0.049691)
##Fortified:
current_progress_cp = 650000 * progress_percent
decay = (0.827635  * current_cp_normiert + 0.04388)

##Exploited:
current_progress_cp = 350000 * progress_percent
decay = (0.922557 * current_cp_normiert + 0.018819)
