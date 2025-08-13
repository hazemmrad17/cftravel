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
    

] 