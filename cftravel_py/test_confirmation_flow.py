#!/usr/bin/env python3
"""
Test script for the confirmation flow functionality
"""

import requests
import json

# Test configuration
API_BASE_URL = "http://localhost:8001"

def test_confirmation_flow():
    """Test the complete confirmation flow"""
    
    print("🧪 Testing Confirmation Flow")
    print("=" * 50)
    
    # Test 1: Send a message that should trigger confirmation
    print("\n1. Testing message that should trigger confirmation...")
    
    test_message = "I want to go to Jordan for 10 days with a cultural experience and medium budget for 2 people"
    
    response = requests.post(f"{API_BASE_URL}/chat", json={
        "message": test_message,
        "conversation_id": "test_conv_001"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response received: {data['status']}")
        
        if data.get('needs_confirmation'):
            print(f"✅ Confirmation needed: {data.get('confirmation_summary')}")
            print(f"✅ Preferences: {data.get('conversation_state', {}).get('user_preferences', {})}")
        else:
            print("⚠️ No confirmation needed")
            
        print(f"✅ Response: {data.get('response', '')[:100]}...")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # Test 2: Test confirmation endpoint
    print("\n2. Testing confirmation endpoint...")
    
    test_preferences = {
        "destination": "amm",
        "duration": "10",
        "travel_style": "cultural",
        "budget": "medium",
        "travelers": "2"
    }
    
    # Test confirm action
    confirm_response = requests.post(f"{API_BASE_URL}/confirmation", json={
        "preferences": test_preferences,
        "conversation_id": "test_conv_001",
        "action": "confirm"
    })
    
    if confirm_response.status_code == 200:
        confirm_data = confirm_response.json()
        print(f"✅ Confirm response: {confirm_data['status']}")
        print(f"✅ Message: {confirm_data['message']}")
        if confirm_data.get('offers'):
            print(f"✅ Offers received: {len(confirm_data['offers'])} offers")
            for i, offer in enumerate(confirm_data['offers'][:2]):  # Show first 2 offers
                print(f"   {i+1}. {offer.get('product_name', 'N/A')}")
                print(f"      Match Score: {offer.get('match_score', 'N/A')}")
        else:
            print("⚠️ No offers received")
    else:
        print(f"❌ Confirm error: {confirm_response.status_code} - {confirm_response.text}")
    
    # Test modify action
    modify_response = requests.post(f"{API_BASE_URL}/confirmation", json={
        "preferences": test_preferences,
        "conversation_id": "test_conv_001",
        "action": "modify"
    })
    
    if modify_response.status_code == 200:
        modify_data = modify_response.json()
        print(f"✅ Modify response: {modify_data['status']}")
        print(f"✅ Message: {modify_data['message']}")
    else:
        print(f"❌ Modify error: {modify_response.status_code} - {modify_response.text}")
    
    print("\n" + "=" * 50)
    print("✅ Confirmation flow test completed!")

def test_health_check():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running on port 8001")
        return False

if __name__ == "__main__":
    print("🚀 Starting Confirmation Flow Tests")
    print("=" * 50)
    
    # First check if API is running
    if test_health_check():
        test_confirmation_flow()
    else:
        print("\n❌ Please start the API server first:")
        print("   cd cftravel_py")
        print("   python -m api.server") 