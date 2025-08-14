#!/usr/bin/env python3
"""
Automated script to scrape prices and dates from Asia.fr using the ENHANCED scraper
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the enhanced scraper directly
sys.path.insert(0, str(project_root / 'cftravel_py' / 'services'))
from asia_scraper_enhanced import AsiaScraperEnhanced
import logging

def main():
    """Main function to run the ENHANCED Asia.fr scraper automatically"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('asia_scraping_enhanced.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize scraper with conservative delays
        scraper = AsiaScraperEnhanced(delay_range=(3.0, 6.0))
        
        # Path to your data file
        data_file = project_root / 'cftravel_py' / 'data' / 'asia' / 'data.json'
        output_file = project_root / 'cftravel_py' / 'data' / 'asia' / 'scraped_data_enhanced.json'
        
        if not data_file.exists():
            logger.error(f"Data file not found: {data_file}")
            return
        
        logger.info(f"Loading offers from: {data_file}")
        
        # Load offers
        offers = scraper.load_offers_from_json(str(data_file))
        
        if not offers:
            logger.error("No offers found in data file")
            return
        
        logger.info(f"Found {len(offers)} offers")
        
        # Count offers with price URLs
        offers_with_urls = [
            offer for offer in offers 
            if offer.get('reference') and offer.get('price_url')
        ]
        
        logger.info(f"Offers with price URLs: {len(offers_with_urls)}")
        
        if not offers_with_urls:
            logger.error("No offers with price URLs found")
            return
        
        # Show first few offers for verification
        logger.info("Sample offers:")
        for i, offer in enumerate(offers_with_urls[:3]):
            logger.info(f"  {i+1}. {offer.get('reference')} - {offer.get('product_name', 'N/A')}")
            logger.info(f"     URL: {offer.get('price_url')}")
            logger.info(f"     Current dates: {offer.get('dates', 'N/A')}")
        
        # Scrape data with limited concurrency to be respectful
        logger.info("Starting enhanced data scraping...")
        results = scraper.scrape_data_batch(offers_with_urls, max_workers=2)
        
        # Save results
        logger.info(f"Saving results to: {output_file}")
        scraper.save_results(results, str(output_file))
        
        # Print summary
        successful = [r for r in results if r.price is not None]
        failed = [r for r in results if r.price is None]
        
        # Count offers with date information
        with_dates = [r for r in results if r.duration or r.date_range]
        
        logger.info("\n" + "="*50)
        logger.info("ENHANCED SCRAPING SUMMARY")
        logger.info("="*50)
        logger.info(f"Total offers processed: {len(results)}")
        logger.info(f"Successful scrapes: {len(successful)}")
        logger.info(f"Failed scrapes: {len(failed)}")
        logger.info(f"Success rate: {len(successful)/len(results)*100:.1f}%")
        logger.info(f"Offers with date info: {len(with_dates)}")
        logger.info(f"Date coverage: {len(with_dates)/len(results)*100:.1f}%")
        
        if successful:
            prices = [r.price for r in successful if r.price]
            if prices:
                logger.info(f"Price range: {min(prices):.0f} - {max(prices):.0f} EUR")
                logger.info(f"Average price: {sum(prices)/len(prices):.0f} EUR")
        
        # Show sample of date information
        if with_dates:
            logger.info("\nSample date information:")
            for i, result in enumerate(with_dates[:5]):
                logger.info(f"  {i+1}. {result.reference}")
                logger.info(f"     Duration: {result.duration}")
                logger.info(f"     Date Range: {result.date_range}")
                logger.info(f"     Departure Dates: {result.departure_dates}")
        
        if failed:
            logger.info("\nFailed references:")
            for result in failed[:10]:  # Show first 10 failures
                logger.info(f"  - {result.reference}: {result.error}")
            
            if len(failed) > 10:
                logger.info(f"  ... and {len(failed) - 10} more")
        
        logger.info(f"\nResults saved to: {output_file}")
        logger.info("Log file: asia_scraping_enhanced.log")
        
    except KeyboardInterrupt:
        logger.info("\nScraping interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main() 