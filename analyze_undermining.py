import json
import os

# Lade alle drei JSON-Dateien
files = [
    r'd:\Apps\EdSystemChecker\json\stronghold_systems.json',
    r'd:\Apps\EdSystemChecker\json\fortified_systems.json', 
    r'd:\Apps\EdSystemChecker\json\exploited_systems.json'
]

total_systems = 0
systems_with_undermining = 0
systems_with_real_undermining_positive = 0
systems_with_real_undermining_negative = 0
systems_with_real_undermining_zero = 0

for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        print(f'=== {data["state"]} ===')
        print(f'Total systems: {len(data["systems"])}')
        
        file_systems_with_undermining = 0
        file_real_undermining_positive = 0
        file_real_undermining_negative = 0
        file_real_undermining_zero = 0
        
        for system in data['systems']:
            total_systems += 1
            
            if system['undermining'] > 0:
                file_systems_with_undermining += 1
                systems_with_undermining += 1
                
            if system['real_undermining'] > 0:
                file_real_undermining_positive += 1
                systems_with_real_undermining_positive += 1
                print(f'  ECHTES UNDERMINING: {system["system"]} = {system["real_undermining"]} CP')
            elif system['real_undermining'] < 0:
                file_real_undermining_negative += 1
                systems_with_real_undermining_negative += 1
            else:
                file_real_undermining_zero += 1
                systems_with_real_undermining_zero += 1
        
        print(f'Systems with undermining: {file_systems_with_undermining}')
        print(f'Real undermining positive: {file_real_undermining_positive}')
        print(f'Real undermining negative: {file_real_undermining_negative}')
        print(f'Real undermining zero: {file_real_undermining_zero}')
        print()

print(f'=== GESAMTSTATISTIK ===')
print(f'Total systems: {total_systems}')
print(f'Systems with undermining data: {systems_with_undermining}')
print(f'Real undermining positive: {systems_with_real_undermining_positive}')
print(f'Real undermining negative: {systems_with_real_undermining_negative}')
print(f'Real undermining zero: {systems_with_real_undermining_zero}')

# Zeige ein paar Beispiele von Systemen mit negativem real_undermining
print(f'\n=== BEISPIELE NEGATIVER REAL_UNDERMINING ===')
count = 0
for file_path in files:
    if os.path.exists(file_path) and count < 5:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        for system in data['systems']:
            if system['real_undermining'] < 0 and count < 5:
                print(f'{system["system"]} ({data["state"]}):')
                print(f'  Undermining: {system["undermining"]}')
                print(f'  Progress: {system["curr_progress"]}%')
                print(f'  Expected decay: {system["expected_undermining_decay"]}')
                print(f'  Current CP: {system["curr_progress_cp"]}')
                print(f'  Real undermining: {system["real_undermining"]}')
                print()
                count += 1
