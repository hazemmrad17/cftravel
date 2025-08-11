#!/usr/bin/env python3
"""
Test Tokyo offers specifically
"""
import json

# Load data
with open('data/asia/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find Tokyo offers
tokyo_offers = []
for offer in data:
    for dest in offer.get('destinations', []):
        if isinstance(dest, dict):
            city = dest.get('city', '').lower()
            country = dest.get('country', '').lower()
            if 'tokyo' in city or 'tokyo' in country:
                tokyo_offers.append(offer)
                break

print(f"Tokyo offers found: {len(tokyo_offers)}")
print("=" * 50)

for i, offer in enumerate(tokyo_offers[:5]):
    print(f"{i+1}. {offer.get('product_name', 'N/A')}")
    print(f"   Duration: {offer.get('duration', 'N/A')} days")
    print(f"   Destinations: {offer.get('destinations', [])}")
    print(f"   Reference: {offer.get('reference', 'N/A')}")
    print()

# Test with OfferService
print("Testing with OfferService:")
print("=" * 50)

try:
    from services.data_service import DataService
    from services.offer_service import OfferService
    
    ds = DataService()
    os = OfferService(ds)
    
    # Test with Tokyo preferences
    test_preferences = {
        "destination": "Tokyo",
        "style": "night life",
        "duration": "14"
    }
    
    print(f"Testing with preferences: {test_preferences}")
    offers = os.match_offers(test_preferences, max_offers=3)
    print(f"Found {len(offers)} matching offers")
    
    if offers:
        for i, offer in enumerate(offers):
            print(f"   {i+1}. {offer.product_name}")
            print(f"      Reference: {offer.reference}")
            print(f"      Match Score: {offer.match_score}")
            print()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 