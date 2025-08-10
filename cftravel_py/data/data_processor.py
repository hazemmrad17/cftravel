"""
Data processing and semantic matching for travel offers
Enhanced with vector store integration
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import numpy as np
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """Enhanced data processor with vector store integration"""
    
    def __init__(self, json_file_path: str = None, vector_store_service = None):
        self.json_file_path = json_file_path
        self.vector_store_service = vector_store_service
        self.offers: List[TravelOffer] = []
        self.offers_data: List[Dict[str, Any]] = []
        
        # Load offers if file path provided
        if json_file_path:
            self.load_offers()
    
    def load_offers(self, json_file_path: str = None):
        """Load offers from JSON file"""
        if json_file_path:
            self.json_file_path = json_file_path
        
        if not self.json_file_path:
            logger.warning("No JSON file path provided")
            return
        
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.offers = []
            self.offers_data = []
            
            for item in data:
                # Create TravelOffer object
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
                self.offers_data.append(item)
            
            logger.info(f"✅ Loaded {len(self.offers)} travel offers")
            
            # Build vector index if service is available
            if self.vector_store_service and self.offers_data:
                self._build_vector_index()
                
        except Exception as e:
            logger.error(f"❌ Error loading offers: {e}")
            self.offers = []
            self.offers_data = []
    
    def _build_vector_index(self):
        """Build vector index using the vector store service"""
        if not self.vector_store_service:
            logger.warning("Vector store service not available")
            return
        
        try:
            logger.info("🔨 Building vector index...")
            success = self.vector_store_service.build_index_from_offers(self.offers_data)
            if success:
                logger.info("✅ Vector index built successfully")
            else:
                logger.error("❌ Failed to build vector index")
        except Exception as e:
            logger.error(f"❌ Error building vector index: {e}")
    
    def filter_by_preferences(self, preferences: Dict[str, Any]) -> List[TravelOffer]:
        """Filter offers by user preferences"""
        if not preferences:
            return self.offers
        
        filtered_offers = []
        for offer in self.offers:
            if offer.matches_preferences(preferences):
                filtered_offers.append(offer)
        
        return filtered_offers
    
    def semantic_search(self, query: str, top_k: int = 10, use_vector_store: bool = True) -> List[Dict[str, Any]]:
        """Perform semantic search using vector store if available"""
        if use_vector_store and self.vector_store_service:
            try:
                logger.info(f"🔍 Performing vector search for: '{query}'")
                results = self.vector_store_service.search(query, top_k)
                return results
            except Exception as e:
                logger.error(f"❌ Vector search failed: {e}")
                # Fallback to basic search
        
        # Fallback to basic text matching
        logger.info(f"🔍 Performing basic text search for: '{query}'")
        return self._basic_text_search(query, top_k)
    
    def _basic_text_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Basic text-based search as fallback"""
        query_lower = query.lower()
        results = []
        
        for offer in self.offers:
            score = 0
            offer_text = offer.get_semantic_text().lower()
            
            # Simple scoring based on keyword matches
            if query_lower in offer_text:
                score += 1
            
            # Check product name
            if query_lower in offer.product_name.lower():
                score += 2
            
            # Check destinations
            for dest in offer.destinations:
                if query_lower in dest.get('city', '').lower() or query_lower in dest.get('country', '').lower():
                    score += 2
            
            # Check highlights
            for highlight in offer.highlights:
                if query_lower in highlight.get('text', '').lower():
                    score += 1
            
            if score > 0:
                offer_dict = {
                    'product_name': offer.product_name,
                    'reference': offer.reference,
                    'destinations': offer.destinations,
                    'departure_city': offer.departure_city,
                    'dates': offer.dates,
                    'duration': offer.duration,
                    'min_group_size': offer.min_group_size,
                    'max_group_size': offer.max_group_size,
                    'offer_type': offer.offer_type,
                    'description': offer.description,
                    'programme': offer.programme,
                    'highlights': offer.highlights,
                    'images': offer.images,
                    'similarity_score': score / 10.0,  # Normalize score
                    'search_rank': len(results) + 1
                }
                results.append(offer_dict)
                
                if len(results) >= top_k:
                    break
        
        # Sort by score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results
    
    def search_with_filters(self, query: str, filters: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        """Search with additional filters"""
        if self.vector_store_service:
            try:
                return self.vector_store_service.search_with_filters(query, filters, top_k)
            except Exception as e:
                logger.error(f"❌ Vector search with filters failed: {e}")
        
        # Fallback to basic search with filtering
        results = self._basic_text_search(query, top_k * 2)
        filtered_results = []
        
        for result in results:
            if self._matches_filters(result, filters):
                filtered_results.append(result)
                if len(filtered_results) >= top_k:
                    break
        
        return filtered_results
    
    def _matches_filters(self, offer: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if offer matches the given filters"""
        # Destination filter
        if filters.get('destination'):
            dest_filter = filters['destination'].lower()
            offer_destinations = []
            
            if offer.get('destinations'):
                for dest in offer['destinations']:
                    if isinstance(dest, dict):
                        if dest.get('country'):
                            offer_destinations.append(dest['country'].lower())
                        if dest.get('city'):
                            offer_destinations.append(dest['city'].lower())
                    elif isinstance(dest, str):
                        offer_destinations.append(dest.lower())
            
            if not any(dest_filter in dest for dest in offer_destinations):
                return False
        
        # Duration filter
        if filters.get('duration'):
            offer_duration = offer.get('duration', 0)
            if isinstance(offer_duration, str):
                try:
                    offer_duration = int(offer_duration)
                except:
                    offer_duration = 0
            
            if abs(offer_duration - filters['duration']) > 2:  # Allow 2 days tolerance
                return False
        
        # Travel style filter
        if filters.get('travel_style'):
            style_filter = filters['travel_style'].lower()
            offer_text = offer.get('description', '').lower()
            
            style_keywords = {
                'beach': ['beach', 'resort', 'lagoon', 'ocean', 'seaside'],
                'adventure': ['adventure', 'trekking', 'hiking', 'exploration', 'outdoor'],
                'cultural': ['cultural', 'heritage', 'historical', 'temple', 'museum'],
                'family': ['family', 'kids', 'children', 'friendly'],
                'romantic': ['romantic', 'couple', 'honeymoon', 'intimate']
            }
            
            if style_filter in style_keywords:
                if not any(keyword in offer_text for keyword in style_keywords[style_filter]):
                    return False
        
        return True
    
    def get_offer_by_reference(self, reference: str) -> Optional[TravelOffer]:
        """Get offer by reference"""
        for offer in self.offers:
            if offer.reference == reference:
                return offer
        return None
    
    def get_offer_by_reference_dict(self, reference: str) -> Optional[Dict[str, Any]]:
        """Get offer as dictionary by reference"""
        for offer_data in self.offers_data:
            if offer_data.get('reference') == reference:
                return offer_data.copy()
        return None
    
    def get_similar_offers(self, reference: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get similar offers based on a reference offer"""
        if self.vector_store_service:
            try:
                return self.vector_store_service.get_similar_offers(reference, top_k)
            except Exception as e:
                logger.error(f"❌ Vector similarity search failed: {e}")
        
        # Fallback to basic similarity
        reference_offer = self.get_offer_by_reference(reference)
        if not reference_offer:
            return []
        
        # Simple similarity based on destination and type
        similar_offers = []
        for offer in self.offers:
            if offer.reference == reference:
                continue
            
            similarity_score = 0
            
            # Check destination similarity
            if offer.destinations and reference_offer.destinations:
                for ref_dest in reference_offer.destinations:
                    for offer_dest in offer.destinations:
                        if (ref_dest.get('country') == offer_dest.get('country') or
                            ref_dest.get('city') == offer_dest.get('city')):
                            similarity_score += 2
            
            # Check type similarity
            if offer.offer_type == reference_offer.offer_type:
                similarity_score += 1
            
            # Check duration similarity
            if abs(offer.duration - reference_offer.duration) <= 2:
                similarity_score += 1
            
            if similarity_score > 0:
                offer_dict = {
                    'product_name': offer.product_name,
                    'reference': offer.reference,
                    'destinations': offer.destinations,
                    'departure_city': offer.departure_city,
                    'dates': offer.dates,
                    'duration': offer.duration,
                    'min_group_size': offer.min_group_size,
                    'max_group_size': offer.max_group_size,
                    'offer_type': offer.offer_type,
                    'description': offer.description,
                    'programme': offer.programme,
                    'highlights': offer.highlights,
                    'images': offer.images,
                    'similarity_score': similarity_score / 5.0,  # Normalize score
                    'search_rank': len(similar_offers) + 1
                }
                similar_offers.append(offer_dict)
                
                if len(similar_offers) >= top_k:
                    break
        
        # Sort by similarity score
        similar_offers.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar_offers
    
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
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get data processor statistics"""
        vector_stats = {}
        if self.vector_store_service:
            try:
                vector_stats = self.vector_store_service.get_statistics()
            except Exception as e:
                vector_stats = {'error': str(e)}
        
        return {
            'total_offers': len(self.offers),
            'total_offers_data': len(self.offers_data),
            'vector_store_available': self.vector_store_service is not None,
            'vector_store_stats': vector_stats
        }

class PreferenceParser:
    """Enhanced preference parser with better extraction logic"""
    
    @staticmethod
    def parse_preferences(user_input: str) -> Dict[str, Any]:
        """Extract preferences from user input"""
        preferences = {}
        
        # Simple keyword extraction
        input_lower = user_input.lower()
        
        # Destination preferences
        destinations = {
            'thailand': ['thailand', 'thai', 'bangkok', 'phuket', 'krabi', 'chiang mai'],
            'japan': ['japan', 'japanese', 'tokyo', 'kyoto', 'osaka'],
            'vietnam': ['vietnam', 'vietnamese', 'hanoi', 'ho chi minh', 'halong bay'],
            'cambodia': ['cambodia', 'cambodian', 'siem reap', 'phnom penh'],
            'australia': ['australia', 'australian', 'melbourne', 'sydney'],
            'mauritius': ['mauritius', 'mauritian'],
            'reunion': ['reunion', 'reunion island'],
            'madagascar': ['madagascar', 'madagascan'],
            'jordan': ['jordan', 'jordanian', 'amman', 'petra'],
            'morocco': ['morocco', 'moroccan', 'marrakech', 'casablanca', 'fes']
        }
        
        for country, keywords in destinations.items():
            if any(keyword in input_lower for keyword in keywords):
                preferences['destination'] = country
                break
        
        # Duration preferences
        import re
        duration_match = re.search(r'(\d+)\s*(day|days|week|weeks)', input_lower)
        if duration_match:
            number = int(duration_match.group(1))
            unit = duration_match.group(2)
            if 'week' in unit:
                preferences['duration'] = number * 7
            else:
                preferences['duration'] = number
        elif 'week' in input_lower or '7 days' in input_lower:
            preferences['duration'] = 7
        elif 'two weeks' in input_lower or '14 days' in input_lower:
            preferences['duration'] = 14
        
        # Style preferences
        style_keywords = []
        if any(word in input_lower for word in ['cultural', 'culture', 'heritage', 'historical']):
            style_keywords.append('cultural')
        if any(word in input_lower for word in ['adventure', 'desert', 'exploration', 'trekking', 'hiking']):
            style_keywords.append('adventure')
        if any(word in input_lower for word in ['luxury', 'premium', 'exclusive', 'high end']):
            style_keywords.append('luxury')
        if any(word in input_lower for word in ['relaxing', 'peaceful', 'tranquil', 'beach', 'resort']):
            style_keywords.append('relaxing')
        if any(word in input_lower for word in ['family', 'kids', 'children', 'friendly']):
            style_keywords.append('family')
        if any(word in input_lower for word in ['romantic', 'couple', 'honeymoon', 'intimate']):
            style_keywords.append('romantic')
        
        if style_keywords:
            preferences['travel_style'] = style_keywords[0]  # Take first match
        
        # Budget preferences
        if any(word in input_lower for word in ['cheap', 'budget', 'affordable', 'low cost', 'economy']):
            preferences['budget'] = 'low'
        elif any(word in input_lower for word in ['expensive', 'luxury', 'premium', 'high end', 'exclusive']):
            preferences['budget'] = 'high'
        
        # Group size preferences
        group_match = re.search(r'(\d+)\s*(person|people|traveler)', input_lower)
        if group_match:
            preferences['group_size'] = int(group_match.group(1))
        
        return preferences 