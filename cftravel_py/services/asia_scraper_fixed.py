import requests
import time
import json
import logging
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScrapedPrice:
    """Data class for scraped price information"""
    reference: str
    price: Optional[float]
    currency: str = "EUR"
    price_type: str = "per_person"
    scraped_at: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None

class AsiaScraperFixed:
    """Web scraper for Asia.fr to extract price information - FIXED VERSION"""
    
    def __init__(self, delay_range: Tuple[float, float] = (1.0, 3.0)):
        self.session = requests.Session()
        self.delay_range = delay_range
        
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _random_delay(self):
        """Add random delay between requests to be respectful"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def _extract_price_from_page(self, soup: BeautifulSoup) -> Tuple[Optional[float], str]:
        """
        Extract price from the page content - FIXED VERSION
        Returns: (price, currency)
        """
        try:
            # FIXED: Look for price patterns that capture the FULL number including spaces
            price_patterns = [
                # Pattern to capture full numbers like "1 990" or "1990"
                r'(\d+(?:\s\d{3})*(?:,\d{2})?)\s*(€|EUR|euros?)',
                r'(\d+(?:\s\d{3})*(?:,\d{2})?)\s*(€|EUR)',
                r'Prix[:\s]*(\d+(?:\s\d{3})*(?:,\d{2})?)\s*(€|EUR|euros?)',
                r'À partir de[:\s]*(\d+(?:\s\d{3})*(?:,\d{2})?)\s*(€|EUR|euros?)',
            ]
            
            page_text = soup.get_text()
            
            for pattern in price_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                if matches:
                    # Take the first match
                    price_str, currency = matches[0]
                    # Clean up price string - remove ALL spaces and replace comma with dot
                    price_str = price_str.replace(' ', '').replace(',', '.')
                    try:
                        price = float(price_str)
                        logger.info(f"Extracted price: {price_str} -> {price}")
                        return price, currency.upper()
                    except ValueError:
                        continue
            
            # Look for specific price elements with better text extraction
            price_selectors = [
                '.price',
                '.prix',
                '[class*="price"]',
                '[class*="prix"]',
                '.tarif',
                '[class*="tarif"]',
                '.montant',
                '[class*="montant"]',
            ]
            
            for selector in price_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    # Try to extract price from element text
                    for pattern in price_patterns:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        if matches:
                            price_str, currency = matches[0]
                            price_str = price_str.replace(' ', '').replace(',', '.')
                            try:
                                price = float(price_str)
                                logger.info(f"Extracted price from element: {price_str} -> {price}")
                                return price, currency.upper()
                            except ValueError:
                                continue
            
            return None, "EUR"
            
        except Exception as e:
            logger.error(f"Error extracting price: {e}")
            return None, "EUR"
    
    def scrape_price_for_reference(self, reference: str, price_url: str) -> ScrapedPrice:
        """
        Scrape price for a specific trip reference
        """
        try:
            logger.info(f"Scraping price for reference: {reference}")
            
            # Add random delay
            self._random_delay()
            
            # Make request
            response = self.session.get(price_url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract price
            price, currency = self._extract_price_from_page(soup)
            
            return ScrapedPrice(
                reference=reference,
                price=price,
                currency=currency,
                scraped_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                url=price_url,
                error=None
            )
            
        except requests.RequestException as e:
            logger.error(f"Request error for {reference}: {e}")
            return ScrapedPrice(
                reference=reference,
                price=None,
                url=price_url,
                error=f"Request error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error for {reference}: {e}")
            return ScrapedPrice(
                reference=reference,
                price=None,
                url=price_url,
                error=f"Unexpected error: {str(e)}"
            )
    
    def scrape_prices_batch(self, offers: List[Dict], max_workers: int = 3) -> List[ScrapedPrice]:
        """
        Scrape prices for multiple offers in parallel
        """
        results = []
        
        # Filter offers that have price_url
        offers_with_urls = [
            offer for offer in offers 
            if offer.get('reference') and offer.get('price_url')
        ]
        
        logger.info(f"Starting batch scrape for {len(offers_with_urls)} offers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scraping tasks
            future_to_offer = {
                executor.submit(
                    self.scrape_price_for_reference, 
                    offer['reference'], 
                    offer['price_url']
                ): offer for offer in offers_with_urls
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_offer):
                result = future.result()
                results.append(result)
                logger.info(f"Completed scraping for {result.reference}: {result.price} {result.currency}")
        
        return results
    
    def save_results(self, results: List[ScrapedPrice], output_file: str):
        """Save scraping results to JSON file"""
        try:
            # Convert to dict for JSON serialization
            data = []
            for result in results:
                data.append({
                    'reference': result.reference,
                    'price': result.price,
                    'currency': result.currency,
                    'price_type': result.price_type,
                    'scraped_at': result.scraped_at,
                    'url': result.url,
                    'error': result.error
                })
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def load_offers_from_json(self, json_file: str) -> List[Dict]:
        """Load offers from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both list and dict formats
            if isinstance(data, dict):
                offers = data.get('offers', [])
            else:
                offers = data
            
            logger.info(f"Loaded {len(offers)} offers from {json_file}")
            return offers
            
        except Exception as e:
            logger.error(f"Error loading offers: {e}")
            return []

def test_fixed_scraper():
    """Test the fixed scraper on a single offer"""
    
    # Test data from your example
    test_reference = "TJOR1W"
    test_url = "https://www.asia.fr/ceto.cfm?idproduit=115&ttc=1"
    
    logger.info(f"Testing FIXED scraper with reference: {test_reference}")
    logger.info(f"URL: {test_url}")
    
    try:
        # Initialize scraper
        scraper = AsiaScraperFixed(delay_range=(1.0, 2.0))
        
        # Scrape single offer
        result = scraper.scrape_price_for_reference(test_reference, test_url)
        
        # Print results
        logger.info("\n" + "="*50)
        logger.info("FIXED SCRAPER TEST RESULTS")
        logger.info("="*50)
        logger.info(f"Reference: {result.reference}")
        logger.info(f"Price: {result.price}")
        logger.info(f"Currency: {result.currency}")
        logger.info(f"Scraped at: {result.scraped_at}")
        logger.info(f"URL: {result.url}")
        logger.info(f"Error: {result.error}")
        
        if result.price:
            logger.info(f"✅ SUCCESS: Found price {result.price} {result.currency}")
            if result.price == 1990.0:
                logger.info("✅ CORRECT: Price is now 1990 EUR (fixed!)")
            else:
                logger.info(f"❌ STILL WRONG: Expected 1990, got {result.price}")
        else:
            logger.info(f"❌ FAILED: No price found - {result.error}")
        
        return result.price == 1990.0
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_fixed_scraper()
    if success:
        logger.info("\n✅ Fixed scraper test passed! The regex issue is resolved.")
    else:
        logger.info("\n❌ Fixed scraper test failed. Need to investigate further.") 