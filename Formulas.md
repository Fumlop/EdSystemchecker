##Generel
last_cycle_cp_actual = curr_progress_cp + undermining - reinforcement
current_cp_normiert = last_cycle_cp_actual / maxCP

##Stronghold:
maxCP = 1000000
current_progress_cp = maxCP * progress_percent
decay = (0.799384 * current_cp_normiert + 0.049691)
##Fortified:
maxCP = 650000
current_progress_cp = maxCP * progress_percent
decay = (0.827635  * current_cp_normiert + 0.04388)

##Exploited:
maxCP = 350000
current_progress_cp = maxCP * progress_percent
decay = (0.922557 * current_cp_normiert + 0.018819)
