"""
Modular configuration for Layla Travel Agent
Uses Groq models for all LLM operations
"""

import os
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Explicitly load .env file
load_dotenv()

class LLMProvider(Enum):
    """Available LLM providers"""
    GROQ = "groq"  # Only Groq is supported

@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: LLMProvider
    model_name: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.llm_config = self._get_llm_config()
        self.data_path = os.getenv("DATA_PATH", "data/asia/data.json")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
    
    def _get_llm_config(self) -> LLMConfig:
        """Get LLM configuration - Only Groq is supported"""
        print("\n=== DEBUG: Model Configuration ===")
        print("Environment Variables:")
        print(f"  GROQ_API_KEY: {'Set' if os.getenv('GROQ_API_KEY') else 'Not set'}")
        print("==============================\n")
        
        # Force Groq provider
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
            
        return LLMConfig(
            provider=LLMProvider.GROQ,
            model_name=os.getenv("GROQ_MODEL", "llama3-8b-8192"),
            temperature=float(os.getenv("GROQ_TEMPERATURE", "0.7")),
            api_key=api_key,
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "1024"))
        )
    
    def get_available_providers(self) -> Dict[str, str]:
        """Get available LLM providers with their status"""
        if os.getenv("GROQ_API_KEY"):
            return {"groq": "Available (Free tier)"}
        return {"groq": "API key required (Free tier available)"}
    
    def get_specialized_models_config(self) -> Dict[str, Any]:
        """Get configuration for specialized models - Only Groq is supported"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
            
        return {
            "reasoning_model": {
                "provider": "groq",
                "model": os.getenv("REASONING_MODEL", "llama3-8b-8192"),
                "temperature": float(os.getenv("REASONING_TEMPERATURE", "0.1")),
                "api_key": api_key,
                "max_tokens": int(os.getenv("GROQ_MAX_TOKENS", "1024"))
            },
                "generation_model": {
        "provider": "groq",
        "model": os.getenv("GENERATION_MODEL", "openai/gpt-oss-120b"),
        "temperature": float(os.getenv("GENERATION_TEMPERATURE", "0.7")),
        "api_key": api_key,
        "max_tokens": int(os.getenv("GROQ_MAX_TOKENS", "1024"))
    },
    "matching_model": {
        "provider": "groq",
        "model": os.getenv("MATCHING_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct"),
        "temperature": float(os.getenv("MATCHING_TEMPERATURE", "0.3")),
        "api_key": api_key,
        "max_tokens": int(os.getenv("GROQ_MAX_TOKENS", "1024"))
    },
            "embedding_model": {
                "model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
                "provider": "sentence-transformers"
            }
        }

    def get_groq_config(self) -> Dict[str, Any]:
        """Get Groq configuration with the most stable models"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
            
        return {
            "reasoning_model": {
                "provider": "groq",
                "model": "llama3-8b-8192",  # Fast and capable for reasoning
                "temperature": 0.1,
                "api_key": api_key,
                "max_tokens": 2048
            },
            "generation_model": {
                "provider": "groq",
                "model": "gpt-oss-120b",  # More powerful model for generation
                "temperature": 0.7,
                "api_key": api_key,
                "max_tokens": 2048
            },
            "matching_model": {
                "provider": "groq",
                "model": "llama-4-scout",  # Fast for matching
                "temperature": 0.3,
                "api_key": api_key,
                "max_tokens": 1024
            },
            "embedding_model": {
                "model": "all-MiniLM-L6-v2",
                "provider": "sentence-transformers"
            }
        }

# Global config instance
config = Config() 