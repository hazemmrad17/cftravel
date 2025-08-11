#!/usr/bin/env python3
"""
Final test to verify Japan offers are working correctly
"""

import sys
import os
sys.path.append('.')

def test_japan_final():
    """Test Japan offer matching with the updated OfferService"""
    print("🧪 Final Japan Offers Test")
    print("=" * 50)
    
    try:
        from services.data_service import DataService
        from services.offer_service import OfferService
        
        # Initialize services
        ds = DataService()
        os = OfferService(ds)
        
        print("✅ Services initialized successfully")
        
        # Test with Japan preferences (like the user's conversation)
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
                
            # Check if these are actually Japan offers
            japan_count = 0
            for offer in offers:
                if any('JP' in str(dest.get('country', '')) for dest in offer.destinations):
                    japan_count += 1
            
            print(f"🎯 {japan_count}/{len(offers)} offers are actually Japan offers")
            
            if japan_count == len(offers):
                print("✅ SUCCESS: All offers are Japan offers!")
                return True
            else:
                print("❌ ERROR: Not all offers are Japan offers!")
                return False
        else:
            print("❌ No offers found!")
            return False
        
    except Exception as e:
        print(f"❌ Error testing Japan offers: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Final Japan Offers Test")
    print("=" * 50)
    
    if test_japan_final():
        print("\n" + "=" * 50)
        print("🎉 Japan offers are working correctly!")
        print("💡 The AI agent should now show actual Japan offers from the catalog.")
    else:
        print("\n❌ Japan offers test failed!")
        sys.exit(1) 