"""
Preference Extractor Component for ASIA.fr Agent
Handles intelligent extraction of travel preferences from user input
"""

import json
import re
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
            r'\b(mongolia|mongolie|mongol)\b'
        ]
        
        self.duration_patterns = [
            r'\b(\d+)\s*(jours?|days?)\b',
            r'\b(\d+)\s*(semaines?|weeks?)\b',
            r'\b(\d+)\s*(mois|months?)\b'
        ]
        
        self.budget_patterns = [
            r'\b(budget\s+(bas|low|faible))\b',
            r'\b(budget\s+(moyen|medium))\b',
            r'\b(budget\s+(élevé|high|haut))\b',
            r'\b(économique|cheap|pas cher)\b',
            r'\b(luxe|luxury|premium)\b'
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
            'mongolia': 'Mongolia', 'mongolie': 'Mongolia', 'mongol': 'Mongolia'
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
            
            # Update context with new preferences
            if merged_preferences:
                context.update_preferences(merged_preferences)
                
                # Update memory service
                self.memory_service.update_user_preferences(context.conversation_id, merged_preferences)
                self.logger.info(f"📊 Extracted preferences: {merged_preferences}")
            
            # Store extraction metadata
            context.add_metadata('extracted_preferences', merged_preferences)
            
            # Check if this is a modification request
            if self._is_modification_request(context.user_input):
                context.add_metadata('is_modification', True)
                self.logger.info("🔄 Detected preference modification request")
            
            return context
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
        
        # Extract budget
        for pattern in self.budget_patterns:
            match = re.search(pattern, input_lower)
            if match:
                if any(word in match.group(0) for word in ['bas', 'low', 'faible', 'économique', 'cheap']):
                    preferences['budget'] = 'low'
                elif any(word in match.group(0) for word in ['moyen', 'medium']):
                    preferences['budget'] = 'medium'
                elif any(word in match.group(0) for word in ['élevé', 'high', 'haut', 'luxe', 'luxury', 'premium']):
                    preferences['budget'] = 'high'
                break
        
        # Extract travel style
        style_patterns = {
            'cultural': ['culturel', 'cultural', 'tradition', 'histoire', 'historique'],
            'adventure': ['aventure', 'adventure', 'trekking', 'randonnée', 'hiking'],
            'relaxation': ['détente', 'relaxation', 'plage', 'bien-être', 'spa'],
            'gastronomy': ['gastronomie', 'cuisine', 'food', 'culinaire', 'dégustation']
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
    
    async def _llm_preference_extraction(self, context: PipelineContext) -> Dict[str, Any]:
        """Use LLM for intelligent preference extraction"""
        prompt = self._build_extraction_prompt(context)
        
        try:
            response = await self.llm_service.generate_text(prompt, model="extractor")
            return self._parse_extraction_response(response)
        except Exception as e:
            self.logger.error(f"❌ LLM preference extraction failed: {e}")
            return {}
    
    def _build_extraction_prompt(self, context: PipelineContext) -> str:
        """Build the preference extraction prompt"""
        return f"""
You are an expert travel preference extractor. Extract ALL travel-related information from this user message. You MUST RESPOND IN FRENCH.

LANGUAGE REQUIREMENT: You are a French travel agent. All your analysis and reasoning must be in French.

USER INPUT: {context.user_input}
ORCHESTRATION CONTEXT: {json.dumps(context.get_metadata('orchestration_result', {}), indent=2, ensure_ascii=False)}

EXTRACT and return a JSON object with these fields:
- destination: specific places, countries, cities mentioned
- duration: how long they want to travel
- budget: low/medium/high based on language used
- style: travel style (cultural, adventure, luxury, relaxation, etc.)
- group_size: solo, couple, family, group
- timing: when they want to travel (season, month, etc.)

EXAMPLES:
- "Je veux aller au Japon pour 2 semaines" → {{"destination": "Japan", "duration": "2 semaines"}}
- "Budget moyen pour une aventure culturelle" → {{"budget": "medium", "style": "cultural"}}
- "Philippines en famille pour 10 jours" → {{"destination": "Philippines", "duration": "10 jours", "group_size": "family"}}

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