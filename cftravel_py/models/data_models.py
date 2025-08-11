"""
Data models for ASIA.fr Agent
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None

class OfferCard(BaseModel):
    """Structure for offer cards"""
    product_name: str
    reference: str
    destinations: List[Dict[str, str]]
    departure_city: str
    dates: List[str]
    duration: int
    offer_type: str
    description: str
    highlights: List[Dict[str, str]]
    images: List[str]
    price_url: Optional[str] = None
    ai_reasoning: Optional[str] = None
    ai_highlights: Optional[List[str]] = None
    match_score: Optional[float] = None
    why_perfect: Optional[str] = None

class DetailedProgram(BaseModel):
    """Structure for detailed program cards"""
    offer_reference: str
    product_name: str
    overview: Dict[str, Any]
    highlights: List[Dict[str, str]]
    included: List[str]
    not_included: List[str]
    itinerary: List[Dict[str, Any]]
    practical_info: Dict[str, str]
    pricing: Dict[str, str]

class PreferenceRequest(BaseModel):
    """Request model for preference updates"""
    key: str
    value: str

class UserPreferences(BaseModel):
    """User preferences model"""
    destination: Optional[str] = None
    duration: Optional[str] = None
    budget: Optional[str] = None
    travel_style: Optional[str] = None
    departure_date: Optional[str] = None
    travelers: Optional[int] = None
    special_requirements: Optional[List[str]] = None

class TravelOffer(BaseModel):
    """Base travel offer model"""
    id: str
    title: str
    description: str
    price: float
    currency: str = "EUR"
    duration: int
    destinations: List[str]
    departure_city: str
    departure_date: str
    return_date: str
    offer_type: str
    highlights: List[str]
    images: List[str]
    rating: Optional[float] = None
    reviews_count: Optional[int] = None

class ConfirmationRequest(BaseModel):
    """Request model for confirmation flow"""
    preferences: Dict[str, Any]
    conversation_id: Optional[str] = None
    action: str  # "confirm", "modify", "show_offers"

class ConfirmationResponse(BaseModel):
    """Response model for confirmation flow"""
    status: str
    message: str
    preferences: Dict[str, Any]
    offers: Optional[List[OfferCard]] = None
    needs_confirmation: bool = False
    confirmation_summary: Optional[str] = None

class ConversationState(BaseModel):
    """Model for conversation state including confirmation flow"""
    conversation_id: str
    user_preferences: Dict[str, Any]
    current_state: str  # "gathering_preferences", "confirmation", "showing_offers", "completed"
    needs_confirmation: bool = False
    confirmation_summary: Optional[str] = None
    turn_count: int = 0
    last_response_type: str = "" 