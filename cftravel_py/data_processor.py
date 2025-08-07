"""
Data processing and semantic matching for travel offers
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import numpy as np
import chromadb
from chromadb.utils import embedding_functions

@dataclass
class TravelOffer:
    """Travel offer data structure"""
    product_name: str
    reference: str
    destinations: List[Dict[str, str]]
    departure_city: str
    dates: List[str]
    duration: int
    min_group_size: int
    max_group_size: int
    offer_type: str
    description: str
    programme: str
    highlights: List[Dict[str, str]]
    images: List[str]
    
    def get_semantic_text(self) -> str:
        """Get semantic text for matching"""
        destinations_text = ", ".join([f"{d.get('city', '')} ({d.get('country', '')})" for d in self.destinations])
        highlights_text = " ".join([h.get('text', '') for h in self.highlights])
        
        return f"{self.product_name} {destinations_text} {self.description} {highlights_text}"
    
    def matches_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Check if offer matches user preferences"""
        # Simple boolean matching - no scoring
        if not preferences:
            return True
        
        # Check destination preferences
        if preferences.get('destination'):
            dest_pref = preferences['destination'].lower()
            for dest in self.destinations:
                if dest_pref in dest.get('city', '').lower() or dest_pref in dest.get('country', '').lower():
                    return True
        
        # Check duration preferences
        if preferences.get('duration'):
            pref_duration = preferences['duration']
            if isinstance(pref_duration, int) and abs(self.duration - pref_duration) <= 2:
                return True
        
        # Check style preferences
        if preferences.get('style'):
            style_prefs = [s.lower() for s in preferences['style']]
            offer_text = self.get_semantic_text().lower()
            for style in style_prefs:
                if style in offer_text:
                    return True
        
        return True  # Default to True if no specific preferences

class DataProcessor:
    """Process travel data and provide offers (no Chroma)"""
    
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.offers: List[TravelOffer] = []
    
    def load_offers(self):
        """Load offers from JSON file"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.offers = []
            for item in data:
                offer = TravelOffer(
                    product_name=item.get('product_name', ''),
                    reference=item.get('reference', ''),
                    destinations=item.get('destinations', []),
                    departure_city=item.get('departure_city', ''),
                    dates=item.get('dates', []),
                    duration=item.get('duration', 0),
                    min_group_size=item.get('min_group_size', 0),
                    max_group_size=item.get('max_group_size', 0),
                    offer_type=item.get('offer_type', ''),
                    description=item.get('description', ''),
                    programme=item.get('programme', ''),
                    highlights=item.get('highlights', []),
                    images=item.get('images', [])
                )
                self.offers.append(offer)
            print(f"\u2705 Loaded {len(self.offers)} travel offers")
        except Exception as e:
            print(f"\u274c Error loading offers: {e}")
            self.offers = []
    
    def filter_by_preferences(self, preferences: Dict[str, Any]) -> List[TravelOffer]:
        """Filter offers by user preferences"""
        if not preferences:
            return self.offers
        
        filtered_offers = []
        for offer in self.offers:
            if offer.matches_preferences(preferences):
                filtered_offers.append(offer)
        
        return filtered_offers
    
    def get_offer_by_reference(self, reference: str) -> Optional[TravelOffer]:
        """Get offer by reference"""
        for offer in self.offers:
            if offer.reference == reference:
                return offer
        return None
    
    def get_offers_summary(self) -> str:
        """Get summary of available offers"""
        if not self.offers:
            return "No offers available"
        
        summary = f"Available Travel Offers ({len(self.offers)} total):\n\n"
        
        for i, offer in enumerate(self.offers[:10], 1):  # Show first 10
            destinations = ", ".join([f"{d.get('city', '')} ({d.get('country', '')})" for d in offer.destinations])
            summary += f"{i}. {offer.product_name} ({offer.reference})\n"
            summary += f"   Destinations: {destinations}\n"
            summary += f"   Duration: {offer.duration} days\n"
            summary += f"   Group: {offer.min_group_size}-{offer.max_group_size} people\n"
            summary += f"   Type: {offer.offer_type}\n"
            summary += f"   Description: {offer.description[:100]}...\n\n"
        
        return summary

class PreferenceParser:
    """Parse user preferences from natural language"""
    
    @staticmethod
    def parse_preferences(user_input: str) -> Dict[str, Any]:
        """Extract preferences from user input"""
        preferences = {}
        
        # Simple keyword extraction
        input_lower = user_input.lower()
        
        # Destination preferences
        if 'jordan' in input_lower:
            preferences['destination'] = 'jordan'
        elif 'morocco' in input_lower:
            preferences['destination'] = 'morocco'
        
        # Duration preferences
        if 'week' in input_lower or '7 days' in input_lower:
            preferences['duration'] = 7
        elif 'two weeks' in input_lower or '14 days' in input_lower:
            preferences['duration'] = 14
        
        # Style preferences
        style_keywords = []
        if any(word in input_lower for word in ['cultural', 'culture', 'heritage']):
            style_keywords.append('cultural')
        if any(word in input_lower for word in ['adventure', 'desert', 'exploration']):
            style_keywords.append('adventure')
        if any(word in input_lower for word in ['luxury', 'premium', 'exclusive']):
            style_keywords.append('luxury')
        if any(word in input_lower for word in ['relaxing', 'peaceful', 'tranquil']):
            style_keywords.append('relaxing')
        
        if style_keywords:
            preferences['style'] = style_keywords
        
        # Budget preferences
        if any(word in input_lower for word in ['cheap', 'budget', 'affordable']):
            preferences['budget'] = 'low'
        elif any(word in input_lower for word in ['expensive', 'luxury', 'premium']):
            preferences['budget'] = 'high'
        
        return preferences 