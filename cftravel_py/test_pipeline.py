#!/usr/bin/env python3
"""
Test the full pipeline with Tokyo input
"""
import sys
import os
sys.path.append('.')

try:
    from pipelines.concrete_pipeline import IntelligentPipeline
    
    # Initialize pipeline
    pipeline = IntelligentPipeline()
    
    # Test with Tokyo input
    test_input = "i'm looking to go to tokyo for night life"
    
    print(f"Testing input: '{test_input}'")
    print("=" * 50)
    
    # Process the input
    result = pipeline.process_user_input(test_input)
    
    print("Pipeline result:")
    print(f"Response: {result.get('response', 'N/A')}")
    print(f"Needs confirmation: {result.get('needs_confirmation', False)}")
    print(f"Confirmation summary: {result.get('confirmation_summary', 'N/A')}")
    print(f"Offers count: {len(result.get('offers', []))}")
    
    # Check preferences
    preferences = pipeline.get_preferences()
    print(f"\nExtracted preferences: {preferences}")
    
    # Check conversation state
    state = result.get('conversation_state', {})
    print(f"Current state: {state.get('current_state', 'N/A')}")
    print(f"User preferences: {state.get('user_preferences', {})}")
    
    if result.get('offers'):
        print(f"\nFound {len(result['offers'])} offers:")
        for i, offer in enumerate(result['offers']):
            print(f"  {i+1}. {offer.product_name}")
            print(f"     Reference: {offer.reference}")
            print(f"     Match Score: {offer.match_score}")
            print()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 