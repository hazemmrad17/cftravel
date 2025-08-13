"""
Orchestrator Component for ASIA.fr Agent
Handles conversation flow decisions and intent classification
"""

import json
import re
from typing import Dict, Any, List
from ..core import PipelineComponent, PipelineContext, PipelineState
from services.llm_service import LLMService
from services.memory_service import MemoryService

class OrchestratorComponent(PipelineComponent):
    """Orchestrates conversation flow and makes intelligent decisions"""
    
    def __init__(self, llm_service: LLMService, memory_service: MemoryService):
        super().__init__("Orchestrator", priority=100)  # Highest priority
        self.llm_service = llm_service
        self.memory_service = memory_service
        
        # Fast path patterns
        self.confirmation_words = [
            "oui", "parfait", "c'est bon", "ok", "d'accord", "confirmer", 
            "exactement", "précisément", "montrer les offres", "voir les offres",
            "c'est parfait", "ça me convient", "parfait", "montrez-moi", "je veux voir"
        ]
        self.greeting_words = ["bonjour", "hello", "salut", "hi", "hey"]
        self.modification_words = [
            "changer", "modifier", "différent", "autre", "plutôt", "préfère", 
            "préférerais", "voudrais", "aimerais", "au lieu de", "pas", "non",
            "corriger", "ajuster", "revoir", "reconsidérer"
        ]
    
    def is_required(self, context: PipelineContext) -> bool:
        """Always required - orchestrator makes the initial decision"""
        return True
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process user input and determine conversation flow"""
        try:
            # Check for simple cases first (fast path)
            if self._is_simple_confirmation(context.user_input):
                orchestration_result = self._fast_confirmation_response(context)
            elif self._is_simple_greeting(context.user_input):
                orchestration_result = self._fast_greeting_response(context)
            elif self._is_modification_request(context.user_input):
                orchestration_result = self._fast_modification_response(context)
            else:
                # Use LLM for complex orchestration
                orchestration_result = await self._llm_orchestrate(context)
            
            # Store orchestration result in context
            context.add_metadata('orchestration_result', orchestration_result)
            context.add_metadata('intent', orchestration_result.get('intent', 'general'))
            context.add_metadata('should_show_offers', orchestration_result.get('should_show_offers', False))
            context.add_metadata('needs_confirmation', orchestration_result.get('needs_confirmation', False))
            context.add_metadata('response_type', orchestration_result.get('response_type', 'question'))
            
            self.logger.info(f"🎯 Orchestration result: {orchestration_result.get('intent')} - Show offers: {orchestration_result.get('should_show_offers')}")
            
            return context
            
        except Exception as e:
            self.log_error(context, e)
            # Fallback to default orchestration
            context.add_metadata('orchestration_result', self._default_orchestration())
            return context
    
    def _is_simple_confirmation(self, user_input: str) -> bool:
        """Fast check for simple confirmation responses"""
        return any(word in user_input.lower() for word in self.confirmation_words)
    
    def _is_simple_greeting(self, user_input: str) -> bool:
        """Fast check for simple greetings"""
        return any(word in user_input.lower() for word in self.greeting_words)
    
    def _is_modification_request(self, user_input: str) -> bool:
        """Fast check for modification requests"""
        return any(word in user_input.lower() for word in self.modification_words)
    
    def _fast_confirmation_response(self, context: PipelineContext) -> Dict[str, Any]:
        """Fast response for confirmations without LLM call"""
        return {
            "intent": "confirmation",
            "confidence": 0.9,
            "response_type": "confirmation",
            "needs_confirmation": False,
            "has_sufficient_details": len(context.user_preferences) >= 3,
            "should_show_offers": len(context.user_preferences) >= 3,
            "show_preference_summary": False,  # Skip summary since user already confirmed
            "offer_count": 3,
            "reasoning": "Utilisateur a confirmé ses préférences"
        }
    
    def _fast_greeting_response(self, context: PipelineContext) -> Dict[str, Any]:
        """Fast response for greetings without LLM call"""
        return {
            "intent": "general",
            "confidence": 0.8,
            "response_type": "question",
            "needs_confirmation": False,
            "has_sufficient_details": False,
            "should_show_offers": False,
            "offer_count": 0,
            "reasoning": "Utilisateur a salué, nécessite de recueillir les préférences"
        }
    
    def _fast_modification_response(self, context: PipelineContext) -> Dict[str, Any]:
        """Fast response for modification requests"""
        return {
            "intent": "modification",
            "confidence": 0.85,
            "response_type": "modification",
            "needs_confirmation": False,
            "has_sufficient_details": False,
            "should_show_offers": False,
            "offer_count": 0,
            "reasoning": "Utilisateur souhaite modifier ses préférences"
        }
    
    async def _llm_orchestrate(self, context: PipelineContext) -> Dict[str, Any]:
        """Use LLM for intelligent orchestration"""
        prompt = self._build_orchestration_prompt(context)
        
        try:
            response = await self.llm_service.generate_text(prompt, model="orchestrator")
            return self._parse_orchestration_response(response)
        except Exception as e:
            self.logger.error(f"❌ LLM orchestration failed: {e}")
            return self._default_orchestration()
    
    def _build_orchestration_prompt(self, context: PipelineContext) -> str:
        """Build the orchestration prompt"""
        return f"""
