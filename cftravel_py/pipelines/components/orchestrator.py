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
        
        # AI will handle all intent detection intelligently
    
    def is_required(self, context: PipelineContext) -> bool:
        """Always required - orchestrator makes the initial decision"""
        return True
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process user input and determine conversation flow using AI intelligence"""
        try:
            # Always use AI for intelligent orchestration - no hardcoded conditions
            self.logger.info(f"🎯 Using AI orchestration for: {context.user_input}")
            self.logger.info(f"🎯 Current preferences: {context.user_preferences}")
            
            # Use LLM for intelligent orchestration
            orchestration_result = await self._llm_orchestrate(context)
            
            self.logger.info(f"🎯 AI orchestration result: {orchestration_result}")
            
            # Store orchestration result in context
            context.add_metadata('orchestration_result', orchestration_result)
            context.add_metadata('intent', orchestration_result.get('intent', 'general'))
            context.add_metadata('should_show_offers', orchestration_result.get('should_show_offers', False))
            context.add_metadata('needs_confirmation', orchestration_result.get('needs_confirmation', False))
            context.add_metadata('response_type', orchestration_result.get('response_type', 'question'))
            
            self.logger.info(f"🎯 Orchestration result: {orchestration_result.get('intent')} - Show offers: {orchestration_result.get('should_show_offers')}")
            self.logger.info(f"🎯 Full orchestration result: {orchestration_result}")
            
            return context
            
        except Exception as e:
            self.log_error(context, e)
            # Fallback to default orchestration
            context.add_metadata('orchestration_result', self._default_orchestration())
            return context
    
    # AI handles all intent detection intelligently - no hardcoded methods needed
    
    async def _llm_orchestrate(self, context: PipelineContext) -> Dict[str, Any]:
        """Use LLM for intelligent orchestration"""
        prompt = self._build_orchestration_prompt(context)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.llm_service.create_reasoning_completion(messages, stream=False)
            result = self._parse_orchestration_response(response)
            
            # Debug logging
            self.logger.info(f"🎯 Orchestration input: {context.user_input}")
            self.logger.info(f"🎯 Current preferences: {context.user_preferences}")
            self.logger.info(f"🎯 Orchestration result: {result}")
            
            return result
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
    "intent": "question|confirmation|modification|booking|general|preference_complete",
    "confidence": 0.0-1.0,
    "response_type": "question|preference_summary|show_offers|modification",
    "needs_confirmation": true/false,
    "has_sufficient_details": true/false,
    "should_show_offers": true/false,
    "offer_count": 3,
    "reasoning": "Your reasoning in French"
}}

INTELLIGENT DETECTION RULES:
You are an intelligent travel agent. Analyze the user's intent naturally and respond appropriately.

INTENT TYPES:
1. **greeting**: User is greeting, thanking, or saying goodbye
2. **confirmation**: User confirms preferences or wants to see offers
3. **modification**: User wants to change preferences or modify choices
4. **preference_complete**: We have sufficient preferences to show summary
5. **general**: User is asking questions, seeking advice, or providing new information
6. **suggestion_request**: User wants AI suggestions or recommendations

RESPONSE TYPES:
- **greeting**: Friendly response to greetings/thanks
- **question**: Ask for more information or preferences
- **preference_summary**: Show current preferences for confirmation
- **show_offers**: Display travel offers
- **modification**: Help user modify preferences
- **suggestion**: Provide AI recommendations
- **conversation**: Natural conversation response

CONTEXT AWARENESS:
- If user has already seen offers and wants to modify → intent: "modification"
- If user asks for suggestions → intent: "suggestion_request"
- If user is just chatting → intent: "general"
- If user confirms after seeing offers → intent: "confirmation", should_show_offers: true
- If user wants different offers → intent: "modification"

UNDERSTAND NATURALLY:
- Don't rely only on keywords, understand the conversation flow
- Consider what the user is trying to achieve
- Be flexible and conversational
- Allow users to modify choices at any time
- Provide helpful suggestions when appropriate

REQUIRED PREFERENCES FOR OFFERS:
- destination (country/city)
- duration (number of days/weeks)
- budget (low/medium/high)
- style (cultural, adventure, luxury, relaxation, etc.)

UNDERSTAND THE USER'S INTENT NATURALLY:
- Don't rely only on keywords, understand the context and meaning
- Consider the conversation flow and what the user is trying to achieve
- If user seems satisfied with their preferences, they likely want to see offers
- If user expresses dissatisfaction or wants changes, they want to modify

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