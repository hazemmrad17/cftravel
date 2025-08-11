#!/usr/bin/env python3
"""
Simple test to debug offer matching
"""
import json

# Load data
with open('data/asia/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total offers: {len(data)}")

# Check first few offers
print("\nFirst 3 offers:")
for i, offer in enumerate(data[:3]):
    print(f"{i+1}. {offer.get('product_name', 'N/A')}")
    print(f"   Destinations: {offer.get('destinations', [])}")
    print(f"   Duration: {offer.get('duration', 'N/A')}")
    print()

# Check Japan offers
print("\nJapan offers:")
japan_count = 0
for offer in data:
    for dest in offer.get('destinations', []):
        if isinstance(dest, dict) and dest.get('country') == 'JP':
            japan_count += 1
            if japan_count <= 3:
                print(f"{japan_count}. {offer.get('product_name', 'N/A')}")
                print(f"   Destinations: {offer.get('destinations', [])}")
                print(f"   Duration: {offer.get('duration', 'N/A')}")
                print()
            break

print(f"Total Japan offers: {japan_count}")

# Test OfferService with Japan
print("\nTesting OfferService with Japan:")
try:
    from services.data_service import DataService
    from services.offer_service import OfferService
    
    ds = DataService()
    os = OfferService(ds)
    
    # Test with Japan preferences
    test_preferences = {
        "destination": "Japan",
        "style": "cultural",
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