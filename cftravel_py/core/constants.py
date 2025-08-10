"""
Constants and enums for ASIA.fr Agent
"""

from enum import Enum

class LLMProvider(Enum):
    """Available LLM providers"""
    GROQ = "groq"

class ModelType(Enum):
    """Types of models"""
    REASONING = "reasoning"
    GENERATION = "generation"
    MATCHING = "matching"
    EMBEDDING = "embedding"

class OfferType(Enum):
    """Types of travel offers"""
    CIRCUIT = "circuit"
    PACKAGE = "package"
    CUSTOM = "custom"
    GROUP = "group"

class TravelStyle(Enum):
    """Travel style preferences"""
    CULTURAL = "cultural"
    ADVENTURE = "adventure"
    LUXURY = "luxury"
    RELAXATION = "relaxation"
    URBAN = "urban"
    NATURE = "nature"

class BudgetLevel(Enum):
    """Budget levels"""
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    LUXURY = "luxury"
    PREMIUM = "premium"

# API Constants
API_VERSION = "1.0.0"
API_TITLE = "ASIA.fr Agent API"
API_DESCRIPTION = "REST API for ASIA.fr Agent - Hybrid LLM + Vector Search"

# Default Configuration
DEFAULT_MAX_TOKENS = 2048
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_OFFERS = 3

# File Paths
DEFAULT_DATA_PATH = "data/asia/data.json"
DEFAULT_CONFIG_PATH = ".env"

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_ERROR = 500

# Error Messages
ERROR_MESSAGES = {
    "config_missing": "Configuration file not found",
    "api_key_missing": "API key not found in environment",
    "llm_unavailable": "LLM service unavailable",
    "data_not_found": "Data file not found",
    "validation_failed": "Data validation failed",
    "memory_error": "Memory operation failed",
    "offer_not_found": "Offer not found"
} 