#!/usr/bin/env python3
"""
Test script to verify data service can load the data file
"""

import sys
import os
from pathlib import Path

# Add cftravel_py to path
sys.path.append('cftravel_py')

try:
    from services.data_service import DataService
    
    # Test with the corrected path
    data_service = DataService("data/asia/data.json")
    offers = data_service.get_offers()
    
    print(f"✅ Data loaded successfully!")
    print(f"📊 Total offers: {len(offers)}")
    
    # Show first few offers
    for i, offer in enumerate(offers[:3]):
        print(f"\n--- Offer {i+1} ---")
        print(f"Title: {offer.get('product_name', 'N/A')}")
        print(f"Reference: {offer.get('reference', 'N/A')}")
        print(f"Price URL: {offer.get('price_url', 'N/A')}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 