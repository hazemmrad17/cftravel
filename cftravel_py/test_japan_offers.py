#!/usr/bin/env python3
"""
Test script to verify Japan offers are working correctly
"""

import sys
import os
sys.path.append('.')

def test_japan_offers():
    """Test Japan offer matching"""
    print("🧪 Testing Japan Offers")
    print("=" * 50)
    
    try:
        from services.data_service import DataService
        from services.offer_service import OfferService
        
        # Initialize services
        ds = DataService()
        os = OfferService(ds)
        
        print("✅ Services initialized successfully")
        
        # Test with Japan preferences
        test_preferences = {
            "destination": "japan",
            "duration": "14",
            "travel_style": "cultural",
            "budget": "medium",
            "travelers": "2"
        }
        
        print(f"🔍 Testing with preferences: {test_preferences}")
        
        # Get offers
        offers = os.match_offers(test_preferences, max_offers=3)
        
        print(f"✅ Found {len(offers)} matching offers")
        
        if offers:
            print("\n📋 Japan offers found:")
            for i, offer in enumerate(offers):
                print(f"   {i+1}. {offer.product_name}")
                print(f"      Reference: {offer.reference}")
                print(f"      Duration: {offer.duration} days")
                print(f"      Match Score: {offer.match_score}")
                print(f"      AI Reasoning: {offer.ai_reasoning}")
                print(f"      Why Perfect: {offer.why_perfect}")
                print()
        else:
            print("❌ No Japan offers found!")
            
            # Let's check what destinations are available
            print("\n🔍 Checking available destinations...")
            all_offers = ds.get_offers()
            destinations = set()
            for offer in all_offers[:20]:  # Check first 20 offers
                for dest in offer.get('destinations', []):
                    if isinstance(dest, dict):
                        destinations.add(dest.get('country', ''))
            
            print(f"Available countries: {list(destinations)}")
            
            # Check for Japan offers specifically
            japan_offers = []
            for offer in all_offers:
                for dest in offer.get('destinations', []):
                    if isinstance(dest, dict) and 'JP' in str(dest.get('country', '')):
                        japan_offers.append(offer)
                        break
            
            print(f"Japan offers in catalog: {len(japan_offers)}")
            if japan_offers:
                print("Sample Japan offers:")
                for i, offer in enumerate(japan_offers[:3]):
                    print(f"   {i+1}. {offer.get('product_name', 'N/A')}")
                    print(f"      Destinations: {offer.get('destinations', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Japan offers: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Japan Offers Test")
    print("=" * 50)
    
    if test_japan_offers():
        print("\n" + "=" * 50)
        print("🎉 Japan offers test completed!")
    else:
        print("\n❌ Japan offers test failed!")
        sys.exit(1) 