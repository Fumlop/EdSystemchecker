import json

with open('json/stronghold_systems.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

systems_with_net_cp = [s for s in data['systems'] if 'net_cp' in s]
print(f'Total strongholds: {len(data["systems"])}')
print(f'Systems with net_cp: {len(systems_with_net_cp)}')

positive_net_cp = [s for s in systems_with_net_cp if s['net_cp'] > 0]
negative_net_cp = [s for s in systems_with_net_cp if s['net_cp'] < 0]

print(f'Positive net_cp: {len(positive_net_cp)}')
print(f'Negative net_cp: {len(negative_net_cp)}')

print("\nTop 5 Reinforcement Winning (Positive Net CP):")
for s in sorted(positive_net_cp, key=lambda x: x['net_cp'], reverse=True)[:5]:
    print(f"  {s['system']}: +{s['net_cp']} CP (U:{s['undermining']:,}, R:{s['reinforcement']:,})")

print("\nTop 5 Undermining Winning (Most Negative Net CP):")
for s in sorted(negative_net_cp, key=lambda x: x['net_cp'])[:5]:
    print(f"  {s['system']}: {s['net_cp']} CP (U:{s['undermining']:,}, R:{s['reinforcement']:,})")
