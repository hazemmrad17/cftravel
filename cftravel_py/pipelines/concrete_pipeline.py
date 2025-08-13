"""
Intelligent AI Pipeline for ASIA.fr Agent
- Uses LLM orchestration for seamless decision-making
- No hardcoded conditions - everything is AI-driven
- Intelligent preference extraction and offer matching
- Enhanced error handling and robustness
- Optimized for speed and performance
"""

import os
import logging
import time
import random
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
import numpy as np
from functools import lru_cache

from core.config import config
from core.constants import LLMProvider
from core.config import LLMConfig
from services.llm_service import LLMFactory
from data.data_processor import DataProcessor, TravelOffer

# Suppress HTTP warnings and logging
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("langchain").setLevel(logging.ERROR)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

def debug_print(message: str):
    """Print debug message if DEBUG is enabled"""
    if DEBUG:
        print(f"🔍 DEBUG: {message}")

class SimpleMemory:
    """Minimal in-process memory replacement (avoids langchain dependency)"""
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]):
        # No-op; we keep chat history in ConversationContext
        return

    def clear(self):
        return

@dataclass
class ConversationContext:
    """Context for the current conversation"""
    user_preferences: Dict[str, Any]
    chat_history: str
    current_intent: str
    conversation_id: str
    turn_count: int
    last_response_type: str = ""
    confidence_score: float = 0.0
    current_state: str = "gathering_preferences"  # "gathering_preferences", "confirmation", "showing_offers", "completed"
    needs_confirmation: bool = False
    confirmation_summary: str = ""

