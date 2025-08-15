"""
Enhanced Recommendation Engine Component for ASIA.fr Agent
Enhanced version that inherits from original RecommendationEngineComponent
Adds semantic search and AI intelligence while preserving original functionality
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .recommendation_engine import RecommendationEngineComponent
import re

class EnhancedRecommendationEngineComponent(RecommendationEngineComponent):
    """Enhanced recommendation engine that inherits from original and adds advanced features"""
    
    def __init__(self, semantic_service, llm_service, data_service):
        # Call parent constructor to preserve original functionality
        super().__init__(semantic_service, llm_service, data_service)
        
        # Add enhanced features
        self.current_date = datetime.now()
        
        # Override component name and priority
        self.name = "EnhancedRecommendationEngine"
        self.priority = 80
        
        # Country code mapping for destination matching
        self.country_mapping = {
            'japon': 'jp',
            'japan': 'jp',
            'vietnam': 'vn',
            'thailand': 'th',
            'thailande': 'th',
            'sri lanka': 'lk',
            'ceylan': 'lk',
            'cambodia': 'kh',
            'cambodge': 'kh',
            'laos': 'la',
            'myanmar': 'mm',
            'birmanie': 'mm',
            'malaysia': 'my',
            'malaisie': 'my',
            'singapore': 'sg',
            'singapour': 'sg',
            'indonesia': 'id',
            'indonesie': 'id',
            'philippines': 'ph',
            'taiwan': 'tw',
            'china': 'cn',
            'chine': 'cn',
            'india': 'in',
            'inde': 'in',
            'nepal': 'np',
            'bhutan': 'bt',
            'mongolia': 'mn',
            'kazakhstan': 'kz',
            'uzbekistan': 'uz',
            'kyrgyzstan': 'kg',
            'tajikistan': 'tj',
            'turkmenistan': 'tm',
            'afghanistan': 'af',
            'pakistan': 'pk',
            'bangladesh': 'bd',
            'maldives': 'mv',
            'maldive': 'mv'
        }
    
    async def process(self, context):
        """Enhanced process that uses original logic + semantic search capabilities"""
        try:
            self.logger.info(f"🎯 Enhanced recommendation processing")
            
            # Check if semantic search is enabled
            semantic_search_enabled = context.get_metadata('semantic_search_enabled', False)
            search_query = context.get_metadata('search_query', '')
            
            if semantic_search_enabled and search_query:
                # Use enhanced semantic search
                offers = await self._semantic_search_recommendations(search_query, context.user_preferences, context)
            else:
                # Use original recommendation logic
                offers = await super()._generate_offers(context.user_preferences)
            
            # Enhance offers with AI intelligence
            enhanced_offers = await self._enhance_offers_with_ai(offers, context.user_preferences, context)
            
            # Store results in context
            context.add_metadata('offers', enhanced_offers)
            context.add_metadata('recommendation_count', len(enhanced_offers))
            context.add_metadata('recommendation_strategy', 'semantic' if semantic_search_enabled else 'traditional')
            
            self.logger.info(f"🎯 Generated {len(enhanced_offers)} enhanced recommendations")
            
            return context
            
        except Exception as e:
            self.log_error(context, e)
            # Fallback to original recommendation logic
            return await super().process(context)
    
    async def _semantic_search_recommendations(self, search_query: str, user_preferences: Dict[str, Any], context) -> List[Dict[str, Any]]:
        """Get recommendations using semantic search"""
        try:
            self.logger.info(f"🔍 Semantic search for: {search_query}")
            
            # Get semantic search results
            semantic_results = await self.semantic_service.search_offers(search_query, top_k=10)
            
            # Filter and enhance results based on user preferences
            filtered_results = await self._filter_semantic_results(semantic_results, user_preferences)
            
            # Limit to requested number
            offer_count = context.get_metadata('orchestration_result', {}).get('offer_count', 3)
            return filtered_results[:offer_count]
            
        except Exception as e:
            self.logger.error(f"❌ Semantic search failed: {e}")
            return []
    
    async def _filter_semantic_results(self, semantic_results: List[Dict[str, Any]], user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter semantic search results based on user preferences"""
        try:
            filtered_results = []
            
            for result in semantic_results:
                offer = result.get('offer', {})
                
                # Check if offer matches user preferences
                if self._offer_matches_preferences(offer, user_preferences):
                    # Add semantic score to offer
                    offer['semantic_score'] = result.get('score', 0)
                    filtered_results.append(offer)
            
            # Sort by semantic score
            filtered_results.sort(key=lambda x: x.get('semantic_score', 0), reverse=True)
            
            return filtered_results
            
        except Exception as e:
            self.logger.error(f"❌ Semantic result filtering failed: {e}")
            return semantic_results
    
    def _offer_matches_preferences(self, offer: Dict[str, Any], user_preferences: Dict[str, Any]) -> bool:
        """Check if an offer matches user preferences with enhanced matching"""
        try:
            # Check destination with country mapping
            if user_preferences.get('destination'):
                destination = user_preferences['destination'].lower()
                offer_destinations = [dest.get('country', '').lower() for dest in offer.get('destinations', [])]
                
                # Try exact match first
                if destination in offer_destinations:
                    pass  # Match found
                # Try country code mapping
                elif destination in self.country_mapping:
                    country_code = self.country_mapping[destination]
                    if country_code in offer_destinations:
                        pass  # Match found
                    else:
                        return False
                # Try partial match
                elif not any(destination in dest for dest in offer_destinations):
                    return False
            
            # Check budget (numeric amount filtering)
            if user_preferences.get('budget_amount'):
                try:
                    budget_amount = float(user_preferences['budget_amount'])
                    offer_price = offer.get('price', {}).get('amount', 0)
                    
                    # Allow offers within 20% of the budget (both above and below)
                    budget_tolerance = budget_amount * 0.2
                    min_price = budget_amount - budget_tolerance
                    max_price = budget_amount + budget_tolerance
                    
                    if offer_price < min_price or offer_price > max_price:
                        return False
                except (ValueError, TypeError):
                    # If budget amount is not a valid number, skip budget filtering
                    pass
            
            # Check duration (less strict filtering)
            if user_preferences.get('duration_range'):
                duration_range = user_preferences['duration_range']
                offer_duration = offer.get('duration', '')
                
                # Extract days from duration string
                days_match = re.search(r'(\d+)\s*jours?', offer_duration)
                if days_match:
                    offer_days = int(days_match.group(1))
                    
                    # More flexible duration ranges
                    if duration_range == '1-7' and offer_days > 10:
                        return False
                    elif duration_range == '8-14' and offer_days > 20:
                        return False
                    elif duration_range == '15-30' and offer_days > 35:
                        return False
                    elif duration_range == '30+' and offer_days < 25:
                        return False
            
            # Check travel dates (required field)
            if user_preferences.get('travel_dates'):
                travel_dates = user_preferences['travel_dates']
                offer_dates = offer.get('dates', [])
                
                # Enhanced date matching
                if offer_dates and travel_dates:
                    # Check if any offer date contains the travel date preference
                    date_match = any(travel_dates.lower() in date.lower() for date in offer_dates)
                    if not date_match:
                        return False
            else:
                # Travel dates are required - if not provided, don't show offers
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Preference matching failed: {e}")
            return True  # Default to include if matching fails
    
    async def _enhance_offers_with_ai(self, offers: List[Dict[str, Any]], user_preferences: Dict[str, Any], context) -> List[Dict[str, Any]]:
        """Enhance offers with AI-generated explanations and recommendations"""
        try:
            enhanced_offers = []
            
            for offer in offers:
                enhanced_offer = offer.copy()
                
                # Add AI-generated explanation
                explanation = await self._generate_offer_explanation(offer, user_preferences)
                enhanced_offer['ai_explanation'] = explanation
                
                # Add recommendation score
                score = await self._calculate_recommendation_score(offer, user_preferences)
                enhanced_offer['recommendation_score'] = score
                
                enhanced_offers.append(enhanced_offer)
            
            # Sort by recommendation score
            enhanced_offers.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
            
            return enhanced_offers
            
        except Exception as e:
            self.logger.error(f"❌ Offer enhancement failed: {e}")
            return offers
    
    async def _generate_offer_explanation(self, offer: Dict[str, Any], user_preferences: Dict[str, Any]) -> str:
        """Generate AI explanation for why this offer is recommended"""
        try:
            prompt = f"""
You are ASIA.fr Agent. Explain why this offer matches the user's preferences.

OFFER:
- Name: {offer.get('product_name', '')}
- Destinations: {[dest.get('country', '') for dest in offer.get('destinations', [])]}
- Duration: {offer.get('duration', '')}
- Price: {offer.get('price', {}).get('amount', 0)}€
- Description: {offer.get('description', '')[:200]}...

USER PREFERENCES:
{json.dumps(user_preferences, indent=2, ensure_ascii=False)}

Provide a brief, friendly explanation in French (max 100 words) of why this offer is a good match.

RESPONSE:
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = await self.llm_service.create_reasoning_completion(messages, stream=False)
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"❌ Explanation generation failed: {e}")
            return "Cette offre correspond à vos préférences de voyage."
    
    async def _calculate_recommendation_score(self, offer: Dict[str, Any], user_preferences: Dict[str, Any]) -> float:
        """Calculate recommendation score for an offer"""
        try:
            score = 0.0
            
            # Destination match (30 points)
            if user_preferences.get('destination'):
                destination = user_preferences['destination'].lower()
                offer_destinations = [dest.get('country', '').lower() for dest in offer.get('destinations', [])]
                if destination in offer_destinations:
                    score += 30
                elif any(destination in dest for dest in offer_destinations):
                    score += 20
            
            # Budget match (25 points)
            if user_preferences.get('budget_amount'):
                try:
                    budget_amount = float(user_preferences['budget_amount'])
                    offer_price = offer.get('price', {}).get('amount', 0)
                    
                    # Calculate budget proximity score
                    budget_diff = abs(offer_price - budget_amount)
                    budget_percentage = budget_diff / budget_amount if budget_amount > 0 else 1
                    
                    if budget_percentage <= 0.1:  # Within 10%
                        score += 25
                    elif budget_percentage <= 0.2:  # Within 20%
                        score += 20
                    elif budget_percentage <= 0.3:  # Within 30%
                        score += 15
                    else:
                        score += 5  # Partial match
                except (ValueError, TypeError):
                    pass
            
            # Duration match (20 points)
            if user_preferences.get('duration_range'):
                duration_range = user_preferences['duration_range']
                offer_duration = offer.get('duration', '')
                
                days_match = re.search(r'(\d+)\s*jours?', offer_duration)
                if days_match:
                    offer_days = int(days_match.group(1))
                    
                    if duration_range == '1-7' and offer_days <= 7:
                        score += 20
                    elif duration_range == '8-14' and 8 <= offer_days <= 14:
                        score += 20
                    elif duration_range == '15-30' and 15 <= offer_days <= 30:
                        score += 20
                    elif duration_range == '30+' and offer_days >= 30:
                        score += 20
                    else:
                        score += 10  # Partial match
            
            # Activity match (15 points)
            if user_preferences.get('activities'):
                user_activities = set(user_preferences['activities'])
                offer_activities = set(self._extract_activities_from_offer(offer))
                
                if user_activities & offer_activities:  # Intersection
                    score += 15
            
            # Date match (10 points)
            if user_preferences.get('travel_dates') and offer.get('dates'):
                travel_dates = user_preferences['travel_dates'].lower()
                offer_dates = [date.lower() for date in offer.get('dates', [])]
                
                if any(travel_dates in date for date in offer_dates):
                    score += 10
            
            return min(score, 100.0)  # Cap at 100
            
        except Exception as e:
            self.logger.error(f"❌ Score calculation failed: {e}")
            return 50.0  # Default score
    
    def _extract_activities_from_offer(self, offer: Dict[str, Any]) -> List[str]:
        """Extract activities from offer description and highlights"""
        activities = []
        
        # Extract from description
        description = offer.get('description', '').lower()
        if 'plage' in description or 'beach' in description:
            activities.append('beach')
        if 'culture' in description or 'temple' in description:
            activities.append('culture')
        if 'aventure' in description or 'adventure' in description:
            activities.append('adventure')
        if 'détente' in description or 'relaxation' in description:
            activities.append('relaxation')
        if 'gastronomie' in description or 'cuisine' in description:
            activities.append('gastronomy')
        if 'nature' in description or 'paysage' in description:
            activities.append('nature')
        
        # Extract from highlights
        highlights = offer.get('highlights', [])
        for highlight in highlights:
            text = highlight.get('text', '').lower()
            if 'plage' in text or 'beach' in text:
                activities.append('beach')
            if 'culture' in text or 'temple' in text:
                activities.append('culture')
            if 'aventure' in text or 'adventure' in text:
                activities.append('adventure')
            if 'détente' in text or 'relaxation' in text:
                activities.append('relaxation')
            if 'gastronomie' in text or 'cuisine' in text:
                activities.append('gastronomy')
            if 'nature' in text or 'paysage' in text:
                activities.append('nature')
        
        return list(set(activities)) 