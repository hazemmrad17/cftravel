"""
LLM Factory for Layla Travel Agent
Only supports Groq models
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from core.config import LLMConfig

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


class LLMService:
    """Service wrapper for LLM operations"""
    
    def __init__(self):
        self._llm_instances = {}
        self._configs = {}
        self._setup_configs()
    
    def _setup_configs(self):
        """Setup different LLM configurations for different use cases"""
        from core.config import config
        
        base_config = config
        
        # Different configurations for different models
        self._configs = {
            "orchestrator": LLMConfig(
                provider="groq",
                api_key=base_config.groq_api_key,
                base_url=base_config.groq_base_url,
                model_name="moonshotai/kimi-k2-instruct",
                temperature=0.1,
                max_tokens=2048
            ),
            "extractor": LLMConfig(
                provider="groq",
                api_key=base_config.groq_api_key,
                base_url=base_config.groq_base_url,
                model_name="moonshotai/kimi-k2-instruct",
                temperature=0.1,
                max_tokens=1024
            ),
            "matcher": LLMConfig(
                provider="groq",
                api_key=base_config.groq_api_key,
                base_url=base_config.groq_base_url,
                model_name="moonshotai/kimi-k2-instruct",
                temperature=0.3,
                max_tokens=2048
            ),
            "generator": LLMConfig(
                provider="groq",
                api_key=base_config.groq_api_key,
                base_url=base_config.groq_base_url,
                model_name="moonshotai/kimi-k2-instruct",
                temperature=0.7,
                max_tokens=2048
            ),
            "default": LLMConfig(
                provider="groq",
                api_key=base_config.groq_api_key,
                base_url=base_config.groq_base_url,
                model_name="moonshotai/kimi-k2-instruct",
                temperature=0.5,
                max_tokens=2048
            )
        }
    
    def _get_llm(self, model: str = "default"):
        """Get or create LLM instance for the specified model"""
        if model not in self._llm_instances:
            config = self._configs.get(model, self._configs["default"])
            self._llm_instances[model] = LLMFactory.create_llm(config)
        return self._llm_instances[model]
    
    async def generate_text(self, prompt: str, model: str = "default") -> str:
        """Generate text using the specified model"""
        try:
            llm = self._get_llm(model)
            response = llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"❌ LLM generation failed: {e}")
            # Return a fallback response
            return "Je suis désolé, j'ai rencontré une difficulté technique. Pouvez-vous reformuler votre demande ?"
    
    def generate_text_sync(self, prompt: str, model: str = "default") -> str:
        """Synchronous version of generate_text"""
        try:
            llm = self._get_llm(model)
            response = llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"❌ LLM generation failed: {e}")
            return "Je suis désolé, j'ai rencontré une difficulté technique. Pouvez-vous reformuler votre demande ?" 