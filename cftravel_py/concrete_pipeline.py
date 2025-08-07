"""
Concrete LangChain Pipeline with Groq Models
- Uses Groq models for reasoning, generation, and matching
- Specialized models for different pipeline steps
"""

import os
import logging
import time
import random
from typing import List, Dict, Any, Optional
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseOutputParser
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
import numpy as np
import json

from config import config, LLMConfig, LLMProvider, LLMProvider
from llm_factory import LLMFactory
from data_processor import DataProcessor, TravelOffer, PreferenceParser

# Suppress HTTP warnings and logging
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("langchain").setLevel(logging.ERROR)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Debug flag
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

def debug_print(message: str):
    """Print debug message if DEBUG is enabled"""
    if DEBUG:
        print(f"🔍 DEBUG: {message}")

class ThoughtProcess(BaseModel):
    """Structured thought process output"""
    understanding: str = Field(description="What the user really wants")
    preferences: Dict[str, Any] = Field(description="Extracted preferences")
    reasoning: str = Field(description="Step-by-step reasoning")
    conclusion: str = Field(description="Final conclusion")

class MatchResult(BaseModel):
    """Structured match result"""
    offer_reference: str = Field(description="Offer reference")
    match_score: float = Field(description="Semantic match score")
    reasoning: str = Field(description="Why this matches")
    highlights: List[str] = Field(description="Key highlights")

