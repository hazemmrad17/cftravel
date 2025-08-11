#!/usr/bin/env python3
"""
Debug script to test offer matching with user preferences
"""
import sys
import os
sys.path.append('cftravel_py')

try:
    from services.data_service import DataService
    from services.offer_service import OfferService
    
    # Initialize services
    ds = DataService()
    os = OfferService(ds)
    
    # Test with user's preferences
    test_preferences = {
        'destination': 'japan',
        'duration': 'two weeks',
        'style': 'city vibes',
        'budget': 'medium',
        'timing': 'implied'
    }
    
    print("Testing offer matching with preferences:")
    print(f"Preferences: {test_preferences}")
    print("=" * 50)
    
    # Get offers
    offers = os.match_offers(test_preferences, max_offers=3)
    
    print(f"Found {len(offers)} offers")
    print("=" * 50)
    
    for i, offer in enumerate(offers):
        print(f"{i+1}. {offer.product_name}")
        print(f"   Duration: {offer.duration} days")
        print(f"   Destinations: {offer.destinations}")
        print(f"   Reference: {offer.reference}")
        print(f"   Match Score: {offer.match_score}")
        print()
    
    # Also test with "city" as destination
    print("Testing with 'city' as destination:")
    test_preferences_city = {
        'destination': 'city',
        'duration': 'two weeks',
        'style': 'city vibes',
        'budget': 'medium'
    }
    
    offers_city = os.match_offers(test_preferences_city, max_offers=3)
    print(f"Found {len(offers_city)} offers with 'city' destination")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 