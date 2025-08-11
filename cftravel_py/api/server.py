"""
FastAPI server for ASIA.fr Agent
Provides REST API endpoints for the travel agent functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
import os
import sys
import logging
import json
import asyncio
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import from new modular structure
from core.config import config
from core.constants import API_TITLE, API_DESCRIPTION, API_VERSION
from models.data_models import ChatRequest, OfferCard, DetailedProgram, PreferenceRequest, ConfirmationRequest
from models.response_models import ChatResponse, AgentStatusResponse, HealthResponse, MemoryResponse, WelcomeResponse, ConfirmationFlowResponse
# from pipelines.concrete_pipeline import ASIAConcreteAgent  # Moved to lazy import in startup
from services.data_service import DataService
from services.memory_service import MemoryService
from services.offer_service import OfferService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=".*",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
agent = None
data_service = None
memory_service = None
offer_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize the ASIA.fr Agent on startup"""
    global agent, data_service, memory_service, offer_service
    
    try:
        logger.info("🚀 Starting ASIA.fr Agent initialization...")
        
        # Initialize services
        data_service = DataService()
        memory_service = MemoryService()
        offer_service = OfferService(data_service)
        
        # Initialize agent with fallback mode
        try:
            # Lazy import to avoid crashing the server if pipeline has issues
            try:
                from pipelines.concrete_pipeline import ASIAConcreteAgent  # type: ignore
            except Exception as import_err:
                logger.warning(f"⚠️ Failed to import ASIAConcreteAgent: {import_err}")
                raise
            agent = ASIAConcreteAgent()
            logger.info("✅ ASIA.fr Agent initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize ASIA.fr Agent with LLM: {e}")
            logger.info("🔄 Starting in fallback mode (no AI functionality)")
            agent = None
        
        logger.info("✅ Server startup complete")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize ASIA.fr Agent: {e}")
        # Don't raise the exception - let the server start in fallback mode
        logger.info("🔄 Server starting in fallback mode")
        agent = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ASIA.fr Agent API",
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
        # Fallback response when AI is not available
        fallback_response = "Hello! I'm ASIA.fr Agent, your travel specialist. I'm currently in maintenance mode, but I can still help you explore our travel offers. Would you like to see some of our best destinations?"
        
        # Try to get some basic offers from the data service
        offers = None
        if offer_service:
            try:
                all_offers = data_service.get_offers()
                if all_offers:
                    # Create basic offer cards from the first 3 offers
                    offer_cards = []
                    for offer in all_offers[:3]:
                        offer_card = OfferCard(
                            product_name=offer.get("product_name", "Travel Package"),
                            reference=offer.get("reference", "OFFER001"),
                            destinations=offer.get("destinations", []),
                            departure_city=offer.get("departure_city", "Paris"),
                            dates=offer.get("dates", "Flexible"),
                            duration=offer.get("duration", "7 days"),
                            offer_type=offer.get("offer_type", "Package"),
                            description=offer.get("description", "Amazing travel experience"),
                            highlights=offer.get("highlights", []),
                            images=offer.get("images", []),
                            price_url=f"https://example.com/offer/{offer.get('reference', 'OFFER001')}",
                            ai_reasoning="Available in our catalog",
                            ai_highlights=["Popular destination", "Great value"],
                            match_score=0.8,
                            why_perfect="Featured offer"
                        )
                        offer_cards.append(offer_card)
                    offers = offer_cards
            except Exception as e:
                logger.warning(f"⚠️ Could not load offers in fallback mode: {e}")
        
        return ChatResponse(
            response=fallback_response,
            conversation_id=request.conversation_id,
            status="success",
            offers=offers
        )
    
    try:
        logger.info(f"📨 Received message: {request.message[:100]}...")
        
        # Add message to memory
        if memory_service and request.conversation_id:
            memory_service.add_message(request.conversation_id, "user", request.message)
        
        # Process the message through the agent
        response_data = agent.chat(request.message)
        
        # Handle the new response format
        if isinstance(response_data, dict):
            response = response_data.get("response", "")
            offers = response_data.get("offers")
            detailed_program = response_data.get("detailed_program")
        else:
            # Fallback for old format
            response = response_data
            offers = None
            detailed_program = None
        
        logger.info(f"🤖 Agent response: {response[:100]}...")
        
        # Add agent response to memory
        if memory_service and request.conversation_id:
            memory_service.add_message(request.conversation_id, "assistant", response)
        
        # Check for detailed program requests using offer service
        if detailed_program is None and offer_service:
            if "détails" in request.message.lower() or "programme" in request.message.lower():
                # Extract offer reference from message
                import re
                offer_ref_match = re.search(r'offre\s+(\w+)', request.message, re.IGNORECASE)
                if offer_ref_match:
                    offer_ref = offer_ref_match.group(1)
                    detailed_program = offer_service.get_offer_details(offer_ref)
                    logger.info(f"📋 Retrieved detailed program for offer {offer_ref}")
        
        # Use offers from the response data if available
        if offers:
            # Convert to OfferCard format if needed
            if isinstance(offers, list) and len(offers) > 0 and not isinstance(offers[0], OfferCard):
                offer_cards = []
                for offer_data in offers:
                    offer_card = OfferCard(
                        product_name=offer_data["product_name"],
                        reference=offer_data["reference"],
                        destinations=offer_data["destinations"],
                        departure_city=offer_data["departure_city"],
                        dates=offer_data["dates"],
                        duration=offer_data["duration"],
                        offer_type=offer_data["offer_type"],
                        description=offer_data["description"],
                        highlights=offer_data["highlights"],
                        images=offer_data["images"],
                        price_url=offer_data["price_url"],
                        ai_reasoning=offer_data.get("ai_reasoning", ""),
                        ai_highlights=offer_data.get("ai_highlights", []),
                        match_score=offer_data.get("match_score", 0.0),
                        why_perfect=offer_data.get("why_perfect", "")
                    )
                    offer_cards.append(offer_card)
                offers = offer_cards
                logger.info(f"📋 Converted {len(offers)} offers to OfferCard format")
        
        return ChatResponse(
            response=response,
            conversation_id=request.conversation_id,
            status="success",
            offers=offers,
            detailed_program=detailed_program
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
        # Fallback response when AI is not available
        fallback_response = "Hello! I'm ASIA.fr Agent, your travel specialist. I'm currently in maintenance mode, but I can still help you explore our travel offers. Would you like to see some of our best destinations?"
        
        async def generate_fallback():
            # Stream the fallback response
            for char in fallback_response:
                yield f"data: {json.dumps({'chunk': char, 'type': 'content'})}\n\n"
                await asyncio.sleep(0.05)  # Simulate typing
            
            # Try to get some basic offers
            if offer_service:
                try:
                    all_offers = data_service.get_offers()
                    if all_offers:
                        offer_cards = []
                        for offer in all_offers[:3]:
                            offer_card = OfferCard(
                                product_name=offer.get("product_name", "Travel Package"),
                                reference=offer.get("reference", "OFFER001"),
                                destinations=offer.get("destinations", []),
                                departure_city=offer.get("departure_city", "Paris"),
                                dates=offer.get("dates", "Flexible"),
                                duration=offer.get("duration", "7 days"),
                                offer_type=offer.get("offer_type", "Package"),
                                description=offer.get("description", "Amazing travel experience"),
                                highlights=offer.get("highlights", []),
                                images=offer.get("images", []),
                                price_url=f"https://example.com/offer/{offer.get('reference', 'OFFER001')}",
                                ai_reasoning="Available in our catalog",
                                ai_highlights=["Popular destination", "Great value"],
                                match_score=0.8,
                                why_perfect="Featured offer"
                            )
                            offer_cards.append(offer_card)
                        
                        yield f"data: {json.dumps({'offers': [offer.dict() for offer in offer_cards], 'type': 'offers'})}\n\n"
                except Exception as e:
                    logger.warning(f"⚠️ Could not load offers in fallback mode: {e}")
            
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
        
        return StreamingResponse(generate_fallback(), media_type="text/plain")
    
    async def generate_response():
        try:
            logger.info(f"📨 Received streaming message: {request.message[:100]}...")
            
            # Get streaming response from agent
            response_stream = agent.chat_stream(request.message)
            
            full_response = ""
            for chunk in response_stream:
                if chunk:
                    full_response += chunk
                    # Send chunk as Server-Sent Event
                    yield f"data: {json.dumps({'chunk': chunk, 'type': 'content'})}\n\n"
            
            # After streaming is complete, check if we should return structured offers
            try:
                # Use the regular chat method to get structured data
                response_data = agent.chat(request.message)
                
                # Send confirmation request if needed
                if isinstance(response_data, dict) and response_data.get("needs_confirmation"):
                    confirmation_data = {
                        "type": "confirmation",
                        "needs_confirmation": True,
                        "confirmation_summary": response_data.get("confirmation_summary"),
                        "preferences": response_data.get("conversation_state", {}).get("user_preferences", {})
                    }
                    yield f"data: {json.dumps(confirmation_data)}\n\n"
                    logger.info("📋 Sent confirmation request via streaming")
                
                # Send offers if available
                elif isinstance(response_data, dict) and "offers" in response_data and response_data["offers"]:
                    offers = response_data["offers"]
                    # Convert to OfferCard format if needed
                    if isinstance(offers, list) and len(offers) > 0 and not isinstance(offers[0], OfferCard):
                        offer_cards = []
                        for offer_data in offers:
                            offer_card = OfferCard(
                                product_name=offer_data["product_name"],
                                reference=offer_data["reference"],
                                destinations=offer_data["destinations"],
                                departure_city=offer_data["departure_city"],
                                dates=offer_data["dates"],
                                duration=offer_data["duration"],
                                offer_type=offer_data["offer_type"],
                                description=offer_data["description"],
                                highlights=offer_data["highlights"],
                                images=offer_data["images"],
                                price_url=offer_data["price_url"],
                                ai_reasoning=offer_data.get("ai_reasoning", ""),
                                ai_highlights=offer_data.get("ai_highlights", []),
                                match_score=offer_data.get("match_score", 0.0),
                                why_perfect=offer_data.get("why_perfect", "")
                            )
                            offer_cards.append(offer_card)
                        offers = offer_cards
                    
                    # Send offers as a special event
                    yield f"data: {json.dumps({'offers': [offer.dict() for offer in offers], 'type': 'offers'})}\n\n"
                    logger.info(f"📋 Sent {len(offers)} offers via streaming")
                
                # Send detailed program if available
                if isinstance(response_data, dict) and "detailed_program" in response_data and response_data["detailed_program"]:
                    detailed_program = response_data["detailed_program"]
                    yield f"data: {json.dumps({'detailed_program': detailed_program.dict() if hasattr(detailed_program, 'dict') else detailed_program, 'type': 'detailed_program'})}\n\n"
                    logger.info("📋 Sent detailed program via streaming")
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not get structured data: {e}")
            
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

@app.options("/chat/stream")
async def options_chat_stream():
    return Response(status_code=200)

@app.options("/memory/clear")
async def options_memory_clear():
    return Response(status_code=200)

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
    try:
        if memory_service:
            # For now, return empty preferences - in a real app, you'd get user-specific preferences
            preferences = {}
            return {"preferences": preferences, "status": "success"}
        else:
            return {"preferences": {}, "status": "error", "message": "Memory system not available"}
    except Exception as e:
        logger.error(f"❌ Error getting preferences: {e}")
        return {"preferences": {}, "status": "error", "message": str(e)}

@app.post("/preferences")
async def update_preference(request: PreferenceRequest):
    """Update a specific preference"""
    try:
        if memory_service:
            # In a real app, you'd store preferences per user/conversation
            # For now, we'll just log the preference update
            logger.info(f"⚙️ Preference updated: {request.key} = {request.value}")
            return {"status": "success", "message": f"Preference '{request.key}' updated"}
        else:
            return {"status": "error", "message": "Memory system not available"}
    except Exception as e:
        logger.error(f"❌ Error updating preference: {e}")
        return {"status": "error", "message": str(e)}

@app.delete("/preferences")
async def clear_preferences():
    """Clear all user preferences"""
    try:
        if memory_service:
            # In a real app, you'd clear user-specific preferences
            logger.info("🗑️ All preferences cleared")
            return {"status": "success", "message": "All preferences cleared"}
        else:
            return {"status": "error", "message": "Memory system not available"}
    except Exception as e:
        logger.error(f"❌ Error clearing preferences: {e}")
        return {"status": "error", "message": str(e)}

@app.delete("/memory")
async def clear_memory():
    """Clear conversation memory"""
    try:
        if memory_service:
            memory_service.clear_all_conversations()
            logger.info("🧹 Memory cleared successfully")
            return MemoryResponse(
                status="success", 
                message="Memory cleared successfully"
            )
        else:
            return MemoryResponse(
                status="error", 
                message="Memory system not available"
            )
    except Exception as e:
        logger.error(f"❌ Error clearing memory: {e}")
        return MemoryResponse(
            status="error", 
            message=str(e)
        )

@app.post("/memory/clear")
async def clear_memory_post():
    """Clear conversation memory (POST method for easier frontend integration)"""
    try:
        if memory_service:
            memory_service.clear_all_conversations()
            logger.info("🧹 Memory cleared successfully")
            return MemoryResponse(
                status="success", 
                message="Memory cleared successfully"
            )
        else:
            return MemoryResponse(
                status="error", 
                message="Memory system not available"
            )
    except Exception as e:
        logger.error(f"❌ Error clearing memory: {e}")
        return MemoryResponse(
            status="error", 
            message=str(e)
        )

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
    try:
        if offer_service and data_service:
            # Get all offers from data service
            all_offers = data_service.get_offers()
            
            # Apply pagination
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paginated_offers = all_offers[start_idx:end_idx]
            
            # Convert to OfferCard format
            offer_cards = []
            for offer in paginated_offers:
                offer_card = offer_service._convert_to_offer_card(offer, 0.8)
                offer_cards.append(offer_card)
            
            return {
                "offers": [offer.dict() for offer in offer_cards],
                "total": len(all_offers),
                "page": page,
                "limit": limit,
                "status": "success"
            }
        else:
            return {
                "offers": [],
                "total": 0,
                "page": page,
                "limit": limit,
                "status": "error",
                "message": "Offer service not available"
            }
    except Exception as e:
        logger.error(f"❌ Error getting offers: {e}")
        return {
            "offers": [],
            "total": 0,
            "page": page,
            "limit": limit,
            "status": "error",
            "message": str(e)
        }

@app.post("/confirmation", response_model=ConfirmationFlowResponse)
async def handle_confirmation(request: ConfirmationRequest):
    """Handle confirmation flow for travel preferences"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        logger.info(f"📋 Confirmation request: {request.action}")
        
        if request.action == "confirm":
            # User confirmed preferences, show offers
            logger.info(f"📋 Confirming preferences: {request.preferences}")
            logger.info(f"📋 Offer service available: {offer_service is not None}")
            
            offers = []
            if offer_service:
                try:
                    offers = offer_service.match_offers(request.preferences, max_offers=3)
                    logger.info(f"📋 Found {len(offers)} matching offers")
                except Exception as e:
                    logger.error(f"❌ Error matching offers: {e}")
                    raise
            else:
                logger.warning("⚠️ Offer service not available")
            
            return ConfirmationFlowResponse(
                status="success",
                message="Perfect! Here are your personalized travel offers.",
                needs_confirmation=False,
                preferences=request.preferences,
                offers=offers,
                conversation_state={
                    "conversation_id": request.conversation_id,
                    "user_preferences": request.preferences,
                    "current_state": "showing_offers",
                    "needs_confirmation": False,
                    "confirmation_summary": None,
                    "turn_count": 0,
                    "last_response_type": "offer_display"
                }
            )
        
        elif request.action == "modify":
            # User wants to modify preferences
            return ConfirmationFlowResponse(
                status="success",
                message="No problem! Let's adjust your preferences. What would you like to change?",
                needs_confirmation=False,
                preferences=request.preferences,
                conversation_state={
                    "conversation_id": request.conversation_id,
                    "user_preferences": request.preferences,
                    "current_state": "gathering_preferences",
                    "needs_confirmation": False,
                    "confirmation_summary": None,
                    "turn_count": 0,
                    "last_response_type": "preference_gathering"
                }
            )
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
            
    except Exception as e:
        logger.error(f"❌ Error handling confirmation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to handle confirmation: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 