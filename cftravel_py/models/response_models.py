"""
Response models for ASIA.fr Agent API
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from .data_models import OfferCard, DetailedProgram, ConfirmationResponse, ConversationState

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    conversation_id: Optional[str] = None
    status: str = "success"
    error: Optional[str] = None
    offers: Optional[List[OfferCard]] = None
    detailed_program: Optional[DetailedProgram] = None
    needs_confirmation: bool = False
    confirmation_summary: Optional[str] = None
    conversation_state: Optional[ConversationState] = None

class AgentStatusResponse(BaseModel):
    """Response model for status endpoint"""
    status: str
    model_info: Dict[str, Any]
    data_info: Dict[str, Any]

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    timestamp: str
    version: str

class PreferencesResponse(BaseModel):
    """Response model for preferences"""
    preferences: Dict[str, Any]
    status: str = "success"

class MemoryResponse(BaseModel):
    """Response model for memory operations"""
    status: str
    message: str
    conversation_id: Optional[str] = None

class WelcomeResponse(BaseModel):
    """Response model for welcome message"""
    message: str
    status: str = "success"

class OffersResponse(BaseModel):
    """Response model for offers endpoint"""
    offers: List[OfferCard]
    total: int
    page: int
    limit: int
    status: str = "success"

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    message: str
    status: str = "error"
    timestamp: str

class ConfirmationFlowResponse(BaseModel):
    """Response model for confirmation flow endpoints"""
    status: str
    message: str
    needs_confirmation: bool = False
    confirmation_summary: Optional[str] = None
    preferences: Dict[str, Any]
    offers: Optional[List[OfferCard]] = None
    conversation_state: Optional[ConversationState] = None 