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

from cftravel_py.core.config import config
from cftravel_py.core.constants import LLMProvider
from cftravel_py.core.config import LLMConfig
from cftravel_py.services.llm_service import LLMFactory
from cftravel_py.data.data_processor import DataProcessor, TravelOffer

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
        
        # Fallback to hardcoded models
        self.orchestrator = self._safe_setup_model("REASONING_MODEL", "deepseek-r1-distill-llama-70b", 0.1, "orchestration")
        self.generator = self._safe_setup_model("GENERATION_MODEL", "llama-3.1-8b-instant", 0.7, "generation")
        self.matcher = self._safe_setup_model("MATCHING_MODEL", "llama-3.1-8b-instant", 0.3, "matching")
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
You are ASIA.fr Agent, an intelligent travel specialist. Analyze this user input and decide the best course of action.

CONVERSATION CONTEXT:
- Turn count: {self.conversation_context.turn_count}
- Current preferences: {json.dumps(self.conversation_context.user_preferences, indent=2)}
- Chat history: {self.conversation_context.chat_history[-500:] if self.conversation_context.chat_history else "None"}
- Last response type: {self.conversation_context.last_response_type}

USER INPUT: {user_input}

ANALYZE AND DECIDE:
1. What is the user's intent? (greeting, preference_sharing, offer_request, question, confirmation, etc.)
2. What information do we need to gather?
3. Should we show offers now? (yes/no)
4. How many offers should we show? (0-3)
5. What type of response should we give? (greeting, question, offer_display, detailed_info, etc.)

CRITICAL RULES:
- Show exactly 3 offers when user has sufficient preferences (destination + style OR destination + duration)
- Show exactly 3 offers when user confirms they want to see offers
- Never show more than 3 offers
- Be natural and conversational
- Build on previous context
- Ask one question at a time
- Use Layla.ai style - charismatic, knowledgeable, friendly
- If user mentions "Japan" and "cultural experience" together, show offers immediately

YOU MUST RESPOND WITH VALID JSON ONLY. NO OTHER TEXT.

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "intent": "user's primary intent",
    "confidence": 0.95,
    "missing_info": ["list", "of", "missing", "preferences"],
    "should_show_offers": true,
    "offer_count": 3,
    "response_type": "type of response to give",
    "reasoning": "step-by-step reasoning for the decision",
    "next_action": "what to do next"
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
You are an expert travel preference extractor. Extract ALL travel-related information from this user message.

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

YOU MUST RESPOND WITH VALID JSON ONLY. NO OTHER TEXT.

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
        
        debug_print(f"🔄 Updated context: {self.conversation_context.user_preferences}")
    
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
        
        # Add offers if needed
        if should_show_offers and offer_count > 0:
            offers = self._get_intelligent_offers(preferences, offer_count)
            if offers:
                response_data["offers"] = offers
                debug_print(f"🎯 Added {len(offers)} offers to response")
        
        return response_data
    
    def _generate_response_text(self, user_input: str, orchestration_result: Dict, preferences: Dict) -> str:
        """
        Generate natural response text using the generator model
        """
        prompt = f"""
You are ASIA.fr Agent, a charismatic and knowledgeable travel specialist specializing in Asian travel.

CONVERSATION CONTEXT:
- User preferences: {json.dumps(preferences, indent=2)}
- Orchestration result: {json.dumps(orchestration_result, indent=2)}
- Chat history: {self.conversation_context.chat_history[-300:] if self.conversation_context.chat_history else "None"}

USER INPUT: {user_input}

GENERATE A NATURAL RESPONSE following these rules:
1. Be charismatic, knowledgeable, and friendly
2. Use casual, engaging language with emojis sparingly
3. Ask ONE question at a time, not multiple questions
4. Build on what users say, don't repeat yourself
5. Be professional but friendly, knowledgeable but approachable
6. Avoid repetitive phrases
7. Make travel planning fun and exciting
8. If showing offers, mention exactly 3 offers
9. If asking for preferences, be specific and helpful
10. If user mentions Japan + cultural experience, show excitement and offer to show relevant offers

RESPONSE TYPE: {orchestration_result.get("response_type", "question")}

Generate a natural, conversational response:
"""
        
        try:
            response = self._call_llm_with_retry(self.generator, prompt)
            return response.strip()
        except Exception as e:
            debug_print(f"❌ Response generation failed: {e}")
            return "I'm here to help you plan your perfect Asian adventure! What kind of trip are you dreaming of?"
    
    def _get_intelligent_offers(self, preferences: Dict, max_offers: int = 3) -> List[Dict]:
        """
        Use AI to intelligently match and rank offers
        """
        try:
            # Get available offers
            available_offers = self.data_processor.offers[:50]  # Limit for performance
            
            # Create offers summary for AI
            offers_summary = []
            for offer in available_offers:
                offers_summary.append({
                    "reference": offer.reference,
                    "product_name": offer.product_name,
                    "destinations": offer.destinations,
                    "duration": offer.duration,
                    "offer_type": offer.offer_type,
                    "description": offer.description,
                    "highlights": offer.highlights
                })

            # Use AI to match offers
            prompt = f"""
You are an expert travel offer matcher. Find the BEST {max_offers} matches from the available offers.

USER PREFERENCES: {json.dumps(preferences, indent=2)}
AVAILABLE OFFERS: {json.dumps(offers_summary, indent=2)}

MATCHING RULES:
1. Focus on semantic similarity and user preferences
2. Consider destination, style, duration, and budget
3. Prioritize offers that match multiple preferences
4. Provide detailed reasoning for each match
5. If user mentions "Japan" and "cultural", prioritize Japan cultural tours
6. If user mentions specific destinations, prioritize those exact destinations

For each selected offer, provide:
- offer_reference: exact reference from available offers
- match_score: 0-1 score based on similarity
- reasoning: why this offer matches
- highlights: key highlights for this offer

YOU MUST RESPOND WITH VALID JSON ONLY. NO OTHER TEXT.

RESPOND IN JSON FORMAT:
{{
    "matches": [
        {{
            "offer_reference": "REF123",
            "match_score": 0.95,
            "reasoning": "Perfect match for cultural experience in Japan",
            "highlights": ["Cultural tours", "Traditional experiences", "Local guides"]
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
                offer = next((o for o in available_offers if o.reference == offer_ref), None)

                if offer:
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
                        "ai_reasoning": match.get("reasoning", ""),
                        "ai_highlights": match.get("highlights", []),
                        "match_score": match.get("match_score", 0.8),
                        "why_perfect": match.get("reasoning", "")
                    }
                    structured_offers.append(structured_offer)
            
            return structured_offers
            
        except Exception as e:
            debug_print(f"❌ Intelligent offer matching failed: {e}")
            return []

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
You are ASIA.fr Agent, a charismatic and knowledgeable travel specialist specializing in Asian travel.

Generate a warm, welcoming message that:
1. Introduces yourself as ASIA.fr Agent
2. Shows personality and expertise
3. Mentions your specialization in Asian travel
4. Invites the user to share their travel dreams
5. Uses casual, engaging language with emojis sparingly
6. Is professional but friendly, knowledgeable but approachable

Keep it under 100 words and make it feel natural and conversational.

Welcome message:
"""
            response = self.pipeline._call_llm_with_retry(self.pipeline.generator, prompt)
            return response.strip()
        except Exception as e:
            debug_print(f"❌ Welcome message generation failed: {e}")
            return "🌏 Hi there! 👋 I'm ASIA.fr Agent, your travel specialist! 😊 I'm here to help you plan your perfect Asian adventure! What kind of trip are you dreaming of? 🎉"