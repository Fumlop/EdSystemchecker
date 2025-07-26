import json

with open('json/stronghold_systems.json', 'r') as f:
    data = json.load(f)

undermining_systems = [s for s in data['systems'] if s.get('net_cp', 0) < 0]
print(f'Total undermining systems: {len(undermining_systems)}')

print("\nAll undermining systems by CP level:")
for system in sorted(undermining_systems, key=lambda x: x['undermining'], reverse=True):
    u = system['undermining']
    category = "High" if u >= 1000 else "Medium" if u >= 500 else "Low" if u >= 100 else "Very Low"
    print(f'{system["system"]}: {u:,} CP undermining ({category})')
