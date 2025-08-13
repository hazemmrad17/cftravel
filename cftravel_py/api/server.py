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

# Import the pipeline
from pipelines.modular_pipeline import ASIAModularPipeline
from services.memory_service import MemoryService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="ASIA.fr Agent API", version="1.0.0")

# Add CORS middleware for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ovg-iagent.cftravel.net",
        "https://iagent.cftravel.net",
        "http://ovg-iagent.cftravel.net",
        "http://iagent.cftravel.net", 
        "http://localhost:8000",
        "http://localhost:8002",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8002",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global variables for lazy loading
_pipeline = None
_memory_service = None
_templates = None

def get_pipeline():
    """Lazy load the pipeline only when needed"""
    global _pipeline
    if _pipeline is None:
        logger.info("🚀 Initializing ASIA.fr Pipeline...")
        _pipeline = ASIAModularPipeline()
        logger.info("✅ ASIA.fr Pipeline initialized successfully")
    return _pipeline

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
        
        # Also clear pipeline memory if it exists
        pipeline = get_pipeline()
        await pipeline.clear_memory(conversation_id)
        logger.info("🧹 Pipeline memory cleared successfully")
        
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
        
        # Lazy load pipeline only when first message is received
        pipeline = get_pipeline()
        
        async def generate_stream():
            """Generate streaming response with optimized performance"""
            try:
                # Process the message with conversation context
                result = await pipeline.process_user_input(user_message, conversation_id)
                
                # Extract response text
                response_text = result.get("response", "") if isinstance(result, dict) else str(result)
                
                # Check if we need to show preference confirmation
                if isinstance(result, dict) and result.get("offers"):
                    # Extract user preferences from the result
                    user_preferences = result.get("user_preferences", {})
                    offers = result["offers"]
                    
                    # Send confirmation data with preferences and offers
                    yield f"data: {json.dumps({'type': 'confirmation', 'needs_confirmation': True, 'user_preferences': user_preferences, 'offers': [offer.model_dump() if hasattr(offer, 'model_dump') else offer for offer in offers]})}\n\n"
                    
                    # Send the response text (preference summary) as content
                    words = response_text.split()
                    for i, word in enumerate(words):
                        if i > 0:
                            yield f"data: {json.dumps({'type': 'content', 'chunk': ' ' + word})}\n\n"
                        else:
                            yield f"data: {json.dumps({'type': 'content', 'chunk': word})}\n\n"
                        
                        if i < len(words) - 1:
                            delay = min(0.05 + (len(word) * 0.01), 0.15)
                            if word.endswith(('.', '!', '?', ':', ';')):
                                delay += 0.1
                            await asyncio.sleep(delay)
                    
                    yield f"data: {json.dumps({'type': 'end'})}\n\n"
                    return
                
                # Stream the response text (only if no offers)
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

@app.post("/chat")
async def chat(request: Request):
    """Regular chat endpoint (fallback for non-streaming)"""
    try:
        # Parse request body
        body = await request.json()
        user_message = body.get("message", "").strip()
        conversation_id = body.get("conversation_id")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        logger.info(f"📨 Received regular message: {user_message[:50]}...")
        
        # Get pipeline
        pipeline = get_pipeline()
        
        # Process the message
        result = await pipeline.process_user_input(user_message, conversation_id)
        
        # Extract response text
        response_text = result.get("response", "") if isinstance(result, dict) else str(result)
        
        # Prepare response
        response_data = {
            "response": response_text,
            "conversation_id": conversation_id,
            "status": "success"
        }
        
        # Add offers if present
        if isinstance(result, dict) and result.get("offers"):
            response_data["offers"] = result["offers"]
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Error in regular chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
static_dir = Path(__file__).parent.parent.parent / "public"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir)), name="assets")

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Environment-based configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    
    # Use different ports for local vs production
    if os.getenv("ENVIRONMENT", "local") == "production":
        port = int(os.getenv("API_PORT", "8000"))
    else:
        port = int(os.getenv("API_PORT", "8002"))
    
    logger.info(f"🚀 Starting ASIA.fr Agent API on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info") 