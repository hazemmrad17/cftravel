"""
Core module for ASIA.fr Agent
"""             


from .exceptions import (
    AgentError,
    APIKeyError,
    APITokensDepletedError,
    StreamError,
    MessageSendError,
    MessageReceiveError,
    NetworkError,
    ServerError,
    ValidationError,
    MemoryError,
    ProcessingError,
    create_error_response,
    ErrorType,
    ErrorSeverity
)
from .constants import (
    LLMProvider,
    ModelType,
    OfferType,
    TravelStyle,
    BudgetLevel,
    API_VERSION,
    API_TITLE,
    API_DESCRIPTION,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_OFFERS,
    ERROR_MESSAGES
)

__all__ = [
    'AgentError',
    'APIKeyError',
    'APITokensDepletedError',
    'StreamError',
    'MessageSendError',
    'MessageReceiveError',
    'NetworkError',
    'ServerError',
    'ValidationError',
    'MemoryError',
    'ProcessingError',
    'create_error_response',
    'ErrorType',
    'ErrorSeverity',
    'LLMProvider',
    'ModelType',
    'OfferType',
    'TravelStyle',
    'BudgetLevel',
    'API_VERSION',
    'API_TITLE',
    'API_DESCRIPTION',
    'DEFAULT_MAX_TOKENS',
    'DEFAULT_TEMPERATURE',
    'DEFAULT_MAX_OFFERS',
    'ERROR_MESSAGES'
]               