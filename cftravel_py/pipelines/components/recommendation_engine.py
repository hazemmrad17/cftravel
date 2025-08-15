"""
Recommendation Engine Component for ASIA.fr Agent
Handles offer matching, ranking, and recommendation generation
"""

import json
import hashlib
from typing import Dict, Any, List, Optional
from ..core import PipelineComponent, PipelineContext, PipelineState
from services.optimized_semantic_service import OptimizedSemanticService
from services.llm_service import LLMService
from services.data_service import DataService

class RecommendationEngineComponent(PipelineComponent):
    """Handles offer recommendation and matching"""
    
    def __init__(self, semantic_service: OptimizedSemanticService, llm_service: LLMService, data_service: DataService):
        super().__init__("RecommendationEngine", priority=80)
        self.semantic_service = semantic_service
        self.llm_service = llm_service
        self.data_service = data_service
        self._offers_cache = {}
        self._last_preferences = {}
    
    def is_required(self, context: PipelineContext) -> bool:
        """Required when user wants to see offers"""
        return context.get_metadata('should_show_offers', False)
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Generate personalized offer recommendations"""
        try:
            # Check cache and clear if preferences changed
            self._manage_cache(context.user_preferences)
            
            # Generate offers using the enhanced pipeline
            offers = await self._generate_offers(context.user_preferences)
            
            # Store offers in context
            context.add_metadata('offers', offers)
            context.add_metadata('offer_count', len(offers))
            
            self.logger.info(f"🎯 Generated {len(offers)} personalized offers")
            
            return context
            
        except Exception as e:
            self.log_error(context, e)
            # Fallback to basic offers
            context.add_metadata('offers', await self._fallback_offers(context.user_preferences))
            return context
    
    def _manage_cache(self, preferences: Dict[str, Any]):
        """Manage offer cache based on preference changes"""
        # Clear cache if preferences have changed significantly
        if self._last_preferences != preferences:
            if self._offers_cache:
                self.logger.info("🔄 Preferences changed, clearing cache")
                self._offers_cache.clear()
        
        # Store current preferences for next comparison
        self._last_preferences = preferences.copy()
    
    async def _generate_offers(self, preferences: Dict[str, Any], offer_count: int = 3) -> List[Dict]:
        """Enhanced offer generation pipeline"""
        # Create cache key based on preferences
        cache_key = self._create_cache_key(preferences)
        
        # Check cache first
        if cache_key in self._offers_cache:
            self.logger.info("⚡ Using cached offers")
            return self._offers_cache[cache_key]
        
        try:
            # Step 1: Build enhanced query for sentence transformer
            query = self._build_enhanced_query(preferences)
            self.logger.info(f"🔍 Building query for sentence transformer: {query}")
            
            # Step 2: Use sentence transformer to find top 10 closest offers
            top_10_offers = await self._vector_search_offers(query, top_k=10)
            self.logger.info(f"🔍 Sentence transformer found {len(top_10_offers)} closest offers")
            
            if not top_10_offers:
                self.logger.warning("❌ No offers found by sentence transformer")
                return []
            
            # Step 3: Use LLM matcher to rank the top 10 offers
            ranked_offers = await self._ai_refine_offers(top_10_offers, preferences, max_offers=offer_count)
            self.logger.info(f"🔍 LLM matcher ranked and selected {len(ranked_offers)} best offers")
            
            if ranked_offers:
                # Cache the result
                self._offers_cache[cache_key] = ranked_offers
                self.logger.info(f"✅ Pipeline complete: {len(ranked_offers)} offers ready for display")
                return ranked_offers
            else:
                self.logger.warning("⚠️ No offers selected by LLM matcher")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Error in offer pipeline: {e}")
            return await self._fallback_offers(preferences, offer_count)
    
    def _create_cache_key(self, preferences: Dict[str, Any]) -> str:
        """Create a cache key based on preferences"""
        sorted_prefs = sorted(preferences.items())
        return hashlib.md5(str(sorted_prefs).encode()).hexdigest()
    
    def _build_enhanced_query(self, preferences: Dict[str, Any]) -> str:
        """Build enhanced search query from preferences"""
        query_parts = []
        
        # Enhanced destination mapping
        destination_mappings = {
            'japan': ['Japon', 'Tokyo', 'Kyoto', 'Osaka', 'Japonais', 'Japon traditionnel', 'Japon culturel'],
            'japon': ['Japon', 'Tokyo', 'Kyoto', 'Osaka', 'Japonais', 'Japon traditionnel', 'Japon culturel'],
            'philippines': ['Philippines', 'Manille', 'Cebu', 'Palawan', 'Philippin', 'Philippines culturel'],
            'philippine': ['Philippines', 'Manille', 'Cebu', 'Palawan', 'Philippin', 'Philippines culturel'],
            'thailand': ['Thaïlande', 'Bangkok', 'Phuket', 'Chiang Mai', 'Thaï', 'Thaïlande culturel'],
            'thaïlande': ['Thaïlande', 'Bangkok', 'Phuket', 'Chiang Mai', 'Thaï', 'Thaïlande culturel'],
            'vietnam': ['Vietnam', 'Hanoï', 'Ho Chi Minh', 'Halong', 'Vietnamien', 'Vietnam culturel'],
            'china': ['Chine', 'Pékin', 'Shanghai', 'Chinois', 'Chine culturel'],
            'chine': ['Chine', 'Pékin', 'Shanghai', 'Chinois', 'Chine culturel'],
            'india': ['Inde', 'Delhi', 'Mumbai', 'Indien', 'Inde culturel'],
            'inde': ['Inde', 'Delhi', 'Mumbai', 'Indien', 'Inde culturel'],
            'indonesia': ['Indonésie', 'Bali', 'Jakarta', 'Indonésien', 'Indonésie culturel'],
            'indonésie': ['Indonésie', 'Bali', 'Jakarta', 'Indonésien', 'Indonésie culturel'],
            'malaysia': ['Malaisie', 'Kuala Lumpur', 'Malaisien', 'Malaisie culturel'],
            'malaisie': ['Malaisie', 'Kuala Lumpur', 'Malaisien', 'Malaisie culturel'],
            'singapore': ['Singapour', 'Singapourien', 'Singapour culturel'],
            'singapour': ['Singapour', 'Singapourien', 'Singapour culturel'],
            'cambodia': ['Cambodge', 'Phnom Penh', 'Cambodgien', 'Cambodge culturel'],
            'cambodge': ['Cambodge', 'Phnom Penh', 'Cambodgien', 'Cambodge culturel'],
            'laos': ['Laos', 'Vientiane', 'Laotien', 'Laos culturel'],
            'myanmar': ['Myanmar', 'Rangoon', 'Myanmarais', 'Myanmar culturel'],
            'sri lanka': ['Sri Lanka', 'Colombo', 'Sri Lankais', 'Sri Lanka culturel'],
            'nepal': ['Népal', 'Katmandou', 'Népalais', 'Népal culturel'],
            'népal': ['Népal', 'Katmandou', 'Népalais', 'Népal culturel'],
            'bhutan': ['Bhoutan', 'Thimphou', 'Bhoutanais', 'Bhoutan culturel'],
            'mongolia': ['Mongolie', 'Oulan-Bator', 'Mongol', 'Mongolie culturel'],
            'mongolie': ['Mongolie', 'Oulan-Bator', 'Mongol', 'Mongolie culturel'],
            'maldives': ['Maldives', 'Maldive', 'Îles Maldives', 'Atoll Maldives', 'Plage paradisiaque', 'Eau turquoise', 'Bungalow sur pilotis', 'Océan Indien', 'Atoll', 'Plage de sable blanc', 'Snorkeling', 'Plongée', 'Resort de luxe'],
            'maldive': ['Maldives', 'Maldive', 'Îles Maldives', 'Atoll Maldives', 'Plage paradisiaque', 'Eau turquoise', 'Bungalow sur pilotis', 'Océan Indien', 'Atoll', 'Plage de sable blanc', 'Snorkeling', 'Plongée', 'Resort de luxe'],
            'australia': ['Australie', 'Sydney', 'Melbourne', 'Perth', 'Adélaïde', 'Darwin', 'Cairns', 'Brisbane', 'Australien', 'Australie culturel', 'Outback', 'Great Barrier Reef', 'Uluru', 'Kangaroo Island', 'Gold Coast'],
            'australie': ['Australie', 'Sydney', 'Melbourne', 'Perth', 'Adélaïde', 'Darwin', 'Cairns', 'Brisbane', 'Australien', 'Australie culturel', 'Outback', 'Great Barrier Reef', 'Uluru', 'Kangaroo Island', 'Gold Coast']
        }
        
        # Add destination terms with enhanced matching
        if preferences.get('destination'):
            destination_lower = preferences['destination'].lower()
            if destination_lower in destination_mappings:
                query_parts.extend(destination_mappings[destination_lower])
                # Add additional context for better matching
                query_parts.extend([
                    f"circuit {destination_lower}",
                    f"voyage {destination_lower}",
                    f"séjour {destination_lower}",
                    f"découverte {destination_lower}",
                    f"aventure {destination_lower}",
                    f"expérience {destination_lower}",
                    f"destination {destination_lower}",
                    f"pays {destination_lower}",
                    f"région {destination_lower}"
                ])
            else:
                # For unknown destinations, create comprehensive search terms
                query_parts.extend([
                    f"voyage {preferences['destination']}",
                    f"circuit {preferences['destination']}",
                    f"découverte {preferences['destination']}",
                    f"séjour {preferences['destination']}",
                    f"aventure {preferences['destination']}",
                    f"destination {preferences['destination']}",
                    f"pays {preferences['destination']}",
                    f"région {preferences['destination']}",
                    f"{preferences['destination']} culturel",
                    f"{preferences['destination']} traditionnel",
                    f"{preferences['destination']} authentique"
                ])
        
        # Add other preferences with enhanced context
        if preferences.get('duration'):
            duration = preferences['duration']
            query_parts.append(f"durée {duration}")
            if 'semaine' in duration.lower() or 'week' in duration.lower():
                query_parts.append("circuit organisé")
            if 'jour' in duration.lower() or 'day' in duration.lower():
                query_parts.append("voyage guidé")
        
        if preferences.get('style'):
            style = preferences['style']
            query_parts.append(f"style {style}")
            if 'culturel' in style.lower() or 'cultural' in style.lower():
                query_parts.extend(["découverte culturelle", "sites historiques", "traditions locales"])
            elif 'aventure' in style.lower() or 'adventure' in style.lower():
                query_parts.extend(["aventure", "expériences uniques", "activités outdoor"])
            elif 'détente' in style.lower() or 'relax' in style.lower():
                query_parts.extend(["détente", "plages", "bien-être"])
            elif 'gastronomie' in style.lower() or 'food' in style.lower():
                query_parts.extend(["gastronomie", "cuisine locale", "dégustations"])
        
        # Budget is optional - only add if clearly specified
        if preferences.get('budget_amount'):
            try:
                budget_amount = float(preferences['budget_amount'])
                # Add budget context to query
                if budget_amount < 2000:
                    query_parts.append("économique")
                elif budget_amount > 5000:
                    query_parts.append("luxe premium")
                else:
                    query_parts.append("moyen de gamme")
            except (ValueError, TypeError):
                # If budget amount is not a valid number, skip budget constraints
                pass
        
        if preferences.get('group_size'):
            group_size = preferences['group_size']
            query_parts.append(f"groupe {group_size}")
            if 'petit' in group_size.lower() or 'small' in group_size.lower():
                query_parts.append("petit groupe")
            elif 'grand' in group_size.lower() or 'large' in group_size.lower():
                query_parts.append("groupe important")
        
        if preferences.get('travel_dates'):
            travel_dates = preferences['travel_dates']
            query_parts.append(f"période {travel_dates}")
        
        # Add enhanced context words
        query_parts.extend([
            "circuit organisé", 
            "voyage guidé", 
            "découverte culturelle",
            "expérience authentique",
            "voyage personnalisé",
            "circuit premium"
        ])
        
        # Remove duplicates and join
        unique_parts = list(dict.fromkeys(query_parts))
        return " ".join(unique_parts)
    
    async def _vector_search_offers(self, query: str, top_k: int = 10) -> List[Dict]:
        """Use sentence transformer to find similar offers"""
        try:
            self.logger.info(f"🔍 Searching for query: '{query}' with top_k={top_k}")
            offers = self.semantic_service.search(query, top_k=top_k)
            
            self.logger.info(f"🔍 Semantic service returned {len(offers)} offers")
            
            # Log first few offers for debugging
            for i, offer in enumerate(offers[:3]):
                self.logger.info(f"🔍 Offer {i+1}: {offer.get('product_name', 'Unknown')}")
            
            # Deduplicate offers by product name
            seen_product_names = set()
            unique_offers = []
            
            for offer in offers:
                product_name = offer.get('product_name', '')
                if product_name and product_name not in seen_product_names:
                    unique_offers.append(offer)
                    seen_product_names.add(product_name)
            
            self.logger.info(f"🔍 Found {len(offers)} offers, {len(unique_offers)} unique after deduplication")
            return unique_offers
            
        except Exception as e:
            self.logger.error(f"❌ Vector search failed: {e}")
            # Fallback to basic search
            self.logger.info("🔄 Falling back to basic search...")
            return await self._fallback_offers({}, top_k)
    
    async def _ai_refine_offers(self, vector_results: List[Dict], preferences: Dict[str, Any], max_offers: int = 3) -> List[Dict]:
        """Use LLM to rank and select the best offers"""
        try:
            if not vector_results:
                return []
            
            # Create simplified offers for LLM processing
            simplified_offers = []
            for offer in vector_results:
                simplified_offer = {
                    'product_name': offer.get('product_name', ''),
                    'description': offer.get('description', '')[:200],  # Truncate for token efficiency
                    'destinations': offer.get('destinations', []),
                    'duration': offer.get('duration', ''),
                    'price_range': offer.get('price_range', ''),
                    'offer_type': offer.get('offer_type', ''),
                    'highlights': offer.get('highlights', [])[:3]  # Limit highlights
                }
                simplified_offers.append(simplified_offer)
            
            # Build LLM prompt for ranking
            prompt = self._build_ranking_prompt(simplified_offers, preferences)
            
            # Get LLM ranking
            messages = [{"role": "user", "content": prompt}]
            response = await self.llm_service.create_matcher_completion(messages, stream=False)
            ranked_offers = self._parse_ranking_response(response, vector_results)
            
            return ranked_offers[:max_offers]
            
        except Exception as e:
            self.logger.error(f"❌ AI refinement failed: {e}")
            return vector_results[:max_offers]  # Fallback to original order
    
    def _build_ranking_prompt(self, offers: List[Dict], preferences: Dict[str, Any]) -> str:
        """Build prompt for LLM offer ranking"""
        return f"""
