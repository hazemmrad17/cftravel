#!/usr/bin/env python3
"""
Simple test script to verify the confirmation flow components work
"""

import sys
import os
sys.path.append('.')

def test_offer_service():
    """Test the offer service directly"""
    print("🧪 Testing Offer Service")
    print("=" * 50)
    
    try:
        from services.data_service import DataService
        from services.offer_service import OfferService
        
        # Initialize services
        ds = DataService()
        os = OfferService(ds)
        
        print("✅ Services initialized successfully")
        
        # Test with a real destination from the data
        test_preferences = {
            "destination": "amm",
            "duration": "10",
            "travel_style": "cultural",
            "budget": "medium",
            "travelers": "2"
        }
        
        print(f"🔍 Testing with preferences: {test_preferences}")
        
        # Get offers
        offers = os.match_offers(test_preferences, max_offers=3)
        
        print(f"✅ Found {len(offers)} matching offers")
        
        if offers:
            print("\n📋 First offer details:")
            offer = offers[0]
            print(f"   Product: {offer.product_name}")
            print(f"   Reference: {offer.reference}")
            print(f"   Match Score: {offer.match_score}")
            print(f"   AI Reasoning: {offer.ai_reasoning}")
            print(f"   Why Perfect: {offer.why_perfect}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing offer service: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_structures():
    """Test data model structures"""
    print("\n🧪 Testing Data Structures")
    print("=" * 50)
    
    try:
        from models.data_models import ConfirmationRequest, ConfirmationResponse, ConversationState
        from models.response_models import ConfirmationFlowResponse
        
        # Test creating instances
        test_preferences = {
            "destination": "amm",
            "duration": "10",
            "travel_style": "cultural"
        }
        
        # Test ConfirmationRequest
        conf_request = ConfirmationRequest(
            preferences=test_preferences,
            conversation_id="test_001",
            action="confirm"
        )
        print("✅ ConfirmationRequest created successfully")
        
        # Test ConversationState
        conv_state = ConversationState(
            conversation_id="test_001",
            user_preferences=test_preferences,
            current_state="confirmation",
            needs_confirmation=True,
            confirmation_summary="Test summary",
            turn_count=1,
            last_response_type="confirmation"
        )
        print("✅ ConversationState created successfully")
        
        # Test ConfirmationResponse
        conf_response = ConfirmationResponse(
            status="success",
            message="Test message",
            preferences=test_preferences,
            needs_confirmation=False
        )
        print("✅ ConfirmationResponse created successfully")
        
        # Test ConfirmationFlowResponse
        flow_response = ConfirmationFlowResponse(
            status="success",
            message="Test message",
            needs_confirmation=False,
            preferences=test_preferences,
            conversation_state=conv_state
        )
        print("✅ ConfirmationFlowResponse created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing data structures: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Simple Tests")
    print("=" * 50)
    
    # Test data structures first
    if test_data_structures():
        print("\n✅ Data structures test passed!")
    else:
        print("\n❌ Data structures test failed!")
        sys.exit(1)
    
    # Test offer service
    if test_offer_service():
        print("\n✅ Offer service test passed!")
    else:
        print("\n❌ Offer service test failed!")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Confirmation flow components are working correctly.")
    print("\n💡 To test the full confirmation flow with the API:")
    print("   1. Start the server: python -m api.server")
    print("   2. Open your browser and go to the chat interface")
    print("   3. Try: 'I want to go to Jordan for 10 days with cultural experience'") 