"""
Data service for ASIA.fr Agent
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from core.exceptions import DataError
from models.data_models import TravelOffer

logger = logging.getLogger(__name__)

class DataService:
    """Service for handling data operations"""
    
    def __init__(self, data_path: str = "data/asia/data.json"):
        self.data_path = Path(data_path)
        self._data = None
        self._offers = None
        
    def load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        try:
            if not self.data_path.exists():
                raise DataError(f"Data file not found: {self.data_path}")
                
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
                logger.info(f"✅ Loaded data from {self.data_path}")
                return self._data
                
        except json.JSONDecodeError as e:
            raise DataError(f"Invalid JSON in data file: {e}")
        except Exception as e:
            raise DataError(f"Failed to load data: {e}")
    
    def get_data(self) -> Dict[str, Any]:
        """Get loaded data"""
        if self._data is None:
            self.load_data()
        return self._data
    
    def get_offers(self) -> List[Dict[str, Any]]:
        """Get all offers from data"""
        data = self.get_data()
        # Data is a list of offers, not a dictionary with 'offers' key
        if isinstance(data, list):
            logger.info(f"✅ Loaded {len(data)} offers from data")
            return data
        else:
            offers = data.get('offers', [])
            logger.info(f"✅ Loaded {len(offers)} offers from data")
            return offers
    
    def get_offer_by_id(self, offer_id: str) -> Optional[Dict[str, Any]]:
        """Get specific offer by ID"""
        offers = self.get_offers()
        for offer in offers:
            if offer.get('id') == offer_id:
                return offer
        return None
    
    def search_offers(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search offers by query"""
        offers = self.get_offers()
        results = []
        
        query_lower = query.lower()
        for offer in offers:
            # Search in title, description, destinations
            title = offer.get('title', '').lower()
            description = offer.get('description', '').lower()
            destinations = ' '.join(offer.get('destinations', [])).lower()
            
            if (query_lower in title or 
                query_lower in description or 
                query_lower in destinations):
                results.append(offer)
                
            if len(results) >= limit:
                break
                
        return results
    
    def filter_offers(self, 
                     destination: Optional[str] = None,
                     duration: Optional[int] = None,
                     budget: Optional[float] = None,
                     offer_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Filter offers by criteria"""
        offers = self.get_offers()
        filtered = []
        
        for offer in offers:
            # Destination filter
            if destination:
                offer_destinations = [d.lower() for d in offer.get('destinations', [])]
                if destination.lower() not in offer_destinations:
                    continue
            
            # Duration filter
            if duration:
                offer_duration = offer.get('duration', 0)
                if offer_duration != duration:
                    continue
            
            # Budget filter
            if budget:
                offer_price = offer.get('price', 0)
                if offer_price > budget:
                    continue
            
            # Offer type filter
            if offer_type:
                if offer.get('offer_type', '').lower() != offer_type.lower():
                    continue
            
            filtered.append(offer)
        
        return filtered
    
    def get_destinations(self) -> List[str]:
        """Get all unique destinations"""
        offers = self.get_offers()
        destinations = set()
        
        for offer in offers:
            destinations.update(offer.get('destinations', []))
        
        return sorted(list(destinations))
    
    def get_offer_types(self) -> List[str]:
        """Get all unique offer types"""
        offers = self.get_offers()
        types = set()
        
        for offer in offers:
            types.add(offer.get('offer_type', ''))
        
        return sorted(list(types))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get data statistics"""
        offers = self.get_offers()
        
        return {
            'total_offers': len(offers),
            'destinations': len(self.get_destinations()),
            'offer_types': len(self.get_offer_types()),
            'price_range': {
                'min': min((offer.get('price', 0) for offer in offers), default=0),
                'max': max((offer.get('price', 0) for offer in offers), default=0)
            },
            'duration_range': {
                'min': min((offer.get('duration', 0) for offer in offers), default=0),
                'max': max((offer.get('duration', 0) for offer in offers), default=0)
            }
        } 