class IntelligentPipeline:
    """
    Intelligent AI Pipeline that uses LLM orchestration for all decisions
    - No hardcoded conditions
    - Seamless preference extraction
    - Intelligent offer matching
    - Natural conversation flow
    - Enhanced error handling and robustness
    - Optimized for speed and performance
    
    """
    
    def __init__(self, data_path: str = None):
        debug_print("🚀 Initializing IntelligentPipeline")
        self.data_path = data_path or config.data_path
        
        # Initialize core components
        self._models_initialized = False
        self._data_initialized = False
        self._memory_initialized = False
        
        # Initialize conversation context immediately
        self.conversation_context = ConversationContext(
            user_preferences={},
            chat_history="",
            current_intent="",
            conversation_id="",
            turn_count=0,
            last_response_type="",
            confidence_score=0.0
        )
        
        # Cache for performance
        self._orchestration_cache = {}
        self._preference_cache = {}
        
        debug_print("✅ IntelligentPipeline initialization complete")
    
    def _ensure_models_loaded(self):
        """Lazy load models only when needed"""
        if not self._models_initialized:
            self.setup_models()
            self._models_initialized = True
    
    def _ensure_data_loaded(self):
        """Lazy load data only when needed"""
        if not self._data_initialized:
            self.setup_data()
            self._data_initialized = True
    
    def _ensure_memory_loaded(self):
        """Lazy load memory only when needed"""
        if not self._memory_initialized:
            self.setup_memory()
            self._memory_initialized = True
    
    def setup_models(self):
        """Setup all AI models for the pipeline using environment configuration"""
        debug_print("🔧 Setting up AI models...")
        
        try:
            # Get all model configurations from environment
            models_config = config.get_all_models_config()
            
            # 1. Orchestrator Model - Makes all decisions
            reasoning_config = models_config["reasoning_model"]
            self.orchestrator = self._setup_model_from_config(reasoning_config, "orchestration")
            
            # 2. Generation Model - Creates responses
            generation_config = models_config["generation_model"]
            self.generator = self._setup_model_from_config(generation_config, "generation")
            
            # 3. Matching Model - Matches offers
            matcher_config = models_config["matcher_model"]
            self.matcher = self._setup_model_from_config(matcher_config, "matching")
            
            # 4. Embedding Model - Semantic search (lazy load)
            self._embedding_config = models_config["embedding_model"]
            
            debug_print("✅ AI models setup complete")
            
        except Exception as e:
            debug_print(f"⚠️ Model setup failed: {e}")
            # Fallback to basic models
            self._setup_fallback_models()

    def _setup_model_from_config(self, model_config: Dict[str, Any], purpose: str):
        """Setup a model using configuration dictionary"""
        try:
            debug_print(f"🤖 Setting up {purpose} model: {model_config['model']}")
            
            llm_config = LLMConfig(
                provider="groq",
                model_name=model_config["model"],
                temperature=model_config["temperature"],
                max_tokens=model_config["max_tokens"],
                api_key=model_config["api_key"],
                base_url=model_config["base_url"]
            )
            
            return LLMFactory.create_llm(llm_config)
            
        except Exception as e:
            debug_print(f"⚠️ {purpose.capitalize()} model setup failed: {e}")
            return None

    def _setup_embedding_model_from_config(self, embedding_config: Dict[str, Any]):
        """Setup embedding model using configuration"""
        try:
            model_name = embedding_config["model"]
            debug_print(f"🔍 Setting up embedding model: {model_name}")
            return SentenceTransformer(model_name)
        except Exception as e:
            debug_print(f"⚠️ Could not load embedding model: {e}")
            return None

    def _setup_fallback_models(self):
        """Setup fallback models if environment configuration fails"""
        debug_print("🔄 Setting up fallback models...")
        
        # Fallback to Kimia K2 models
        self.orchestrator = self._safe_setup_model("REASONING_MODEL", "openai/gpt-oss-120b", 0.1, "orchestration")
        self.generator = self._safe_setup_model("GENERATION_MODEL", "moonshotai/kimi-k2-instruct", 0.7, "generation")
        self.matcher = self._safe_setup_model("MATCHING_MODEL", "moonshotai/kimi-k2-instruct", 0.3, "matching")
        self.embedding_model = self._setup_embedding_model()
    
    def _safe_setup_model(self, env_var: str, default_model: str, temperature: float, purpose: str):
        """Wrapper to prevent initialization failures from breaking the agent startup"""
        try:
            return self._setup_model(env_var, default_model, temperature, purpose)
        except Exception as e:
            debug_print(f"⚠️ {purpose.capitalize()} model setup failed: {e}")
            return None
    
    def _setup_model(self, env_var: str, default_model: str, temperature: float, purpose: str):
        """Setup a specific model with enhanced error handling"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            debug_print(f"⚠️ GROQ_API_KEY not set - {purpose} model unavailable")
            return None
        
        model_name = os.getenv(env_var, default_model)
        config = LLMConfig(
            provider="groq",
            model_name=model_name,
            temperature=temperature,
            max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "2048")),
            api_key=api_key,
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        )
        
        debug_print(f"🤖 {purpose.capitalize()} model: {model_name}")
        return LLMFactory.create_llm(config)
    
    def _setup_embedding_model(self):
        """Setup embedding model for semantic search"""
        try:
            return SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            debug_print(f"⚠️ Could not load embedding model: {e}")
            return None
    
    def setup_data(self):
        """Setup data processor with lazy loading"""
        debug_print("📊 Setting up data processor...")
        json_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "asia", "data.json")
        
        try:
            self.data_processor = DataProcessor(json_file_path)
            debug_print(f"📊 Loaded {len(self.data_processor.offers)} offers")
        except Exception as e:
            debug_print(f"❌ Data processor setup failed: {e}")
            self.data_processor = None
    
    def setup_memory(self):
        """Setup memory system"""
        debug_print("🧠 Setting up memory...")
        self.memory = SimpleMemory()
        debug_print("✅ Memory setup complete")
    
    def _call_llm_with_retry(self, llm, prompt: str, max_retries: int = 3, timeout: int = 30):
        """Call LLM with retry logic and enhanced error handling"""
        if llm is None:
            raise Exception("LLM model not available")
        
        for attempt in range(max_retries):
            try:
                debug_print(f"🔄 LLM call attempt {attempt + 1}/{max_retries}")
                start_time = time.time()
                response = llm.invoke(prompt)
                elapsed_time = time.time() - start_time
                debug_print(f"✅ LLM call successful in {elapsed_time:.2f}s")
                return response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                error_msg = str(e)
                debug_print(f"❌ LLM call failed (attempt {attempt + 1}): {error_msg}")
                
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    if attempt < max_retries - 1:
                        delay = (2 ** attempt) + random.uniform(0, 1)
                        debug_print(f"⏳ Rate limited. Waiting {delay:.2f}s...")
                        time.sleep(delay)
                        continue
                    raise Exception(f"Rate limit exceeded after {max_retries} attempts")
                
                if attempt == max_retries - 1:
                    raise
        
        raise Exception(f"LLM call failed after {max_retries} attempts")

    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Main method to process user input and generate appropriate response
        Optimized for speed and performance
        """
        start_time = time.time()
        
        try:
            # Lazy load components only when needed
            self._ensure_models_loaded()
            
            # Update conversation context
            self.conversation_context.turn_count += 1
            self.conversation_context.chat_history += f"\nUser: {user_input}"
            
            # Check cache for similar inputs
            cache_key = f"{user_input[:50]}_{self.conversation_context.turn_count}"
            if cache_key in self._orchestration_cache:
                debug_print("⚡ Using cached orchestration result")
                orchestration_result = self._orchestration_cache[cache_key]
            else:
                # Use orchestrator to make intelligent decisions
                orchestration_result = self._orchestrate_conversation(user_input)
            # Cache the result
            self._orchestration_cache[cache_key] = orchestration_result
            
            # Extract preferences intelligently
            preferences = self._extract_preferences_intelligently(user_input, orchestration_result)
            
            # Update conversation context with new preferences
            self._update_context(preferences, orchestration_result)
            
            # Generate response based on orchestration result
            response = self._generate_intelligent_response(user_input, orchestration_result, preferences)
            
            processing_time = time.time() - start_time
            debug_print(f"⚡ Processing completed in {processing_time:.2f}s")
            
            return response
            
        except Exception as e:
            debug_print(f"❌ Error in process_user_input: {e}")
            return {
                "response": f"I encountered an error: {str(e)}. Please try rephrasing your request.",
                "error": str(e)
            }
    
    def _orchestrate_conversation(self, user_input: str) -> Dict[str, Any]:
        """
        Use the orchestrator model to make intelligent decisions about the conversation
        Optimized with caching and faster processing
        """
        # Check if we can use a simple heuristic for common cases
        if self._is_simple_confirmation(user_input):
            return self._fast_confirmation_response()
        
        if self._is_simple_greeting(user_input):
            return self._fast_greeting_response()
        
        prompt = f"""
You are ASIA.fr Agent, an intelligent travel specialist. You MUST ALWAYS RESPOND IN FRENCH. Analyze this user input and decide the best course of action.

LANGUAGE REQUIREMENT: You are a French travel agent. All your responses, reasoning, and analysis must be in French.

CONVERSATION CONTEXT:
- Turn count: {self.conversation_context.turn_count}
- Current preferences: {json.dumps(self.conversation_context.user_preferences, indent=2)}
- Current state: {self.conversation_context.current_state}
- Chat history: {self.conversation_context.chat_history[-300:] if self.conversation_context.chat_history else "None"}

USER INPUT: "{user_input}"

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
        
        try:
            response = self.orchestrator.invoke(prompt)
            debug_print(f"🎯 Orchestrator response: {response}")
            
            # Extract content from response object
            response_text = response.content if hasattr(response, 'content') else str(response)
            debug_print(f"🎯 Orchestrator response text: {response_text}")
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                debug_print(f"✅ Orchestration result: {result}")
                return result
            else:
                debug_print(f"❌ No JSON found in orchestrator response")
                return self._default_orchestration()
                
        except Exception as e:
            debug_print(f"❌ Orchestration failed: {e}")
            return self._default_orchestration()
    
    def _is_simple_confirmation(self, user_input: str) -> bool:
        """Fast check for simple confirmation responses"""
        confirmation_words = ["oui", "parfait", "c'est bon", "ok", "d'accord", "confirmer", "exactement", "précisément"]
        return any(word in user_input.lower() for word in confirmation_words)
    
    def _is_simple_greeting(self, user_input: str) -> bool:
        """Fast check for simple greetings"""
        greeting_words = ["bonjour", "hello", "salut", "hi", "hey"]
        return any(word in user_input.lower() for word in greeting_words)
    
    def _fast_confirmation_response(self) -> Dict[str, Any]:
        """Fast response for confirmations without LLM call"""
        return {
            "intent": "confirmation",
            "confidence": 0.9,
            "response_type": "confirmation",
            "needs_confirmation": False,
            "has_sufficient_details": len(self.conversation_context.user_preferences) >= 3,
            "should_show_offers": len(self.conversation_context.user_preferences) >= 3,
            "offer_count": 3,
            "reasoning": "Utilisateur a confirmé ses préférences"
        }
    
    def _fast_greeting_response(self) -> Dict[str, Any]:
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
    
    def _extract_preferences_intelligently(self, user_input: str, orchestration_result: Dict) -> Dict[str, Any]:
        """
        Use AI to intelligently extract preferences from user input
        """
        prompt = f"""
You are an expert travel preference extractor. Extract ALL travel-related information from this user message. You MUST RESPOND IN FRENCH.

LANGUAGE REQUIREMENT: You are a French travel agent. All your analysis and reasoning must be in French.

USER INPUT: {user_input}
ORCHESTRATION CONTEXT: {json.dumps(orchestration_result, indent=2)}

EXTRACT and return a JSON object with these fields:
- destination: specific places, countries, cities mentioned
- duration: how long they want to travel
- budget: low/medium/high based on language used
- style: travel style (cultural, adventure, luxury, relaxation, etc.)
- group_size: solo, couple, family, group
- timing: when they want to travel (dates, seasons, etc.)

