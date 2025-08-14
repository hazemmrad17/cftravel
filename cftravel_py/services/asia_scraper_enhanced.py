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
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScrapedData:
    """Data class for scraped information"""
    reference: str
    price: Optional[float]
    currency: str = "EUR"
    price_type: str = "per_person"
    duration: Optional[str] = None
    departure_dates: Optional[List[str]] = None
    date_range: Optional[str] = None
    scraped_at: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None

class AsiaScraperEnhanced:
    """Enhanced web scraper for Asia.fr to extract price and date information"""
    
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
        """Extract price from the page content"""
        try:
            # Look for price patterns that capture the FULL number including spaces
            price_patterns = [
                r'(\d+(?:\s\d{3})*(?:,\d{2})?)\s*(€|EUR|euros?)',
                r'(\d+(?:\s\d{3})*(?:,\d{2})?)\s*(€|EUR)',
                r'Prix[:\s]*(\d+(?:\s\d{3})*(?:,\d{2})?)\s*(€|EUR|euros?)',
                r'À partir de[:\s]*(\d+(?:\s\d{3})*(?:,\d{2})?)\s*(€|EUR|euros?)',
            ]
            
            page_text = soup.get_text()
            
            for pattern in price_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                if matches:
                    price_str, currency = matches[0]
                    price_str = price_str.replace(' ', '').replace(',', '.')
                    try:
                        price = float(price_str)
                        return price, currency.upper()
                    except ValueError:
                        continue
            
            return None, "EUR"
            
        except Exception as e:
            logger.error(f"Error extracting price: {e}")
            return None, "EUR"
    
    def _extract_dates_from_page(self, soup: BeautifulSoup) -> Tuple[Optional[str], Optional[List[str]], Optional[str]]:
        """Extract date information from the page content"""
        try:
            page_text = soup.get_text()
            
            # Look for duration patterns
            duration_patterns = [
                r'(\d+)\s*jours?\s*/\s*(\d+)\s*nuits?',
                r'(\d+)\s*jours?',
                r'(\d+)\s*nuits?',
            ]
            
            duration = None
            for pattern in duration_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                if matches:
                    if len(matches[0]) == 2:  # jours/nuits format
                        jours, nuits = matches[0]
                        duration = f"{jours} jours / {nuits} nuits"
                    else:  # single number
                        duration = f"{matches[0][0]} jours"
                    break
            
            # Look for date range patterns
            date_range_patterns = [
                r'Entre le (\d{2}/\d{2}/\d{4}) et le (\d{2}/\d{2}/\d{4})',
                r'Du (\d{2}/\d{2}/\d{4}) au (\d{2}/\d{2}/\d{4})',
                r'(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})',
            ]
            
            date_range = None
            departure_dates = []
            
            for pattern in date_range_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    start_date, end_date = matches[0]
                    date_range = f"{start_date} - {end_date}"
                    departure_dates = [start_date, end_date]
                    break
            
            # Look for specific departure dates
            if not departure_dates:
                date_patterns = [
                    r'(\d{2}/\d{2}/\d{4})',
                    r'(\d{1,2}\s+\w+\s+\d{4})',
                ]
                
                for pattern in date_patterns:
                    matches = re.findall(pattern, page_text)
                    if matches:
                        # Filter out dates that look like current year or future
                        current_year = datetime.now().year
                        for match in matches:
                            if str(current_year) in match or str(current_year + 1) in match:
                                departure_dates.append(match)
                        if departure_dates:
                            break
            
            # Look for date elements in HTML
            date_selectors = [
                '.date',
                '.departure-date',
                '.date-depart',
                '[class*="date"]',
                '[class*="depart"]',
            ]
            
            for selector in date_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    if not duration and 'jour' in text.lower():
                        # Extract duration from element
                        for pattern in duration_patterns:
                            matches = re.findall(pattern, text, re.IGNORECASE)
                            if matches:
                                if len(matches[0]) == 2:
                                    jours, nuits = matches[0]
                                    duration = f"{jours} jours / {nuits} nuits"
                                else:
                                    duration = f"{matches[0][0]} jours"
                                break
                    
                    if not date_range and ('entre' in text.lower() or 'du' in text.lower()):
                        # Extract date range from element
                        for pattern in date_range_patterns:
                            matches = re.findall(pattern, text)
                            if matches:
                                start_date, end_date = matches[0]
                                date_range = f"{start_date} - {end_date}"
                                departure_dates = [start_date, end_date]
                                break
            
            return duration, departure_dates, date_range
            
        except Exception as e:
            logger.error(f"Error extracting dates: {e}")
            return None, None, None
    
    def scrape_data_for_reference(self, reference: str, price_url: str) -> ScrapedData:
        """Scrape price and date information for a specific trip reference"""
        try:
            logger.info(f"Scraping data for reference: {reference}")
            
            # Add random delay
            self._random_delay()
            
            # Make request
            response = self.session.get(price_url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract price
            price, currency = self._extract_price_from_page(soup)
            
            # Extract dates
            duration, departure_dates, date_range = self._extract_dates_from_page(soup)
            
            return ScrapedData(
                reference=reference,
                price=price,
                currency=currency,
                duration=duration,
                departure_dates=departure_dates,
                date_range=date_range,
                scraped_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                url=price_url,
                error=None
            )
            
        except requests.RequestException as e:
            logger.error(f"Request error for {reference}: {e}")
            return ScrapedData(
                reference=reference,
                price=None,
                url=price_url,
                error=f"Request error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error for {reference}: {e}")
            return ScrapedData(
                reference=reference,
                price=None,
                url=price_url,
                error=f"Unexpected error: {str(e)}"
            )
    
    def scrape_data_batch(self, offers: List[Dict], max_workers: int = 3) -> List[ScrapedData]:
        """Scrape data for multiple offers in parallel"""
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
                    self.scrape_data_for_reference, 
                    offer['reference'], 
                    offer['price_url']
                ): offer for offer in offers_with_urls
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_offer):
                result = future.result()
                results.append(result)
                logger.info(f"Completed scraping for {result.reference}: {result.price} {result.currency}, Duration: {result.duration}")
        
        return results
    
    def save_results(self, results: List[ScrapedData], output_file: str):
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
                    'duration': result.duration,
                    'departure_dates': result.departure_dates,
                    'date_range': result.date_range,
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

