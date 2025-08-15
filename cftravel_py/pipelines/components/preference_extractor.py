"""
Preference Extractor Component for ASIA.fr Agent
Handles intelligent extraction of travel preferences from user input
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..core import PipelineComponent, PipelineContext, PipelineState
from services.llm_service import LLMService
from services.memory_service import MemoryService

class PreferenceExtractorComponent(PipelineComponent):
    """Extracts and updates travel preferences from user input"""
    
    def __init__(self, llm_service: LLMService, memory_service: MemoryService):
        super().__init__("PreferenceExtractor", priority=90)
        self.llm_service = llm_service
        self.memory_service = memory_service
        
        # Enhanced preference patterns for fast extraction
        self.destination_patterns = [
            r'\b(japon|japan|japanese)\b',
            r'\b(philippines|philippine)\b',
            r'\b(thailand|thaïlande|thaï)\b',
            r'\b(vietnam|vietnamien)\b',
            r'\b(china|chine|chinois)\b',
            r'\b(india|inde|indien)\b',
            r'\b(indonesia|indonésie|indonésien)\b',
            r'\b(malaysia|malaisie|malaisien)\b',
            r'\b(singapore|singapour|singapourien)\b',
            r'\b(cambodia|cambodge|cambodgien)\b',
            r'\b(laos|laotien)\b',
            r'\b(myanmar|myanmarais)\b',
            r'\b(sri lanka|sri lankais)\b',
            r'\b(nepal|népal|népalais)\b',
            r'\b(bhutan|bhoutan|bhoutanais)\b',
            r'\b(mongolia|mongolie|mongol)\b',
            r'\b(maldives|maldive)\b',
            r'\b(australia|australie)\b'
        ]
        
        self.duration_patterns = [
            r'\b(\d+)\s*(jours?|days?)\b',
            r'\b(\d+)\s*(semaines?|weeks?)\b',
            r'\b(\d+)\s*(mois|months?)\b'
        ]
        
        # Enhanced date patterns with current date awareness
        self.date_patterns = [
            r'\b(printemps|spring)\b',
            r'\b(été|summer)\b',
            r'\b(automne|fall|autumn)\b',
            r'\b(hiver|winter)\b',
            r'\b(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\b',
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b(\d{1,2})-(\d{1,2})-(\d{4})\b',  # MM-DD-YYYY or DD-MM-YYYY
            r'\b(dans|in)\s+(\d+)\s*(jours?|days?|semaines?|weeks?|mois|months?)\b',
            r'\b(prochain|next)\s+(mois|month|semaine|week)\b',
            r'\b(cette|this)\s+(année|year)\b',
            r'\b(l\'année|next year)\s+prochaine\b',
            r'\b(ce|this)\s+(printemps|été|automne|hiver)\b',
            r'\b(le|on)\s+(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\b'
        ]
        
        # Budget patterns (optional - only extract if clearly mentioned)
        self.budget_patterns = [
            r'\b(\d+(?:[.,]\d+)?)\s*(?:€|euros?)\b',  # Numeric budget amount
            r'\b(budget\s+de\s+(\d+(?:[.,]\d+)?)\s*(?:€|euros?))\b',  # "budget de X euros"
            r'\b(environ|maximum|jusqu\'à)\s+(\d+(?:[.,]\d+)?)\s*(?:€|euros?)\b',  # "environ X euros"
            r'\b(prix|coût|tarif)\s+(de\s+)?(\d+(?:[.,]\d+)?)\s*(?:€|euros?)\b'  # "prix de X euros"
        ]
        
        # Enhanced hotel/resort patterns for better matching
        self.accommodation_patterns = [
            r'\b(hôtel|hotel)\b',
            r'\b(resort|station)\s+balnéaire\b',
            r'\b(bungalow|villa|suite)\b',
            r'\b(5\s*étoiles?|5\s*stars?)\b',
            r'\b(4\s*étoiles?|4\s*stars?)\b',
            r'\b(3\s*étoiles?|3\s*stars?)\b',
            r'\b(luxe|premium|standard|économique)\s+(hôtel|hotel)\b'
        ]
        
        # Activity and experience patterns
        self.activity_patterns = [
            r'\b(plage|beach)\b',
            r'\b(culture|culturel)\b',
            r'\b(aventure|adventure)\b',
            r'\b(détente|relaxation)\b',
            r'\b(gastronomie|cuisine|food)\b',
            r'\b(sport|activité)\b',
            r'\b(visite|découverte)\b',
            r'\b(shopping|achats)\b',
            r'\b(nature|paysage)\b',
            r'\b(histoire|historique)\b',
            r'\b(tradition|traditionnel)\b',
            r'\b(plongée|diving)\b',
            r'\b(surf|kitesurf)\b',
            r'\b(yoga|méditation)\b',
            r'\b(spa|massage)\b'
        ]
        
        # Destination mapping for standardization
        self.destination_mapping = {
            'japon': 'Japan', 'japan': 'Japan', 'japanese': 'Japan',
            'philippines': 'Philippines', 'philippine': 'Philippines',
            'thailand': 'Thailand', 'thaïlande': 'Thailand', 'thaï': 'Thailand',
            'vietnam': 'Vietnam', 'vietnamien': 'Vietnam',
            'china': 'China', 'chine': 'China', 'chinois': 'China',
            'india': 'India', 'inde': 'India', 'indien': 'India',
            'indonesia': 'Indonesia', 'indonésie': 'Indonesia', 'indonésien': 'Indonesia',
            'malaysia': 'Malaysia', 'malaisie': 'Malaysia', 'malaisien': 'Malaysia',
            'singapore': 'Singapore', 'singapour': 'Singapore', 'singapourien': 'Singapore',
            'cambodia': 'Cambodia', 'cambodge': 'Cambodia', 'cambodgien': 'Cambodia',
            'laos': 'Laos', 'laotien': 'Laos',
            'myanmar': 'Myanmar', 'myanmarais': 'Myanmar',
            'sri lanka': 'Sri Lanka', 'sri lankais': 'Sri Lanka',
            'nepal': 'Nepal', 'népal': 'Nepal', 'népalais': 'Nepal',
            'bhutan': 'Bhutan', 'bhoutan': 'Bhutan', 'bhoutanais': 'Bhutan',
            'mongolia': 'Mongolia', 'mongolie': 'Mongolia', 'mongol': 'Mongolia',
            'maldives': 'Maldives', 'maldive': 'Maldives',
            'australia': 'Australia', 'australie': 'Australia'
        }
        
        # Month mapping for date processing
        self.month_mapping = {
            'janvier': 1, 'january': 1,
            'février': 2, 'february': 2,
            'mars': 3, 'march': 3,
            'avril': 4, 'april': 4,
            'mai': 5, 'may': 5,
            'juin': 6, 'june': 6,
            'juillet': 7, 'july': 7,
            'août': 8, 'august': 8,
            'septembre': 9, 'september': 9,
            'octobre': 10, 'october': 10,
            'novembre': 11, 'november': 11,
            'décembre': 12, 'december': 12
        }
    
    def is_required(self, context: PipelineContext) -> bool:
        """Required for all user inputs to extract preferences"""
        return True
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Extract preferences from user input and update context"""
        try:
            # Fast pattern-based extraction first
            fast_preferences = self._fast_preference_extraction(context.user_input)
            
            # LLM-based extraction for complex cases
            llm_preferences = await self._llm_preference_extraction(context)
            
            # Merge preferences (LLM takes precedence)
            merged_preferences = self._merge_preferences(fast_preferences, llm_preferences)
            
            # Add current date context for date-aware processing
            merged_preferences['current_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Update context with new preferences
            if merged_preferences:
                context.update_preferences(merged_preferences)
                
                # Update memory service
                self.memory_service.update_user_preferences(context.conversation_id, merged_preferences)
                self.logger.info(f"📊 EXTRACTED PREFERENCES: {merged_preferences}")
                self.logger.info(f"📊 UPDATED CONTEXT PREFERENCES: {context.user_preferences}")
            else:
                self.logger.info(f"📊 NO PREFERENCES EXTRACTED from: {context.user_input}")
            
            # Store extraction metadata
            context.add_metadata('extracted_preferences', merged_preferences)
            
            # Check if this is a modification request
            if self._is_modification_request(context.user_input):
                context.add_metadata('is_modification', True)
                self.logger.info("🔄 Detected preference modification request")
            
            context.add_metadata('preference_count', len(context.user_preferences))
            
            return context
            
        except Exception as e:
            self.log_error(context, e)
            return context
    
    def _fast_preference_extraction(self, user_input: str) -> Dict[str, Any]:
        """Fast pattern-based preference extraction"""
        preferences = {}
        input_lower = user_input.lower()
        
        # Extract destination
        for pattern in self.destination_patterns:
            match = re.search(pattern, input_lower)
            if match:
                destination = match.group(1)
                preferences['destination'] = self.destination_mapping.get(destination, destination.title())
                break
        
        # Extract duration
        for pattern in self.duration_patterns:
            match = re.search(pattern, input_lower)
            if match:
                number = match.group(1)
                unit = match.group(2)
                if 'semaine' in unit or 'week' in unit:
                    preferences['duration'] = f"{number} semaines"
                elif 'mois' in unit or 'month' in unit:
                    preferences['duration'] = f"{number} mois"
                else:
                    preferences['duration'] = f"{number} jours"
                break
        
        # Extract travel dates/timing with current date awareness
        timing_info = self._extract_timing_info(input_lower)
        if timing_info:
            preferences['timing'] = timing_info
        
        # Extract budget (optional - only if clearly mentioned)
        budget_info = self._extract_budget_info(input_lower)
        if budget_info:
            preferences['budget'] = budget_info
        
        # Extract accommodation preferences
        accommodation_info = self._extract_accommodation_info(input_lower)
        if accommodation_info:
            preferences['accommodation'] = accommodation_info
        
        # Extract activities and experiences
        activities = self._extract_activities(input_lower)
        if activities:
            preferences['activities'] = activities
        
        # Extract travel style
        style_patterns = {
            'cultural': ['culturel', 'cultural', 'tradition', 'histoire', 'historique'],
            'adventure': ['aventure', 'adventure', 'trekking', 'randonnée', 'hiking'],
            'relaxation': ['détente', 'relaxation', 'plage', 'bien-être', 'spa'],
            'gastronomy': ['gastronomie', 'cuisine', 'food', 'culinaire', 'dégustation'],
            'luxury': ['luxe', 'premium', 'haut de gamme', 'exclusif'],
            'budget': ['économique', 'budget', 'pas cher', 'bon marché']
        }
        
        for style, keywords in style_patterns.items():
            if any(keyword in input_lower for keyword in keywords):
                preferences['style'] = style
                break
        
        # Extract group size
        group_patterns = {
            'solo': ['seul', 'solo', 'individuel'],
            'couple': ['couple', 'deux', 'romantique'],
            'family': ['famille', 'enfant', 'kids'],
            'group': ['groupe', 'amis', 'friends']
        }
        
        for size, keywords in group_patterns.items():
            if any(keyword in input_lower for keyword in keywords):
                preferences['group_size'] = size
                break
        
        return preferences
    
    def _extract_timing_info(self, input_lower: str) -> str:
        """Extract travel timing with current date awareness"""
        current_date = datetime.now()
        
        # Check for specific dates
        for pattern in self.date_patterns:
            match = re.search(pattern, input_lower)
            if match:
                if 'printemps' in match.group(0) or 'spring' in match.group(0):
                    return "printemps"
                elif 'été' in match.group(0) or 'summer' in match.group(0):
                    return "été"
                elif 'automne' in match.group(0) or 'fall' in match.group(0) or 'autumn' in match.group(0):
                    return "automne"
                elif 'hiver' in match.group(0) or 'winter' in match.group(0):
                    return "hiver"
                elif any(month in match.group(0) for month in self.month_mapping.keys()):
                    # Extract month
                    for month_name, month_num in self.month_mapping.items():
                        if month_name in match.group(0):
                            return month_name
                elif 'dans' in match.group(0) or 'in' in match.group(0):
                    # Relative timing like "dans 2 semaines"
                    return match.group(0)
                elif 'prochain' in match.group(0) or 'next' in match.group(0):
                    return "prochain mois"
                elif 'cette année' in match.group(0) or 'this year' in match.group(0):
                    return "cette année"
        
        return None
    
    def _extract_budget_info(self, input_lower: str) -> str:
        """Extract budget information (optional) - returns numeric amount"""
        for pattern in self.budget_patterns:
            match = re.search(pattern, input_lower)
            if match:
                # Extract numeric amount from the match
                if len(match.groups()) >= 1:
                    amount_str = match.group(1) if match.group(1) else match.group(2)
                    if amount_str:
                        # Convert to float, handling comma as decimal separator
                        amount = float(amount_str.replace(',', '.'))
                        return str(amount)
        
        return None
    
    def _extract_accommodation_info(self, input_lower: str) -> str:
        """Extract accommodation preferences"""
        for pattern in self.accommodation_patterns:
            match = re.search(pattern, input_lower)
            if match:
                if '5' in match.group(0):
                    return '5_stars'
                elif '4' in match.group(0):
                    return '4_stars'
                elif '3' in match.group(0):
                    return '3_stars'
                elif 'luxe' in match.group(0) or 'premium' in match.group(0):
                    return 'luxury'
                elif 'économique' in match.group(0):
                    return 'budget'
                else:
                    return 'standard'
        
        return None
    
    def _extract_activities(self, input_lower: str) -> List[str]:
        """Extract activity and experience preferences"""
        activities = []
        for pattern in self.activity_patterns:
            match = re.search(pattern, input_lower)
            if match:
                activity = match.group(1)
                if activity not in activities:
                    activities.append(activity)
        
        return activities if activities else None
    
    async def _llm_preference_extraction(self, context: PipelineContext) -> Dict[str, Any]:
        """Use LLM for intelligent preference extraction"""
        prompt = self._build_extraction_prompt(context)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.llm_service.create_extractor_completion(messages, stream=False)
            return self._parse_extraction_response(response)
        except Exception as e:
            self.logger.error(f"❌ LLM preference extraction failed: {e}")
            return {}
    
    def _build_extraction_prompt(self, context: PipelineContext) -> str:
        """Build the preference extraction prompt"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        return f"""
You are an expert travel preference extractor. Extract ALL travel-related information from this user message. You MUST RESPOND IN FRENCH.

LANGUAGE REQUIREMENT: You are a French travel agent. All your analysis and reasoning must be in French.

CURRENT DATE: {current_date}

USER INPUT: {context.user_input}
ORCHESTRATION CONTEXT: {json.dumps(context.get_metadata('orchestration_result', {}), indent=2, ensure_ascii=False)}

EXTRACT and return a JSON object with these fields:
- destination: specific places, countries, cities mentioned
- duration: how long they want to travel
- travel_dates: when they want to travel (season, month, relative dates like "dans 2 semaines") - REQUIRED
- budget_amount: numeric amount in euros (optional - only if clearly mentioned with specific amount)
- style: travel style (cultural, adventure, luxury, relaxation, gastronomy, etc.)
- group_size: solo, couple, family, group
- accommodation: hotel preferences (5_stars, 4_stars, 3_stars, luxury, budget, standard)
- activities: array of activities they want (plage, culture, aventure, détente, gastronomie, etc.)

EXAMPLES:
- "Je veux aller au Japon pour 2 semaines en avril" → {{"destination": "Japan", "duration": "2 semaines", "travel_dates": "avril"}}
- "Budget de 3000 euros pour une aventure culturelle" → {{"budget_amount": 3000, "style": "cultural"}}
- "Philippines en famille pour 10 jours avec plages" → {{"destination": "Philippines", "duration": "10 jours", "group_size": "family", "activities": ["plage"]}}
- "Hôtel 5 étoiles au Maldives" → {{"destination": "Maldives", "accommodation": "5_stars"}}

RESPOND ONLY WITH VALID JSON:
"""
    
    def _parse_extraction_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM extraction response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                self.logger.debug(f"✅ Parsed extraction result: {result}")
                return result
            else:
                self.logger.warning("❌ No JSON found in extraction response")
                return {}
        except Exception as e:
            self.logger.error(f"❌ Failed to parse extraction response: {e}")
            return {}
    
    def _merge_preferences(self, fast_prefs: Dict[str, Any], llm_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge fast and LLM preferences (LLM takes precedence)"""
        merged = fast_prefs.copy()
        
        for key, value in llm_prefs.items():
            if value:  # Only update if LLM provided a value
                merged[key] = value
        
        return merged
    
    def _is_modification_request(self, user_input: str) -> bool:
        """Detect if user wants to modify preferences"""
        modification_indicators = [
            "changer", "modifier", "différent", "autre", "plutôt", "préfère", 
            "préférerais", "voudrais", "aimerais", "au lieu de", "pas", "non",
            "corriger", "ajuster", "revoir", "reconsidérer", "modifiez", "changez"
        ]
        
        user_input_lower = user_input.lower()
        return any(indicator in user_input_lower for indicator in modification_indicators) 