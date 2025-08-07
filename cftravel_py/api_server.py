"""
FastAPI server for Layla Travel Agent
Provides REST API endpoints for the travel agent functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import sys
import logging
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from concrete_pipeline import LaylaConcreteAgent
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Layla Travel Agent API",
    description="REST API for Layla Travel Agent - Hybrid LLM + Vector Search",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent = None

class ChatRequest(BaseModel):
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

class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None
    status: str = "success"
    error: Optional[str] = None
    offers: Optional[List[OfferCard]] = None

class AgentStatusResponse(BaseModel):
    status: str
    model_info: Dict[str, Any]
    data_info: Dict[str, Any]

class PreferenceRequest(BaseModel):
    key: str
    value: str

@app.on_event("startup")
async def startup_event():
    """Initialize the travel agent on startup"""
    global agent
    try:
        logger.info("🚀 Initializing Layla Travel Agent...")
        agent = LaylaConcreteAgent()
        logger.info("✅ Layla Travel Agent initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Layla Travel Agent API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_loaded": agent is not None
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        logger.info(f"📨 Received message: {request.message[:100]}...")
        
        # Process the message through the agent
        response = agent.chat(request.message)
        
        logger.info(f"🤖 Agent response: {response[:100]}...")
        
        # Check if this is an offer request and get offers
        offers = None
        if agent._is_offer_request(request.message):
            try:
                preferences = agent.get_preferences()
                filtered_offers = agent._filter_offers(preferences, max_offers=5)
                offers = []
                for offer in filtered_offers:
                    offer_card = OfferCard(
                        product_name=offer.product_name,
                        reference=offer.reference,
                        destinations=offer.destinations,
                        departure_city=offer.departure_city,
                        dates=offer.dates,
                        duration=offer.duration,
                        offer_type=offer.offer_type,
                        description=offer.description,
                        highlights=offer.highlights,
                        images=offer.images,
                        price_url=f"https://example.com/offer/{offer.reference}"  # Placeholder URL
                    )
                    offers.append(offer_card)
                logger.info(f"🎯 Found {len(offers)} matching offers")
            except Exception as e:
                logger.error(f"❌ Error getting offers: {e}")
        
        return ChatResponse(
            response=response,
            conversation_id=request.conversation_id,
            status="success",
            offers=offers
        )
    
    except Exception as e:
        logger.error(f"❌ Error processing chat: {e}")
        return ChatResponse(
            response="Désolé, je rencontre des difficultés techniques. Veuillez réessayer.",
            conversation_id=request.conversation_id,
            status="error",
            error=str(e)
        )

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    async def generate_response():
        try:
            logger.info(f"📨 Received streaming message: {request.message[:100]}...")
            
            # Get streaming response from agent
            response_stream = agent.chat_stream(request.message)
            
            for chunk in response_stream:
                if chunk:
                    # Send chunk as Server-Sent Event
                    yield f"data: {json.dumps({'chunk': chunk, 'type': 'content'})}\n\n"
            
            # Send end marker
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
            
        except Exception as e:
            logger.error(f"❌ Error in streaming chat: {e}")
            yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

@app.get("/status", response_model=AgentStatusResponse)
async def get_status():
    """Get agent status and configuration"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        status = agent.get_status()
        return AgentStatusResponse(
            status="running",
            model_info=status.get("models", {}),
            data_info=status.get("data", {})
        )
    except Exception as e:
        logger.error(f"❌ Error getting status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent status")

@app.get("/preferences")
async def get_preferences():
    """Get current user preferences"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        preferences = agent.get_preferences()
        return {"preferences": preferences}
    except Exception as e:
        logger.error(f"❌ Error getting preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to get preferences")

@app.post("/preferences")
async def update_preference(request: PreferenceRequest):
    """Update a specific preference"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        agent.modify_preference(request.key, request.value)
        return {"status": "success", "message": f"Preference '{request.key}' updated"}
    except Exception as e:
        logger.error(f"❌ Error updating preference: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preference")

@app.delete("/preferences")
async def clear_preferences():
    """Clear all user preferences"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        agent.clear_preferences()
        return {"status": "success", "message": "All preferences cleared"}
    except Exception as e:
        logger.error(f"❌ Error clearing preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear preferences")

@app.delete("/memory")
async def clear_memory():
    """Clear conversation memory"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        agent.clear_memory()
        return {"status": "success", "message": "Conversation memory cleared"}
    except Exception as e:
        logger.error(f"❌ Error clearing memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear memory")

@app.post("/memory/clear")
async def clear_memory_post():
    """Clear conversation memory (POST method for easier frontend integration)"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        agent.clear_memory()
        return {"status": "success", "message": "Conversation memory cleared"}
    except Exception as e:
        logger.error(f"❌ Error clearing memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear memory")

@app.get("/welcome")
async def get_welcome_message():
    """Get a welcome message from the agent"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        welcome_message = agent.get_welcome_message()
        return {"message": welcome_message}
    except Exception as e:
        logger.error(f"❌ Error getting welcome message: {e}")
        raise HTTPException(status_code=500, detail="Failed to get welcome message")

@app.get("/offers")
async def get_offers(limit: int = 10, page: int = 1):
    """Get available travel offers"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # This would need to be implemented in the agent
        # For now, return a placeholder
        return {
            "offers": [],
            "total": 0,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"❌ Error getting offers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get offers")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 