You are ASIA.fr Agent, an intelligent travel specialist. You MUST ALWAYS RESPOND IN FRENCH. Analyze this user input and decide the best course of action.

LANGUAGE REQUIREMENT: You are a French travel agent. All your responses, reasoning, and analysis must be in French.

CONVERSATION CONTEXT:
- Turn count: {context.turn_count}
- Current preferences: {json.dumps(context.user_preferences, indent=2, ensure_ascii=False)}
- Conversation history: {context.conversation_history[-300:] if context.conversation_history else "None"}

USER INPUT: "{context.user_input}"

ANALYZE THE USER INPUT AND PROVIDE A JSON RESPONSE WITH THE FOLLOWING STRUCTURE:
{{
    "intent": "question|confirmation|modification|booking|general",
    "confidence": 0.0-1.0,
    "response_type": "question|confirmation|offers|modification",
    "needs_confirmation": true/false,
    "has_sufficient_details": true/false,
    "should_show_offers": true/false,
    "offer_count": 3,
    "reasoning": "Your reasoning in French"
}}

DETECTION RULES:
1. If user says "oui", "parfait", "c'est bon", "ok", "d'accord", "confirmer", "montrer les offres", "voir les offres" AND we have sufficient details → intent: "confirmation", should_show_offers: true
2. If user wants to modify preferences → intent: "modification", response_type: "modification"
3. If we have all required preferences (destination, duration, budget, travel_style) → has_sufficient_details: true
4. If user confirms and we have sufficient details → should_show_offers: true, offer_count: 3

REQUIRED PREFERENCES FOR OFFERS:
- destination (country/city)
- duration (number of days)
- budget (price range)
- travel_style (luxury, adventure, cultural, etc.)

RESPOND ONLY WITH VALID JSON:
"""
    
    def _parse_orchestration_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM orchestration response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                self.logger.debug(f"✅ Parsed orchestration result: {result}")
                return result
            else:
                self.logger.warning("❌ No JSON found in orchestrator response")
                return self._default_orchestration()
        except Exception as e:
            self.logger.error(f"❌ Failed to parse orchestration response: {e}")
            return self._default_orchestration()
    
    def _default_orchestration(self) -> Dict[str, Any]:
        """Default orchestration when LLM fails"""
        return {
            "intent": "general",
            "confidence": 0.5,
            "response_type": "question",
            "needs_confirmation": False,
            "has_sufficient_details": False,
            "should_show_offers": False,
            "offer_count": 0,
            "reasoning": "Fallback orchestration due to error"
        } 