EXAMPLES:
- "I'm heading to Japan" → {{"destination": "Japan"}}
- "I want cultural experience" → {{"style": "cultural"}}
- "Japan for cultural experience" → {{"destination": "Japan", "style": "cultural"}}
- "yes exactly i want cultural experience" → {{"style": "cultural"}}

CRITICAL: If the user mentions ANY destination (like "Japan", "Tokyo", etc.), extract it as destination.
If they mention ANY travel style (like "cultural", "adventure", etc.), extract it as style.

YOU MUST RESPOND WITH VALID JSON ONLY. NO OTHER TEXT. ALL ANALYSIS MUST BE IN FRENCH.

Return ONLY valid JSON in this format:
{{
    "destination": "extracted destination",
    "duration": "extracted duration",
    "budget": "low/medium/high",
    "style": "extracted style",
    "group_size": "extracted group size",
    "timing": "extracted timing"
}}

JSON Response:
"""
        
        try:
            response = self._call_llm_with_retry(self.generator, prompt)
            preferences = self._parse_json_safely(response)
            
            # Clean up preferences
            cleaned_prefs = {}
            for key, value in preferences.items():
                if value and str(value).lower() not in ['null', 'none', 'unknown', '']:
                    cleaned_prefs[key] = str(value).strip()
            
            # Map specific cities to countries for better matching
            if cleaned_prefs.get('destination'):
                dest = cleaned_prefs['destination'].lower()
                city_to_country = {
                    'tokyo': 'japan',
                    'kyoto': 'japan',
                    'osaka': 'japan',
                    'hanoi': 'vietnam',
                    'ho chi minh': 'vietnam',
                    'bangkok': 'thailand',
                    'phuket': 'thailand',
                    'siem reap': 'cambodia',
                    'phnom penh': 'cambodia',
                    'vientiane': 'laos',
                    'luang prabang': 'laos',
                    'yangon': 'myanmar',
                    'mandalay': 'myanmar',
                    'singapore': 'singapore',
                    'kuala lumpur': 'malaysia',
                    'jakarta': 'indonesia',
                    'bali': 'indonesia',
                    'manila': 'philippines',
                    'beijing': 'china',
                    'shanghai': 'china',
                    'mumbai': 'india',
                    'delhi': 'india',
                    'kathmandu': 'nepal',
                    'thimphu': 'bhutan',
                    'colombo': 'sri lanka',
                    'male': 'maldives',
                    'amman': 'jordan',
                    'beirut': 'lebanon',
                    'damascus': 'syria',
                    'baghdad': 'iraq',
                    'tehran': 'iran',
                    'muscat': 'oman',
                    'sanaa': 'yemen',
                    'riyadh': 'saudi arabia',
                    'jeddah': 'saudi arabia',
                    'kuwait city': 'kuwait',
                    'doha': 'qatar',
                    'manama': 'bahrain',
                    'dubai': 'uae',
                    'abu dhabi': 'uae'
                }
                
                if dest in city_to_country:
                    cleaned_prefs['destination'] = city_to_country[dest]
                    debug_print(f"🔄 Mapped city '{dest}' to country '{city_to_country[dest]}'")
            
            debug_print(f"📊 Extracted preferences: {cleaned_prefs}")
            return cleaned_prefs
            
        except Exception as e:
            debug_print(f"❌ Preference extraction failed: {e}")
            return {}
    
    def _update_context(self, new_preferences: Dict, orchestration_result: Dict):
        """Update conversation context with new information"""
        # Merge preferences
        for key, value in new_preferences.items():
            if value:
                self.conversation_context.user_preferences[key] = value
        
        # Update intent and confidence
        self.conversation_context.current_intent = orchestration_result.get("intent", "general")
        self.conversation_context.confidence_score = orchestration_result.get("confidence", 0.0)
        self.conversation_context.last_response_type = orchestration_result.get("response_type", "")
        
        # Handle confirmation flow based on orchestration results
        needs_confirmation = orchestration_result.get("needs_confirmation", False)
        has_sufficient_details = orchestration_result.get("has_sufficient_details", False)
        should_show_offers = orchestration_result.get("should_show_offers", False)
        
        # Check if user is confirming (intent is confirmation)
        is_confirmation = orchestration_result.get("intent") == "confirmation"
        
        if has_sufficient_details and needs_confirmation and not is_confirmation:
            # User has provided sufficient details, ask for confirmation through text
            self.conversation_context.current_state = "confirmation"
            self.conversation_context.needs_confirmation = False  # No UI card needed
            debug_print(f"📋 Setting confirmation state - user has sufficient details (text-based)")
        elif is_confirmation and should_show_offers:
            # User has confirmed, show offers
            self.conversation_context.current_state = "showing_offers"
            self.conversation_context.needs_confirmation = False
            debug_print(f"🎯 User confirmed - showing offers")
        elif orchestration_result.get("intent") == "modification":
            # User wants to modify preferences
            self.conversation_context.current_state = "gathering_preferences"
            self.conversation_context.needs_confirmation = False
            debug_print(f"🔄 User wants to modify preferences")
        elif should_show_offers and not needs_confirmation:
            # Direct offer request (e.g., user explicitly asks for offers)
            self.conversation_context.current_state = "showing_offers"
            self.conversation_context.needs_confirmation = False
            debug_print(f"🎯 Direct offer request - showing offers")
        else:
            # Continue gathering preferences
            self.conversation_context.current_state = "gathering_preferences"
            self.conversation_context.needs_confirmation = False
        
        debug_print(f"🔄 Updated context: {self.conversation_context.user_preferences}, State: {self.conversation_context.current_state}")
    
    def _check_sufficient_details(self) -> bool:
        """Check if we have sufficient details to ask for confirmation"""
        preferences = self.conversation_context.user_preferences
        
        # Count how many key preferences we have
        key_preferences = ['destination', 'duration', 'style', 'budget', 'travelers']
        preference_count = sum(1 for pref in key_preferences if preferences.get(pref))
        
        # We need at least 2 key preferences to ask for confirmation
        return preference_count >= 2
    
    def _generate_confirmation_summary(self) -> str:
        """Generate a concise summary of preferences for confirmation in French"""
        preferences = self.conversation_context.user_preferences
        
        summary_parts = []
        
        if preferences.get('destination'):
            summary_parts.append(f"• Destination : {preferences['destination']}")
        
        if preferences.get('duration'):
            summary_parts.append(f"• Durée : {preferences['duration']}")
        
        if preferences.get('style'):
            summary_parts.append(f"• Style : {preferences['style']}")
        
        if preferences.get('budget'):
            summary_parts.append(f"• Budget : {preferences['budget']}")
        
        if preferences.get('group_size'):
            summary_parts.append(f"• Voyageurs : {preferences['group_size']}")
        
        if preferences.get('timing'):
            summary_parts.append(f"• Période : {preferences['timing']}")
        
        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "Aucune préférence définie"
    
    def _generate_intelligent_response(self, user_input: str, orchestration_result: Dict, preferences: Dict) -> Dict[str, Any]:
        """
        Generate intelligent response based on orchestration results
        """
        should_show_offers = orchestration_result.get("should_show_offers", False)
        offer_count = orchestration_result.get("offer_count", 0)
        response_type = orchestration_result.get("response_type", "question")
        needs_confirmation = orchestration_result.get("needs_confirmation", False)
        has_sufficient_details = orchestration_result.get("has_sufficient_details", False)
        is_confirmation = orchestration_result.get("intent") == "confirmation"
        
        # Generate the response text
        response = self._generate_response_text(user_input, orchestration_result, preferences)
        
        # Initialize response structure
        response = {
            "response": response,
            "preferences": preferences,
            "intent": orchestration_result.get("intent", "general"),
            "confidence": orchestration_result.get("confidence", 0.0),
            "response_type": response_type,
            "needs_confirmation": needs_confirmation,
            "has_sufficient_details": has_sufficient_details
        }
        
        # Handle offer display when user confirms or explicitly requests offers
        if should_show_offers and has_sufficient_details:
            try:
                # Use the improved pipeline: sentence transformer → MATCHER LLM → card display
                offers = self._get_ai_selected_offers(preferences, offer_count)
                
                if offers:
                    response["offers"] = offers
                    response["response_type"] = "offers"
                    debug_print(f"🎯 Generated {len(offers)} offers using improved pipeline (sentence transformer → MATCHER LLM → card display)")
                else:
                    debug_print("❌ No offers found through the pipeline")
                    response["response"] += "\n\nJe n'ai pas trouvé d'offres correspondant exactement à vos critères. Pouvez-vous ajuster vos préférences ?"
                    
            except Exception as e:
                debug_print(f"❌ Error in offer pipeline: {e}")
                response["response"] += "\n\nDésolé, j'ai rencontré une erreur lors de la recherche d'offres. Pouvez-vous réessayer ?"
        
        return response
    
    def _generate_response_text(self, user_input: str, orchestration_result: Dict, preferences: Dict) -> str:
        """
        Generate natural response text using the generator model
        Focus on essential criteria only and format lists properly
        """
        response_type = orchestration_result.get("response_type", "question")
        needs_confirmation = orchestration_result.get("needs_confirmation", False)
        has_sufficient_details = orchestration_result.get("has_sufficient_details", False)
        is_confirmation = orchestration_result.get("intent") == "confirmation"
        
        prompt = f"""
