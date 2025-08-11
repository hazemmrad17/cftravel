"""
Complete LangChain Pipeline for Layla Travel Agent
Uses LLMs/transformers at every step of the process
"""

import os
from typing import List, Dict, Any, Optional
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain.schema import BaseOutputParser
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json

from core.config import config
from services.llm_service import LLMFactory, ReasoningLLM
from data.data_processor import DataProcessor, TravelOffer

class PreferenceParser(BaseModel):
    """Structured output for preference parsing"""
    destination: Optional[str] = Field(description="Extracted destination")
    duration: Optional[int] = Field(description="Extracted duration in days")
    group_size: Optional[int] = Field(description="Extracted group size")
    budget: Optional[str] = Field(description="Budget level: low, medium, high")
    keywords: List[str] = Field(description="Extracted keywords and preferences")
    dates: List[str] = Field(description="Extracted dates")

class OfferMatch(BaseModel):
    """Structured output for offer matching"""
    offer_reference: str = Field(description="Offer reference")
    match_score: float = Field(description="Match score (0-1)")
    reasoning: str = Field(description="Why this offer matches")
    highlights: List[str] = Field(description="Key highlights for user")

class LangChainPipeline:
    """Complete LangChain pipeline using LLMs at every step"""
    
    def __init__(self, data_path: str = None):
        self.data_path = data_path or config.data_path
        self.setup_components()
        self.setup_chains()
    
    def setup_components(self):
        """Setup all pipeline components"""
        # Initialize LLM
        llm = LLMFactory.create_llm(config.llm_config)
        self.llm = llm
        
        # Initialize data processor
        self.data_processor = DataProcessor(self.data_path)
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    
    def setup_chains(self):
        """Setup all LangChain chains"""
        
        # 1. Preference Parsing Chain
        preference_prompt = PromptTemplate(
            input_variables=["user_input"],
            template="""
You are an intelligent travel preference parser. Extract structured preferences from user input.

User Input: {user_input}

Extract the following information:
- Destination (country, city, region)
- Duration (number of days)
- Group size (number of people)
- Budget level (low, medium, high)
- Keywords (cultural, adventure, luxury, budget, etc.)
- Dates (specific dates mentioned)

Respond in JSON format with these fields:
{{
    "destination": "extracted destination or null",
    "duration": "number of days or null",
    "group_size": "number of people or null", 
    "budget": "low/medium/high or null",
    "keywords": ["list", "of", "keywords"],
    "dates": ["list", "of", "dates"]
}}
"""
        )
        
        self.preference_chain = LLMChain(
            llm=self.llm,
            prompt=preference_prompt,
            output_key="parsed_preferences"
        )
        
        # 2. Semantic Matching Chain
        matching_prompt = PromptTemplate(
            input_variables=["user_input", "parsed_preferences", "available_offers"],
            template="""
You are an intelligent travel offer matcher. Match user preferences to available offers.

User Input: {user_input}
Parsed Preferences: {parsed_preferences}
Available Offers: {available_offers}

For each relevant offer, provide:
- Offer reference
- Match score (0-1)
- Reasoning for the match
- Key highlights for the user

Respond in JSON format:
{{
    "matches": [
        {{
            "offer_reference": "offer_ref",
            "match_score": 0.85,
            "reasoning": "Why this matches",
            "highlights": ["highlight1", "highlight2"]
        }}
    ]
}}
"""
        )
        
        self.matching_chain = LLMChain(
            llm=self.llm,
            prompt=matching_prompt,
            output_key="offer_matches"
        )
        
        # 3. Reasoning Chain
        reasoning_prompt = PromptTemplate(
            input_variables=["user_input", "parsed_preferences", "offer_matches"],
            template="""
You are Layla, an intelligent travel agent. Provide thoughtful reasoning about travel recommendations.

User Input: {user_input}
Parsed Preferences: {parsed_preferences}
Matched Offers: {offer_matches}

Think through this step by step:
1. What does the user really want?
2. How do the preferences align with the offers?
3. What makes each offer a good match?
4. How should I explain this to the user?

Provide a conversational response with clear reasoning:
"""
        )
        
        self.reasoning_chain = LLMChain(
            llm=self.llm,
            prompt=reasoning_prompt,
            output_key="reasoned_response"
        )
        
        # 4. Response Generation Chain
        response_prompt = PromptTemplate(
            input_variables=["user_input", "reasoned_response", "chat_history"],
            template="""
You are Layla, a friendly and intelligent travel agent. Generate a helpful response.

Chat History: {chat_history}
User Input: {user_input}
Reasoned Analysis: {reasoned_response}

Generate a conversational, helpful response that:
- Addresses the user's request
- Explains your reasoning clearly
- Suggests specific offers when relevant
- Maintains a friendly, helpful tone

Response:
"""
        )
        
        self.response_chain = LLMChain(
            llm=self.llm,
            prompt=response_prompt,
            output_key="final_response"
        )
        
        # 5. Complete Sequential Chain
        self.full_pipeline = SequentialChain(
            chains=[
                self.preference_chain,
                self.matching_chain,
                self.reasoning_chain,
                self.response_chain
            ],
            input_variables=["user_input", "available_offers", "chat_history"],
            output_variables=["parsed_preferences", "offer_matches", "reasoned_response", "final_response"],
            verbose=config.debug
        )
    
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input through the complete LangChain pipeline"""
        try:
            # Prepare available offers for the pipeline
            offers_summary = self._prepare_offers_summary()
            
            # Get chat history
            chat_history = self._get_chat_history()
            
            # Run the complete pipeline
            result = self.full_pipeline.run({
                "user_input": user_input,
                "available_offers": offers_summary,
                "chat_history": chat_history
            })
            
            # Parse the results
            parsed_preferences = self._parse_json_safely(result.get("parsed_preferences", "{}"))
            offer_matches = self._parse_json_safely(result.get("offer_matches", "{}"))
            
            return {
                "user_input": user_input,
                "parsed_preferences": parsed_preferences,
                "offer_matches": offer_matches,
                "reasoned_response": result.get("reasoned_response", ""),
                "final_response": result.get("final_response", ""),
                "pipeline_steps": [
                    "preference_parsing",
                    "semantic_matching", 
                    "reasoning",
                    "response_generation"
                ]
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "final_response": f"I encountered an error while processing your request: {str(e)}. Please try rephrasing."
            }
    
    def _prepare_offers_summary(self) -> str:
        """Prepare a summary of available offers for the LLM"""
        offers = self.data_processor.offers[:10]  # Limit to first 10 for context
        summary = "Available Travel Offers:\n\n"
        
        for i, offer in enumerate(offers, 1):
            destinations = ", ".join([f"{d.get('city', '')} ({d.get('country', '')})" for d in offer.destinations])
            summary += f"{i}. {offer.product_name} ({offer.reference})\n"
            summary += f"   Destinations: {destinations}\n"
            summary += f"   Duration: {offer.duration} days\n"
            summary += f"   Group: {offer.min_group_size}-{offer.max_group_size} people\n"
            summary += f"   Type: {offer.offer_type}\n"
            summary += f"   Description: {offer.description[:100]}...\n\n"
        
        return summary
    
    def _get_chat_history(self) -> str:
        """Get formatted chat history"""
        if not self.memory.chat_memory.messages:
            return "No previous conversation."
        
        history = "Previous conversation:\n"
        for message in self.memory.chat_memory.messages[-6:]:  # Last 6 messages
            if hasattr(message, 'content'):
                role = "User" if hasattr(message, 'type') and message.type == 'human' else "Layla"
                history += f"{role}: {message.content}\n"
        
        return history
    
    def _parse_json_safely(self, json_str: str) -> Dict[str, Any]:
        """Safely parse JSON string"""
        try:
            # Clean up the JSON string
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
        """Get pipeline status and capabilities"""
        return {
            "llm_provider": config.llm_config.provider.value,
            "model": config.llm_config.model_name,
            "pipeline_steps": [
                "Preference Parsing (LLM)",
                "Semantic Matching (LLM)", 
                "Reasoning (LLM)",
                "Response Generation (LLM)"
            ],
            "memory_enabled": True,
            "offers_loaded": len(self.data_processor.offers),
            "debug_mode": config.debug
        }

class LaylaLangChainAgent:
    """Main agent using complete LangChain pipeline"""
    
    def __init__(self, data_path: str = None):
        self.pipeline = LangChainPipeline(data_path)
    
    def chat(self, user_input: str) -> str:
        """Chat with the agent using the complete LangChain pipeline"""
        try:
            # Process through the complete pipeline
            result = self.pipeline.process_user_input(user_input)
            
            if "error" in result:
                return result["final_response"]
            
            # Add to memory
            self.pipeline.add_to_memory(user_input, result["final_response"])
            
            return result["final_response"]
            
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try rephrasing your request."
    
    def get_detailed_response(self, user_input: str) -> Dict[str, Any]:
        """Get detailed response with all pipeline steps"""
        result = self.pipeline.process_user_input(user_input)
        
        if "error" not in result:
            self.pipeline.add_to_memory(user_input, result["final_response"])
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return self.pipeline.get_pipeline_status()

# Example usage
if __name__ == "__main__":
    # Initialize agent
    agent = LaylaLangChainAgent()
    
    print("🤖 Layla LangChain Pipeline Agent initialized!")
    print(f"LLM Provider: {agent.get_status()['llm_provider']}")
    print(f"Model: {agent.get_status()['model']}")
    print("Pipeline Steps:")
    for step in agent.get_status()['pipeline_steps']:
        print(f"  - {step}")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        
        response = agent.chat(user_input)
        print(f"Layla: {response}\n") 