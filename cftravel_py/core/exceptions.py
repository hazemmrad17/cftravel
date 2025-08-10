"""
Custom exceptions for ASIA.fr Agent
"""

class ASIAException(Exception):
    """Base exception for ASIA.fr Agent"""
    pass

class ConfigurationError(ASIAException):
    """Raised when there's a configuration error"""
    pass

class LLMError(ASIAException):
    """Raised when there's an LLM-related error"""
    pass

class DataError(ASIAException):
    """Raised when there's a data processing error"""
    pass

class APIError(ASIAException):
    """Raised when there's an API-related error"""
    pass

class ValidationError(ASIAException):
    """Raised when data validation fails"""
    pass

class MemoryError(ASIAException):
    """Raised when there's a memory-related error"""
    pass

class OfferError(ASIAException):
    """Raised when there's an offer-related error"""
    pass 