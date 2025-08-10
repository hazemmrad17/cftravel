"""
Models module for ASIA.fr Agent
"""

from .data_models import (
    ChatRequest,
    OfferCard,
    DetailedProgram,
    PreferenceRequest,
    UserPreferences,
    TravelOffer
)
from .response_models import (
    ChatResponse,
    AgentStatusResponse,
    HealthResponse,
    PreferencesResponse,
    MemoryResponse,
    WelcomeResponse,
    OffersResponse,
    ErrorResponse
)
from .llm_models import (
    ModelType,
    ModelProvider,
    LLMConfig,
    LLMRequest,
    LLMResponse,
    StreamingChunk,
    ConversationMessage,
    Conversation
)

__all__ = [
    # Data models
    'ChatRequest',
    'OfferCard',
    'DetailedProgram',
    'PreferenceRequest',
    'UserPreferences',
    'TravelOffer',
    
    # Response models
    'ChatResponse',
    'AgentStatusResponse',
    'HealthResponse',
    'PreferencesResponse',
    'MemoryResponse',
    'WelcomeResponse',
    'OffersResponse',
    'ErrorResponse',
    
    # LLM models
    'ModelType',
    'ModelProvider',
    'LLMConfig',
    'LLMRequest',
    'LLMResponse',
    'StreamingChunk',
    'ConversationMessage',
    'Conversation'
] 