You are an expert travel offer matcher. Rank these offers based on user preferences. You MUST RESPOND IN FRENCH.

USER PREFERENCES: {json.dumps(preferences, indent=2, ensure_ascii=False)}

AVAILABLE OFFERS:
{json.dumps(offers, indent=2, ensure_ascii=False)}

RANK the offers by relevance to user preferences and return a JSON array with:
- product_name: the offer name
- match_score: 0.0-1.0 (how well it matches preferences)
- reasoning: brief explanation in French

RESPOND ONLY WITH VALID JSON ARRAY:
"""
    
    def _parse_ranking_response(self, response: str, original_offers: List[Dict]) -> List[Dict]:
        """Parse LLM ranking response and return ranked offers"""
        try:
            # Extract JSON array from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                ranking = json.loads(json_match.group())
                
                # Create mapping of product names to original offers
                offer_map = {offer['product_name']: offer for offer in original_offers}
                
                # Build ranked list with deduplication
                ranked_offers = []
                seen_product_names = set()
                
                for ranked_item in ranking:
                    product_name = ranked_item.get('product_name')
                    if product_name in offer_map and product_name not in seen_product_names:
                        offer = offer_map[product_name].copy()
                        offer['match_score'] = ranked_item.get('match_score', 0.5)
                        offer['match_reasoning'] = ranked_item.get('reasoning', '')
                        ranked_offers.append(offer)
                        seen_product_names.add(product_name)
                
                # Sort by match score
                ranked_offers.sort(key=lambda x: x.get('match_score', 0), reverse=True)
                return ranked_offers
            else:
                self.logger.warning("❌ No JSON array found in ranking response")
                return original_offers[:3]
                
        except Exception as e:
            self.logger.error(f"❌ Failed to parse ranking response: {e}")
            return original_offers[:3]
    
    async def _fallback_offers(self, preferences: Dict[str, Any], offer_count: int = 3) -> List[Dict]:
        """Fallback offer selection when main pipeline fails"""
        try:
            # Get all offers from data service
            all_offers = self.data_service.get_offers()
            
            # Simple keyword matching
            matching_offers = []
            for offer in all_offers:
                score = self._calculate_simple_match_score(offer, preferences)
                if score > 0.3:  # Minimum threshold
                    offer_with_score = offer.copy()
                    offer_with_score['match_score'] = score
                    matching_offers.append(offer_with_score)
            
            # Sort by score and return top offers
            matching_offers.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            return matching_offers[:offer_count]
            
        except Exception as e:
            self.logger.error(f"❌ Fallback offer selection failed: {e}")
            return []
    
    def _calculate_simple_match_score(self, offer: Dict, preferences: Dict[str, Any]) -> float:
        """Calculate simple match score for fallback"""
        score = 0.0
        
        # Destination matching
        if preferences.get('destination'):
            offer_text = f"{offer.get('product_name', '')} {offer.get('description', '')}"
            if preferences['destination'].lower() in offer_text.lower():
                score += 0.4
        
        # Duration matching
        if preferences.get('duration'):
            offer_duration = offer.get('duration', '')
            if preferences['duration'] in offer_duration:
                score += 0.3
        
        # Style matching
        if preferences.get('style'):
            offer_type = offer.get('offer_type', '')
            if preferences['style'].lower() in offer_type.lower():
                score += 0.2
        
        # Budget matching
        if preferences.get('budget_amount'):
            try:
                budget_amount = float(preferences['budget_amount'])
                offer_price = offer.get('price', {}).get('amount', 0)
                
                # Allow offers within 30% of the budget
                budget_tolerance = budget_amount * 0.3
                if abs(offer_price - budget_amount) <= budget_tolerance:
                    score += 0.1
            except (ValueError, TypeError):
                pass
        
        return min(score, 1.0) 