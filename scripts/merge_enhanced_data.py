#!/usr/bin/env python3
"""
Script to merge ENHANCED scraped data (prices + dates) back into the original dataset
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging

def load_json_file(file_path: Path) -> List[Dict]:
    """Load JSON file and return list of dictionaries"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both list and dict formats
        if isinstance(data, dict):
            return data.get('offers', [])
        else:
            return data
    except Exception as e:
        logging.error(f"Error loading {file_path}: {e}")
        return []

def main():
    """Main function to merge enhanced data"""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # File paths
    original_data_file = project_root / 'cftravel_py' / 'data' / 'asia' / 'data.json'
    scraped_data_file = project_root / 'cftravel_py' / 'data' / 'asia' / 'scraped_data_enhanced.json'
    output_file = project_root / 'cftravel_py' / 'data' / 'asia' / 'data_with_enhanced_info.json'
    
    # Check if enhanced data exists
    if not scraped_data_file.exists():
        logger.error(f"Enhanced data file not found: {scraped_data_file}")
        logger.info("Please run the enhanced scraper first!")
        return
    
    # Load original offers
    logger.info("Loading original offers...")
    offers = load_json_file(original_data_file)
    
    if not offers:
        logger.error("No offers found in original data file")
        return
    
    # Load scraped enhanced data
    logger.info("Loading enhanced scraped data...")
    scraped_data = load_json_file(scraped_data_file)
    
    if not scraped_data:
        logger.error("No enhanced data found")
        return
    
    logger.info(f"Loaded {len(offers)} offers and {len(scraped_data)} scraped data entries")
    
    # Clean up old date fields in all offers before merging
    logger.info("Cleaning up old date fields...")
    for offer in offers:
        # Remove old date_context field if it exists
        if 'date_context' in offer:
            del offer['date_context']
        
        # Remove any null or empty date_range entries
        if offer.get('date_range') is None or offer.get('date_range') == '':
            if 'date_range' in offer:
                del offer['date_range']
    
    # Create a mapping of reference to enhanced data
    enhanced_data_map = {}
    for data_entry in scraped_data:
        reference = data_entry.get('reference')
        if reference:
            enhanced_data_map[reference] = {
                'price': {
                    'amount': data_entry.get('price'),
                    'currency': data_entry.get('currency', 'EUR'),
                    'price_type': data_entry.get('price_type', 'per_person'),
                    'scraped_at': data_entry.get('scraped_at'),
                    'url': data_entry.get('url')
                },
                'duration': data_entry.get('duration'),
                'departure_dates': data_entry.get('departure_dates'),
                'date_range': data_entry.get('date_range')
            }
    
    # Merge enhanced data into offers
    logger.info("Merging enhanced data...")
    offers_with_prices = 0
    offers_with_dates = 0
    offers_without_enhanced_data = 0
    
    for offer in offers:
        reference = offer.get('reference')
        if reference and reference in enhanced_data_map:
            enhanced_data = enhanced_data_map[reference]
            
            # Update price information
            if enhanced_data['price']['amount'] is not None:
                offer['price'] = enhanced_data['price']
                offers_with_prices += 1
            
            # Update date information
            if enhanced_data['duration'] or enhanced_data['date_range']:
                # Update duration if available
                if enhanced_data['duration']:
                    offer['duration'] = enhanced_data['duration']
                
                # Update dates if available
                if enhanced_data['departure_dates']:
                    offer['dates'] = enhanced_data['departure_dates']
                
                # Add date range information (this will overwrite any existing date_range)
                if enhanced_data['date_range']:
                    offer['date_range'] = enhanced_data['date_range']
                
                # Clean up old date fields that might cause confusion
                # Remove date_context if it exists (old field structure)
                if 'date_context' in offer:
                    del offer['date_context']
                
                # Remove any null or empty date_range entries
                if offer.get('date_range') is None or offer.get('date_range') == '':
                    del offer['date_range']
                
                offers_with_dates += 1
        else:
            offers_without_enhanced_data += 1
    
    # Save merged data
    logger.info(f"Saving merged data to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(offers, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Data saved to {output_file}")
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("ENHANCED DATA MERGE SUMMARY")
    logger.info("="*50)
    logger.info(f"Total offers: {len(offers)}")
    logger.info(f"Offers with updated prices: {offers_with_prices}")
    logger.info(f"Offers with updated dates: {offers_with_dates}")
    logger.info(f"Offers without enhanced data: {offers_without_enhanced_data}")
    logger.info(f"Price coverage: {offers_with_prices/len(offers)*100:.1f}%")
    logger.info(f"Date coverage: {offers_with_dates/len(offers)*100:.1f}%")
    
    # Calculate price statistics
    prices = [offer['price']['amount'] for offer in offers if offer.get('price', {}).get('amount')]
    if prices:
        logger.info(f"Price range: {min(prices):.0f} - {max(prices):.0f} EUR")
        logger.info(f"Average price: {sum(prices)/len(prices):.0f} EUR")
    
    # Show sample merged offers
    logger.info("\nSample merged offers:")
    for i, offer in enumerate(offers[:3]):
        reference = offer.get('reference', 'N/A')
        name = offer.get('product_name', 'N/A')
        price = offer.get('price', {}).get('amount', 'N/A')
        duration = offer.get('duration', 'N/A')
        dates = offer.get('dates', 'N/A')
        date_range = offer.get('date_range', 'N/A')
        
        logger.info(f"  {i+1}. {reference} - {name}")
        logger.info(f"      Price: {price} €")
        logger.info(f"      Duration: {duration}")
        logger.info(f"      Dates: {dates}")
        logger.info(f"      Date Range: {date_range}")
    
    logger.info(f"\nMerged data saved to: {output_file}")
    
    # Ask if user wants to replace the original file
    response = input(f"\nReplace original data.json with enhanced data? (y/N): ")
    if response.lower() == 'y':
        # Create backup
        backup_file = project_root / 'cftravel_py' / 'data' / 'asia' / 'data_backup_before_enhanced.json'
        import shutil
        shutil.copy2(original_data_file, backup_file)
        logger.info(f"Backup created: {backup_file}")
        
        # Replace original
        shutil.copy2(output_file, original_data_file)
        logger.info(f"Original data.json replaced with enhanced data!")
    else:
        logger.info("Original data.json preserved. Enhanced data available in data_with_enhanced_info.json")

if __name__ == "__main__":
    main() 