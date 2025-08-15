"""
Travel Planning Orchestrator Component
Handles the preference-confirmation-search flow with no hardcoded conditions
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class TravelPreference:
    """Structured travel preference data"""
    destination: Optional[str] = None
    duration: Optional[str] = None
    budget_amount: Optional[float] = None
    group_size: Optional[str] = None
    style: Optional[str] = None
    travel_dates: Optional[str] = None
    special_requirements: Optional[List[str]] = None

@dataclass
class SearchResult:
    """Search result with matching score"""
    offer: Dict[str, Any]
    match_score: float
    budget_indicator: str
    relevance_score: float

class TravelOrchestrator:
    """
    AI Travel Planning Orchestrator
    
    Implements the preference-confirmation-search flow:
    1. Extract preferences from user input
    2. Create natural language summary
    3. Ask for confirmation
    4. Search and recommend offers
    5. Handle modifications iteratively
    """
    
    def __init__(self, llm_service, data_service, logger=None):
        self.llm_service = llm_service
        self.data_service = data_service
        self.logger = logger or logging.getLogger(__name__)
        
        # Conversation state
        self.current_preferences = TravelPreference()
        self.confirmation_pending = False
        self.last_summary = None
        
    async def process_user_input(self, user_input: str, conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestrator method - processes user input and determines next action
        """
        try:
            self.logger.info(f"🎯 Processing user input: '{user_input[:50]}...'")
            self.logger.info(f"📝 Conversation context type: {type(conversation_context)}")
            
            # Step 1: Use AI to intelligently determine the user's intent
            self.logger.info("🔍 Step 1: Analyzing user intent...")
            intent_analysis = await self._analyze_user_intent(user_input, conversation_context)
            
            # Step 2: Extract preferences from user input
            self.logger.info("🔍 Step 2: Extracting preferences...")
            extracted_preferences = await self._extract_preferences(user_input, conversation_context)
            
            # Step 3: Update current preferences
            self._update_preferences(extracted_preferences)
            
            # Step 4: Determine response based on intent and preferences
            return await self._determine_response(user_input, intent_analysis)
                
        except Exception as e:
            self.logger.error(f"❌ Orchestrator error: {e}")
            return {
                'text': "Je suis désolé, j'ai rencontré une difficulté. Pouvez-vous reformuler votre demande ?",
                'type': 'error'
            }
    
    async def _extract_preferences(self, user_input: str, conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract travel preferences from user input using LLM"""
        try:
            self.logger.info("🔍 Starting preference extraction...")
            self.logger.info(f"🔍 Current orchestrator preferences: {self.current_preferences}")
            self.logger.info(f"🔍 Conversation context: {conversation_context}")
            
            prompt = f"""
You are a travel preference extractor. Extract travel preferences from the user input.

USER INPUT: {user_input}
CURRENT CONVERSATION CONTEXT: {json.dumps(conversation_context, indent=2, ensure_ascii=False)}
CURRENT PREFERENCES: {self._create_natural_summary()}

IMPORTANT: Only extract NEW preferences that are mentioned in the user input. 
Do NOT repeat preferences that are already known from the conversation context.

Extract the following preferences if mentioned:
- destination: specific places, countries, cities
- duration: how long they want to travel (e.g., "2 weeks", "10 days")
- budget_amount: numeric amount in euros (e.g., "3000€" = 3000)
- group_size: who they're traveling with (e.g., "couple", "family", "solo")
- style: travel style (e.g., "luxury", "adventure", "cultural", "relaxation")
- travel_dates: when they want to travel (e.g., "summer", "April", "next month")
- special_requirements: any special needs or preferences

Return ONLY a JSON object with the extracted preferences. If a preference is not mentioned, don't include it.

Example:
{{
  "destination": "Maldives",
  "duration": "2 weeks", 
  "budget_amount": 5000,
  "group_size": "couple",
  "style": "luxury",
  "travel_dates": "summer",
  "special_requirements": ["privacy", "premium accommodations"]
}}

RESPOND ONLY WITH THE JSON:
"""
        
            messages = [{"role": "user", "content": prompt}]
            response = await self.llm_service.create_generation_completion(messages, stream=False)
            
            try:
                return json.loads(response.strip())
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse preference extraction response")
                return {}
        except Exception as e:
            self.logger.error(f"❌ Preference extraction failed: {e}")
            return {}
    
    async def _analyze_user_intent(self, user_input: str, conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to intelligently analyze user intent"""
        try:
            self.logger.info("🎯 Starting intelligent intent analysis...")
            
            prompt = f"""
You are ASIA.fr Agent, an intelligent travel specialist. Analyze the user's intent and determine the best course of action.

LANGUAGE REQUIREMENT: You are a French travel agent. All your responses, reasoning, and analysis must be in French.

CONVERSATION CONTEXT:
- Current preferences: {self._create_natural_summary()}
- Conversation context: {json.dumps(conversation_context, indent=2, ensure_ascii=False)}
- Confirmation pending: {self.confirmation_pending}

USER INPUT: "{user_input}"

ANALYZE THE USER INPUT AND PROVIDE A JSON RESPONSE WITH THE FOLLOWING STRUCTURE:
{{
    "intent": "greeting|confirmation|modification|preference_complete|general|suggestion_request|vague_question|information_request|new_search|recommendation_request",
    "confidence": 0.0-1.0,
    "response_type": "greeting|question|preference_summary|show_offers|modification|suggestion|conversation|clarification|information|recommendation",
    "needs_confirmation": true/false,
    "has_sufficient_details": true/false,
    "should_show_offers": true/false,
    "reasoning": "Your reasoning in French"
}}

DECISION RULES:
- **should_show_offers**: Set to true if user explicitly wants to see offers, confirms preferences (oui, c'est bon, parfait), or asks for recommendations with sufficient details
- **needs_confirmation**: Set to true if we have preferences but user hasn't explicitly confirmed them yet
- **has_sufficient_details**: Set to true if we have destination, duration, and travel_dates (the 3 required fields)
- **intent**: Choose the most appropriate intent based on what the user is trying to achieve

INTENT TYPES:
1. **greeting**: User is greeting, thanking, or saying goodbye
2. **confirmation**: User confirms preferences or wants to see offers
3. **modification**: User wants to change preferences or modify choices
4. **preference_complete**: We have sufficient preferences to show summary
5. **general**: User is asking questions, seeking advice, or providing new information
6. **suggestion_request**: User wants AI suggestions or recommendations
7. **vague_question**: User asks vague questions that need clarification
8. **information_request**: User wants general travel information
9. **new_search**: User wants to start a new search with different criteria
10. **recommendation_request**: User wants specific recommendations based on preferences

CONTEXT AWARENESS:
- If user has already seen offers and wants to modify → intent: "modification"
- If user asks for suggestions → intent: "suggestion_request"
- If user asks for specific recommendations → intent: "recommendation_request"
- If user is just chatting → intent: "general"
- If user confirms preferences (oui, c'est bon, parfait, etc.) → intent: "confirmation", should_show_offers: true
- If user wants different offers → intent: "modification"
- If user asks vague questions → intent: "vague_question"
- If user wants general info → intent: "information_request"
- If user wants to start fresh → intent: "new_search"

UNDERSTAND NATURALLY:
- Don't rely only on keywords, understand the conversation flow
- Consider what the user is trying to achieve
- Be flexible and conversational
- Allow users to modify choices at any time
- Provide helpful suggestions when appropriate
- Handle vague questions intelligently
- Preserve conversation memory and context

RESPOND ONLY WITH VALID JSON:
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = await self.llm_service.create_generation_completion(messages, stream=False)
            
            try:
                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    self.logger.info(f"✅ Intent analysis result: {result}")
                    return result
                else:
                    self.logger.warning("❌ No JSON found in intent analysis response")
                    return self._default_intent_analysis()
            except json.JSONDecodeError:
                self.logger.warning("❌ Failed to parse intent analysis response")
                return self._default_intent_analysis()
                
        except Exception as e:
            self.logger.error(f"❌ Intent analysis failed: {e}")
            return self._default_intent_analysis()
    
    def _default_intent_analysis(self) -> Dict[str, Any]:
        """Default intent analysis when AI fails"""
        return {
            "intent": "general",
            "confidence": 0.5,
            "response_type": "question",
            "needs_confirmation": False,
            "has_sufficient_details": False,
            "should_show_offers": False,
            "reasoning": "Fallback intent analysis due to error"
        }
    
    def _update_preferences(self, new_preferences: Dict[str, Any]):
        """Update current preferences with new information"""
        for key, value in new_preferences.items():
            if value is not None:
                setattr(self.current_preferences, key, value)
        
        # Also update conversation context with current preferences
        self.logger.info(f"📝 Updated preferences: {new_preferences}")
        self.logger.info(f"📝 Current preferences: {self.current_preferences}")
    
    def _has_sufficient_preferences(self) -> bool:
        """Check if we have enough preferences to start searching"""
        required_fields = ['destination', 'duration', 'travel_dates']
        optional_fields = ['group_size', 'style', 'budget_amount']
        
        # Need ALL required fields to proceed
        required_count = sum(1 for field in required_fields if getattr(self.current_preferences, field))
        optional_count = sum(1 for field in optional_fields if getattr(self.current_preferences, field))
        
        # Must have all 3 required fields (destination, duration, travel_dates)
        return required_count >= 3
    
    async def _determine_response(self, user_input: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligently determine the appropriate response based on intent and preferences"""
        try:
            intent = intent_analysis.get('intent', 'general')
            response_type = intent_analysis.get('response_type', 'question')
            confidence = intent_analysis.get('confidence', 0.5)
            should_show_offers = intent_analysis.get('should_show_offers', False)
            needs_confirmation = intent_analysis.get('needs_confirmation', False)
            has_sufficient_details = intent_analysis.get('has_sufficient_details', False)
            
            self.logger.info(f"🎯 Intent: {intent}, Response type: {response_type}, Confidence: {confidence}")
            self.logger.info(f"🎯 Should show offers: {should_show_offers}, Needs confirmation: {needs_confirmation}")
            
            # Handle different intents intelligently
            if intent == 'greeting':
                return await self._handle_greeting(user_input)
            
            elif intent == 'confirmation':
                # User is confirming - proceed to search and show offers
                self.confirmation_pending = False
                self.logger.info("✅ User confirmed preferences, proceeding to search and show offers")
                return await self._search_and_recommend()
            
            elif intent == 'modification':
                # User wants to modify preferences
                return await self._handle_modification(user_input)
            
            elif intent == 'preference_complete':
                # We have sufficient preferences
                if has_sufficient_details:
                    if self.confirmation_pending:
                        return await self._handle_confirmation(user_input)
                    else:
                        return await self._create_summary_and_confirm()
                else:
                    return await self._ask_for_missing_preferences()
            
            elif intent == 'suggestion_request':
                return await self._handle_suggestion_request(user_input)
            
            elif intent == 'recommendation_request':
                # User wants specific recommendations
                if should_show_offers and has_sufficient_details:
                    return await self._search_and_recommend()
                else:
                    return await self._handle_recommendation_request(user_input)
            
            elif intent == 'vague_question':
                return await self._handle_vague_question(user_input)
            
            elif intent == 'information_request':
                return await self._handle_information_request(user_input)
            
            elif intent == 'new_search':
                return await self._handle_new_search(user_input)
            
            else:  # general or other intents
                # Use intent analysis to determine best course of action
                if should_show_offers and has_sufficient_details:
                    # AI determined we should show offers
                    return await self._search_and_recommend()
                elif needs_confirmation and self._has_sufficient_preferences():
                    # AI determined we need confirmation
                    if self.confirmation_pending:
                        return await self._handle_confirmation(user_input)
                    else:
                        return await self._create_summary_and_confirm()
                elif has_sufficient_details and self._has_sufficient_preferences():
                    # We have enough details, create summary
                    return await self._create_summary_and_confirm()
                else:
                    # Need more preferences
                    return await self._ask_for_missing_preferences()
                    
        except Exception as e:
            self.logger.error(f"❌ Response determination failed: {e}")
            return {
                'text': "Je suis désolé, j'ai rencontré une difficulté. Pouvez-vous reformuler votre demande ?",
                'type': 'error'
            }
    
    async def _create_summary_and_confirm(self) -> Dict[str, Any]:
        """Create preference summary and ask for confirmation"""
        summary = self._create_natural_summary()
        self.last_summary = summary
        self.confirmation_pending = True
        
        self.logger.info(f"📝 Creating summary and confirmation: {summary}")
        
        prompt = f"""
You are ASIA.fr Agent, a friendly travel specialist. Create a response that presents the travel summary and asks for confirmation.

PREFERENCE SUMMARY: {summary}

Generate a warm, friendly response in French that:
1. Shows enthusiasm about their travel plans
2. Presents the summary naturally and clearly
3. Asks for explicit confirmation before searching
4. Uses emojis naturally
5. Keeps it conversational
6. Makes it clear what will happen next (showing offers)

IMPORTANT: 
- Always ask for confirmation
- Be specific about what you'll do next (search and show offers)
- Example: "Est-ce que ce résumé vous convient pour que je puisse rechercher les meilleures offres ?"

RESPOND ONLY WITH THE RESPONSE TEXT:
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm_service.create_generation_completion(messages, stream=False)
        
        return {
            'text': response.strip(),
            'type': 'confirmation_request',
            'summary': summary
        }
    
    def _create_natural_summary(self) -> str:
        """Create natural language summary of current preferences"""
        parts = []
        
        if self.current_preferences.destination:
            parts.append(f"destination {self.current_preferences.destination}")
        if self.current_preferences.duration:
            parts.append(f"pour {self.current_preferences.duration}")
        if self.current_preferences.group_size:
            parts.append(f"pour {self.current_preferences.group_size}")
        if self.current_preferences.travel_dates:
            parts.append(f"en {self.current_preferences.travel_dates}")
        if self.current_preferences.style:
            parts.append(f"style {self.current_preferences.style}")
        if self.current_preferences.budget_amount:
            parts.append(f"avec un budget de {self.current_preferences.budget_amount}€")
        if self.current_preferences.special_requirements:
            parts.append(f"avec {', '.join(self.current_preferences.special_requirements)}")
        
        if parts:
            return f"Vous planifiez un voyage vers {', '.join(parts)}."
        else:
            return "Vous avez commencé à planifier votre voyage."
    
    async def _handle_confirmation(self, user_input: str) -> Dict[str, Any]:
        """Handle user confirmation and trigger search"""
        # Check if user is confirming
        confirmation_keywords = ['oui', 'yes', 'correct', 'parfait', 'ok', 'd\'accord', 'confirmer', 'c\'est bon', 'c est bon', 'go', 'vas-y', 'vas y']
        is_confirming = any(keyword in user_input.lower() for keyword in confirmation_keywords)
        
        if is_confirming:
            self.confirmation_pending = False
            self.logger.info("✅ User confirmed preferences, proceeding to search and show offers")
            return await self._search_and_recommend()
        else:
            # User is modifying preferences
            self.logger.info("🔄 User wants to modify preferences")
            return await self._handle_modification(user_input)
    
    async def _search_and_recommend(self) -> Dict[str, Any]:
        """Search for offers and create recommendations using LLM with fallback"""
        try:
            self.logger.info("🔍 Starting search and recommendation process")
            self.logger.info(f"📝 Current preferences: {self._create_natural_summary()}")
            
            # Get all offers (data_service.get_offers() is a sync method)
            try:
                self.logger.info(f"🔧 Data service type: {type(self.data_service)}")
                self.logger.info(f"🔧 Data service methods: {[method for method in dir(self.data_service) if not method.startswith('_')]}")
                
                all_offers = self.data_service.get_offers()
                self.logger.info(f"📊 Retrieved {len(all_offers)} offers from data service")
            except Exception as e:
                self.logger.error(f"❌ Failed to get offers: {e}")
                self.logger.error(f"❌ Data service error details: {type(e).__name__}: {str(e)}")
                return {
                    'text': "Je suis désolé, j'ai rencontré une difficulté lors de la récupération des offres. Pouvez-vous réessayer ?",
                    'type': 'error'
                }
            
            # Try LLM-based selection first
            try:
                self.logger.info("🧠 Attempting LLM-based recommendation")
                llm_results = await self._llm_based_recommendation(all_offers)
                if llm_results:
                    self.logger.info("✅ LLM-based recommendation successful")
                    return llm_results
            except Exception as e:
                self.logger.warning(f"⚠️ LLM recommendation failed, using fallback: {e}")
            
            # Fallback to classic scoring
            self.logger.info("🔄 Using classic scoring fallback")
            return self._classic_scoring_fallback(all_offers)
            
        except Exception as e:
            self.logger.error(f"❌ Search error: {e}")
            return {
                'text': "Je suis désolé, j'ai rencontré une difficulté lors de la recherche. Pouvez-vous réessayer ?",
                'type': 'error'
            }
    
    async def _llm_based_recommendation(self, all_offers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Use LLM to intelligently select and rank offers"""
        try:
            # Filter offers by destination match first
            destination_filtered_offers = []
            for offer in all_offers:
                if offer.get('destinations') and self.current_preferences.destination:
                    dest_match = self._check_destination_match(offer['destinations'])
                    if dest_match > 0.5:  # Only include offers with strong destination match
                        destination_filtered_offers.append(offer)
            
            # If no destination matches found, use all offers but prioritize destination
            if not destination_filtered_offers:
                self.logger.warning("⚠️ No strong destination matches found, using all offers")
                destination_filtered_offers = all_offers
            
            # Limit offers to prevent token overflow (max 20 offers)
            limited_offers = destination_filtered_offers[:20]
            
            # Create preference summary
            preference_summary = self._create_natural_summary()
            
            # Prepare offers for LLM (simplified format to save tokens)
            offers_for_llm = []
            for i, offer in enumerate(limited_offers):
                offer_info = {
                    'id': i,
                    'name': offer.get('product_name', 'Unknown'),
                    'destination': ', '.join([d.get('country', '') for d in offer.get('destinations', [])]),
                    'duration': f"{offer.get('duration', 0)} jours",
                    'price': f"{offer.get('price', {}).get('amount', 0)}€",
                    'style': offer.get('offer_type', 'Standard'),
                    'description': offer.get('description', '')[:200] + '...' if offer.get('description') else ''
                }
                offers_for_llm.append(offer_info)
            
            prompt = f"""
You are an expert travel agent for ASIA.fr. Select the 3 best offers for the user based on their preferences.

USER PREFERENCES: {preference_summary}

AVAILABLE OFFERS:
{json.dumps(offers_for_llm, indent=2, ensure_ascii=False)}

IMPORTANT RULES:
1. You MUST ONLY select from the provided offers (use the exact offer_id numbers)
2. Do NOT create or suggest offers that are not in the list
3. If no offers match well, select the 3 closest matches
4. DESTINATION MATCH IS MANDATORY - Only select offers that match the user's destination preference
5. Focus on destination match first, then duration, then budget
6. Provide realistic explanations based on the actual offer details

Your task:
1. Analyze each offer against the user's preferences
2. Select the 3 best matches considering destination, duration, budget, style, and overall appeal
3. Rank them from best to good
4. Provide a brief explanation for each selection based on the actual offer details

Return ONLY a JSON object with this exact structure:
{{
  "selected_offers": [offer_id1, offer_id2, offer_id3],
  "explanations": [
    "Brief explanation why offer 1 is perfect based on actual details",
    "Brief explanation why offer 2 is great based on actual details", 
    "Brief explanation why offer 3 is good based on actual details"
  ],
  "confidence": "high/medium/low"
}}

RESPOND ONLY WITH THE JSON:
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = await self.llm_service.create_matcher_completion(messages, stream=False)
            
            # Parse LLM response
            llm_result = json.loads(response.strip())
            selected_ids = llm_result.get('selected_offers', [])
            explanations = llm_result.get('explanations', [])
            
            # Get the selected offers
            selected_offers = []
            for offer_id in selected_ids:
                if offer_id < len(limited_offers):
                    selected_offers.append(limited_offers[offer_id])
            
            # Calculate match scores for selected offers (for display)
            match_scores = []
            budget_indicators = []
            
            for offer in selected_offers:
                match_score = self._calculate_match_score(offer)
                budget_indicator = self._get_budget_indicator(offer)
                match_scores.append(match_score)
                budget_indicators.append(budget_indicator)
            
            # Create response text with explanations
            response_text = f"""Parfait ! J'ai analysé toutes les offres disponibles dans notre base de données et sélectionné les 3 meilleures options qui correspondent à vos critères :

"""
            
            for i, (offer, explanation) in enumerate(zip(selected_offers, explanations)):
                response_text += f"{i+1}. **{offer.get('product_name', 'Offre')}** - {explanation}\n\n"
            
            response_text += "Ces offres sont directement disponibles dans notre système. Choisissez celle qui vous convient le mieux !"
            
            return {
                'text': response_text,
                'type': 'offers',
                'offers': selected_offers,
                'match_scores': match_scores,
                'budget_indicators': budget_indicators,
                'llm_selected': True,
                'confidence': llm_result.get('confidence', 'medium')
            }
            
        except Exception as e:
            self.logger.error(f"❌ LLM recommendation failed: {e}")
            return None
    
    def _classic_scoring_fallback(self, all_offers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback to classic scoring method"""
        try:
            # Filter and score offers using classic method
            search_results = []
            for offer in all_offers:
                match_score = self._calculate_match_score(offer)
                relevance_score = self._calculate_relevance_score(offer)
                budget_indicator = self._get_budget_indicator(offer)
                
                # Check destination match specifically
                dest_match = 0.0
                if offer.get('destinations') and self.current_preferences.destination:
                    dest_match = self._check_destination_match(offer['destinations'])
                
                # Only include offers with destination match > 0.5 (strong match) and overall match > 0.3
                if dest_match > 0.5 and match_score > 0.3:
                    search_results.append(SearchResult(
                        offer=offer,
                        match_score=match_score,
                        budget_indicator=budget_indicator,
                        relevance_score=relevance_score
                    ))
            
            # Sort by match score and take top 3
            search_results.sort(key=lambda x: x.match_score, reverse=True)
            top_offers = search_results[:3]
            
            # Create response
            response_text = f"""Parfait ! J'ai trouvé {len(top_offers)} offres exceptionnelles dans notre base de données qui correspondent à vos critères.

Voici les meilleures options disponibles pour votre voyage :"""
            
            return {
                'text': response_text,
                'type': 'offers',
                'offers': [result.offer for result in top_offers],
                'match_scores': [result.match_score for result in top_offers],
                'budget_indicators': [result.budget_indicator for result in top_offers],
                'llm_selected': False,
                'confidence': 'high'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Classic scoring fallback failed: {e}")
            raise
    
    def _calculate_match_score(self, offer: Dict[str, Any]) -> float:
        """Calculate match score between offer and preferences (0-1)"""
        score = 0.0
        total_weight = 0.0
        
        # Destination match (highest weight - 60%)
        if self.current_preferences.destination and offer.get('destinations'):
            dest_match = self._check_destination_match(offer['destinations'])
            score += dest_match * 0.6
            total_weight += 0.6
        
        # Duration match (20%)
        if self.current_preferences.duration and offer.get('duration'):
            duration_match = self._check_duration_match(offer['duration'])
            score += duration_match * 0.2
            total_weight += 0.2
        
        # Budget match (15%)
        if self.current_preferences.budget_amount and offer.get('price', {}).get('amount'):
            budget_match = self._check_budget_match(offer['price']['amount'])
            score += budget_match * 0.15
            total_weight += 0.15
        
        # Style match (3%)
        if self.current_preferences.style and offer.get('offer_type'):
            style_match = self._check_style_match(offer['offer_type'])
            score += style_match * 0.03
            total_weight += 0.03
        
        # Date match (2%)
        if self.current_preferences.travel_dates and offer.get('dates'):
            date_match = self._check_date_match(offer['dates'])
            score += date_match * 0.02
            total_weight += 0.02
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _check_destination_match(self, offer_destinations: List[Dict[str, str]]) -> float:
        """Check destination match (0-1)"""
        if not self.current_preferences.destination:
            return 0.0
        
        # Country code to name mapping
        country_mapping = {
            'jp': 'japon',
            'vn': 'vietnam',
            'th': 'thailande',
            'kh': 'cambodge',
            'la': 'laos',
            'mm': 'myanmar',
            'my': 'malaisie',
            'sg': 'singapour',
            'id': 'indonesie',
            'ph': 'philippines',
            'in': 'inde',
            'np': 'nepal',
            'bd': 'bangladesh',
            'lk': 'sri lanka',
            'jo': 'jordanie',
            'lb': 'liban',
            'sy': 'syrie',
            'iq': 'irak',
            'ir': 'iran',
            'af': 'afghanistan',
            'pk': 'pakistan',
            'cn': 'chine',
            'kr': 'coree du sud',
            'kp': 'coree du nord',
            'mn': 'mongolie',
            'tw': 'taiwan',
            'hk': 'hong kong',
            'mo': 'macao'
        }
        
        user_dest = self.current_preferences.destination.lower()
        
        for dest in offer_destinations:
            offer_country_code = dest.get('country', '').lower()
            offer_city = dest.get('city', '').lower()
            
            # Check if country code matches user destination
            if offer_country_code in country_mapping:
                offer_country_name = country_mapping[offer_country_code]
                if user_dest in offer_country_name or offer_country_name in user_dest:
                    return 1.0
            
            # Check direct country code match
            if user_dest in offer_country_code or offer_country_code in user_dest:
                return 1.0
            
            # Check city match
            if user_dest in offer_city or offer_city in user_dest:
                return 1.0
        
        return 0.0
    
    def _check_duration_match(self, offer_duration) -> float:
        """Check duration match (0-1)"""
        if not self.current_preferences.duration:
            return 0.0
        
        # Convert offer_duration to int if it's a string
        try:
            if isinstance(offer_duration, str):
                # Extract number from string like "8 jours / 7 nuits jours"
                import re
                duration_match = re.search(r'(\d+)', offer_duration)
                if duration_match:
                    offer_duration = int(duration_match.group(1))
                else:
                    offer_duration = 0
            else:
                offer_duration = int(offer_duration)
        except (ValueError, TypeError):
            self.logger.warning(f"⚠️ Could not convert offer duration to int: {offer_duration}")
            return 0.0
        
        # Extract number of days from user preference
        import re
        duration_text = self.current_preferences.duration.lower()
        days_match = re.search(r'(\d+)\s*(jours?|days?)', duration_text)
        weeks_match = re.search(r'(\d+)\s*(semaines?|weeks?)', duration_text)
        
        user_days = 0
        if days_match:
            user_days = int(days_match.group(1))
        elif weeks_match:
            user_days = int(weeks_match.group(1)) * 7
        
        if user_days == 0:
            return 0.5  # Neutral score if we can't parse duration
        
        # Calculate match based on difference
        diff = abs(offer_duration - user_days)
        if diff <= 2:
            return 1.0
        elif diff <= 5:
            return 0.8
        elif diff <= 10:
            return 0.6
        else:
            return 0.3
    
    def _check_budget_match(self, offer_price) -> float:
        """Check budget match (0-1)"""
        if not self.current_preferences.budget_amount:
            return 0.0
        
        # Convert offer_price to float if it's a string
        try:
            if isinstance(offer_price, str):
                # Remove currency symbols and convert to float
                offer_price = float(offer_price.replace('€', '').replace(',', '').strip())
            else:
                offer_price = float(offer_price)
        except (ValueError, TypeError):
            self.logger.warning(f"⚠️ Could not convert offer price to float: {offer_price}")
            return 0.0
        
        user_budget = float(self.current_preferences.budget_amount)
        
        # Avoid division by zero
        if user_budget == 0:
            return 0.0
        
        diff_percentage = abs(offer_price - user_budget) / user_budget
        
        if diff_percentage <= 0.1:  # Within 10%
            return 1.0
        elif diff_percentage <= 0.2:  # Within 20%
            return 0.8
        elif diff_percentage <= 0.3:  # Within 30%
            return 0.6
        else:
            return 0.3
    
    def _check_style_match(self, offer_style: str) -> float:
        """Check style match (0-1)"""
        if not self.current_preferences.style:
            return 0.0
        
        user_style = self.current_preferences.style.lower()
        offer_style_lower = offer_style.lower()
        
        # Simple keyword matching
        style_keywords = {
            'luxury': ['luxe', 'premium', 'haut de gamme'],
            'adventure': ['aventure', 'trek', 'exploration'],
            'cultural': ['culturel', 'culture', 'tradition'],
            'relaxation': ['détente', 'relaxation', 'bien-être']
        }
        
        for style, keywords in style_keywords.items():
            if user_style in keywords or any(keyword in user_style for keyword in keywords):
                if any(keyword in offer_style_lower for keyword in keywords):
                    return 1.0
        
        return 0.3  # Neutral score for style
    
    def _check_date_match(self, offer_dates: List[str]) -> float:
        """Check date match (0-1)"""
        if not self.current_preferences.travel_dates:
            return 0.0
        
        # Simple season matching
        user_dates = self.current_preferences.travel_dates.lower()
        seasons = {
            'été': ['summer', 'june', 'july', 'august'],
            'hiver': ['winter', 'december', 'january', 'february'],
            'printemps': ['spring', 'march', 'april', 'may'],
            'automne': ['autumn', 'september', 'october', 'november']
        }
        
        for season, months in seasons.items():
            if season in user_dates or any(month in user_dates for month in months):
                if any(month in ' '.join(offer_dates).lower() for month in months):
                    return 1.0
        
        return 0.5  # Neutral score for dates
    
    def _calculate_relevance_score(self, offer: Dict[str, Any]) -> float:
        """Calculate relevance score (0-1) - how relevant the offer is overall"""
        # This could be enhanced with more sophisticated relevance algorithms
        return 0.8  # Default relevance score
    
    def _get_budget_indicator(self, offer: Dict[str, Any]) -> str:
        """Get budget indicator (€€€, €€€€, €€€€€)"""
        price = offer.get('price', {}).get('amount', 0)
        
        # Convert price to float if it's a string
        try:
            if isinstance(price, str):
                # Remove currency symbols and convert to float
                price = float(price.replace('€', '').replace(',', '').strip())
            else:
                price = float(price)
        except (ValueError, TypeError):
            self.logger.warning(f"⚠️ Could not convert price to float: {price}")
            price = 0
        
        if price < 2000:
            return '€€€'
        elif price < 5000:
            return '€€€€'
        else:
            return '€€€€€'
    
    async def _ask_for_missing_preferences(self) -> Dict[str, Any]:
        """Ask for missing preferences"""
        missing = self._get_missing_preferences()
        
        prompt = f"""
You are ASIA.fr Agent. Ask for missing travel preferences in a friendly way.

MISSING PREFERENCES: {missing}
CURRENT PREFERENCES: {self._create_natural_summary()}

Generate a friendly response asking for the missing preferences. Format bullet points with proper spacing:
- Each bullet point should be on its own line
- Add a blank line between each bullet point
- Use proper indentation
- Be encouraging and warm

IMPORTANT: 
- Destination, duration, and travel dates are REQUIRED fields
- Group size and style are OPTIONAL but helpful for better recommendations
- Budget is completely optional and will help narrow the search if provided
- Prioritize asking for required fields first

Example format:
• Destination : Où rêvez-vous de partir ?

• Durée : Combien de jours souhaitez-vous rester ?

• Période de voyage : Quand souhaitez-vous partir ?

Make sure each bullet point is separated by a blank line for proper formatting.

RESPOND ONLY WITH THE RESPONSE TEXT:
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm_service.create_generation_completion(messages, stream=False)
        
        return {
            'text': response.strip(),
            'type': 'missing_preferences'
        }
    
    def _get_missing_preferences(self) -> List[str]:
        """Get list of missing preferences"""
        missing = []
        
        # Required fields (must have all 3)
        if not self.current_preferences.destination:
            missing.append("destination")
        if not self.current_preferences.duration:
            missing.append("durée")
        if not self.current_preferences.travel_dates:
            missing.append("période de voyage")
        
        # Optional fields (helpful but not required)
        if not self.current_preferences.group_size:
            missing.append("nombre de voyageurs")
        if not self.current_preferences.style:
            missing.append("style de voyage")
        # Budget is completely optional - don't ask for it
        
        return missing
    
    async def _handle_modification(self, user_input: str) -> Dict[str, Any]:
        """Handle preference modification"""
        # Reset confirmation state
        self.confirmation_pending = False
        self.logger.info("🔄 Handling preference modification")
        
        # Extract new preferences from modification
        new_preferences = await self._extract_preferences(user_input, {})
        self._update_preferences(new_preferences)
        
        # Check if we have sufficient preferences after modification
        if self._has_sufficient_preferences():
            self.logger.info("✅ Sufficient preferences after modification, creating summary")
            return await self._create_summary_and_confirm()
        else:
            self.logger.info("⚠️ Still missing required preferences after modification")
            return await self._ask_for_missing_preferences()
    
    async def _handle_greeting(self, user_input: str) -> Dict[str, Any]:
        """Handle greeting messages"""
        prompt = f"""
You are ASIA.fr Agent, a friendly travel specialist. Respond to the user's greeting in a warm, welcoming way.

USER INPUT: "{user_input}"

Generate a friendly greeting response in French that:
1. Acknowledges their greeting warmly
2. Shows enthusiasm for helping them plan their trip
3. Encourages them to share their travel dreams
4. Uses natural, conversational French
5. Keeps it brief but welcoming

RESPOND ONLY WITH THE RESPONSE TEXT:
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm_service.create_generation_completion(messages, stream=False)
        
        return {
            'text': response.strip(),
            'type': 'greeting'
        }
    
    async def _handle_suggestion_request(self, user_input: str) -> Dict[str, Any]:
        """Handle requests for travel suggestions"""
        prompt = f"""
You are ASIA.fr Agent, a knowledgeable travel specialist. Provide intelligent travel suggestions based on the user's request.

USER INPUT: "{user_input}"
CURRENT PREFERENCES: {self._create_natural_summary()}

Generate helpful travel suggestions in French that:
1. Address their specific request
2. Consider their current preferences if any
3. Provide intelligent, personalized recommendations
4. Be encouraging and enthusiastic
5. Suggest specific destinations, activities, or travel styles
6. Keep it conversational and friendly
7. Guide them toward providing specific preferences so we can show them actual offers from our database

IMPORTANT: Do not make up specific offers. Instead, guide them to provide preferences so we can show them real offers from our database.

RESPOND ONLY WITH THE RESPONSE TEXT:
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm_service.create_generation_completion(messages, stream=False)
        
        return {
            'text': response.strip(),
            'type': 'suggestion'
        }
    
    async def _handle_recommendation_request(self, user_input: str) -> Dict[str, Any]:
        """Handle requests for specific recommendations"""
        self.logger.info("🎯 Handling recommendation request")
        
        if self._has_sufficient_preferences():
            # If we have enough preferences, show offers
            self.logger.info("✅ Sufficient preferences for recommendations, showing offers")
            return await self._search_and_recommend()
        else:
            # Ask for missing preferences first
            self.logger.info("⚠️ Missing required preferences for recommendations")
            return await self._ask_for_missing_preferences()
    
    async def _handle_vague_question(self, user_input: str) -> Dict[str, Any]:
        """Handle vague questions that need clarification"""
        prompt = f"""
You are ASIA.fr Agent, a helpful travel specialist. The user has asked a vague question that needs clarification.

USER INPUT: "{user_input}"

Generate a friendly response in French that:
1. Acknowledges their question
2. Asks for clarification in a helpful way
3. Provides some context about what information would be useful
4. Encourages them to be more specific
5. Keeps it warm and supportive

RESPOND ONLY WITH THE RESPONSE TEXT:
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm_service.create_generation_completion(messages, stream=False)
        
        return {
            'text': response.strip(),
            'type': 'clarification'
        }
    
    async def _handle_information_request(self, user_input: str) -> Dict[str, Any]:
        """Handle requests for general travel information"""
        prompt = f"""
You are ASIA.fr Agent, a knowledgeable travel specialist. Provide helpful travel information based on the user's request.

USER INPUT: "{user_input}"

Generate informative travel information in French that:
1. Addresses their specific question
2. Provides useful, accurate information
3. Be helpful and educational
4. Keep it conversational and friendly
5. Encourage further engagement

RESPOND ONLY WITH THE RESPONSE TEXT:
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm_service.create_generation_completion(messages, stream=False)
        
        return {
            'text': response.strip(),
            'type': 'information'
        }
    
    async def _handle_new_search(self, user_input: str) -> Dict[str, Any]:
        """Handle requests to start a new search"""
        # Reset current preferences and start fresh
        self.current_preferences = TravelPreference()
        self.confirmation_pending = False
        self.last_summary = None
        
        prompt = f"""
You are ASIA.fr Agent, a friendly travel specialist. The user wants to start a new travel search.

USER INPUT: "{user_input}"

Generate a welcoming response in French that:
1. Acknowledges their desire to start fresh
2. Shows enthusiasm for helping them plan a new trip
3. Ask for their travel preferences in a friendly way
4. Encourage them to share their dreams
5. Keep it warm and inviting

RESPOND ONLY WITH THE RESPONSE TEXT:
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm_service.create_generation_completion(messages, stream=False)
        
        return {
            'text': response.strip(),
            'type': 'new_search'
        } 