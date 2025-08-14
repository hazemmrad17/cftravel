"""
Custom exceptions for ASIA.fr Agent
"""

from enum import Enum
from typing import Optional, Dict, Any

class ErrorType(Enum):
    """Error types for frontend display"""
    API_KEY_INVALID = "api_key_invalid"
    API_TOKENS_DEPLETED = "api_tokens_depleted"
    STREAM_ERROR = "stream_error"
    MESSAGE_SEND_ERROR = "message_send_error"
    MESSAGE_RECEIVE_ERROR = "message_receive_error"
    NETWORK_ERROR = "network_error"
    SERVER_ERROR = "server_error"
    VALIDATION_ERROR = "validation_error"
    MEMORY_ERROR = "memory_error"
    PROCESSING_ERROR = "processing_error"
    UNKNOWN_ERROR = "unknown_error"

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AgentError(Exception):
    """Base exception for agent errors with user-friendly messages"""
    
    def __init__(
        self, 
        message: str, 
        error_type: ErrorType,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        user_message: Optional[str] = None,
        technical_details: Optional[str] = None,
        error_code: Optional[str] = None
    ):
        self.message = message
        self.error_type = error_type
        self.severity = severity
        self.user_message = user_message or self._get_default_user_message(error_type)
        self.technical_details = technical_details
        self.error_code = error_code or error_type.value
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API response"""
        return {
            "error": True,
            "error_type": self.error_type.value,
            "error_code": self.error_code,
            "severity": self.severity.value,
            "user_message": self.user_message,
            "technical_details": self.technical_details,
            "message": self.message
        }
    
    def _get_default_user_message(self, error_type: ErrorType) -> str:
        """Get default user-friendly message for error type"""
        messages = {
            ErrorType.API_KEY_INVALID: "🔑 Désolé, il y a un problème avec la configuration de l'agent. Veuillez réessayer dans quelques instants.",
            ErrorType.API_TOKENS_DEPLETED: "💳 Les crédits de l'agent sont temporairement épuisés. Veuillez réessayer plus tard.",
            ErrorType.STREAM_ERROR: "📡 Problème de connexion avec l'agent. Veuillez rafraîchir la page et réessayer.",
            ErrorType.MESSAGE_SEND_ERROR: "📤 Impossible d'envoyer votre message. Veuillez réessayer.",
            ErrorType.MESSAGE_RECEIVE_ERROR: "📥 Problème de réception de la réponse. Veuillez réessayer.",
            ErrorType.NETWORK_ERROR: "🌐 Problème de connexion réseau. Vérifiez votre connexion internet.",
            ErrorType.SERVER_ERROR: "🖥️ Problème temporaire du serveur. Veuillez réessayer dans quelques minutes.",
            ErrorType.VALIDATION_ERROR: "⚠️ Informations invalides. Veuillez vérifier vos données et réessayer.",
            ErrorType.MEMORY_ERROR: "🧠 Problème de mémoire de conversation. Veuillez rafraîchir la page.",
            ErrorType.PROCESSING_ERROR: "⚙️ Erreur de traitement. Veuillez réessayer.",
            ErrorType.UNKNOWN_ERROR: "❓ Une erreur inattendue s'est produite. Veuillez réessayer."
        }
        return messages.get(error_type, messages[ErrorType.UNKNOWN_ERROR])

class APIKeyError(AgentError):
    """API key related errors"""
    def __init__(self, message: str = "Invalid API key", technical_details: Optional[str] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.API_KEY_INVALID,
            severity=ErrorSeverity.HIGH,
            technical_details=technical_details
        )

class APITokensDepletedError(AgentError):
    """API tokens depleted error"""
    def __init__(self, message: str = "API tokens depleted", technical_details: Optional[str] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.API_TOKENS_DEPLETED,
            severity=ErrorSeverity.MEDIUM,
            technical_details=technical_details
        )

class StreamError(AgentError):
    """Streaming errors"""
    def __init__(self, message: str = "Stream error occurred", technical_details: Optional[str] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.STREAM_ERROR,
            severity=ErrorSeverity.MEDIUM,
            technical_details=technical_details
        )

class MessageSendError(AgentError):
    """Message sending errors"""
    def __init__(self, message: str = "Failed to send message", technical_details: Optional[str] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.MESSAGE_SEND_ERROR,
            severity=ErrorSeverity.MEDIUM,
            technical_details=technical_details
        )

class MessageReceiveError(AgentError):
    """Message receiving errors"""
    def __init__(self, message: str = "Failed to receive message", technical_details: Optional[str] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.MESSAGE_RECEIVE_ERROR,
            severity=ErrorSeverity.MEDIUM,
            technical_details=technical_details
        )

class NetworkError(AgentError):
    """Network related errors"""
    def __init__(self, message: str = "Network error occurred", technical_details: Optional[str] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.NETWORK_ERROR,
            severity=ErrorSeverity.MEDIUM,
            technical_details=technical_details
        )

class ServerError(AgentError):
    """Server related errors"""
    def __init__(self, message: str = "Server error occurred", technical_details: Optional[str] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.SERVER_ERROR,
            severity=ErrorSeverity.HIGH,
            technical_details=technical_details
        )

class ValidationError(AgentError):
    """Validation errors"""
    def __init__(self, message: str = "Validation error", technical_details: Optional[str] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.VALIDATION_ERROR,
            severity=ErrorSeverity.LOW,
            technical_details=technical_details
        )

class MemoryError(AgentError):
    """Memory related errors"""
    def __init__(self, message: str = "Memory error occurred", technical_details: Optional[str] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.MEMORY_ERROR,
            severity=ErrorSeverity.MEDIUM,
            technical_details=technical_details
        )

class ProcessingError(AgentError):
    """Processing errors"""
    def __init__(self, message: str = "Processing error occurred", technical_details: Optional[str] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.PROCESSING_ERROR,
            severity=ErrorSeverity.MEDIUM,
            technical_details=technical_details
        )

def create_error_response(error: Exception) -> Dict[str, Any]:
    """Create standardized error response from any exception"""
    if isinstance(error, AgentError):
        return error.to_dict()
    
    # Convert generic exceptions to AgentError
    if "api key" in str(error).lower() or "authentication" in str(error).lower():
        return APIKeyError(str(error)).to_dict()
    elif "token" in str(error).lower() or "quota" in str(error).lower():
        return APITokensDepletedError(str(error)).to_dict()
    elif "stream" in str(error).lower():
        return StreamError(str(error)).to_dict()
    elif "network" in str(error).lower() or "connection" in str(error).lower():
        return NetworkError(str(error)).to_dict()
    elif "validation" in str(error).lower():
        return ValidationError(str(error)).to_dict()
    else:
        return AgentError(
            message=str(error),
            error_type=ErrorType.UNKNOWN_ERROR,
            severity=ErrorSeverity.MEDIUM,
            technical_details=str(error)
        ).to_dict() 