class ConcretePipeline:
    """Concrete pipeline with lightweight models for each step"""
    
    def __init__(self, data_path: str = None):
        debug_print("🚀 Initializing ConcretePipeline")
        self.data_path = data_path or config.data_path
        self.setup_groq_models()
        self.setup_pipeline()
        self.user_preferences = {}  # Persisted user preferences across turns
        self.last_page = 1
        debug_print("✅ ConcretePipeline initialization complete")
    
    def setup_groq_models(self):
        """Setup Groq models for each pipeline step"""
        debug_print("🔧 Setting up Groq models...")
        
        # 1. Reasoning Model - for thought process
        debug_print("🧠 Setting up reasoning model...")
        self.reasoning_model = self._setup_reasoning_model()
        
        # 2. Generation Model - for final responses
        debug_print("🤖 Setting up generation model...")
        self.generation_model = self._setup_generation_model()
        
        # 3. Embedding Model - for semantic matching
        debug_print("🔍 Setting up embedding model...")
        self.embedding_model = self._setup_embedding_model()
        
        # 4. Matching Model - for offer matching
        debug_print("🎯 Setting up matching model...")
        self.matching_model = self._setup_matching_model()
        
        # 5. Data processor
        debug_print("📊 Setting up data processor...")
        # Construct the path to the JSON file
        json_file_path = os.path.join(self.data_path, "asia", "data.json")
        debug_print(f"📁 Looking for data file at: {json_file_path}")
        self.data_processor = DataProcessor(json_file_path)
        self.data_processor.load_offers()  # Actually load the offers
        debug_print(f"📊 Loaded {len(self.data_processor.offers)} offers")
        
        # 6. Memory
        debug_print("🧠 Setting up memory...")
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        debug_print("✅ Groq models setup complete")
    
    def _setup_reasoning_model(self):
        """Setup model for reasoning and thought process"""
        print("🔧 Configuring reasoning model...")
        
        # Check if API key is available
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("⚠️ GROQ_API_KEY not set - using fallback mode")
            return None
        
        # Use Groq for reasoning
        reasoning_config = LLMConfig(
            provider="groq",  # Use string directly instead of enum
            model_name=os.getenv("REASONING_MODEL", "llama3-8b-8192"),
            temperature=float(os.getenv("REASONING_TEMPERATURE", "0.1")),
            max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "2048")),
            api_key=api_key,
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        )
        print("🧠 Using Groq for reasoning")
        
        return LLMFactory.create_llm(reasoning_config)
    
    def _setup_generation_model(self):
        """Setup model for generating final responses"""
        print("🔧 Configuring generation model...")
        
        # Check if API key is available
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("⚠️ GROQ_API_KEY not set - using fallback mode")
            return None
        
        # Use Groq for generation
        generation_config = LLMConfig(
            provider="groq",  # Use string directly instead of enum
            model_name=os.getenv("GENERATION_MODEL", "openai/gpt-oss-120b"),
            temperature=float(os.getenv("GENERATION_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "2048")),
            api_key=api_key,
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        )
        print("🤖 Using Groq for generation")
        
        return LLMFactory.create_llm(generation_config)
    
    def _setup_embedding_model(self):
        """Setup embedding model for semantic matching"""
        try:
            return SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load embedding model: {e}")
            return None
    
    def _setup_matching_model(self):
        """Setup model for offer matching"""
        print("🔧 Configuring matching model...")
        
        # Check if API key is available
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("⚠️ GROQ_API_KEY not set - using fallback mode")
            return None
        
        # Use Groq for matching
        matching_config = LLMConfig(
            provider="groq",  # Use string directly instead of enum
            model_name=os.getenv("MATCHING_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct"),
            temperature=float(os.getenv("MATCHING_TEMPERATURE", "0.3")),
            max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "1024")),
            api_key=api_key,
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        )
        print("🔍 Using Groq for matching")
        
        return LLMFactory.create_llm(matching_config)
    
    def _call_llm_with_retry(self, llm, prompt: str, max_retries: int = 3, base_delay: float = 1.0, timeout: int = 30):
        """Call LLM with retry logic for rate limiting and timeout"""
        if llm is None:
            debug_print("❌ LLM model is None - API key not set")
            raise Exception("LLM model not available - GROQ_API_KEY not set")
        
        debug_print(f"🤖 Making LLM call with {max_retries} max retries, {timeout}s timeout")
        
        for attempt in range(max_retries):
            try:
                debug_print(f"🔄 LLM call attempt {attempt + 1}/{max_retries}")
                start_time = time.time()
                
                # Set a timeout for the LLM call
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"LLM call timed out after {timeout} seconds")
                
                # Set up timeout (only works on Unix-like systems)
                try:
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(timeout)
                except (AttributeError, OSError):
                    # Windows doesn't support SIGALRM, we'll rely on the LLM's internal timeout
                    debug_print("⚠️  Timeout not supported on this platform, relying on LLM internal timeout")
                
                try:
                    response = llm.invoke(prompt)
                finally:
                    # Cancel the alarm
                    try:
                        signal.alarm(0)
                    except (AttributeError, OSError):
                        pass
                
                elapsed_time = time.time() - start_time
                debug_print(f"✅ LLM call successful in {elapsed_time:.2f}s")
                
                response_text = response.content if hasattr(response, 'content') else str(response)
                return response_text
                
            except TimeoutError as e:
                debug_print(f"⏰ LLM call timed out (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    debug_print(f"⏳ Waiting {delay:.2f}s before retry...")
                    time.sleep(delay)
                    continue
                else:
                    debug_print("❌ Max retries reached for timeout")
                    raise Exception(f"LLM call timed out after {max_retries} attempts")
                    
            except Exception as e:
                error_msg = str(e)
                debug_print(f"❌ LLM call failed (attempt {attempt + 1}): {error_msg}")
                
                # Check if it's a rate limit error
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        debug_print(f"⏳ Rate limited. Waiting {delay:.2f}s before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        debug_print("❌ Max retries reached for rate limit")
                        raise Exception(f"Rate limit exceeded after {max_retries} attempts: {error_msg}")
                
                # For other errors, don't retry
                debug_print(f"❌ Non-rate-limit error, not retrying: {error_msg}")
                raise e
        
        raise Exception(f"LLM call failed after {max_retries} attempts")

    def setup_pipeline(self):
        """Setup the complete pipeline with Groq models"""
        debug_print("🔧 Setting up pipeline chains...")
        
        # 0. Preference Extraction Chain
        preference_prompt = PromptTemplate(
            input_variables=["user_input"],
            template="""
Extract the user's travel preferences from the following message. Return a JSON object with fields: destination, timing, duration, budget, style, group_size. 

For timing, accept:
- Specific dates (e.g., "June 1", "May 31")
- Date ranges (e.g., "late May to June", "early June")
- Flexible expressions (e.g., "I'm flexible from May 31", "any time in June")
- Seasons (e.g., "spring", "summer")
- Events (e.g., "cherry blossom season")

User: {user_input}
"""
        )
        self.preference_chain = preference_prompt | self.generation_model
        
        # 1. Thought Process Chain (Enhanced for vague questions)
        thought_prompt = PromptTemplate(
            input_variables=["user_input", "chat_history"],
            template="""
You are Layla, an intelligent travel agent. Analyze the user's request step by step, even if it's vague or unclear.

Chat History: {chat_history}
User Input: {user_input}

Think through this request carefully:

1. UNDERSTANDING: What is the user really asking for?
   - If the request is vague, infer what they might want
   - Consider context from chat history
   - Think about common travel patterns and preferences

2. PREFERENCES: What can I infer about their preferences?
   - Destination preferences (specific or general regions)
   - Duration preferences (short trip, long vacation, etc.)
   - Budget level (budget, mid-range, luxury)
   - Travel style (cultural, adventure, relaxation, luxury)
   - Group size (solo, couple, family, group)
   - Timing (seasonal preferences, specific dates)

3. REASONING: How should I approach this request?
   - What type of travel experience matches their needs?
   - What constraints or preferences should I consider?
   - How can I provide helpful suggestions even with limited information?

4. CONCLUSION: What is my final understanding and approach?
   - Summarize what I understand they want
   - Explain my approach to helping them

IMPORTANT: Only work with the actual travel offers available in the catalogue. Do not create or suggest fictional offers.

Respond in JSON format:
{{
    "understanding": "clear explanation of what user wants, even if vague",
    "preferences": {{
        "destination": "extracted or inferred destination",
        "duration": "extracted or inferred duration",
        "budget": "low/medium/high based on language used",
        "style": ["cultural", "adventure", "luxury", "relaxation"],
        "group_size": "solo/couple/family/group",
        "timing": "specific dates or seasonal preferences"
    }},
    "reasoning": "step-by-step reasoning process",
    "conclusion": "final approach and strategy"
}}
"""
        )
        
        self.thought_chain = thought_prompt | self.reasoning_model
        
        # 2. Semantic Matching Chain (Enhanced to use real offers)
        matching_prompt = PromptTemplate(
            input_variables=["user_input", "thought_process", "available_offers"],
            template="""
You are an expert travel offer matcher. Your job is to find the BEST matches from the available offers ONLY.

User Input: {user_input}
Thought Process: {thought_process}
Available Offers: {available_offers}

IMPORTANT RULES:
1. ONLY use offers from the available offers list above
2. Do NOT create or suggest fictional offers
3. If no good matches exist, say so clearly
4. Focus on semantic similarity and user preferences
5. Provide detailed reasoning for each match

For each relevant offer, provide:
- Offer reference (from the available offers)
- Match score (0-1) based on semantic similarity
- Detailed reasoning for the match
- Key highlights that make this offer suitable

If the user's request is vague, try to match based on:
- General travel style (cultural, adventure, luxury, etc.)
- Duration preferences
- Destination preferences
- Budget level

Respond in JSON format:
{{
    "matches": [
        {{
            "offer_reference": "exact_reference_from_available_offers",
            "match_score": 0.85,
            "reasoning": "detailed explanation of why this specific offer matches",
            "highlights": ["specific_highlight1", "specific_highlight2", "specific_highlight3"]
        }}
    ],
    "total_offers_checked": "number of offers considered",
    "matching_strategy": "explanation of how you approached the matching"
}}
"""
        )
        
        self.matching_chain = matching_prompt | self.matching_model
        
        # 3. Response Generation Chain (Enhanced for Layla.ai style brevity)
        response_prompt = PromptTemplate(
            input_variables=["user_input", "thought_process", "offer_matches", "chat_history"],
            template="""
You are Layla, a friendly travel agent. Keep responses concise and conversational like Layla.ai.

Chat History: {chat_history}
User Input: {user_input}
Thought Process: {thought_process}
Matched Offers: {offer_matches}

CRITICAL RULES:
1. ONLY suggest offers from the matched offers list
2. Keep responses under 150 words
3. Use bullet points for clarity
4. Be warm but brief
5. Focus on key details only

Response style:
- Direct and helpful
- Use emojis sparingly
- Include offer reference and key highlights
- Suggest next steps briefly

Response:
"""
        )
        
        self.response_chain = response_prompt | self.generation_model
        
        # 4. Complete Pipeline (using modern LangChain syntax)
        # Note: SequentialChain is deprecated, we'll handle the pipeline manually
        # RunnableSequence objects don't have verbose attribute
        debug_print("✅ Pipeline setup complete")
    
    def _is_travel_intent(self, user_input: str) -> bool:
        """Detect if the user input expresses travel intent"""
        travel_keywords = [
            "travel", "trip", "vacation", "holiday", "tour", "visit", "go to", "explore", "journey", "destination", "book", "plan", "adventure", "itinerary", "package"
        ]
        input_lower = user_input.lower()
        return any(kw in input_lower for kw in travel_keywords)

    def _update_preferences_in_memory(self, user_input: str):
        """Update preferences in memory - this method is deprecated in favor of _update_preferences"""
        debug_print("⚠️ _update_preferences_in_memory is deprecated, using _update_preferences instead")
        self._update_preferences(user_input)
    
    def clear_preferences(self):
        """Clear all user preferences - only call this when user explicitly wants to reset"""
        debug_print("🗑️ User requested to clear all preferences")
        self.user_preferences = {}
        debug_print("✅ All preferences cleared")
    
    def modify_preference(self, key: str, value: str):
        """Modify a specific preference - for when user wants to change something specific"""
        debug_print(f"✏️ Modifying preference '{key}' to '{value}'")
        old_value = self.user_preferences.get(key)
        self.user_preferences[key] = value
        debug_print(f"✅ Preference '{key}' updated: '{old_value}' → '{value}'")
    
    def get_preferences(self) -> dict:
        """Get current user preferences"""
        return self.user_preferences.copy()

    def _is_offer_request(self, user_input: str) -> bool:
        offer_keywords = [
            "show me offers", "suggestions", "what do you suggest", "give me options",
            "recommend", "show trips", "show packages", "show tours", "show deals", "show me trips"
        ]
        input_lower = user_input.lower()
        return any(kw in input_lower for kw in offer_keywords)

    LAYLA_PERSONA = (
        "You are Layla, a super friendly, playful, and knowledgeable travel agent. "
        "You love to use emojis, travel metaphors, and always keep the conversation energetic and fun. "
        "You never sound robotic. You gather travel preferences step by step, always recapping what you know and asking for the next most relevant detail."
    )

    def _ask_for_next_preference(self, known_prefs, missing_prefs, chat_history):
        prompt = (
            f"{self.LAYLA_PERSONA}\n"
            f"Here's what the user has told you so far: {known_prefs}\n"
            f"You're missing: {missing_prefs}\n"
            f"Chat history: {chat_history}\n"
            "In a single, playful, Layla-style message, recap what you know and ask for the next most relevant missing detail. Use emojis and keep it energetic."
        )
        response = self.reasoning_model.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)

    def _recap_and_show_offers(self, prefs, offers, chat_history):
        prompt = (
            f"{self.LAYLA_PERSONA}\n"
            f"User's travel plan: {prefs}\n"
            f"Here are the top matching offers: {offers}\n"
            f"Chat history: {chat_history}\n"
            "Recap the user's plan in a fun, Layla-style way, then present the offers with excitement and a call to action."
        )
        response = self.generation_model.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)

    def _extract_preferences(self, user_input: str) -> dict:
        """Extract preferences from user input using simple regex/keyword approach (fallback)."""
        prefs = {}
        text = user_input.lower()
        
        # Destination extraction
        destinations = ['japan', 'vietnam', 'thailand', 'singapore', 'malaysia', 'indonesia', 'philippines']
        for dest in destinations:
            if dest in text:
                prefs['destination'] = dest
                break
        
        # Duration extraction
        if 'week' in text:
            if 'two' in text or '2' in text or 'second' in text:
                prefs['duration'] = 14
            elif 'three' in text or '3' in text or 'third' in text:
                prefs['duration'] = 21
            elif 'one' in text or '1' in text or 'first' in text:
                prefs['duration'] = 7
            elif 'four' in text or '4' in text or 'fourth' in text:
                prefs['duration'] = 28
        elif 'day' in text:
            if 'two' in text or '2' in text:
                prefs['duration'] = 2
            elif 'three' in text or '3' in text:
                prefs['duration'] = 3
            elif 'five' in text or '5' in text:
                prefs['duration'] = 5
            elif 'seven' in text or '7' in text:
                prefs['duration'] = 7
            elif 'ten' in text or '10' in text:
                prefs['duration'] = 10
            elif 'fourteen' in text or '14' in text:
                prefs['duration'] = 14
        
        # Group size extraction
        if 'solo' in text or 'alone' in text or 'single' in text:
            prefs['group_size'] = 'solo'
        elif 'couple' in text or 'two' in text and 'people' in text:
            prefs['group_size'] = 'couple'
        elif 'family' in text:
            prefs['group_size'] = 'family'
        elif 'group' in text:
            prefs['group_size'] = 'group'
        
        # Style extraction
        if 'culture' in text or 'cultural' in text:
            prefs['style'] = 'cultural'
        elif 'adventure' in text or 'adventurous' in text:
            prefs['style'] = 'adventure'
        elif 'luxury' in text or 'premium' in text:
            prefs['style'] = 'luxury'
        elif 'relax' in text or 'relaxation' in text:
            prefs['style'] = 'relaxation'
        
        # Timing extraction
        if 'flexible' in text or 'any time' in text:
            prefs['timing'] = 'flexible'
        elif 'spring' in text:
            prefs['timing'] = 'spring'
        elif 'summer' in text:
            prefs['timing'] = 'summer'
        elif 'autumn' in text or 'fall' in text:
            prefs['timing'] = 'autumn'
        elif 'winter' in text:
            prefs['timing'] = 'winter'
        
        return prefs

    def _update_preferences(self, user_input: str):
        """Update self.user_preferences using LLM-driven preference extraction."""
        debug_print(f"🔄 Updating preferences from input: '{user_input[:50]}...'")
        debug_print(f"📋 Current preferences before update: {self.user_preferences}")
        
        try:
            # Use LLM-driven preference extraction
            preference_result = self.preference_chain.invoke({"user_input": user_input})
            new_prefs = self._parse_json_safely(preference_result.content if hasattr(preference_result, 'content') else str(preference_result))
            
            debug_print(f"🤖 LLM extracted preferences: {new_prefs}")
            
            # Update preferences with new information (preserve existing preferences)
            updated_count = 0
            for k, v in new_prefs.items():
                if v and v != "null" and v != "":  # Only update if we have valid data
                    old_value = self.user_preferences.get(k)
                    self.user_preferences[k] = v
                    if old_value != v:
                        updated_count += 1
                        debug_print(f"✅ Updated preference '{k}': '{old_value}' → '{v}'")
            
            debug_print(f"📊 Updated {updated_count} preferences")
            debug_print(f"📋 Current preferences after update: {self.user_preferences}")
            
        except Exception as e:
            debug_print(f"⚠️ LLM preference extraction failed: {e}. Using fallback.")
            # Fallback to simple extraction
            new_prefs = self._extract_preferences(user_input)
            debug_print(f"🔧 Fallback extracted preferences: {new_prefs}")
            
            updated_count = 0
            for k, v in new_prefs.items():
                if v:
                    old_value = self.user_preferences.get(k)
                    self.user_preferences[k] = v
                    if old_value != v:
                        updated_count += 1
                        debug_print(f"✅ Updated preference '{k}': '{old_value}' → '{v}'")
            
            debug_print(f"📊 Updated {updated_count} preferences via fallback")
            debug_print(f"📋 Current preferences after fallback update: {self.user_preferences}")
        
        # Ensure preferences are never empty - they should persist across the conversation
        if not self.user_preferences:
            debug_print("⚠️ Warning: No preferences found, this might indicate an issue")
        else:
            debug_print(f"✅ Preferences successfully maintained: {len(self.user_preferences)} items")

    def _filter_offers(self, preferences, max_offers=30):
        """Filter offers based on preferences (destination, duration, etc.), or return a diverse sample if vague."""
        filtered = []
        offers = self.data_processor.offers
        # Filter by destination
        if preferences.get('destination'):
            for offer in offers:
                if any(preferences['destination'].lower() in d.get('city', '').lower() or preferences['destination'].lower() in d.get('country', '').lower() for d in offer.destinations):
                    filtered.append(offer)
        # Filter by duration
        if preferences.get('duration') and filtered:
            filtered = [o for o in filtered if abs(o.duration - int(preferences['duration'])) <= 3]
        # Filter by style
        if preferences.get('style') and filtered:
            filtered = [o for o in filtered if preferences['style'].lower() in o.offer_type.lower() or preferences['style'].lower() in o.description.lower()]
        # If not enough, fill up with diverse types
        if len(filtered) < max_offers:
            needed = max_offers - len(filtered)
            seen_types = set(o.offer_type for o in filtered)
            for offer in offers:
                if offer not in filtered and offer.offer_type not in seen_types:
                    filtered.append(offer)
                    seen_types.add(offer.offer_type)
                    if len(filtered) >= max_offers:
                        break
        # Still not enough? Just fill up
        if len(filtered) < max_offers:
            for offer in offers:
                if offer not in filtered:
                    filtered.append(offer)
                    if len(filtered) >= max_offers:
                        break
        return filtered[:max_offers]

    def _prepare_offers_summary(self, preferences: dict, max_offers: int = 5, page: int = 1) -> str:
        """Prepare a filtered summary of offers for the LLM (limited to 3-5 top offers)."""
        offers = self._filter_offers(preferences, max_offers * page)
        start = (page - 1) * max_offers
        end = start + max_offers
        paged = offers[start:end]
        
        # If user has a specific destination, only show relevant offers
        if preferences.get('destination'):
            destination = preferences['destination'].lower()
            relevant_offers = []
            for offer in paged:
                offer_destinations = [d.get('city', '').lower() + ' ' + d.get('country', '').lower() for d in offer.destinations]
                if any(destination in dest for dest in offer_destinations):
                    relevant_offers.append(offer)
            paged = relevant_offers[:5]  # Limit to 5 offers maximum
        
        summary = f"Top {len(paged)} Relevant Travel Offers:\n\n"
        for i, offer in enumerate(paged, 1):
            destinations = ", ".join([f"{d.get('city', '')} ({d.get('country', '')})" for d in offer.destinations])
            summary += f"{i}. {offer.product_name} (Ref: {offer.reference})\n"
            summary += f"   Destinations: {destinations}\n"
            summary += f"   Duration: {offer.duration} days\n"
            summary += f"   Type: {offer.offer_type}\n"
            summary += f"   Description: {offer.description[:60]}...\n\n"
        if len(paged) == 0:
            summary += "No relevant offers found for your destination.\n"
        return summary

    def process_user_input(self, user_input: str, page: int = 1) -> Dict[str, Any]:
        """LLM-driven, Layla-style conversational flow, with strict slot-filling and permission before showing full offers."""
        import re
        
        debug_print(f"🚀 Starting to process user input: '{user_input[:50]}...'")
        
        # Check for repetitive confirmation requests
        chat_history = self._get_chat_history()
        debug_print(f"📝 Chat history length: {len(chat_history)} characters")
        
        # Check for preference modification requests
        preference_modification_keywords = [
            "change", "modify", "update", "different", "instead", "actually", "correction",
            "not that", "wrong", "mistake", "different destination", "different duration",
            "different timing", "different style", "different budget"
        ]
        
        is_preference_modification = any(keyword in user_input.lower() for keyword in preference_modification_keywords)
        if is_preference_modification:
            debug_print("✏️ Detected preference modification request")
        
        if "show" in user_input.lower() or "yes" in user_input.lower() or "please" in user_input.lower():
            # Count how many times the user has said yes/show/please
            yes_count = chat_history.lower().count("yes") + chat_history.lower().count("show") + chat_history.lower().count("please")
            if yes_count > 2:  # If user has said yes/show/please more than 2 times, force show offers
                user_input = "FORCE_SHOW_OFFERS: " + user_input
                debug_print("🔄 Force showing offers due to repetitive requests")
        
        # Update preferences only if new info is provided
        if user_input.strip().lower() != 'next':
            # Clean up user_input if we added FORCE_SHOW_OFFERS prefix
            clean_user_input = user_input.replace("FORCE_SHOW_OFFERS: ", "")
            debug_print("🔄 Updating user preferences")
            
            # Store preferences before update to ensure we don't lose them
            old_preferences = self.user_preferences.copy()
            self._update_preferences(clean_user_input)
            
            # Safety check: if preferences were somehow lost, restore them
            if not self.user_preferences and old_preferences:
                debug_print("⚠️ Preferences were lost, restoring from backup")
                self.user_preferences = old_preferences
            
            self.last_page = 1
        else:
            self.last_page += 1
            debug_print(f"📄 Moving to page {self.last_page}")
        
        # Require destination and duration before showing offers (timing is optional)
        required_slots = ['destination', 'duration']
        missing_slots = [slot for slot in required_slots if not self.user_preferences.get(slot)]
        debug_print(f"🎯 Required slots: {required_slots}, Missing: {missing_slots}")
        debug_print(f"👤 Current preferences: {self.user_preferences}")
        
        try:
            debug_print("🔄 Getting chat history for LLM prompt")
            chat_history = self._get_chat_history()
            
            # Hybrid approach: LLM understanding + Vector search + LLM ranking
            # This provides the best of both worlds - LLM intelligence with vector speed
            debug_print("🔍 Preparing offers summary...")
            if len(self.data_processor.offers) > 50:  # Use hybrid for medium+ datasets
                debug_print("🔍 Using hybrid search strategy")
                offers_summary = self._hybrid_search_strategy(user_input)
            else:  # Small dataset - use smart filtering
                debug_print("🔍 Using smart filtering")
                offers_summary = self._prepare_smart_offers_summary()
            
            debug_print(f"📊 Offers summary length: {len(offers_summary)} characters")
            
            # Progressive slot-filling prompt
            clean_user_input = user_input.replace("FORCE_SHOW_OFFERS: ", "")
            debug_print("🤖 Building LLM prompt...")
            
            llm_prompt = f"""
You are Layla, a super friendly, playful, and knowledgeable travel agent. 
You help users match with real travel packages from the list below, which are official offers from asia.fr.

IMPORTANT RULES:
- Do NOT suggest or show offers until you have at least the user's destination and duration. Timing is helpful but optional - you can suggest offers based on destination and duration alone.
- FLEXIBLE DATE HANDLING: If the user provides a date range (e.g., "late May to June"), says they are flexible (e.g., "I'm flexible from May 31"), or gives a general timeframe, treat this as sufficient to proceed. Match to the closest available offer date and suggest it.
- If the user is flexible with dates, show the best available options and ask for confirmation rather than repeatedly asking for exact dates.
- CONVERSATION FLOW: When you have enough info (destination + duration), follow this sequence:
  1. First, summarize the user's travel intent
  2. Ask if they want to modify any preferences
  3. Only after confirmation, show 3-5 top relevant offers
  4. Do NOT bombard with full catalogue - show only the best matches
- SEMANTIC MATCHING: You have access to a smart subset of offers (prioritizing user preferences). Use your semantic understanding to find the best matches based on user preferences. Consider destination, duration, timing, style, and group size when matching.
- You may ONLY suggest, describe, or match travel offers from the provided list. Do NOT invent or create new offers.
- If the user asks for something not in the list, explain that only the listed offers are available.
- PREFERENCE PERSISTENCE: User preferences are stored in memory and should NEVER be removed unless the user explicitly wants to modify them. Always maintain and build upon existing preferences.
- If the user changes their preferences (duration, destination, timing, group size, style, budget, etc.), update your understanding and re-match offers accordingly. Always use the most recent user preferences from the conversation history.
- When suggesting or matching offers, always return the offer reference(s) (e.g., Ref: TJPS2V) for the best matches in your reply. Do NOT return full offer details—just the references and a short explanation.
- If you need more info, ask for it in a fun, Layla-style way.
- Never invent or suggest offers not in the provided list.

Current user preferences: {self.user_preferences}

Here is the conversation so far:
{chat_history}

Here are available travel offers for you to choose from:
{offers_summary}

DATE HANDLING GUIDANCE:
- If the user says they are "flexible" with dates, treat this as sufficient to proceed with offer suggestions
- If the user provides a date range (e.g., "late May to June"), find the closest matching offers
- If the user says "I'm free from X date", treat this as a valid timing preference
- Do NOT repeatedly ask for exact dates if the user has already indicated flexibility or provided a range

User's latest message:
{clean_user_input}

Respond as Layla, following the rules above. When suggesting offers, always include their references. If the user says 'next', you will see the next page of offers. If you want to show full details for a specific offer, ask the user for permission first.
"""
            
            debug_print(f"📝 LLM prompt length: {len(llm_prompt)} characters")
            
            # If missing required slots, ask for them
            if missing_slots:
                llm_prompt += f"\n\nIMPORTANT: Do NOT suggest or show any offers yet. Instead, ask the user for the following missing information: {', '.join(missing_slots)}."
                debug_print(f"❓ Missing slots, will ask for: {missing_slots}")
            else:
                # User has destination and duration, so we can proceed with offer suggestions
                # Check if user is asking to see offers or confirming
                show_offers_keywords = ["yes", "show", "please", "sure", "okay", "ok", "go ahead", "spit it", "give it", "show me", "let's see", "perfect", "sounds good"]
                user_wants_offers = any(keyword in user_input.lower() for keyword in show_offers_keywords)
                
                if user_wants_offers or "FORCE_SHOW_OFFERS" in user_input:
                    # User wants to see offers, so show them directly
                    llm_prompt += "\n\nIMPORTANT: The user has confirmed they want to see offers. Show the 3-5 top relevant offers from the list above with their references (Ref: XXX). Do NOT ask for more confirmation."
                    debug_print("✅ User wants to see offers, will show them directly")
                else:
                    # User hasn't explicitly asked for offers yet, so ask for confirmation
                    debug_print("🤔 User hasn't explicitly asked for offers, will ask for confirmation")
                    intent_summary = self._create_intent_summary()
                    llm_prompt += f"\n\nUSER INTENT SUMMARY:\n{intent_summary}\n\n"
                    llm_prompt += "IMPORTANT: Summarize the user's travel intent and ask if they want to see the 3-5 top relevant offers. Only show offers after they confirm."
            
            debug_print("🤖 Making LLM call with retry logic...")
            response_text = self._call_llm_with_retry(self.generation_model, llm_prompt)
            debug_print(f"✅ LLM response received, length: {len(response_text)} characters")
            
            # Extract offer references from LLM response (simple regex for Ref: ...)
            refs = re.findall(r"Ref: ([A-Za-z0-9_-]+)", response_text)
            debug_print(f"🔍 Found {len(refs)} offer references in response: {refs}")
            
            # Check if user is asking for specific offer details
            show_details_keywords = ["show details", "details", "full info", "more info", "see details", "full program", "program", "itinerary"]
            user_wants_details = any(kw in user_input.lower() for kw in show_details_keywords)
            
            # Check if user mentioned a specific reference
            user_refs = re.findall(r"([A-Za-z0-9_-]+)", user_input.upper())
            specific_refs = [ref for ref in user_refs if ref in [r.strip() for r in refs]]
            
            if user_wants_details and (refs or specific_refs):
                # Use specific refs if user mentioned them, otherwise use all refs
                refs_to_show = specific_refs if specific_refs else refs
                debug_print(f"📋 User wants details for refs: {refs_to_show}")
                details = self._get_offers_by_references(refs_to_show)
                debug_print("✅ Returning response with offer details")
                return {
                    "user_input": user_input,
                    "final_response": response_text + "\n\n" + details,
                    "pipeline_steps": ["fully_llm_driven", "show_matched_offers"]
                }
            
            debug_print("✅ Returning standard response")
            return {
                "user_input": user_input,
                "final_response": response_text,
                "pipeline_steps": ["fully_llm_driven"]
            }
            
        except Exception as e:
            error_msg = str(e)
            debug_print(f"❌ Error in process_user_input: {error_msg}")
            
            # Check if it's a rate limit error
            if "429" in error_msg or "Too Many Requests" in error_msg:
                return {
                    "error": error_msg,
                    "final_response": "I'm experiencing high traffic right now. Please wait a moment and try again, or try rephrasing your request."
                }
            elif "500" in error_msg or "Internal Server Error" in error_msg:
                return {
                    "error": error_msg,
                    "final_response": "I'm experiencing temporary connection issues with my AI models. This is likely a temporary server issue. Please try again in a few moments, or try rephrasing your request."
                }
            else:
                return {
                    "error": error_msg,
                    "final_response": f"I encountered an error: {error_msg}. Please try rephrasing your request."
                }
    
    def _is_vague_request(self, user_input: str) -> bool:
        """Check if user input is vague and needs preference gathering"""
        vague_keywords = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "i want to travel", "i want to go somewhere", "help me plan", "suggest",
            "recommend", "ideas", "options", "possibilities"
        ]
        
        # Check if it's a general question that can be answered directly
        general_question_keywords = [
            "what are", "what is", "tell me about", "show me", "popular", "famous",
            "monuments", "attractions", "sites", "places", "destinations"
        ]
        
        input_lower = user_input.lower()
        
        # If it's a general question, don't treat it as vague
        if any(keyword in input_lower for keyword in general_question_keywords):
            return False
            
        return any(keyword in input_lower for keyword in vague_keywords)
    
    def _handle_preference_gathering(self, user_input: str, chat_history: str) -> Dict[str, Any]:
        """Handle preference gathering like Layla.ai"""
        try:
            # Check if this is a general question that can be answered directly
            general_question_keywords = [
                "what are", "what is", "tell me about", "show me", "popular", "famous",
                "monuments", "attractions", "sites", "places", "destinations"
            ]
            
            input_lower = user_input.lower()
            is_general_question = any(keyword in input_lower for keyword in general_question_keywords)
            
            if is_general_question:
                # Handle general questions by providing information and then suggesting offers
                return self._handle_general_question(user_input, chat_history)
            else:
                # Handle vague requests by gathering preferences
                reasoning_prompt = f"""
You are Layla, an intelligent travel agent. The user has made a request that needs more details to provide good recommendations.

User Input: {user_input}
Chat History: {chat_history}

Analyze what information we have and what we still need to gather. Generate a helpful response that:
1. Acknowledges their request warmly
2. Asks for the most important missing details (destination, duration, budget, style, group size)
3. Provides examples to help them think about their preferences
4. Encourages them to share more details

Focus on gathering the key criteria that will help narrow down from 181 available offers to the best 2-3 matches.

Response:
"""
                
                response = self.reasoning_model.invoke(reasoning_prompt)
                
                return {
                    "user_input": user_input,
                    "thought_process": {"preference_gathering": "Gathering key travel criteria"},
                    "offer_matches": {},
                    "final_response": response.content if hasattr(response, 'content') else str(response),
                    "pipeline_steps": ["preference_gathering (Phi-4)"],
                    "models_used": {
                        "reasoning": "Phi-4 (Lightweight)",
                        "matching": "Not used yet",
                        "generation": "Not used yet",
                        "embeddings": "Not used yet"
                    }
                }
            
        except Exception as e:
            return {
                "error": str(e),
                "final_response": "I'd love to help you plan your trip! To find the perfect match from our 181 offers, could you tell me:\n\n• Where would you like to go?\n• How long do you want to travel?\n• What's your budget range?\n• What type of experience interests you (culture, adventure, relaxation, luxury)?\n• How many people are traveling?"
            }
    
    def _handle_general_question(self, user_input: str, chat_history: str) -> Dict[str, Any]:
        """Handle general questions by providing information and suggesting relevant offers"""
        try:
            # First, provide informative response about the topic
            info_prompt = f"""
You are Layla, an intelligent travel agent. The user has asked a general question about travel destinations or attractions.

User Input: {user_input}
Chat History: {chat_history}

Provide a helpful, informative response that:
1. Answers their question directly with relevant information
2. Mentions that you have specific travel offers available
3. Suggests they might want to see actual travel packages
4. Maintains a warm, helpful tone

For example, if they ask about Japan's monuments, mention popular ones like:
- Tokyo: Senso-ji Temple, Meiji Shrine, Tokyo Skytree
- Kyoto: Fushimi Inari Shrine, Kinkaku-ji (Golden Pavilion), Kiyomizu-dera
- Hiroshima: Peace Memorial Park, Miyajima Island
- Osaka: Osaka Castle, Dotonbori district

Then mention that you have curated travel packages that include these attractions.

Response:
"""
            
            info_response = self.reasoning_model.invoke(info_prompt)
            
            # Then find relevant offers
            offers_summary = self._prepare_offers_summary(self.user_preferences)
            
            matching_prompt = f"""
You are an expert travel offer matcher. The user asked: {user_input}

Available Offers: {offers_summary}

Find the BEST matches that relate to their question. For example, if they asked about Japan's monuments, find Japan-related offers.

IMPORTANT RULES:
1. ONLY use offers from the available offers list above
2. Do NOT create or suggest fictional offers
3. Focus on semantic similarity to their question
4. Provide detailed reasoning for each match

Respond in JSON format:
{{
    "matches": [
        {{
            "offer_reference": "exact_reference_from_available_offers",
            "match_score": 0.85,
            "reasoning": "detailed explanation of why this specific offer matches",
            "highlights": ["specific_highlight1", "specific_highlight2", "specific_highlight3"]
        }}
    ],
    "total_offers_checked": "number of offers considered",
    "matching_strategy": "explanation of how you approached the matching"
}}
"""
            
            matches_response = self.matching_model.invoke(matching_prompt)
            offer_matches = self._parse_json_safely(matches_response.content if hasattr(matches_response, 'content') else str(matches_response))
            
            # Generate final response combining info and offers
            final_prompt = f"""
You are Layla, a friendly travel agent. Generate a helpful response that combines:

1. The informative answer about their question
2. Suggestions for relevant travel offers

User Question: {user_input}
Informative Answer: {info_response.content if hasattr(info_response, 'content') else str(info_response)}
Relevant Offers: {offer_matches}

Create a response that:
1. Provides the informative answer first
2. Then mentions you have relevant travel packages
3. Suggests they might want to see specific offers
4. Maintains a warm, helpful tone

Response:
"""
            
            final_response = self.generation_model.invoke(final_prompt)
            
            return {
                "user_input": user_input,
                "thought_process": {"general_question": "Providing information and relevant offers"},
                "offer_matches": offer_matches,
                "final_response": final_response.content if hasattr(final_response, 'content') else str(final_response),
                "pipeline_steps": ["information_providing (Phi-4)", "offer_matching (Phi-4)", "response_generation (Qwen2.5)"],
                "models_used": {
                    "reasoning": "Phi-4 (Lightweight)",
                    "matching": "Phi-4 (Lightweight)",
                    "generation": "Qwen2.5-0.5B (Lightweight)",
                    "embeddings": "Not used"
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "final_response": f"I'd be happy to help you with information about {user_input}! Let me provide some details and then show you relevant travel packages we have available."
            }
    
    def _get_chat_history(self) -> str:
        """Get formatted chat history"""
        if not self.memory.chat_memory.messages:
            return "No previous conversation."
        
        history = "Previous conversation:\n"
        for message in self.memory.chat_memory.messages[-8:]:  # Last 8 messages
            if hasattr(message, 'content'):
                role = "User" if hasattr(message, 'type') and message.type == 'human' else "Layla"
                history += f"{role}: {message.content}\n"
        
        return history
    
    def _parse_json_safely(self, json_str: str) -> Dict[str, Any]:
        """Safely parse JSON string"""
        try:
            json_str = json_str.strip()
            if json_str.startswith('```json'):
                json_str = json_str[7:]
            if json_str.endswith('```'):
                json_str = json_str[:-3]
            
            return json.loads(json_str)
        except Exception:
            return {}
    
    def add_to_memory(self, user_input: str, response: str):
        """Add conversation to memory"""
        self.memory.chat_memory.add_user_message(user_input)
        self.memory.chat_memory.add_ai_message(response)
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get pipeline status and model information"""
        # Get actual model names from environment or defaults
        reasoning_model_name = os.getenv("REASONING_MODEL", "llama3-8b-8192")
        generation_model_name = os.getenv("GENERATION_MODEL", "openai/gpt-oss-120b")
        matching_model_name = os.getenv("MATCHING_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
        
        return {
            "reasoning_model": f"Groq {reasoning_model_name}",
            "generation_model": f"Groq {generation_model_name}",
            "matching_model": f"Groq {matching_model_name}",
            "embedding_model": "SentenceTransformers (Local)",
            "pipeline_steps": [
                f"Thought Process (Groq)",
                f"Semantic Matching (Groq)", 
                f"Response Generation (Groq)"
            ],
            "memory_enabled": True,
            "offers_loaded": len(self.data_processor.offers) if hasattr(self, 'data_processor') and self.data_processor.offers else 0,
            "debug_mode": config.debug,
            "hybrid_mode": True,  # Always using Groq models now
            "user_preferences": self.user_preferences  # Include current preferences in status
        }

    def _get_offers_by_references(self, references):
        """Return full details for offers matching the given references."""
        offers = self.data_processor.offers
        ref_set = set(references)
        details = ""
        found_refs = []
        
        for offer in offers:
            if offer.reference in ref_set:
                found_refs.append(offer.reference)
                destinations = ", ".join([f"{d.get('city', '')} ({d.get('country', '')})" for d in offer.destinations])
                details += f"🎯 **{offer.product_name}** (Ref: {offer.reference})\n"
                details += f"   🌍 Destinations: {destinations}\n"
                details += f"   🛫 Departure City: {offer.departure_city}\n"
                details += f"   📅 Dates: {', '.join(offer.dates)}\n"
                details += f"   ⏱️ Duration: {offer.duration} days\n"
                details += f"   👥 Group Size: {offer.min_group_size}-{offer.max_group_size}\n"
                details += f"   🏷️ Type: {offer.offer_type}\n"
                details += f"   📝 Description: {offer.description}\n"
                details += f"   🗺️ Programme: {offer.programme}\n"
                details += f"   ⭐ Highlights: {', '.join([h.get('text', '') for h in offer.highlights])}\n"
                details += f"   📸 Images: {', '.join(offer.images)}\n\n"
        
        # Check for missing references
        missing_refs = ref_set - set(found_refs)
        if missing_refs:
            details += f"❌ **Not Found**: {', '.join(missing_refs)}\n"
            # Suggest similar references
            for missing_ref in missing_refs:
                similar_refs = []
                for offer in offers:
                    if missing_ref in offer.reference or offer.reference in missing_ref:
                        similar_refs.append(offer.reference)
                if similar_refs:
                    details += f"💡 Did you mean: {', '.join(similar_refs)}?\n"
        
        return details or "No matching offers found."

    def _find_closest_departure_dates(self, user_timing: str, max_offers: int = 5) -> list:
        """Find the closest available departure dates for offers based on user timing preferences."""
        if not user_timing:
            return []
        
        offers = self.data_processor.offers
        matching_offers = []
        
        # Parse user timing preferences
        user_timing_lower = user_timing.lower()
        
        for offer in offers:
            # Check if any of the offer's dates match the user's timing
            for date_str in offer.dates:
                date_lower = date_str.lower()
                
                # Check for month matches
                month_matches = {
                    'january': 'jan', 'february': 'feb', 'march': 'mar', 'april': 'apr',
                    'may': 'may', 'june': 'jun', 'july': 'jul', 'august': 'aug',
                    'september': 'sep', 'october': 'oct', 'november': 'nov', 'december': 'dec'
                }
                
                # Check for season matches
                season_matches = {
                    'spring': ['mar', 'apr', 'may'],
                    'summer': ['jun', 'jul', 'aug'],
                    'autumn': ['sep', 'oct', 'nov'],
                    'fall': ['sep', 'oct', 'nov'],
                    'winter': ['dec', 'jan', 'feb']
                }
                
                # Check for specific month mentions
                for month, abbrev in month_matches.items():
                    if month in user_timing_lower or abbrev in user_timing_lower:
                        if abbrev in date_lower:
                            matching_offers.append({
                                'offer': offer,
                                'date': date_str,
                                'match_type': 'month'
                            })
                            break
                
                # Check for season mentions
                for season, months in season_matches.items():
                    if season in user_timing_lower:
                        if any(month in date_lower for month in months):
                            matching_offers.append({
                                'offer': offer,
                                'date': date_str,
                                'match_type': 'season'
                            })
                            break
                
                # Check for specific date mentions (e.g., "June 1", "May 31")
                import re
                date_patterns = [
                    r'(\w+)\s+(\d{1,2})',  # "June 1", "May 31"
                    r'(\d{1,2})\s+(\w+)',  # "1 June", "31 May"
                ]
                
                for pattern in date_patterns:
                    matches = re.findall(pattern, user_timing_lower)
                    for match in matches:
                        if len(match) == 2:
                            month_part, day_part = match
                            # Check if this matches the offer date
                            if month_part in date_lower and day_part in date_lower:
                                matching_offers.append({
                                    'offer': offer,
                                    'date': date_str,
                                    'match_type': 'specific_date'
                                })
                                break
        
        # Remove duplicates and sort by relevance
        unique_offers = []
        seen_refs = set()
        for match in matching_offers:
            if match['offer'].reference not in seen_refs:
                unique_offers.append(match)
                seen_refs.add(match['offer'].reference)
        
        # Sort by match type priority (specific_date > month > season)
        match_priority = {'specific_date': 3, 'month': 2, 'season': 1}
        unique_offers.sort(key=lambda x: match_priority.get(x['match_type'], 0), reverse=True)
        
        return unique_offers[:max_offers]

    def _format_limited_offers(self, offers: list, max_offers: int = 5) -> str:
        """Format exactly the specified number of offers for display."""
        if not offers:
            return "No relevant offers found."
        
        # Take only the first max_offers
        limited_offers = offers[:max_offers]
        
        summary = f"Top {len(limited_offers)} Relevant Travel Offers:\n\n"
        for i, offer in enumerate(limited_offers, 1):
            destinations = ", ".join([f"{d.get('city', '')} ({d.get('country', '')})" for d in offer.destinations])
            summary += f"{i}. {offer.product_name} (Ref: {offer.reference})\n"
            summary += f"   Destinations: {destinations}\n"
            summary += f"   Duration: {offer.duration} days\n"
            summary += f"   Type: {offer.offer_type}\n"
            summary += f"   Description: {offer.description[:60]}...\n\n"
        
        return summary

    def _prepare_smart_offers_summary(self) -> str:
        """Prepare a smart subset of offers for Kimi K2 to prevent token overflow."""
        offers = self.data_processor.offers
        
        # If user has specific preferences, prioritize those
        if self.user_preferences.get('destination'):
            destination = self.user_preferences['destination'].lower()
            # Get offers that match the destination
            matching_offers = []
            for offer in offers:
                offer_destinations = [d.get('city', '').lower() + ' ' + d.get('country', '').lower() for d in offer.destinations]
                if any(destination in dest for dest in offer_destinations):
                    matching_offers.append(offer)
            
            # If we have matching offers, use them + some diverse samples
            if matching_offers:
                # Take up to 15 matching offers + 10 diverse samples
                selected_offers = matching_offers[:15]
                # Add diverse samples from other destinations
                other_offers = [o for o in offers if o not in matching_offers]
                selected_offers.extend(other_offers[:10])
            else:
                # No exact matches, use diverse sample
                selected_offers = offers[:25]
        else:
            # No specific destination, use diverse sample
            selected_offers = offers[:25]
        
        summary = f"Available Travel Offers (showing {len(selected_offers)} of {len(offers)} total):\n\n"
        
        for i, offer in enumerate(selected_offers, 1):
            destinations = ", ".join([f"{d.get('city', '')} ({d.get('country', '')})" for d in offer.destinations])
            summary += f"{i}. {offer.product_name} (Ref: {offer.reference})\n"
            summary += f"   Destinations: {destinations}\n"
            summary += f"   Duration: {offer.duration} days\n"
            summary += f"   Type: {offer.offer_type}\n"
            summary += f"   Description: {offer.description[:80]}...\n\n"
        
        return summary

    def _semantic_search_offers(self, query: str, top_k: int = 10) -> list:
        """Use vector search to find semantically similar offers for large datasets."""
        try:
            # Create embeddings for the query
            if self.embedding_model:
                query_embedding = self.embedding_model.encode(query)
                
                # Get embeddings for all offers (cache these)
                offer_embeddings = []
                for offer in self.data_processor.offers:
                    offer_text = f"{offer.product_name} {offer.description} {offer.offer_type}"
                    for dest in offer.destinations:
                        offer_text += f" {dest.get('city', '')} {dest.get('country', '')}"
                    
                    embedding = self.embedding_model.encode(offer_text)
                    offer_embeddings.append((offer, embedding))
                
                # Calculate similarities and return top matches
                similarities = []
                for offer, embedding in offer_embeddings:
                    similarity = np.dot(query_embedding, embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding))
                    similarities.append((offer, similarity))
                
                # Sort by similarity and return top_k
                similarities.sort(key=lambda x: x[1], reverse=True)
                return [offer for offer, _ in similarities[:top_k]]
            
            else:
                # Fallback to keyword search
                return self._keyword_search_offers(query, top_k)
                
        except Exception as e:
            print(f"Semantic search failed: {e}")
            return self._keyword_search_offers(query, top_k)

    def _keyword_search_offers(self, query: str, top_k: int = 10) -> list:
        """Fallback keyword search for offers."""
        query_lower = query.lower()
        matches = []
        
        for offer in self.data_processor.offers:
            score = 0
            offer_text = f"{offer.product_name} {offer.description} {offer.offer_type}".lower()
            
            # Check for keyword matches
            for word in query_lower.split():
                if word in offer_text:
                    score += 1
            
            if score > 0:
                matches.append((offer, score))
        
        # Sort by score and return top_k
        matches.sort(key=lambda x: x[1], reverse=True)
        return [offer for offer, _ in matches[:top_k]]

    def _create_intent_summary(self) -> str:
        """Create a summary of the user's travel intent based on their preferences."""
        summary_parts = []
        
        if self.user_preferences.get('destination'):
            summary_parts.append(f"Destination: {self.user_preferences['destination']}")
        
        if self.user_preferences.get('duration'):
            summary_parts.append(f"Duration: {self.user_preferences['duration']} days")
        
        if self.user_preferences.get('timing'):
            summary_parts.append(f"Timing: {self.user_preferences['timing']}")
        
        if self.user_preferences.get('group_size'):
            summary_parts.append(f"Group Size: {self.user_preferences['group_size']}")
        
        if self.user_preferences.get('style'):
            summary_parts.append(f"Travel Style: {self.user_preferences['style']}")
        
        if self.user_preferences.get('budget'):
            summary_parts.append(f"Budget: {self.user_preferences['budget']}")
        
        if summary_parts:
            return " | ".join(summary_parts)
        else:
            return "No specific preferences set yet"

    def _prepare_vector_search_summary(self, user_input: str) -> str:
        """Use semantic search to find the most relevant offers for large datasets."""
        # Create a search query from user preferences
        search_query = ""
        if self.user_preferences.get('destination'):
            search_query += f"destination {self.user_preferences['destination']} "
        if self.user_preferences.get('duration'):
            search_query += f"duration {self.user_preferences['duration']} days "
        if self.user_preferences.get('timing'):
            search_query += f"timing {self.user_preferences['timing']} "
        if self.user_preferences.get('style'):
            search_query += f"style {self.user_preferences['style']} "
        
        # If no specific preferences, use the user input as query
        if not search_query:
            search_query = user_input
        
        # Get top 15 most relevant offers
        relevant_offers = self._semantic_search_offers(search_query, top_k=15)
        
        if not relevant_offers:
            # Fallback to diverse sample
            relevant_offers = self.data_processor.offers[:15]
        
        summary = f"Most Relevant Travel Offers (semantic search results):\n\n"
        
        for i, offer in enumerate(relevant_offers, 1):
            destinations = ", ".join([f"{d.get('city', '')} ({d.get('country', '')})" for d in offer.destinations])
            summary += f"{i}. {offer.product_name} (Ref: {offer.reference})\n"
            summary += f"   Destinations: {destinations}\n"
            summary += f"   Duration: {offer.duration} days\n"
            summary += f"   Type: {offer.offer_type}\n"
            summary += f"   Description: {offer.description[:80]}...\n\n"
        
        return summary

    def _hybrid_search_strategy(self, user_input: str) -> str:
        """Hybrid approach: LLM understanding + Vector search + LLM ranking"""
        
        # Step 1: LLM creates optimized search query
        search_query = self._create_llm_search_query(user_input)
        
        # Step 2: Vector search finds candidates
        candidates = self._semantic_search_offers(search_query, top_k=25)
        
        # Step 3: LLM ranks and selects final offers
        final_offers = self._llm_rank_offers(candidates, user_input, top_k=5)
        
        # Step 4: Format final results
        return self._format_hybrid_results(final_offers, user_input)

    def _create_llm_search_query(self, user_input: str) -> str:
        """Use LLM to create an optimized search query from user input and preferences"""
        query_prompt = PromptTemplate(
            input_variables=["user_input", "preferences"],
            template="""
You are an expert search query optimizer. Create the most effective search query to find relevant travel offers.

User Input: {user_input}
Current Preferences: {preferences}

Create a search query that will find the most relevant travel offers. Consider:
- Destination preferences
- Duration requirements  
- Travel style (cultural, adventure, luxury, etc.)
- Budget level
- Group size
- Timing preferences

Return ONLY the search query, nothing else. Make it specific and effective for semantic search.

Search Query:
"""
        )
        
        try:
            preferences_str = json.dumps(self.user_preferences, indent=2)
            result = self.generation_model.invoke(
                query_prompt.format(user_input=user_input, preferences=preferences_str)
            )
            search_query = result.content if hasattr(result, 'content') else str(result)
            return search_query.strip()
        except Exception as e:
            print(f"LLM search query creation failed: {e}")
            # Fallback to simple query
            return self._create_simple_search_query(user_input)

    def _create_simple_search_query(self, user_input: str) -> str:
        """Create a simple search query without LLM"""
        query_parts = [user_input]
        
        # Add preferences to query
        if self.user_preferences.get('destination'):
            query_parts.append(self.user_preferences['destination'])
        if self.user_preferences.get('duration'):
            query_parts.append(f"{self.user_preferences['duration']} days")
        if self.user_preferences.get('style'):
            query_parts.append(self.user_preferences['style'])
        if self.user_preferences.get('timing'):
            query_parts.append(self.user_preferences['timing'])
        
        return " ".join(query_parts)

    def _llm_rank_offers(self, candidates: list, user_input: str, top_k: int = 5) -> list:
        """Use LLM to rank and select the best offers from candidates"""
        if not candidates:
            return []
        
        # Format candidates for LLM
        candidates_text = ""
        for i, offer in enumerate(candidates, 1):
            destinations = ", ".join([f"{d.get('city', '')} ({d.get('country', '')})" for d in offer.destinations])
            candidates_text += f"{i}. {offer.product_name} (Ref: {offer.reference})\n"
            candidates_text += f"   Destinations: {destinations}\n"
            candidates_text += f"   Duration: {offer.duration} days\n"
            candidates_text += f"   Type: {offer.offer_type}\n"
            candidates_text += f"   Description: {offer.description[:100]}...\n\n"
        
        ranking_prompt = PromptTemplate(
            input_variables=["user_input", "preferences", "candidates", "top_k"],
            template="""
You are an expert travel advisor. Rank the following travel offers based on the user's needs and preferences.

User Input: {user_input}
User Preferences: {preferences}
Number of offers to select: {top_k}

Available Offers:
{candidates}

Your task:
1. Analyze each offer against the user's preferences
2. Consider destination match, duration fit, style alignment, and overall relevance
3. Select the top {top_k} most relevant offers
4. Provide a brief reason for each selection

Return ONLY a JSON array with the selected offer references and reasons:
[
    {{
        "reference": "offer_reference",
        "reason": "brief explanation of why this offer is perfect for the user"
    }}
]

Selected Offers:
"""
        )
        
        try:
            preferences_str = json.dumps(self.user_preferences, indent=2)
            result = self.generation_model.invoke(
                ranking_prompt.format(
                    user_input=user_input,
                    preferences=preferences_str,
                    candidates=candidates_text,
                    top_k=top_k
                )
            )
            
            ranking_result = result.content if hasattr(result, 'content') else str(result)
            selected_refs = self._parse_ranking_result(ranking_result)
            
            # Get the actual offer objects for selected references
            final_offers = []
            for ref in selected_refs:
                for offer in candidates:
                    if offer.reference == ref:
                        final_offers.append(offer)
                        break
            
            return final_offers[:top_k]
            
        except Exception as e:
            print(f"LLM ranking failed: {e}")
            # Fallback to simple ranking based on preferences
            return self._simple_rank_offers(candidates, user_input, top_k)

    def _simple_rank_offers(self, candidates: list, user_input: str, top_k: int = 5) -> list:
        """Simple ranking without LLM when API is down"""
        if not candidates:
            return []
        
        # Simple scoring based on preference matches
        scored_offers = []
        for offer in candidates:
            score = 0
            
            # Check destination match
            if self.user_preferences.get('destination'):
                dest_pref = self.user_preferences['destination'].lower()
                offer_destinations = [d.get('city', '').lower() + ' ' + d.get('country', '').lower() for d in offer.destinations]
                if any(dest_pref in dest for dest in offer_destinations):
                    score += 3
            
            # Check duration match
            if self.user_preferences.get('duration'):
                try:
                    pref_duration = int(self.user_preferences['duration'])
                    if abs(offer.duration - pref_duration) <= 2:  # Within 2 days
                        score += 2
                except:
                    pass
            
            # Check style match
            if self.user_preferences.get('style'):
                style_pref = self.user_preferences['style'].lower()
                if style_pref in offer.description.lower() or style_pref in offer.offer_type.lower():
                    score += 1
            
            scored_offers.append((offer, score))
        
        # Sort by score and return top_k
        scored_offers.sort(key=lambda x: x[1], reverse=True)
        return [offer for offer, _ in scored_offers[:top_k]]

    def _parse_ranking_result(self, ranking_result: str) -> list:
        """Parse LLM ranking result to extract offer references"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\[.*\]', ranking_result, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                return [item.get('reference', '') for item in data if item.get('reference')]
            
            # Fallback: extract references using regex
            refs = re.findall(r'"reference":\s*"([^"]+)"', ranking_result)
            return refs
            
        except Exception as e:
            print(f"Failed to parse ranking result: {e}")
            return []


    
    def _format_hybrid_results(self, offers: list, user_input: str) -> str:
        """Format the final hybrid search results"""
        if not offers:
            return "No relevant offers found based on your preferences."
        
        summary = f"🎯 Top {len(offers)} Most Relevant Offers (AI-curated):\n\n"
        
        for i, offer in enumerate(offers, 1):
            destinations = ", ".join([f"{d.get('city', '')} ({d.get('country', '')})" for d in offer.destinations])
            summary += f"{i}. {offer.product_name} (Ref: {offer.reference})\n"
            summary += f"   🌍 Destinations: {destinations}\n"
            summary += f"   ⏱️ Duration: {offer.duration} days\n"
            summary += f"   🏷️ Type: {offer.offer_type}\n"
            summary += f"   📝 Description: {offer.description[:80]}...\n\n"
        
        return summary

    def process_user_input_stream(self, user_input: str):
        """Process user input with streaming response"""
        debug_print(f"🚀 Starting to process user input with streaming: '{user_input[:50]}...'")
        
        # Get chat history
        chat_history = self._get_chat_history()
        debug_print(f"📝 Chat history length: {len(chat_history)} characters")
        
        # Update preferences
        debug_print("🔄 Updating user preferences")
        self._update_preferences(user_input)
        
        # Check if we have enough preferences for offer matching
        required_slots = ['destination', 'duration']
        missing_slots = [slot for slot in required_slots if not self.user_preferences.get(slot)]
        
        debug_print(f"🎯 Required slots: {required_slots}, Missing: {missing_slots}")
        debug_print(f"👤 Current preferences: {self.user_preferences}")
        
        # Prepare offers summary
        debug_print("🔍 Preparing offers summary...")
        offers_summary = self._prepare_smart_offers_summary()
        debug_print(f"📊 Offers summary length: {len(offers_summary)} characters")
        
        # Build LLM prompt
        debug_print("🤖 Building LLM prompt...")
        llm_prompt = self._build_llm_prompt(user_input, chat_history, offers_summary)
        debug_print(f"📝 LLM prompt length: {len(llm_prompt)} characters")
        
        # Check if user explicitly asks for offers
        if self._is_offer_request(user_input):
            debug_print("🎯 User explicitly asked for offers, will show them")
            intent_summary = self._create_intent_summary()
            llm_prompt += f"\n\nUSER INTENT SUMMARY:\n{intent_summary}\n\n"
            llm_prompt += "IMPORTANT: Show the 3-5 top relevant offers based on user preferences."
        else:
            debug_print("🤔 User hasn't explicitly asked for offers, will ask for confirmation")
            intent_summary = self._create_intent_summary()
            llm_prompt += f"\n\nUSER INTENT SUMMARY:\n{intent_summary}\n\n"
            llm_prompt += "IMPORTANT: Summarize the user's travel intent and ask if they want to see the 3-5 top relevant offers. Only show offers after they confirm."
        
        debug_print("🤖 Making streaming LLM call...")
        
        # Stream the response
        if self.generation_model:
            try:
                # Use streaming call
                response_stream = self.generation_model.stream(llm_prompt)
                
                for chunk in response_stream:
                    if hasattr(chunk, 'content') and chunk.content:
                        yield chunk.content
                    elif isinstance(chunk, str):
                        yield chunk
                        
            except Exception as e:
                debug_print(f"❌ Streaming LLM call failed: {e}")
                yield f"I encountered an error: {str(e)}. Please try rephrasing your request."
        else:
            debug_print("❌ No generation model available")
            yield "I'm sorry, but I'm currently unable to process your request. Please try again later."

    def _build_llm_prompt(self, user_input: str, chat_history: str, offers_summary: str) -> str:
        """Build the LLM prompt for streaming responses"""
        debug_print("🔨 Building LLM prompt for streaming...")
        
        # Create a simple, direct prompt for streaming
        prompt = f"""You are Layla, a friendly and helpful travel agent. Respond to the user's request in a conversational, helpful manner.

Chat History:
{chat_history}

Available Travel Offers:
{offers_summary}

User Request: {user_input}

Please provide a helpful, conversational response. Keep it concise and friendly. If the user is asking for travel recommendations, suggest relevant offers from the available list above.

Response:"""
        
        debug_print(f"✅ LLM prompt built, length: {len(prompt)} characters")
        return prompt

class LaylaConcreteAgent:
    """Main agent using concrete pipeline with Groq models"""
    
    def __init__(self, data_path: str = None):
        debug_print("🤖 Initializing LaylaConcreteAgent")
        self.pipeline = ConcretePipeline(data_path)
        debug_print("✅ LaylaConcreteAgent initialization complete")
    
    def chat(self, user_input: str) -> str:
        """Chat with the agent using the concrete pipeline"""
        debug_print(f"💬 Starting chat with input: '{user_input[:50]}...'")
        
        try:
            debug_print("🔄 Calling pipeline.process_user_input...")
            result = self.pipeline.process_user_input(user_input)
            debug_print("✅ Pipeline processing complete")
            
            if "error" in result:
                debug_print(f"❌ Error in result: {result['error']}")
                return result["final_response"]
            
            # Add to memory
            debug_print("🧠 Adding to memory...")
            self.pipeline.add_to_memory(user_input, result["final_response"])
            debug_print("✅ Memory updated")
            
            debug_print(f"📤 Returning response, length: {len(result['final_response'])} characters")
            return result["final_response"]
            
        except Exception as e:
            debug_print(f"❌ Exception in chat: {str(e)}")
            return f"I encountered an error: {str(e)}. Please try rephrasing your request."
    
    def chat_stream(self, user_input: str):
        """Stream chat with the agent using the concrete pipeline"""
        debug_print(f"💬 Starting streaming chat with input: '{user_input[:50]}...'")
        
        try:
            debug_print("🔄 Calling pipeline.process_user_input_stream...")
            response_stream = self.pipeline.process_user_input_stream(user_input)
            
            full_response = ""
            for chunk in response_stream:
                if chunk:
                    full_response += chunk
                    yield chunk
            
            # Add to memory after streaming is complete
            debug_print("🧠 Adding to memory...")
            self.pipeline.add_to_memory(user_input, full_response)
            debug_print("✅ Memory updated")
            
        except Exception as e:
            debug_print(f"❌ Exception in streaming chat: {str(e)}")
            yield f"I encountered an error: {str(e)}. Please try rephrasing your request."
    
    def get_detailed_response(self, user_input: str) -> Dict[str, Any]:
        """Get detailed response with all pipeline data"""
        debug_print(f"📊 Getting detailed response for: '{user_input[:50]}...'")
        
        result = self.pipeline.process_user_input(user_input)
        
        if "error" not in result:
            debug_print("🧠 Adding to memory for detailed response...")
            self.pipeline.add_to_memory(user_input, result["final_response"])
        
        debug_print("✅ Detailed response ready")
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        debug_print("📊 Getting agent status...")
        status = self.pipeline.get_pipeline_status()
        debug_print("✅ Status retrieved")
        return status
    
    def get_preferences(self) -> dict:
        """Get current user preferences"""
        return self.pipeline.get_preferences()
    
    def clear_preferences(self):
        """Clear all user preferences - only call this when user explicitly wants to reset"""
        return self.pipeline.clear_preferences()
    
    def modify_preference(self, key: str, value: str):
        """Modify a specific preference - for when user wants to change something specific"""
        return self.pipeline.modify_preference(key, value)
    
    def clear_memory(self):
        """Clear conversation memory"""
        debug_print("🧠 Clearing conversation memory...")
        self.pipeline.memory.clear()
        debug_print("✅ Conversation memory cleared")
    
    def _is_offer_request(self, user_input: str) -> bool:
        """Check if user is requesting offers"""
        return self.pipeline._is_offer_request(user_input)
    
    def _filter_offers(self, preferences, max_offers=5):
        """Filter offers based on preferences"""
        return self.pipeline._filter_offers(preferences, max_offers)

    def get_welcome_message(self) -> str:
        """Get a welcome message from the agent"""
        debug_print("👋 Generating welcome message...")
        
        try:
            if self.pipeline.generation_model is None:
                debug_print("❌ No generation model available for welcome message")
                return "Bonjour! Je suis Layla, votre agent de voyage personnel! 🧳✈️ Je peux vous aider à planifier vos voyages, trouver des destinations, des hôtels, des activités et bien plus encore. Dites-moi où vous souhaitez partir ou ce que vous cherchez!"
            
            welcome_prompt = """You are Layla, a friendly and professional travel agent. Generate a warm, welcoming message in French that introduces yourself and explains how you can help with travel planning.

The message should:
- Be warm and welcoming
- Be in French
- Introduce yourself as Layla
- Explain that you can help with travel planning, destinations, hotels, activities
- Invite the user to tell you where they want to go or what they're looking for
- Be concise (under 100 words)
- Use appropriate emojis sparingly

Generate the welcome message:"""
            
            response = self.pipeline._call_llm_with_retry(
                self.pipeline.generation_model, 
                welcome_prompt
            )
            
            debug_print(f"✅ Welcome message generated: {response[:50]}...")
            return response.strip()
            
        except Exception as e:
            debug_print(f"❌ Error generating welcome message: {e}")
            return "Bonjour! Je suis Layla, votre agent de voyage personnel! 🧳✈️ Je peux vous aider à planifier vos voyages, trouver des destinations, des hôtels, des activités et bien plus encore. Dites-moi où vous souhaitez partir ou ce que vous cherchez!"

# Example usage
if __name__ == "__main__":
    # Initialize agent
    agent = LaylaConcreteAgent()
    
    print("🤖 Layla Concrete Pipeline Agent initialized!")
    print(f"Reasoning Model: Groq DeepSeek R1 (superior thinking)")
    print(f"Generation Model: Groq Kimi K2 (1T parameter MoE - superior creativity)")
    print(f"Matching Model: Groq Llama 4 Scout (superior semantic understanding & function calling)")
    print(f"Embedding Model: SentenceTransformers (Local)")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        
        response = agent.chat(user_input)
        print(f"Layla: {response}\n") 