"""
LLM Factory for Layla Travel Agent
Only supports Groq models
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from cftravel_py.core.config import LLMConfig

class LLMFactory:
    """Factory for creating Groq LLM instances"""
    
    @staticmethod
    def create_llm(config: LLMConfig) -> any:
        """Create LLM instance based on configuration"""
        if config.provider != "groq":
            raise ValueError("Only Groq provider is supported")
        return LLMFactory._create_groq_llm(config)
    
    @staticmethod
    def _create_groq_llm(config: LLMConfig) -> ChatOpenAI:
        """Create Groq LLM using OpenAI-compatible interface"""
        print("\n=== DEBUG: Groq Configuration ===")
        print(f"Provider: {config.provider}")
        print(f"API Key present: {'Yes' if config.api_key else 'No'}")
        if config.api_key:
            print(f"API Key starts with: {config.api_key[:5]}...{config.api_key[-3:]}")
        print(f"Model: {config.model_name}")
        print(f"Base URL: {config.base_url}")
        print(f"Temperature: {config.temperature}")
        print(f"Max Tokens: {config.max_tokens}")
        print("============================\n")
        
        if not config.api_key:
            raise ValueError("Groq API key is required")
        
        try:
            print("\n=== DEBUG: Creating ChatOpenAI instance ===")
            llm = ChatOpenAI(
                model=config.model_name,
                temperature=config.temperature,
                openai_api_key=config.api_key,
                max_tokens=config.max_tokens,
                base_url=config.base_url,
                request_timeout=10  # Add timeout to prevent hanging
            )
            print("ChatOpenAI instance created successfully")
            print("Testing API call...")
            # Test the API with a simple call
            test_prompt = "Hello, this is a test. Please respond with 'OK'"
            response = llm.invoke(test_prompt)
            print(f"API Test Response: {response}")
            print("API Test Successful!")
            print("============================\n")
            return llm
        except Exception as e:
            print("\n=== DEBUG: Error during API call ===")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            print("============================\n")
            raise
    


class ReasoningLLM:
    """Enhanced LLM with reasoning capabilities"""
    
    def __init__(self, llm: any):
        self.llm = llm
        self.thought_process = []
    
    def reason(self, prompt: str, context: str = "") -> str:
        """Generate response with reasoning process"""
        reasoning_prompt = f"""
You are Layla, an intelligent travel agent. Think through your response step by step.

Context: {context}

User Request: {prompt}

Think through this step by step:
1. What does the user want?
2. What preferences can I infer?
3. What travel offers would match these preferences?
4. How should I explain my reasoning?

Now provide your response with clear reasoning:
"""
        
        response = self.llm.invoke(reasoning_prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def chain_of_thought(self, prompt: str) -> dict:
        """Generate response with explicit chain of thought"""
        cot_prompt = f"""
You are Layla, an intelligent travel agent. Use chain of thought reasoning.

User Request: {prompt}

Let me think through this step by step:

1. Understanding the request:
2. Inferring preferences:
3. Matching to travel offers:
4. Formulating response:

Response:
"""
        
        response = self.llm.invoke(cot_prompt)
        return {
            "reasoning": cot_prompt,
            "response": response.content if hasattr(response, 'content') else str(response)
        } 