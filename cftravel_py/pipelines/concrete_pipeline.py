"""
Intelligent AI Pipeline for ASIA.fr Agent
- Uses LLM orchestration for seamless decision-making
- No hardcoded conditions - everything is AI-driven
- Intelligent preference extraction and offer matching
- Enhanced error handling and robustness
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
    """
    
    def __init__(self, data_path: str = None):
        debug_print("🚀 Initializing IntelligentPipeline")
        self.data_path = data_path or config.data_path
        self.setup_models()
        self.setup_data()
        self.setup_memory()
        self.conversation_context = ConversationContext(
            user_preferences={},
            chat_history="",
            current_intent="",
            conversation_id="",
            turn_count=0,
            last_response_type="",
            confidence_score=0.0
        )
        debug_print("✅ IntelligentPipeline initialization complete")
    
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
            
            # 4. Embedding Model - Semantic search
            embedding_config = models_config["embedding_model"]
            self.embedding_model = self._setup_embedding_model_from_config(embedding_config)
            
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
        """Setup data processor"""
        debug_print("📊 Setting up data processor...")
        json_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "asia", "data.json")
        self.data_processor = DataProcessor(json_file_path)
        self.data_processor.load_offers()
        debug_print(f"📊 Loaded {len(self.data_processor.offers)} offers")
    
    def setup_memory(self):
        """Setup conversation memory"""
        debug_print("🧠 Setting up memory...")
        self.memory = SimpleMemory()
    
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

    def process_user_input(self, user_input: str, conversation_id: str = None) -> Dict[str, Any]:
        """
        Main entry point - processes user input using intelligent AI orchestration
        """
        try:
            debug_print(f"🎯 Processing user input: {user_input[:50]}...")
            
            # Update conversation context
            self.conversation_context.turn_count += 1
            if conversation_id:
                self.conversation_context.conversation_id = conversation_id
            
            # Step 1: Orchestrate the conversation
            orchestration_result = self._orchestrate_conversation(user_input)
            
            # Step 2: Extract preferences intelligently
            preferences = self._extract_preferences_intelligently(user_input, orchestration_result)
            
            # Step 3: Update conversation context
            self._update_context(preferences, orchestration_result)
            
            # Step 4: Generate response based on orchestration
            response_data = self._generate_intelligent_response(user_input, orchestration_result, preferences)
            
            # Step 5: Add to memory
            self._add_to_memory(user_input, response_data.get("response", ""))
            
            return response_data
            
        except Exception as e:
            debug_print(f"❌ Error in process_user_input: {e}")
            return {
                "response": f"I encountered an error: {str(e)}. Please try rephrasing your request.",
                "error": str(e)
            }
    
    def _orchestrate_conversation(self, user_input: str) -> Dict[str, Any]:
        """
        Use the orchestrator model to make intelligent decisions about the conversation
        """
        prompt = f"""
You are ASIA.fr Agent, an intelligent travel specialist. You MUST ALWAYS RESPOND IN FRENCH. Analyze this user input and decide the best course of action.

LANGUAGE REQUIREMENT: You are a French travel agent. All your responses, reasoning, and analysis must be in French.

CONVERSATION CONTEXT:
- Turn count: {self.conversation_context.turn_count}
- Current preferences: {json.dumps(self.conversation_context.user_preferences, indent=2)}
- Current state: {self.conversation_context.current_state}
- Chat history: {self.conversation_context.chat_history[-500:] if self.conversation_context.chat_history else "None"}
- Last response type: {self.conversation_context.last_response_type}

USER INPUT: {user_input}

ANALYZE AND DECIDE:
1. What is the user's intent? (greeting, preference_sharing, recommend_place, offer_request, question, confirmation, modification, etc.)
2. What information do we need to gather?
3. Should we show offers now? (yes/no)
4. How many offers should we show? (0-3)
5. What type of response should we give? (greeting, question, offer_display, detailed_info, confirmation_request, etc.)
6. Do we need confirmation before showing offers? (yes/no)

CONFIRMATION FLOW RULES:
- When user provides sufficient details (destination + duration OR destination + style + budget), ALWAYS ask for confirmation FIRST
- Sufficient details = at least 2 key preferences (destination, duration, style, budget, travelers)
- NEVER show offers immediately when user has sufficient details - ALWAYS ask for confirmation first
- Only show offers after user explicitly confirms
- If user says "yes", "confirm", "perfect", "sounds good", "show me", "oui", "parfait", "c'est bon", treat as confirmation
- If user says "no", "modify", "change", "different", "non", "modifier", "changer", treat as modification request

CRITICAL RULES:
- Set intent to "recommend_place" when user asks for recommendations, suggestions, or wants to see places
- Show exactly 3 offers ONLY when user explicitly confirms they want to see offers
- NEVER show offers immediately when user has sufficient preferences - ALWAYS ask for confirmation first
- Never show more than 3 offers
- Be natural and conversational in French
- Build on previous context
- Ask MULTIPLE preference questions at once to speed up the conversation (like Layla.ai)
- Use Layla.ai style - charismatic, knowledgeable, friendly
- If user mentions "Japan" and "cultural experience" together, show offers immediately

INTENT DETECTION RULES:
- "recommend_place": User asks for recommendations, suggestions, "show me places", "what should I visit", etc.
- "offer_request": User specifically asks for offers, deals, packages
- "preference_sharing": User shares travel preferences
- "greeting": Hello, hi, how are you, etc.
- "question": General questions about travel
- "confirmation": User confirms or agrees to something
- "modification": User wants to change or modify preferences

YOU MUST RESPOND WITH VALID JSON ONLY. NO OTHER TEXT. ALL REASONING AND ANALYSIS MUST BE IN FRENCH.

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "intent": "user's primary intent",
    "confidence": 0.95,
    "missing_info": ["list", "of", "missing", "preferences"],
    "should_show_offers": true,
    "offer_count": 3,
    "response_type": "type of response to give",
    "reasoning": "step-by-step reasoning for the decision in French",
    "next_action": "what to do next",
    "needs_confirmation": false,
    "has_sufficient_details": false
}}

JSON Response:
"""
        
        try:
            response = self._call_llm_with_retry(self.orchestrator, prompt)
            result = self._parse_json_safely(response)
            debug_print(f"🎯 Orchestration result: {result}")
            return result
        except Exception as e:
            debug_print(f"❌ Orchestration failed: {e}")
            # Fallback orchestration
            return {
                "intent": "general",
                "confidence": 0.5,
                "missing_info": [],
                "should_show_offers": False,
                "offer_count": 0,
                "response_type": "question",
                "reasoning": "Fallback due to orchestration error",
                "next_action": "ask_for_preferences"
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
        
        # Check if we have sufficient details for confirmation
        has_sufficient_details = self._check_sufficient_details()
        needs_confirmation = orchestration_result.get("needs_confirmation", False)
        
        if has_sufficient_details and needs_confirmation:
            self.conversation_context.current_state = "confirmation"
            self.conversation_context.needs_confirmation = True
            self.conversation_context.confirmation_summary = self._generate_confirmation_summary()
        elif orchestration_result.get("should_show_offers", False):
            self.conversation_context.current_state = "showing_offers"
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
        """Generate a summary of preferences for confirmation in French"""
        preferences = self.conversation_context.user_preferences
        
        summary_parts = []
        
        if preferences.get('destination'):
            summary_parts.append(f"Destination : {preferences['destination']}")
        
        if preferences.get('duration'):
            summary_parts.append(f"Durée : {preferences['duration']} jours")
        
        if preferences.get('style'):
            summary_parts.append(f"Style : {preferences['style']}")
        
        if preferences.get('budget'):
            summary_parts.append(f"Budget : {preferences['budget']}")
        
        if preferences.get('travelers'):
            summary_parts.append(f"Voyageurs : {preferences['travelers']}")
        
        if preferences.get('timing'):
            summary_parts.append(f"Période : {preferences['timing']}")
        
        return " | ".join(summary_parts) if summary_parts else "Aucune préférence définie"
    
    def _generate_intelligent_response(self, user_input: str, orchestration_result: Dict, preferences: Dict) -> Dict[str, Any]:
        """
        Generate intelligent response based on orchestration results
        """
        should_show_offers = orchestration_result.get("should_show_offers", False)
        offer_count = orchestration_result.get("offer_count", 0)
        response_type = orchestration_result.get("response_type", "question")
        
        # Generate the response text
        response_text = self._generate_response_text(user_input, orchestration_result, preferences)
        
        # Prepare response data
        response_data = {
            "response": response_text,
            "conversation_id": self.conversation_context.conversation_id,
            "status": "success"
        }
        
        # Add confirmation information if needed
        if self.conversation_context.needs_confirmation:
            response_data["needs_confirmation"] = True
            response_data["confirmation_summary"] = self.conversation_context.confirmation_summary
        
        # Add conversation state
        response_data["conversation_state"] = {
            "conversation_id": self.conversation_context.conversation_id,
            "user_preferences": self.conversation_context.user_preferences,
            "current_state": self.conversation_context.current_state,
            "needs_confirmation": self.conversation_context.needs_confirmation,
            "confirmation_summary": self.conversation_context.confirmation_summary,
            "turn_count": self.conversation_context.turn_count,
            "last_response_type": self.conversation_context.last_response_type
        }
        
        # Add offers if needed
        if should_show_offers and offer_count > 0:
            # Use the OfferService instead of our own offer matching
            try:
                from services.offer_service import OfferService
                from services.data_service import DataService
                
                # Initialize services
                ds = DataService()
                os = OfferService(ds)
                
                # Get offers using our tested OfferService
                offers = os.match_offers(preferences, max_offers=offer_count)
                if offers:
                    response_data["offers"] = offers
                    debug_print(f"🎯 Added {len(offers)} offers using OfferService")
            except Exception as e:
                debug_print(f"❌ Error using OfferService: {e}")
                # Fallback to our own method
                offers = self._get_intelligent_offers(preferences, offer_count)
                if offers:
                    response_data["offers"] = offers
                    debug_print(f"🎯 Added {len(offers)} offers using fallback method")
        
        return response_data
    
    def _generate_response_text(self, user_input: str, orchestration_result: Dict, preferences: Dict) -> str:
        """
        Generate natural response text using the generator model
        """
        prompt = f"""
You are ASIA.fr Agent, a charismatic and knowledgeable travel specialist specializing in Asian travel. You MUST ALWAYS RESPOND IN FRENCH.

LANGUAGE REQUIREMENT: You are a French travel agent. All your responses must be in French. Be natural, friendly, and professional in French.

CONVERSATION CONTEXT:
- User preferences: {json.dumps(preferences, indent=2)}
- Orchestration result: {json.dumps(orchestration_result, indent=2)}
- Chat history: {self.conversation_context.chat_history[-300:] if self.conversation_context.chat_history else "None"}
- Current state: {self.conversation_context.current_state}

USER INPUT: {user_input}

GENERATE A NATURAL RESPONSE IN FRENCH following these rules:
1. Be charismatic, knowledgeable, and friendly in French
2. Use casual, engaging French language with emojis sparingly
3. Ask MULTIPLE preference questions at once to speed up the conversation (like Layla.ai)
4. Build on what users say, don't repeat yourself
5. Be professional but friendly, knowledgeable but approachable
6. Avoid repetitive phrases
7. Make travel planning fun and exciting
8. If showing offers, mention exactly 3 offers
9. If asking for preferences, be specific and helpful
10. If user mentions Japan + cultural experience, show excitement and offer to show relevant offers

CONFIRMATION FLOW:
- If asking for confirmation, summarize their preferences and ask if they want to proceed
- Be enthusiastic about their choices and make them feel confident
- Offer to show them the best 3 offers that match their preferences
- If they want to modify, be helpful and ask what they'd like to change

MULTIPLE QUESTIONS STYLE (like Layla.ai):
- When gathering preferences, ask 2-3 related questions at once
- Format questions as a proper list with line breaks between each item
- Example: "Parfait ! Pour vous proposer les meilleures offres, j'aimerais savoir :

• Quelle destination vous attire le plus en Asie ?
• Pour combien de jours souhaitez-vous partir ?
• Quel est votre budget approximatif ?"

- Group related preferences together naturally
- Make it conversational, not interrogative
- Use bullet points (•) with proper line breaks for clarity
- Avoid wall of text - each question should be on its own line

RESPONSE TYPE: {orchestration_result.get("response_type", "question")}

Generate a natural, conversational response in French:
"""
        
        try:
            response = self._call_llm_with_retry(self.generator, prompt)
            return response.strip()
        except Exception as e:
            debug_print(f"❌ Response generation failed: {e}")
            return "Je suis là pour vous aider à planifier votre parfait voyage en Asie ! Quel type de voyage rêvez-vous de faire ?"
    
    def _get_intelligent_offers(self, preferences: Dict, max_offers: int = 3) -> List[Dict]:
        """
        Use AI and vector search to intelligently match and rank offers
        """
        try:
            # Build search query from preferences
            search_query = self._build_search_query(preferences)
            debug_print(f"🔍 Search query: {search_query}")
            
            # Use vector search for semantic matching
            vector_results = self._vector_search_offers(search_query, max_offers * 2)
            
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
        """Use Sentence Transformers for semantic search"""
        try:
            # Use the data processor's semantic search
            search_results = self.data_processor.semantic_search(query, top_k=top_k)
            
            # Convert to structured format
            structured_results = []
            for result in search_results:
                offer = result.get('offer')
                if offer:
                    structured_result = {
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
                        "vector_score": result.get('score', 0.0),
                        "semantic_match": result.get('semantic_match', "")
                    }
                    structured_results.append(structured_result)
            
            return structured_results
            
        except Exception as e:
            debug_print(f"❌ Vector search failed: {e}")
            # Fallback to basic search
            return self._basic_search_offers(query, top_k)
    
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
        self.memory.clear()
        self.conversation_context.chat_history = ""
        self.conversation_context.turn_count = 0
        debug_print("✅ Memory cleared")

class ASIAConcreteAgent:
    """
    Main agent class that uses the intelligent pipeline
    """
    
    def __init__(self, data_path: str = None):
        self.pipeline = IntelligentPipeline(data_path)
    
    def chat(self, user_input: str) -> Dict[str, Any]:
        """Main chat method"""
        return self.pipeline.process_user_input(user_input)
    
    def chat_stream(self, user_input: str):
        """Streaming chat method that yields chunks"""
        try:
            # Get the full response first
            result = self.chat(user_input)
            
            # Extract the response text
            response_text = result.get("response", "") if isinstance(result, dict) else str(result)
            
            # Yield the response character by character for streaming effect
            for char in response_text:
                yield char
            
        except Exception as e:
            debug_print(f"❌ Streaming failed: {e}")
            yield f"Error: {str(e)}"
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences"""
        return self.pipeline.get_preferences()
    
    def clear_preferences(self):
        """Clear user preferences"""
        self.pipeline.clear_preferences()
    
    def clear_memory(self):
        """Clear conversation memory"""
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