"""
Offer service for ASIA.fr Agent
"""

import logging
from typing import Dict, Any, List, Optional
from cftravel_py.core.exceptions import OfferError
from cftravel_py.models.data_models import OfferCard, DetailedProgram
from cftravel_py.services.data_service import DataService

logger = logging.getLogger(__name__)

class OfferService:
    """Service for offer matching and processing"""
    
    def __init__(self, data_service: DataService):
        self.data_service = data_service
        
    def match_offers(self, user_preferences: Dict[str, Any], max_offers: int = 3) -> List[OfferCard]:
        """Match offers based on user preferences"""
        try:
            # Extract preferences
            destination = user_preferences.get('destination')
            duration = user_preferences.get('duration')
            budget = user_preferences.get('budget')
            travel_style = user_preferences.get('travel_style')
            
            # Get all offers
            all_offers = self.data_service.get_offers()
            matched_offers = []
            
            for offer in all_offers:
                score = self._calculate_match_score(offer, user_preferences)
                if score > 0.5:  # Minimum match threshold
                    offer_card = self._convert_to_offer_card(offer, score, user_preferences)
                    matched_offers.append(offer_card)
            
            # Sort by match score and limit results
            matched_offers.sort(key=lambda x: x.match_score or 0, reverse=True)
            return matched_offers[:max_offers]
            
        except Exception as e:
            raise OfferError(f"Failed to match offers: {e}")
    
    def get_offer_details(self, offer_reference: str) -> Optional[DetailedProgram]:
        """Get detailed program for an offer"""
        try:
            # Find the offer by reference
            offers = self.data_service.get_offers()
            offer = None
            
            for o in offers:
                if o.get('reference') == offer_reference:
                    offer = o
                    break
            
            if not offer:
                return None
            
            # Convert to detailed program
            return self._convert_to_detailed_program(offer)
            
        except Exception as e:
            raise OfferError(f"Failed to get offer details: {e}")
    
    def search_offers(self, query: str, limit: int = 10) -> List[OfferCard]:
        """Search offers by query"""
        try:
            raw_offers = self.data_service.search_offers(query, limit)
            offer_cards = []
            
            for offer in raw_offers:
                offer_card = self._convert_to_offer_card(offer, 0.8)  # Default score for search
                offer_cards.append(offer_card)
            
            return offer_cards
            
        except Exception as e:
            raise OfferError(f"Failed to search offers: {e}")
    
    def get_popular_offers(self, limit: int = 5) -> List[OfferCard]:
        """Get popular offers based on rating"""
        try:
            offers = self.data_service.get_offers()
            
            # Sort by rating (if available)
            sorted_offers = sorted(
                offers, 
                key=lambda x: x.get('rating', 0), 
                reverse=True
            )
            
            offer_cards = []
            for offer in sorted_offers[:limit]:
                offer_card = self._convert_to_offer_card(offer, 0.9)  # High score for popular
                offer_cards.append(offer_card)
            
            return offer_cards
            
        except Exception as e:
            raise OfferError(f"Failed to get popular offers: {e}")
    
    def _calculate_match_score(self, offer: Dict[str, Any], preferences: Dict[str, Any]) -> float:
        """Calculate match score between offer and preferences"""
        score = 0.0
        total_weight = 0.0
        
        # Destination match (weight: 0.4)
        if preferences.get('destination'):
            offer_destinations = [d.lower() for d in offer.get('destinations', [])]
            pref_destination = preferences['destination'].lower()
            
            if pref_destination in offer_destinations:
                score += 0.4
            elif any(pref_destination in dest for dest in offer_destinations):
                score += 0.2
            total_weight += 0.4
        
        # Duration match (weight: 0.3)
        if preferences.get('duration'):
            offer_duration = offer.get('duration', 0)
            pref_duration = int(preferences['duration'])
            
            if offer_duration == pref_duration:
                score += 0.3
            elif abs(offer_duration - pref_duration) <= 2:
                score += 0.15
            total_weight += 0.3
        
        # Budget match (weight: 0.2)
        if preferences.get('budget'):
            offer_price = offer.get('price', 0)
            pref_budget = float(preferences['budget'])
            
            if offer_price <= pref_budget:
                score += 0.2
            elif offer_price <= pref_budget * 1.2:
                score += 0.1
            total_weight += 0.2
        
        # Travel style match (weight: 0.1)
        if preferences.get('travel_style'):
            offer_type = offer.get('offer_type', '').lower()
            pref_style = preferences['travel_style'].lower()
            
            if offer_type == pref_style:
                score += 0.1
            total_weight += 0.1
        
        # Normalize score
        if total_weight > 0:
            return score / total_weight
        
        return 0.0
    
    def _convert_to_offer_card(self, offer: Dict[str, Any], match_score: float, preferences: Optional[Dict[str, Any]] = None) -> OfferCard:
        """Convert raw offer to OfferCard"""
        # Generate AI reasoning
        ai_reasoning = self._generate_ai_reasoning(offer, preferences) if preferences else ""
        
        # Generate AI highlights
        ai_highlights = self._generate_ai_highlights(offer)
        
        # Generate why perfect
        why_perfect = self._generate_why_perfect(offer, match_score, preferences) if preferences else ""
        
        return OfferCard(
            product_name=offer.get('title', ''),
            reference=offer.get('reference', ''),
            destinations=[{'city': dest} for dest in offer.get('destinations', [])],
            departure_city=offer.get('departure_city', ''),
            dates=offer.get('dates', []),
            duration=offer.get('duration', 0),
            offer_type=offer.get('offer_type', ''),
            description=offer.get('description', ''),
            highlights=[{'text': highlight} for highlight in offer.get('highlights', [])],
            images=offer.get('images', []),
            price_url=offer.get('price_url'),
            ai_reasoning=ai_reasoning,
            ai_highlights=ai_highlights,
            match_score=match_score,
            why_perfect=why_perfect
        )
    
    def _convert_to_detailed_program(self, offer: Dict[str, Any]) -> DetailedProgram:
        """Convert raw offer to DetailedProgram"""
        return DetailedProgram(
            offer_reference=offer.get('reference', ''),
            product_name=offer.get('title', ''),
            overview={
                'description': offer.get('description', ''),
                'duration': offer.get('duration', 0),
                'destinations': offer.get('destinations', []),
                'departure_city': offer.get('departure_city', '')
            },
            highlights=[{'text': highlight} for highlight in offer.get('highlights', [])],
            included=offer.get('included', []),
            not_included=offer.get('not_included', []),
            itinerary=offer.get('itinerary', []),
            practical_info=offer.get('practical_info', {}),
            pricing=offer.get('pricing', {})
        )
    
    def _generate_ai_reasoning(self, offer: Dict[str, Any], preferences: Dict[str, Any]) -> str:
        """Generate AI reasoning for offer match"""
        reasoning_parts = []
        
        if preferences.get('destination'):
            destinations = offer.get('destinations', [])
            if destinations:
                reasoning_parts.append(f"Destination parfaite: {', '.join(destinations)}")
        
        if preferences.get('duration'):
            duration = offer.get('duration', 0)
            reasoning_parts.append(f"Durée idéale: {duration} jours")
        
        if preferences.get('budget'):
            price = offer.get('price', 0)
            reasoning_parts.append(f"Prix attractif: {price}€")
        
        if preferences.get('travel_style'):
            offer_type = offer.get('offer_type', '')
            reasoning_parts.append(f"Style de voyage: {offer_type}")
        
        return " | ".join(reasoning_parts) if reasoning_parts else "Offre recommandée par notre IA"
    
    def _generate_ai_highlights(self, offer: Dict[str, Any]) -> List[str]:
        """Generate AI highlights for offer"""
        highlights = []
        
        # Add rating highlight
        rating = offer.get('rating')
        if rating and rating >= 4.5:
            highlights.append(f"⭐ Note exceptionnelle: {rating}/5")
        
        # Add duration highlight
        duration = offer.get('duration')
        if duration:
            highlights.append(f"⏱️ Durée optimale: {duration} jours")
        
        # Add price highlight
        price = offer.get('price')
        if price:
            highlights.append(f"💰 Prix compétitif: {price}€")
        
        # Add destination highlight
        destinations = offer.get('destinations', [])
        if destinations:
            highlights.append(f"🌍 Destinations: {', '.join(destinations)}")
        
        return highlights
    
    def _generate_why_perfect(self, offer: Dict[str, Any], match_score: float, preferences: Dict[str, Any]) -> str:
        """Generate why this offer is perfect"""
        if match_score >= 0.9:
            return "Offre parfaitement adaptée à vos critères"
        elif match_score >= 0.7:
            return "Excellente correspondance avec vos préférences"
        elif match_score >= 0.5:
            return "Bonne correspondance avec vos critères"
        else:
            return "Offre intéressante à découvrir" 