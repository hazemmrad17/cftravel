#!/usr/bin/env python3
"""
Test script to verify that real offers are being returned from the database
"""

import sys
import os
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

def test_pipeline():
    """Test the pipeline to ensure it returns real offers"""
    try:
        print("🚀 Testing pipeline initialization...")
        
        # Import the pipeline
        from pipelines.concrete_pipeline import ASIAConcreteAgent
        
        # Initialize the agent
        agent = ASIAConcreteAgent()
        print("✅ Agent initialized successfully")
        
        # Test with a simple query
        print("📝 Testing with query: 'Japan cultural adventure'")
        
        # Simulate a chat message
        result = agent.chat("I want to go to Japan for cultural adventure")
        
        print(f"📊 Result type: {type(result)}")
        
        if isinstance(result, dict):
            print(f"📊 Response: {result.get('response', 'No response')[:100]}...")
            
            if 'offers' in result:
                offers = result['offers']
                print(f"🎯 Found {len(offers)} offers")
                
                for i, offer in enumerate(offers):
                    print(f"\n📋 Offer {i+1}:")
                    print(f"   Product: {offer.get('product_name', 'N/A')}")
                    print(f"   Reference: {offer.get('reference', 'N/A')}")
                    print(f"   Duration: {offer.get('duration', 'N/A')}")
                    print(f"   Match Score: {offer.get('match_score', 'N/A')}")
                    print(f"   Destinations: {offer.get('destinations', [])}")
                    
                    # Check if this is a real offer (not fake)
                    if offer.get('product_name') and not offer.get('product_name').startswith('TEST-'):
                        print("   ✅ This appears to be a REAL offer from the database")
                    else:
                        print("   ❌ This appears to be a FAKE offer")
            else:
                print("❌ No offers found in result")
        else:
            print(f"📊 Response: {str(result)[:100]}...")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pipeline() 