You are ASIA.fr Agent, a charismatic and knowledgeable travel specialist specializing in Asian travel. You MUST ALWAYS RESPOND IN FRENCH.

LANGUAGE REQUIREMENT: You are a French travel agent. All your responses must be in French. Be natural, friendly, and professional in French.

CONVERSATION CONTEXT:
- User preferences: {json.dumps(preferences, indent=2)}
- Orchestration result: {json.dumps(orchestration_result, indent=2)}
- Chat history: {self.conversation_context.chat_history[-300:] if self.conversation_context.chat_history else "None"}
- Current state: {self.conversation_context.current_state}

USER INPUT: {user_input}

GENERATE A NATURAL RESPONSE IN FRENCH following these CRITICAL RULES:

1. **FOCUS ONLY ON ESSENTIAL CRITERIA**: Only ask about these 4 core criteria:
   - Destination (pays/ville)
   - Durée (nombre de jours)
   - Budget (faible/moyen/élevé)
   - Style de voyage (culturel, aventure, luxe, détente, etc.)

2. **FORMAT LISTS PROPERLY**: When asking multiple questions, use proper formatting:
   ```
   • Question 1
   • Question 2  
   • Question 3
   ```
   NOT like this: "• Question 1 • Question 2 • Question 3"

3. **BE CONCISE**: Don't ask unnecessary questions about:
   - Hébergements spécifiques
   - Activités détaillées
   - Centres d'intérêt spécifiques
   - Plans d'activités
   - Expériences culinaires
   - Onsen, temples, etc.

4. **ASK EFFICIENTLY**: If multiple criteria are missing, ask them all at once in a clean list format.

5. **BE FRIENDLY**: Use casual, engaging French with occasional emojis.

6. **AVOID REPETITION**: Don't repeat what the user already told you.

RESPONSE EXAMPLES:
✅ GOOD: "Parfait ! Pour finaliser votre voyage au Japon, j'ai besoin de savoir :
• Quelle durée prévoyez-vous ?
• Quel est votre budget (faible/moyen/élevé) ?
• Quel style de voyage préférez-vous (culturel, aventure, détente) ?"

❌ BAD: "Superbe choix, le Japon pendant la saison des cerisiers en fleurs est tout simplement magnifique ! 💕 Pour vous proposer des offres de voyage qui correspondent parfaitement à vos attentes, j'aimerais savoir : • Quels sont vos centres d'intérêt au Japon ? Les temples et les sites historiques, la nourriture japonaise, les onsen (sources chaudes), les parcs nationaux, ou autre chose ? • Avez-vous des préférences pour les hébergements ? Des hôtels traditionnels ryokan, des auberges de jeunesse, ou des appartements meublés ? • Quels sont vos plans pour les activités ? Vous préférez les visites guidées, les excursions en solo, ou les expériences culinaires ? Plus j'en saurai sur vos préférences, mieux je pourrai vous proposer des offres de voyage qui correspondent à vos attentes ! 😊"

