#!/usr/bin/env python3
import json

# Load data
with open('data/asia/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find Japan offers
japan_offers = []
for offer in data:
    for dest in offer.get('destinations', []):
        if isinstance(dest, dict) and 'JP' in str(dest.get('country', '')):
            japan_offers.append(offer)
            break

print(f"Japan offers found: {len(japan_offers)}")
print("=" * 50)

for i, offer in enumerate(japan_offers[:5]):
    print(f"{i+1}. {offer.get('product_name', 'N/A')}")
    print(f"   Duration: {offer.get('duration', 'N/A')} days")
    print(f"   Destinations: {offer.get('destinations', [])}")
    print(f"   Reference: {offer.get('reference', 'N/A')}")
    print() 