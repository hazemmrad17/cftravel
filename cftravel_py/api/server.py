"""
FastAPI server for ASIA.fr Agent
Provides REST API endpoints for the travel agent functionality
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import asyncio
import logging
from typing import Dict, Any, List
import os
from pathlib import Path

# Import services
from services.memory_service import MemoryService

# Pipeline imports will be done lazily to avoid startup issues

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="ASIA.fr Agent API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for lazy loading
_agent = None
_memory_service = None
_templates = None

def get_agent():
    """Lazy load the agent only when needed"""
    global _agent
    if _agent is None:
        try:
            logger.info("🚀 Initializing ASIA.fr Agent...")
            from pipelines.concrete_pipeline import ASIAConcreteAgent
            _agent = ASIAConcreteAgent()
            logger.info("✅ ASIA.fr Agent initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ASIA.fr Agent: {e}")
            raise HTTPException(status_code=500, detail="AI Agent not available")
    return _agent

def get_memory_service():
    """Lazy load memory service only when needed"""
    global _memory_service
    if _memory_service is None:
        logger.info("🧠 Initializing memory service...")
        _memory_service = MemoryService()
        logger.info("✅ Memory service initialized successfully")
    return _memory_service

def get_templates():
    """Lazy load templates only when needed"""
    global _templates
    if _templates is None:
        templates_dir = Path(__file__).parent.parent.parent / "templates"
        _templates = Jinja2Templates(directory=str(templates_dir))
    return _templates

@app.on_event("startup")
async def startup_event():
    """Fast startup - only initialize essential components"""
    logger.info("🚀 Starting ASIA.fr Agent initialization...")
    
    # Initialize memory service immediately (needed for clear endpoints)
    get_memory_service()
    
    logger.info("✅ Server startup complete")
        
@app.on_event("shutdown")
async def shutdown_event():     
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down ASIA.fr Agent...")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main chat interface"""
    templates = get_templates()
    return templates.TemplateResponse("chat/index.html.twig", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def read_home(request: Request):
    """Serve the home page"""
    templates = get_templates()
    return templates.TemplateResponse("chat/index.html.twig", {"request": request})

@app.get("/test")
async def test():
    """Simple test endpoint"""
    return {
        "message": "Server is running!",
        "status": "success",
        "timestamp": "2024-01-15T12:00:00Z"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_loaded": _agent is not None,
        "memory_service_loaded": _memory_service is not None
    }

@app.post("/memory/clear")
async def clear_memory(request: Request):
    """Clear conversation memory"""
    try:
        # Handle both JSON and empty body cases
        try:
            body = await request.json()
            conversation_id = body.get("conversation_id") if body else None
        except:
            conversation_id = None
        
        memory_service = get_memory_service()
        if conversation_id:
            memory_service.clear_conversation(conversation_id)
            logger.info(f"🧹 Memory service cleared for conversation: {conversation_id}")
        else:
            memory_service.clear_all_conversations()
            logger.info("🧹 Memory service cleared all conversations")
        
        # Also clear agent memory if it exists
        if _agent:
            _agent.clear_memory(conversation_id)
            logger.info("🧹 Agent memory cleared successfully")
        
        return {"message": "Memory cleared successfully"}
    except Exception as e:
        logger.error(f"❌ Error clearing memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: Request):
    """Streaming chat endpoint with optimized performance"""
    try:
        # Parse request body
        body = await request.json()
        user_message = body.get("message", "").strip()
        conversation_id = body.get("conversation_id")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        logger.info(f"📨 Received streaming message: {user_message[:50]}...")
        
        # Lazy load agent only when first message is received
        agent = get_agent()
        
        async def generate_stream():
            """Generate streaming response with optimized performance"""
            try:
                # Process the message with conversation context
                result = agent.chat(user_message, conversation_id)
                
                # Extract response text
                response_text = result.get("response", "") if isinstance(result, dict) else str(result)
                
                # Check if we need to show offers
                if isinstance(result, dict) and result.get("offers"):
                    # Convert real offers to proper format
                    offers = result["offers"]
                    converted_offers = []
                    
                    for offer in offers:
                        # Convert real offer data to offer card format
                        converted_offer = {
                            "reference": offer.get("reference", f"OFFER-{len(converted_offers)+1:03d}"),
                            "product_name": offer.get("product_name", "Travel Package"),
                            "description": offer.get("description", "Amazing travel experience"),
                            "duration": offer.get("duration", 7),
                            "departure_city": offer.get("departure_city", "Paris"),
                            "destinations": offer.get("destinations", []),
                            "highlights": offer.get("highlights", []),
                            "images": offer.get("images", ["/assets/images/placeholder-travel.jpg"]),
                            "match_score": offer.get("match_score", 0.8),
                            "price_url": offer.get("price_url", "#"),
                            "offer_type": offer.get("offer_type", "Package"),
                            "dates": offer.get("dates", "Flexible"),
                            "ai_reasoning": "Selected from our database based on your preferences",
                            "ai_highlights": ["Real offer", "Database match", "Personalized selection"],
                            "why_perfect": f"Matches your preferences for {offer.get('destinations', [{}])[0].get('country', 'travel')}"
                        }
                        converted_offers.append(converted_offer)
                    
                    yield f"data: {json.dumps({'offers': converted_offers, 'type': 'offers'})}\n\n"
                
                # Stream the response text
                words = response_text.split()
                for i, word in enumerate(words):
                    # Add space before word (except first word)
                    if i > 0:
                        yield f"data: {json.dumps({'type': 'content', 'chunk': ' ' + word})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'content', 'chunk': word})}\n\n"
                    
                    # Optimized delays for better performance
                    if i < len(words) - 1:  # Don't delay after the last word
                        # Shorter delays for faster response
                        delay = min(0.05 + (len(word) * 0.01), 0.15)  # Between 0.05 and 0.15 seconds
                        
                        # Add extra delay after punctuation for natural flow
                        if word.endswith(('.', '!', '?', ':', ';')):
                            delay += 0.1
                        
                        await asyncio.sleep(delay)
                
                # Send end marker
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                
            except Exception as e:
                logger.error(f"❌ Error in streaming: {e}")
                error_message = f"Je suis désolé, j'ai rencontré une erreur: {str(e)}"
                yield f"data: {json.dumps({'type': 'content', 'chunk': error_message})}\n\n"
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error in chat stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
static_dir = Path(__file__).parent.parent.parent / "public"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir)), name="assets")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
                