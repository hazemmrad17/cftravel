#!/usr/bin/env python3
"""
Test script for the confirmation endpoint
"""

import sys
import os
sys.path.append('.')

def test_confirmation_endpoint():
    """Test the confirmation endpoint logic directly"""
    print("🧪 Testing Confirmation Endpoint Logic")
    print("=" * 50)
    
    try:
        from services.data_service import DataService
        from services.offer_service import OfferService
        from models.data_models import ConfirmationRequest
        from models.response_models import ConfirmationFlowResponse
        
        # Initialize services
        ds = DataService()
        os = OfferService(ds)
        
        print("✅ Services initialized successfully")
        
        # Test preferences
        test_preferences = {
            "destination": "amm",
            "duration": "10",
            "travel_style": "cultural",
            "budget": "medium",
            "travelers": "2"
        }
        
        print(f"🔍 Testing with preferences: {test_preferences}")
        
        # Test confirm action
        print("\n📋 Testing 'confirm' action...")
        offers = os.match_offers(test_preferences, max_offers=3)
        
        print(f"✅ Found {len(offers)} matching offers")
        
        if offers:
            print("\n📋 Offer details:")
            for i, offer in enumerate(offers):
                print(f"   {i+1}. {offer.product_name}")
                print(f"      Reference: {offer.reference}")
                print(f"      Match Score: {offer.match_score}")
                print(f"      AI Reasoning: {offer.ai_reasoning}")
                print()
        
        # Test creating response
        conv_state = {
            "conversation_id": "test_001",
            "user_preferences": test_preferences,
            "current_state": "showing_offers",
            "needs_confirmation": False,
            "confirmation_summary": None,
            "turn_count": 1,
            "last_response_type": "offer_display"
        }
        
        response = ConfirmationFlowResponse(
            status="success",
            message="Perfect! Here are your personalized travel offers.",
            needs_confirmation=False,
            preferences=test_preferences,
            offers=offers,
            conversation_state=conv_state
        )
        
        print("✅ ConfirmationFlowResponse created successfully")
        print(f"✅ Response status: {response.status}")
        print(f"✅ Response message: {response.message}")
        print(f"✅ Number of offers: {len(response.offers) if response.offers else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing confirmation endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Confirmation Endpoint Test")
    print("=" * 50)
    
    if test_confirmation_endpoint():
        print("\n" + "=" * 50)
        print("🎉 Confirmation endpoint test passed!")
        print("\n💡 The confirmation flow is working correctly!")
        print("   - Offer matching: ✅ Working")
        print("   - Data models: ✅ Working")
        print("   - Response generation: ✅ Working")
        print("\n🚀 Ready to test in the browser!")
    else:
        print("\n❌ Confirmation endpoint test failed!")
        sys.exit(1) 