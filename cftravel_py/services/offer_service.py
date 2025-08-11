"""
Offer service for ASIA.fr Agent
"""

import logging
from typing import Dict, Any, List, Optional
from core.exceptions import OfferError
from models.data_models import OfferCard, DetailedProgram
from services.data_service import DataService

logger = logging.getLogger(__name__)

class OfferService:
    """Service for offer matching and processing"""
    
    def __init__(self, data_service: DataService):
        self.data_service = data_service
        
    def match_offers(self, user_preferences: Dict[str, Any], max_offers: int = 3) -> List[OfferCard]:
        """Match offers based on user preferences"""
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            logger.info(f"🔍 Matching offers with preferences: {user_preferences}")
            
            # Extract preferences
            destination = user_preferences.get('destination')
            duration = user_preferences.get('duration')
            budget = user_preferences.get('budget')
            travel_style = user_preferences.get('travel_style') or user_preferences.get('style')  # Handle both field names
            
            logger.info(f"🔍 Extracted: dest={destination}, duration={duration}, budget={budget}, style={travel_style}")
            
            # Get all offers
            all_offers = self.data_service.get_offers()
            logger.info(f"🔍 Processing {len(all_offers)} offers")
            
            matched_offers = []
            
            for i, offer in enumerate(all_offers):
                try:
                    score = self._calculate_match_score(offer, user_preferences)
                    if score > 0.5:  # Minimum match threshold
                        offer_card = self._convert_to_offer_card(offer, score, user_preferences)
                        matched_offers.append(offer_card)
                except Exception as e:
                    logger.error(f"❌ Error processing offer {i}: {e}")
                    logger.error(f"❌ Offer data: {offer}")
                    raise
            
            # Sort by match score and limit results
            matched_offers.sort(key=lambda x: x.match_score or 0, reverse=True)
            result = matched_offers[:max_offers]
            logger.info(f"🔍 Found {len(result)} matching offers")
            return result
            
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
            # Country name to country code mapping
            country_mapping = {
                'japan': 'jp',
                'japon': 'jp',
                'vietnam': 'vn',
                'thailand': 'th',
                'thailande': 'th',
                'cambodia': 'kh',
                'cambodge': 'kh',
                'laos': 'la',
                'myanmar': 'mm',
                'singapore': 'sg',
                'malaysia': 'my',
                'indonesia': 'id',
                'philippines': 'ph',
                'china': 'cn',
                'chine': 'cn',
                'india': 'in',
                'nepal': 'np',
                'bhutan': 'bt',
                'sri lanka': 'lk',
                'maldives': 'mv',
                'jordan': 'jo',
                'jordanie': 'jo',
                'lebanon': 'lb',
                'syria': 'sy',
                'iraq': 'iq',
                'iran': 'ir',
                'oman': 'om',
                'yemen': 'ye',
                'saudi arabia': 'sa',
                'arabie saoudite': 'sa',
                'kuwait': 'kw',
                'qatar': 'qa',
                'bahrain': 'bh',
                'uae': 'ae',
                'emirates': 'ae'
            }
            
            # Destinations are dictionaries with 'city' and 'country' fields
            offer_destinations = []
            for dest in offer.get('destinations', []):
                if isinstance(dest, dict):
                    offer_destinations.append(dest.get('city', '').lower())
                    offer_destinations.append(dest.get('country', '').lower())
                else:
                    offer_destinations.append(str(dest).lower())
            
            pref_destination = preferences['destination'].lower()
            
            # Check if preference matches country code directly
            if pref_destination in offer_destinations:
                score += 0.4
            # Check if preference matches country name (mapped to country code)
            elif pref_destination in country_mapping:
                country_code = country_mapping[pref_destination]
                if country_code in offer_destinations:
                    score += 0.4
            # Check for partial matches
            elif any(pref_destination in dest for dest in offer_destinations):
                score += 0.2
            total_weight += 0.4
        
        # Duration match (weight: 0.3)
        if preferences.get('duration'):
            offer_duration = offer.get('duration', 0)
            pref_duration = preferences['duration']
            
            # Handle duration as string or numeric
            if isinstance(pref_duration, str):
                try:
                    duration_value = int(pref_duration)
                except ValueError:
                    duration_value = 7  # Default to 7 days
            else:
                duration_value = int(pref_duration)
            
            if offer_duration == duration_value:
                score += 0.3
            elif abs(offer_duration - duration_value) <= 2:
                score += 0.15
            total_weight += 0.3
        
        # Budget match (weight: 0.2)
        if preferences.get('budget'):
            offer_price = offer.get('price', 0)
            pref_budget = preferences['budget']
            
            # Handle budget as string (low, medium, high) or numeric
            if isinstance(pref_budget, str):
                pref_budget_lower = pref_budget.lower()
                if pref_budget_lower == 'low':
                    budget_value = 1000
                elif pref_budget_lower == 'medium':
                    budget_value = 2500
                elif pref_budget_lower == 'high':
                    budget_value = 5000
                else:
                    # Try to convert to float if it's a numeric string
                    try:
                        budget_value = float(pref_budget)
                    except ValueError:
                        budget_value = 2500  # Default to medium
            else:
                budget_value = float(pref_budget)
            
            if offer_price <= budget_value:
                score += 0.2
            elif offer_price <= budget_value * 1.2:
                score += 0.1
            total_weight += 0.2
        
        # Travel style match (weight: 0.1)
        travel_style = preferences.get('travel_style') or preferences.get('style')
        if travel_style:
            offer_type = offer.get('offer_type', '').lower()
            pref_style = travel_style.lower()
            
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
            product_name=offer.get('product_name', ''),
            reference=offer.get('reference', ''),
            destinations=offer.get('destinations', []),
            departure_city=offer.get('departure_city', ''),
            dates=offer.get('dates', []),
            duration=offer.get('duration', 0),
            offer_type=offer.get('offer_type', ''),
            description=offer.get('description', ''),
            highlights=offer.get('highlights', []),
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
            product_name=offer.get('product_name', ''),
            overview={
                'description': offer.get('description', ''),
                'duration': offer.get('duration', 0),
                'destinations': offer.get('destinations', []),
                'departure_city': offer.get('departure_city', '')
            },
            highlights=offer.get('highlights', []),
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
                # Destinations are dictionaries with 'city' and 'country' fields
                dest_names = []
                for dest in destinations:
                    if isinstance(dest, dict):
                        city = dest.get('city', '')
                        country = dest.get('country', '')
                        if city and country:
                            dest_names.append(f"{city} ({country})")
                        elif city:
                            dest_names.append(city)
                        elif country:
                            dest_names.append(country)
                    else:
                        dest_names.append(str(dest))
                
                if dest_names:
                    reasoning_parts.append(f"Destination parfaite: {', '.join(dest_names)}")
        
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
            # Destinations are dictionaries with 'city' and 'country' fields
            dest_names = []
            for dest in destinations:
                if isinstance(dest, dict):
                    city = dest.get('city', '')
                    country = dest.get('country', '')
                    if city and country:
                        dest_names.append(f"{city} ({country})")
                    elif city:
                        dest_names.append(city)
                    elif country:
                        dest_names.append(country)
                else:
                    dest_names.append(str(dest))
            
            if dest_names:
                highlights.append(f"🌍 Destinations: {', '.join(dest_names)}")
        
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