Generate your response in French:
"""
        
        try:
            response = self._call_llm_with_retry(self.generator, prompt)
            return response.strip()
        except Exception as e:
            debug_print(f"❌ Response generation failed: {e}")
            return self._generate_fallback_response(user_input, preferences)
    
    def _generate_fallback_response(self, user_input: str, preferences: Dict) -> str:
        """Generate a simple fallback response focusing on essential criteria"""
        missing_criteria = []
        
        if not preferences.get('duration'):
            missing_criteria.append("durée")
        if not preferences.get('budget'):
            missing_criteria.append("budget")
        if not preferences.get('style'):
            missing_criteria.append("style de voyage")
        
        if missing_criteria:
            criteria_list = "\n• ".join(missing_criteria)
            return f"Parfait ! Pour finaliser votre voyage, j'ai besoin de savoir :\n• {criteria_list}"
        else:
            return "Parfait ! J'ai toutes les informations nécessaires pour vous proposer des offres personnalisées."
    
    def _get_intelligent_offers(self, preferences: Dict, max_offers: int = 3) -> List[Dict]:
        """
        Use AI and vector search to intelligently match and rank offers
        """
        try:
            # Build search query from preferences
            search_query = self._build_search_query(preferences)
            debug_print(f"🔍 Search query: {search_query}")
            
            # Use vector search for semantic matching
            vector_results = self._vector_search_offers(search_query, top_k=max_offers * 2)
            
            # Use AI to refine and rank the vector results
            refined_offers = self._ai_refine_offers(vector_results, preferences, max_offers)
            
            return refined_offers
            
        except Exception as e:
            debug_print(f"❌ Intelligent offer matching failed: {e}")
            return []
    
    def _build_search_query(self, preferences: Dict) -> str:
        """Build a semantic search query from user preferences"""
        query_parts = []
        
        if preferences.get('destination'):
            query_parts.append(f"travel to {preferences['destination']}")
        
        if preferences.get('style'):
            query_parts.append(f"{preferences['style']} experience")
        
        if preferences.get('duration'):
            query_parts.append(f"{preferences['duration']} days")
        
        if preferences.get('budget'):
            query_parts.append(f"{preferences['budget']} budget")
        
        # Add context from conversation
        if self.conversation_context.chat_history:
            # Extract key terms from recent conversation
            recent_context = self.conversation_context.chat_history[-200:]
            query_parts.append(recent_context)
        
        return " ".join(query_parts) if query_parts else "travel offers"
    
    def _vector_search_offers(self, query: str, top_k: int = 6) -> List[Dict]:
        """Use OptimizedSemanticService for semantic search"""
        try:
            # Initialize semantic service if not already done
            if not hasattr(self, 'semantic_service'):
                from services.optimized_semantic_service import OptimizedSemanticService
                self.semantic_service = OptimizedSemanticService()
                debug_print("🔍 Initialized semantic service")
            
            # Use sentence transformer to search the JSON database
            search_results = self.semantic_service.search(query, top_k)
            debug_print(f"🔍 Sentence transformer found {len(search_results)} closest offers")
            
            # Debug: Show first offer to verify it's from database
            if search_results:
                first_offer = search_results[0]
                debug_print(f"🔍 First offer from database: {first_offer.get('product_name', 'Unknown')} - {first_offer.get('destinations', [])}")
            
            return search_results
            
        except Exception as e:
            debug_print(f"❌ Sentence transformer search failed: {e}")
            # Fallback to basic search
            return self._fallback_text_search(query, top_k)
    
    def _basic_search_offers(self, query: str, top_k: int = 6) -> List[Dict]:
        """Basic text-based search fallback"""
        try:
            available_offers = self.data_processor.offers[:50]
            query_lower = query.lower()
            
            scored_offers = []
            for offer in available_offers:
                score = 0
                offer_text = offer.get_semantic_text().lower()
                
                # Simple keyword matching
                if query_lower in offer_text:
                    score += 1
                
                # Destination matching
                for dest in offer.destinations:
                    if query_lower in dest.get('city', '').lower() or query_lower in dest.get('country', '').lower():
                        score += 2
                
                if score > 0:
                    structured_offer = {
                        "product_name": offer.product_name,
                        "reference": offer.reference,
                        "destinations": offer.destinations,
                        "departure_city": offer.departure_city,
                        "dates": offer.dates,
                        "duration": offer.duration,
                        "offer_type": offer.offer_type,
                        "description": offer.description,
                        "highlights": offer.highlights,
                        "images": getattr(offer, 'images', []),
                        "price_url": f"https://example.com/offer/{offer.reference}",
                        "vector_score": score,
                        "semantic_match": "Basic text match"
                    }
                    scored_offers.append(structured_offer)
            
            # Sort by score and return top_k
            scored_offers.sort(key=lambda x: x['vector_score'], reverse=True)
            return scored_offers[:top_k]
            
        except Exception as e:
            debug_print(f"❌ Basic search failed: {e}")
            return []
    
    def _ai_refine_offers(self, vector_results: List[Dict], preferences: Dict, max_offers: int = 3) -> List[Dict]:
        """Use AI to refine and rank vector search results"""
        try:
            if not vector_results:
                return []
            
            # Create offers summary for AI
            offers_summary = []
            for offer in vector_results:
                offers_summary.append({
                    "reference": offer.get("reference"),
                    "product_name": offer.get("product_name"),
                    "destinations": offer.get("destinations"),
                    "duration": offer.get("duration"),
                    "offer_type": offer.get("offer_type"),
                    "description": offer.get("description"),
                    "highlights": offer.get("highlights"),
                    "vector_score": offer.get("vector_score", 0.0)
                })

            # Use AI to refine and rank
            prompt = f"""
You are an expert travel offer matcher. Refine and rank the BEST {max_offers} matches from these vector search results.

USER PREFERENCES: {json.dumps(preferences, indent=2)}
VECTOR SEARCH RESULTS: {json.dumps(offers_summary, indent=2)}

REFINEMENT RULES:
1. Consider both vector scores and user preferences
2. Prioritize offers that match multiple preferences
3. Consider destination, style, duration, and budget
4. Provide detailed reasoning for each match
5. If user mentions specific destinations, prioritize those exact destinations
6. Consider the conversation context and user's intent

For each selected offer, provide:
- offer_reference: exact reference from available offers
- match_score: 0-1 score based on overall similarity
- reasoning: why this offer matches the user's preferences
- highlights: key highlights for this offer
- why_perfect: why this offer is perfect for the user

YOU MUST RESPOND WITH VALID JSON ONLY. NO OTHER TEXT.

RESPOND IN JSON FORMAT:
{{
    "matches": [
        {{
            "offer_reference": "REF123",
            "match_score": 0.95,
            "reasoning": "Perfect match for cultural experience in Japan",
            "highlights": ["Cultural tours", "Traditional experiences", "Local guides"],
            "why_perfect": "This offer perfectly matches your desire for cultural experiences in Japan"
        }}
    ]
}}

