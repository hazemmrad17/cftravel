"""
LLM model definitions for ASIA.fr Agent
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum

class ModelType(str, Enum):
    """Types of LLM models"""
    REASONING = "reasoning"
    GENERATION = "generation"
    MATCHING = "matching"
    EMBEDDING = "embedding"

class ModelProvider(str, Enum):
    """LLM providers"""
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class LLMConfig(BaseModel):
    """Configuration for LLM models"""
    model_name: str
    provider: ModelProvider
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    class Config:
        use_enum_values = True

class LLMRequest(BaseModel):
    """Request model for LLM calls"""
    prompt: str
    config: LLMConfig
    context: Optional[Dict[str, Any]] = None
    stream: bool = False

class LLMResponse(BaseModel):
    """Response model for LLM calls"""
    text: str
    model_used: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class StreamingChunk(BaseModel):
    """Model for streaming response chunks"""
    chunk: str
    type: str = "content"
    metadata: Optional[Dict[str, Any]] = None

class ConversationMessage(BaseModel):
    """Model for conversation messages"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

class Conversation(BaseModel):
    """Model for conversation context"""
    id: str
    messages: List[ConversationMessage]
    user_preferences: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str 