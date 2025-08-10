#!/usr/bin/env python3
"""
Test script for offer detection and structured offer creation
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from concrete_pipeline import LaylaConcreteAgent

def test_offer_detection():
    """Test the offer detection functionality"""
    print("🧪 Testing offer detection...")
    
    # Initialize agent
    agent = LaylaConcreteAgent()
    
    # Test cases
    test_cases = [
        ("I want to go to Japan", False),
        ("yes", True),
        ("looks good", True),
        ("show me offers", True),
        ("perfect", True),
        ("what do you suggest", True),
        ("tell me more", True),
        ("show me the details", True),
    ]
    
    for user_input, expected in test_cases:
        result = agent._should_show_offers(user_input, "")
        status = "✅" if result == expected else "❌"
        print(f"{status} '{user_input}' -> {result} (expected: {expected})")
    
    print("\n🎯 Testing structured offer creation...")
    
    # Test preferences
    test_preferences = {
        "destination": "Japan",
        "duration": "14 days",
        "budget": "medium"
    }
    
    # Set preferences
    agent.user_preferences = test_preferences
    
    # Create structured offers
    structured_offers = agent._create_structured_offers(test_preferences, max_offers=3)
    
    print(f"📊 Created {len(structured_offers)} structured offers")
    
    for i, offer in enumerate(structured_offers, 1):
        print(f"\n📋 Offer {i}:")
        print(f"   Name: {offer['product_name']}")
        print(f"   Reference: {offer['reference']}")
        print(f"   Duration: {offer['duration']} days")
        print(f"   Type: {offer['offer_type']}")
        print(f"   Destinations: {len(offer['destinations'])} destinations")
        print(f"   Highlights: {len(offer['highlights'])} highlights")
    
    print("\n✅ Offer detection and creation test completed!")

if __name__ == "__main__":
    test_offer_detection() 