Select exactly {max_offers} offers:
"""
            
            response = self._call_llm_with_retry(self.matcher, prompt)
            match_result = self._parse_json_safely(response)

            # Convert to structured offers
            structured_offers = []
            for match in match_result.get("matches", [])[:max_offers]:
                offer_ref = match.get("offer_reference")
                original_offer = next((o for o in vector_results if o.get("reference") == offer_ref), None)

                if original_offer:
                    structured_offer = {
                        "product_name": original_offer.get("product_name"),
                        "reference": original_offer.get("reference"),
                        "destinations": original_offer.get("destinations"),
                        "departure_city": original_offer.get("departure_city"),
                        "dates": original_offer.get("dates"),
                        "duration": original_offer.get("duration"),
                        "offer_type": original_offer.get("offer_type"),
                        "description": original_offer.get("description"),
                        "highlights": original_offer.get("highlights"),
                        "images": original_offer.get("images", []),
                        "price_url": original_offer.get("price_url"),
                        "ai_reasoning": match.get("reasoning", ""),
                        "ai_highlights": match.get("highlights", []),
                        "match_score": match.get("match_score", 0.8),
                        "why_perfect": match.get("why_perfect", ""),
                        "vector_score": original_offer.get("vector_score", 0.0)
                    }
                    structured_offers.append(structured_offer)
            
            return structured_offers
            
        except Exception as e:
            debug_print(f"❌ AI refinement failed: {e}")
            # Return vector results as fallback
            return vector_results[:max_offers]

    def _add_to_memory(self, user_input: str, response: str):
        """Add conversation to memory"""
        try:
            self.memory.save_context(
                {"input": user_input},
                {"output": response}
            )
            self.conversation_context.chat_history += f"\nUser: {user_input}\nAssistant: {response}"
        except Exception as e:
            debug_print(f"⚠️ Failed to add to memory: {e}")
    
    def _parse_json_safely(self, json_str: str) -> Dict[str, Any]:
        """Safely parse JSON string with enhanced error handling"""
        try:
            # Clean the JSON string
            cleaned = re.sub(r'```json\s*|\s*```', '', json_str.strip())

            # Try to find JSON content between curly braces
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group(0)

            # Handle common JSON issues
            cleaned = cleaned.replace('\n', ' ').replace('\r', ' ')
            cleaned = re.sub(r'\s+', ' ', cleaned)

            # Try to parse
            result = json.loads(cleaned)
            debug_print(f"✅ JSON parsed successfully: {list(result.keys())}")
            return result

        except json.JSONDecodeError as e:
            debug_print(f"❌ JSON parsing failed: {e}")
            debug_print(f"📝 Raw response: {json_str[:200]}...")

            # Try to extract key-value pairs using regex
            try:
                extracted = {}
                # Look for common patterns
                patterns = [
                    r'"([^"]+)"\s*:\s*"([^"]*)"',  # "key": "value"
                    r'"([^"]+)"\s*:\s*(\d+\.?\d*)',  # "key": number
                    r'"([^"]+)"\s*:\s*(true|false)',  # "key": boolean
                    r'"([^"]+)"\s*:\s*\[([^\]]*)\]',  # "key": [array]
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, json_str)
                    for key, value in matches:
                        if isinstance(value, str) and value.lower() in ['true', 'false']:
                            extracted[key] = value.lower() == 'true'
                        elif isinstance(value, str) and value.replace('.', '').isdigit():
                            extracted[key] = float(value) if '.' in value else int(value)
                        elif isinstance(value, str) and value.startswith('[') and value.endswith(']'):
                            # Simple array parsing
                            array_content = value[1:-1]
                            if array_content:
                                extracted[key] = [item.strip().strip('"') for item in array_content.split(',')]
                            else:
                                extracted[key] = []
                        else:
                            extracted[key] = value

                if extracted:
                    debug_print(f"🔧 Extracted partial JSON: {extracted}")
                    return extracted

            except Exception as extract_error:
                debug_print(f"❌ Extraction also failed: {extract_error}")

            return {}
        except Exception as e:
            debug_print(f"❌ Unexpected error in JSON parsing: {e}")
            return {}
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get current user preferences"""
        return self.conversation_context.user_preferences.copy()
    
    def clear_preferences(self):
        """Clear all user preferences"""
        self.conversation_context.user_preferences = {}
        debug_print("✅ All preferences cleared")
    
    def clear_memory(self):
        """Clear conversation memory"""
        # Clear conversation context
        self.conversation_context.chat_history = ""
        self.conversation_context.turn_count = 0
        debug_print("✅ Memory cleared")

    def _build_preference_query(self, preferences: Dict) -> str:
        """Build a comprehensive search query from user preferences for sentence transformer"""
        query_parts = []
        
        # Prioritize destination - make it the most important part
        if preferences.get('destination'):
            destination = preferences['destination']
            
            # Enhanced destination mapping for better semantic search
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
                'sri lanka': ['Sri Lanka', 'Colombo', 'Sri Lankais', 'Sri Lanka culturel'],
                'nepal': ['Népal', 'Katmandou', 'Népalais', 'Népal culturel'],
                'népal': ['Népal', 'Katmandou', 'Népalais', 'Népal culturel'],
                'bhutan': ['Bhoutan', 'Thimphou', 'Bhoutanais', 'Bhoutan culturel'],
                'mongolia': ['Mongolie', 'Oulan-Bator', 'Mongol', 'Mongolie culturel'],
                'mongolie': ['Mongolie', 'Oulan-Bator', 'Mongol', 'Mongolie culturel']
            }
            
            # Get destination terms or use generic approach
            destination_lower = destination.lower()
            if destination_lower in destination_mappings:
                query_parts.extend(destination_mappings[destination_lower])
            else:
                # Generic approach for unknown destinations
                query_parts.extend([
                    f"voyage {destination}",
                    f"circuit {destination}",
                    f"découverte {destination}",
                    f"{destination} culturel",
                    f"{destination} traditionnel"
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
            # Add style-specific terms
            if 'culturel' in style.lower() or 'cultural' in style.lower():
                query_parts.extend(["découverte culturelle", "sites historiques", "traditions locales"])
            elif 'aventure' in style.lower() or 'adventure' in style.lower():
                query_parts.extend(["aventure", "expériences uniques", "activités outdoor"])
            elif 'détente' in style.lower() or 'relax' in style.lower():
                query_parts.extend(["détente", "plages", "bien-être"])
            elif 'gastronomie' in style.lower() or 'food' in style.lower():
                query_parts.extend(["gastronomie", "cuisine locale", "dégustations"])
        
        if preferences.get('budget'):
            budget = preferences['budget']
            query_parts.append(f"budget {budget}")
            if 'moyen' in budget.lower() or 'medium' in budget.lower():
                query_parts.append("prix moyen")
            elif 'élevé' in budget.lower() or 'high' in budget.lower():
                query_parts.append("luxe premium")
            elif 'bas' in budget.lower() or 'low' in budget.lower():
                query_parts.append("économique")
        
        if preferences.get('group_size'):
            group_size = preferences['group_size']
            query_parts.append(f"groupe {group_size}")
            if 'petit' in group_size.lower() or 'small' in group_size.lower():
                query_parts.append("petit groupe")
            elif 'grand' in group_size.lower() or 'large' in group_size.lower():
                query_parts.append("groupe important")
        
        if preferences.get('timing'):
            timing = preferences['timing']
            query_parts.append(f"période {timing}")
        
        # Add enhanced context words for better semantic matching
        query_parts.extend([
            "circuit organisé", 
            "voyage guidé", 
            "découverte culturelle",
            "expérience authentique",
            "voyage personnalisé",
            "circuit premium"
        ])
        
        # Remove duplicates and join
        unique_parts = list(dict.fromkeys(query_parts))  # Preserve order while removing duplicates
        return " ".join(unique_parts)
    

    
    def _fallback_text_search(self, query: str, top_k: int = 6) -> List[Dict]:
        """Fallback text-based search if semantic search fails"""
        try:
            # Ensure data is loaded
            self._ensure_data_loaded()
            
            # Get all offers from the data processor
            all_offers = self.data_processor.get_all_offers()
            if not all_offers:
                debug_print("❌ No offers available in data processor")
                return []
            
            # Simple text-based matching
            matching_offers = []
            query_lower = query.lower()
            
            for offer in all_offers:
                score = 0
                offer_text = f"{offer.get('product_name', '')} {offer.get('description', '')} {offer.get('destinations', [])}"
                offer_text_lower = offer_text.lower()
                
                # Simple keyword matching
                for word in query_lower.split():
                    if word in offer_text_lower:
                        score += 1
                
                if score > 0:
                    offer['match_score'] = score / len(query_lower.split())
                    matching_offers.append(offer)
            
            # Sort by match score and return top_k
            matching_offers.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            return matching_offers[:top_k]
            
        except Exception as e:
            debug_print(f"❌ Fallback search failed: {e}")
            return []
    
    def _ai_refine_offers(self, vector_results: List[Dict], preferences: Dict, max_offers: int = 3) -> List[Dict]:
        """Use the MATCHER LLM to rank the top 10 offers from sentence transformer based on user preferences"""
        try:
            if not vector_results:
                return []
            
            # Ensure models are loaded
            self._ensure_models_loaded()
            
            # Create a simplified version of offers to reduce token usage
            simplified_offers = []
            for offer in vector_results:
                simplified_offer = {
                    'product_name': offer.get('product_name', ''),
                    'destinations': offer.get('destinations', []),
                    'duration': offer.get('duration', 0),
                    'description': offer.get('description', '')[:150],  # Limit description length
                    'offer_type': offer.get('offer_type', ''),
                    'similarity_score': offer.get('similarity_score', 0.0)
                }
                simplified_offers.append(simplified_offer)
            
            # Create a prompt for the MATCHER LLM to rank the top 10 offers
            prompt = f"""
You are an expert travel agent. Rank and select the best {max_offers} offers from these 10 candidates (found by sentence transformer).

USER PREFERENCES:
{json.dumps(preferences, indent=2, ensure_ascii=False)}

TOP 10 OFFERS FROM SENTENCE TRANSFORMER:
{json.dumps(simplified_offers, indent=2, ensure_ascii=False)}

TASK: As the MATCHER LLM, analyze each offer and select the {max_offers} best matches. Consider:
1. Destination compatibility (exact match gets highest score)
2. Duration appropriateness (within ±2 days of preference)
3. Budget level compatibility (low/medium/high)
4. Travel style alignment (cultural, adventure, luxury, etc.)
5. Overall relevance and quality

For each selected offer, add a 'match_score' field (0.0-1.0) based on how well it matches preferences.

Return ONLY a JSON array with the selected offers (include product_name for mapping):
"""
            
            # Use the MATCHER LLM specifically for this task
            response = self._call_llm_with_retry(self.matcher, prompt)
            debug_print(f"🔍 MATCHER LLM response: {response[:200]}...")
            # Try to parse as JSON array first
            try:
                # Clean the response
                cleaned_response = response.strip()
                
                # Try to find JSON array in the response
                start_idx = cleaned_response.find('[')
                end_idx = cleaned_response.rfind(']')
                
                if start_idx != -1 and end_idx != -1:
                    json_str = cleaned_response[start_idx:end_idx + 1]
                    selected_simplified = json.loads(json_str)
                    debug_print(f"✅ JSON array parsed successfully: {len(selected_simplified)} items")
                else:
                    # Try parsing as object with array
                    selected_simplified = self._parse_json_safely(response)
                    if isinstance(selected_simplified, dict) and 'offers' in selected_simplified:
                        selected_simplified = selected_simplified['offers']
                    elif isinstance(selected_simplified, dict) and 'matches' in selected_simplified:
                        selected_simplified = selected_simplified['matches']
                    else:
                        selected_simplified = []
                        
            except Exception as e:
                debug_print(f"❌ JSON parsing failed: {e}")
                selected_simplified = []
            
            if isinstance(selected_simplified, list) and selected_simplified:
                # Map back to original offers and add match scores
                selected_offers = []
                for simplified in selected_simplified:
                    # Find the original offer by product name
                    for original in vector_results:
                        if original.get('product_name') == simplified.get('product_name'):
                            # Add match score to original offer
                            original['match_score'] = simplified.get('match_score', 0.8)
                            selected_offers.append(original)
                            break
                
                return selected_offers[:max_offers]
            else:
                # Fallback: return top results by semantic similarity score
                return sorted(vector_results, key=lambda x: x.get('similarity_score', 0), reverse=True)[:max_offers]
                
        except Exception as e:
            debug_print(f"❌ AI refinement failed: {e}")
            # Fallback: return top results by semantic similarity score with basic scoring
            fallback_offers = []
            for offer in vector_results[:max_offers]:
                # Add a basic match score based on similarity
                offer['match_score'] = offer.get('similarity_score', 0.8)
                fallback_offers.append(offer)
            
            debug_print(f"🔄 Using fallback scoring for {len(fallback_offers)} offers")
            return fallback_offers
    
    def _get_ai_selected_offers(self, preferences: Dict, offer_count: int = 3) -> List[Dict]:
        """
        Get AI-selected offers using the improved pipeline:
        1. Sentence transformer finds top 10 closest offers from JSON database
        2. MATCHER LLM ranks them based on user preferences
        3. Returns top 3 for card display
        """
        # Create cache key based on preferences
        cache_key = f"{hash(str(sorted(preferences.items())))}"
        
        # Clear cache if preferences have changed significantly (especially destination)
        if hasattr(self, '_last_preferences') and self._last_preferences != preferences:
            if hasattr(self, '_offers_cache'):
                debug_print("🔄 Preferences changed, clearing cache")
                self._offers_cache.clear()
        
        # Store current preferences for next comparison
        self._last_preferences = preferences.copy()
        
        if hasattr(self, '_offers_cache') and cache_key in self._offers_cache:
            debug_print("⚡ Using cached offers")
            return self._offers_cache[cache_key]
        
        try:
            # Step 1: Build query for sentence transformer
            query = self._build_preference_query(preferences)
            debug_print(f"🔍 Building query for sentence transformer: {query}")
            
            # Step 2: Use sentence transformer to find top 10 closest offers from JSON database
            top_10_offers = self._vector_search_offers(query, top_k=10)
            debug_print(f"🔍 Sentence transformer found {len(top_10_offers)} closest offers from database")
            
            if not top_10_offers:
                debug_print("❌ No offers found by sentence transformer")
                return []
            
            # Step 3: Use MATCHER LLM to rank the top 10 offers based on user preferences
            ranked_offers = self._ai_refine_offers(top_10_offers, preferences, max_offers=offer_count)
            debug_print(f"🔍 MATCHER LLM ranked and selected {len(ranked_offers)} best offers")
            
            if ranked_offers:
                # Cache the result
                if not hasattr(self, '_offers_cache'):
                    self._offers_cache = {}
                self._offers_cache[cache_key] = ranked_offers
                
                debug_print(f"✅ Pipeline complete: {len(ranked_offers)} offers ready for card display")
                return ranked_offers
            else:
                debug_print("⚠️ No offers selected by MATCHER LLM")
                return []
                
        except Exception as e:
            debug_print(f"❌ Error in offer pipeline: {e}")
            # Fallback to basic matching
            return self._fallback_offer_selection(preferences, offer_count)
    
    def _fallback_offer_selection(self, preferences: Dict, offer_count: int = 3) -> List[Dict]:
        """Fallback to basic offer selection if semantic search fails"""
        try:
            from services.offer_service import OfferService
            from services.data_service import DataService
            
            # Initialize services
            ds = DataService()
            os = OfferService(ds)
            
            # Get raw offers from database
            raw_offers = ds.get_offers()
            
            # Calculate match scores for all offers
            scored_offers = []
            for offer in raw_offers:
                try:
                    score = os._calculate_match_score(offer, preferences)
                    if score > 0.5:  # Minimum match threshold
                        # Add match score to the raw offer data
                        offer_with_score = offer.copy()
                        offer_with_score['match_score'] = score
                        scored_offers.append(offer_with_score)
                except Exception as e:
                    debug_print(f"❌ Error scoring offer {offer.get('reference', 'unknown')}: {e}")
                    continue
            
            # Sort by match score and limit results
            scored_offers.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            result = scored_offers[:offer_count]
            
            if result:
                debug_print(f"✅ Fallback: Found {len(result)} offers with basic matching")
                return result
            else:
                debug_print("⚠️ No offers found in fallback")
                return []
                
        except Exception as e:
            debug_print(f"❌ Error in fallback offer selection: {e}")
            return []
    
    def _default_orchestration(self) -> Dict[str, Any]:
        """
        Default orchestration when the main orchestration fails
        """
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

class ASIAConcreteAgent:
    """
    Main agent class that uses the intelligent pipeline
    """
    
    def __init__(self, data_path: str = None):
        self.pipeline = IntelligentPipeline(data_path)
        # Store conversation contexts by conversation_id
        self.conversation_contexts = {}
    
    def _get_or_create_context(self, conversation_id: str = None) -> ConversationContext:
        """Get or create conversation context for a specific conversation"""
        if not conversation_id:
            conversation_id = "default"
        
        if conversation_id not in self.conversation_contexts:
            self.conversation_contexts[conversation_id] = ConversationContext(
                user_preferences={},
                chat_history="",
                current_intent="",
                conversation_id=conversation_id,
                turn_count=0,
                last_response_type="",
                confidence_score=0.0
            )
        
        return self.conversation_contexts[conversation_id]
    
    def chat(self, user_input: str, conversation_id: str = None) -> Dict[str, Any]:
        """Main chat method with conversation context support"""
        # Set the conversation context for this conversation
        context = self._get_or_create_context(conversation_id)
        self.pipeline.conversation_context = context
        return self.pipeline.process_user_input(user_input)
    
    async def chat_stream(self, user_input: str):
        """Streaming chat method that yields chunks with natural typing effect"""
        try:
            # Get the full response first
            result = self.chat(user_input)
            
            # Extract the response text
            response_text = result.get("response", "") if isinstance(result, dict) else str(result)
            
            # Split into words for more natural streaming
            words = response_text.split()
            
            # Stream word by word with natural delays
            for i, word in enumerate(words):
                # Add space before word (except first word)
                if i > 0:
                    yield " " + word
                else:
                    yield word
                
                # Add natural typing delay
                # Shorter delay for short words, longer for longer words
                delay = min(0.1 + (len(word) * 0.02), 0.3)  # Between 0.1 and 0.3 seconds
                
                # Add extra delay after punctuation for more natural flow
                if word.endswith(('.', '!', '?', ':', ';')):
                    delay += 0.2
                
                # Use asyncio.sleep instead of time.sleep for non-blocking delay
                import asyncio
                await asyncio.sleep(delay)
            
        except Exception as e:
            debug_print(f"❌ Streaming failed: {e}")
            yield f"Error: {str(e)}"
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences"""
        return self.pipeline.get_preferences()
    
    def clear_preferences(self):
        """Clear user preferences"""
        self.pipeline.clear_preferences()
    
    def clear_memory(self, conversation_id: str = None):
        """Clear conversation memory for specific conversation or all"""
        if conversation_id:
            if conversation_id in self.conversation_contexts:
                del self.conversation_contexts[conversation_id]
                debug_print(f"🧹 Cleared memory for conversation: {conversation_id}")
        else:
            # Clear all conversations
            self.conversation_contexts.clear()
            debug_print("🧹 Cleared all conversation memory")
        
        # Also clear the pipeline's current context
        self.pipeline.clear_memory()
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "status": "active",
            "preferences": self.pipeline.get_preferences(),
            "turn_count": self.pipeline.conversation_context.turn_count
        }
    
    def get_welcome_message(self) -> str:
        """Get welcome message"""
        try:
            prompt = """
You are ASIA.fr Agent, a charismatic and knowledgeable travel specialist specializing in Asian travel. You MUST RESPOND IN FRENCH.

Generate a warm, welcoming message in French that:
1. Introduces yourself as ASIA.fr Agent
2. Shows personality and expertise
3. Mentions your specialization in Asian travel
4. Invites the user to share their travel dreams
5. Uses casual, engaging French language with emojis sparingly
6. Is professional but friendly, knowledgeable but approachable
7. Demonstrates the Layla.ai style by asking 2-3 preference questions at once

Example style: "🌏 Bonjour ! Je suis ASIA.fr Agent, votre spécialiste de voyage en Asie ! 😊 Pour vous proposer les meilleures offres, j'aimerais savoir :

• Quelle destination vous attire le plus ?
• Pour combien de jours souhaitez-vous partir ?
• Quel est votre budget approximatif ?"

Keep it under 120 words and make it feel natural and conversational in French.

Welcome message in French:
"""
            response = self.pipeline._call_llm_with_retry(self.pipeline.generator, prompt)
            return response.strip()
        except Exception as e:
            debug_print(f"❌ Welcome message generation failed: {e}")
            return "🌏 Bonjour ! 👋 Je suis ASIA.fr Agent, votre spécialiste de voyage ! 😊 Je suis là pour vous aider à planifier votre parfait voyage en Asie ! Quel type de voyage rêvez-vous de faire ? 🎉"
    
    def _parse_json_response(self, response: str) -> List[Dict]:
        """Parse JSON response from LLM with error handling"""
        try:
            # Clean the response
            cleaned_response = response.strip()
            
            # Try to find JSON array in the response
            start_idx = cleaned_response.find('[')
            end_idx = cleaned_response.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                json_str = cleaned_response[start_idx:end_idx + 1]
                parsed = json.loads(json_str)
                debug_print(f"✅ JSON parsed successfully: {len(parsed)} items")
                return parsed
            else:
                debug_print("❌ No JSON array found in response")
                return []
                
        except json.JSONDecodeError as e:
            debug_print(f"❌ JSON decode error: {e}")
            return []
        except Exception as e:
            debug_print(f"❌ Error parsing JSON: {e}")
            return []