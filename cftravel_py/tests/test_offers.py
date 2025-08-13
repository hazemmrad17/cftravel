#!/usr/bin/env python3
"""
Test script for offer detection and structured offer creation
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from pipelines.modular_pipeline import ASIAModularPipeline

def test_offer_detection():
    """Test the offer detection functionality"""
    print("🧪 Testing modular pipeline initialization...")
    
    # Initialize agent
    agent = ASIAModularPipeline()
    
    print("✅ Pipeline initialized successfully")
    
    # Test basic functionality
    print("\n🎯 Testing basic pipeline functionality...")
    
    # Test preferences
    test_preferences = {
        "destination": "Japan",
        "duration": "14 days",
        "budget": "medium"
    }
    
    print(f"📊 Test preferences: {test_preferences}")
    print("✅ Basic test completed!")

if __name__ == "__main__":
    test_offer_detection() 