def test_enhanced_scraper():
    """Test the enhanced scraper on a single offer"""
    
    # Test data from your example
    test_reference = "TJOR1W"
    test_url = "https://www.asia.fr/ceto.cfm?idproduit=115&ttc=1"
    
    logger.info(f"Testing ENHANCED scraper with reference: {test_reference}")
    logger.info(f"URL: {test_url}")
    
    try:
        # Initialize scraper
        scraper = AsiaScraperEnhanced(delay_range=(1.0, 2.0))
        
        # Scrape single offer
        result = scraper.scrape_data_for_reference(test_reference, test_url)
        
        # Print results
        logger.info("\n" + "="*50)
        logger.info("ENHANCED SCRAPER TEST RESULTS")
        logger.info("="*50)
        logger.info(f"Reference: {result.reference}")
        logger.info(f"Price: {result.price} {result.currency}")
        logger.info(f"Duration: {result.duration}")
        logger.info(f"Date Range: {result.date_range}")
        logger.info(f"Departure Dates: {result.departure_dates}")
        logger.info(f"Scraped at: {result.scraped_at}")
        logger.info(f"URL: {result.url}")
        logger.info(f"Error: {result.error}")
        
        if result.price:
            logger.info(f"✅ SUCCESS: Found price {result.price} {result.currency}")
        else:
            logger.info(f"❌ FAILED: No price found - {result.error}")
        
        if result.duration or result.date_range:
            logger.info(f"✅ SUCCESS: Found date information")
        else:
            logger.info(f"⚠️  WARNING: No date information found")
        
        return result.price is not None
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced_scraper()
    if success:
        logger.info("\n✅ Enhanced scraper test passed!")
    else:
        logger.info("\n❌ Enhanced scraper test failed.") 