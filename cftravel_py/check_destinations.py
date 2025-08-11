#!/usr/bin/env python3
"""
Check all destinations in the data
"""
import json

# Load data
with open('data/asia/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Collect all destinations
all_destinations = set()
japan_destinations = set()

for offer in data:
    for dest in offer.get('destinations', []):
        if isinstance(dest, dict):
            city = dest.get('city', '').strip()
            country = dest.get('country', '').strip()
            if city:
                all_destinations.add(f"{city} ({country})")
                if country == 'JP':
                    japan_destinations.add(f"{city} ({country})")
            elif country:
                all_destinations.add(country)
                if country == 'JP':
                    japan_destinations.add(country)

print(f"Total unique destinations: {len(all_destinations)}")
print(f"Japan destinations: {len(japan_destinations)}")
print("=" * 50)

print("Japan destinations:")
for dest in sorted(japan_destinations):
    print(f"  - {dest}")

# Check for Tokyo specifically
print("\n" + "=" * 50)
print("Checking for Tokyo mentions:")
tokyo_count = 0
for offer in data:
    for dest in offer.get('destinations', []):
        if isinstance(dest, dict):
            city = dest.get('city', '').lower()
            if 'tokyo' in city:
                tokyo_count += 1
                print(f"  Found Tokyo in: {offer.get('product_name', 'N/A')}")
                print(f"    Destinations: {offer.get('destinations', [])}")
                print()

print(f"Total Tokyo mentions: {tokyo_count}")

# Show first few Japan offers
print("\n" + "=" * 50)
print("First 5 Japan offers:")
japan_offers = []
for offer in data:
    for dest in offer.get('destinations', []):
        if isinstance(dest, dict) and dest.get('country') == 'JP':
            japan_offers.append(offer)
            break

for i, offer in enumerate(japan_offers[:5]):
    print(f"{i+1}. {offer.get('product_name', 'N/A')}")
    print(f"   Destinations: {offer.get('destinations', [])}")
    print() 