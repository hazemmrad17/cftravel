"""
Modular configuration for ASIA.fr Travel Agent
Uses Groq models for all LLM operations - fully configurable via environment variables
"""

import os
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path

# Load environment file from the current directory or parent
current_dir = Path(__file__).parent.parent
env_path = None

# First try to load env.local for local development
env_path = current_dir / 'env.local'
if not env_path.exists():
    env_path = current_dir.parent / 'env.local'
if not env_path.exists():
    env_path = current_dir.parent.parent / 'env.local'

# If env.local not found, try .env
if not env_path.exists():
    env_path = current_dir / '.env'
if not env_path.exists():
    env_path = current_dir.parent / '.env'
if not env_path.exists():
    env_path = current_dir.parent.parent / '.env'

print(f"Loading environment from: {env_path}")
print(f"File exists: {env_path.exists()}")
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    print("⚠️ No environment file found - using environment variables only")

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
    """Main configuration class - fully environment-driven"""
    
    def __init__(self):
        self.data_path = os.getenv("DATA_PATH", "data")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        # Force the correct base URL for Groq API
        self.groq_base_url = "https://api.groq.com/openai/v1"
        
        # Validate required configuration
        if not self.groq_api_key:
            print("⚠️ WARNING: GROQ_API_KEY not set - AI functionality will be limited")
            print("🔄 Server will run in fallback mode with basic functionality")
    
    def get_model_config(self, model_type: str) -> Dict[str, Any]:
        """Get configuration for a specific model type from environment variables"""
        if not self.groq_api_key:
            raise ValueError(f"GROQ_API_KEY required for {model_type}")
        
        # Model-specific environment variables
        model_env_var = f"{model_type.upper()}_MODEL"
        temp_env_var = f"{model_type.upper()}_TEMPERATURE"
        tokens_env_var = f"{model_type.upper()}_MAX_TOKENS"
        
        # Default values for each model type - Using Kimi K2 for better performance
        defaults = {
            "reasoning": {
                "model": "moonshotai/kimi-k2-instruct",
                "temperature": 0.1,
                "max_tokens": 2048
            },
            "generation": {
                "model": "moonshotai/kimi-k2-instruct",
                "temperature": 0.7,
                "max_tokens": 2048
            },
            "matcher": {
                "model": "moonshotai/kimi-k2-instruct",
                "temperature": 0.3,
                "max_tokens": 2048
            },
            "extractor": {
                "model": "moonshotai/kimi-k2-instruct",
                "temperature": 0.1,
                "max_tokens": 1024
            }
        }
        
        default = defaults.get(model_type, defaults["generation"])
        
        return {
            "provider": "groq",
            "model": default["model"],  # Use default models instead of env vars
            "temperature": float(os.getenv(temp_env_var, str(default["temperature"]))),
            "max_tokens": int(os.getenv(tokens_env_var, str(default["max_tokens"]))),
            "api_key": self.groq_api_key,
            "base_url": self.groq_base_url
        }
    
    def get_embedding_config(self) -> Dict[str, Any]:
        """Get embedding model configuration"""
        return {
            "model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            "provider": "sentence-transformers"
        }
    
    def get_all_models_config(self) -> Dict[str, Any]:
        """Get configuration for all models"""
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        return {
            "reasoning_model": self.get_model_config("reasoning"),
            "generation_model": self.get_model_config("generation"),
            "matcher_model": self.get_model_config("matcher"),
            "extractor_model": self.get_model_config("extractor"),
            "embedding_model": self.get_embedding_config()
        }
    
    def print_configuration(self):
        """Print current configuration for debugging"""
        print("\n=== ASIA.fr Agent Configuration ===")
        print(f"Debug Mode: {self.debug}")
        print(f"Data Path: {self.data_path}")
        print(f"Groq API Key: {'Set' if self.groq_api_key else 'Not set'}")
        print(f"Groq Base URL: {self.groq_base_url}")
        
        if self.groq_api_key:
            print("\nModel Configuration:")
            try:
                models = self.get_all_models_config()
                for model_name, config in models.items():
                    if model_name != "embedding_model":
                        print(f"  {model_name}: {config['model']} (temp: {config['temperature']}, tokens: {config['max_tokens']})")
                    else:
                        print(f"  {model_name}: {config['model']}")
            except Exception as e:
                print(f"  Error loading model config: {e}")
        
        print("================================\n")

# Global config instance
config = Config()

# Print configuration on import
if __name__ != "__main__":
    config.print_configuration() 