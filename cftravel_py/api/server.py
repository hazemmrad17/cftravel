"""
FastAPI server for ASIA.fr Agent
Provides REST API endpoints for the travel agent functionality
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import asyncio
import logging
import time
from typing import Dict, Any, List
import os
from pathlib import Path
from core.exceptions import create_error_response, AgentError, APIKeyError, APITokensDepletedError, StreamError, NetworkError, ServerError, ValidationError

# Import the pipeline
from pipelines.modular_pipeline import ASIAModularPipeline
from services.memory_service import MemoryService

from services.backup_model_service import backup_model_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="ASIA.fr Agent API", version="1.0.0")

# Import unified configuration
from core.unified_config import unified_config

# Add CORS middleware using unified configuration
try:
    cors_config = unified_config.get_cors()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config['allowed_origins'],
        allow_credentials=cors_config['allow_credentials'],
        allow_methods=cors_config['allowed_methods'],
        allow_headers=cors_config['allowed_headers'],
    )
except Exception as e:
    logger.warning(f"⚠️ Using fallback CORS configuration: {e}")
    # Fallback CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            'https://ovg-iagent.cftravel.net',
            'https://iagent.cftravel.net',
            'http://ovg-iagent.cftravel.net',
            'http://iagent.cftravel.net',
            'http://localhost:8000',
            'http://localhost:8001',
            'http://localhost:8002',
            'http://localhost:3000',
            'http://127.0.0.1:8000',
            'http://127.0.0.1:8001',
            'http://127.0.0.1:8002',
            'http://127.0.0.1:3000'
        ],
        allow_credentials=True,
        allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        allow_headers=['*'],
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

@app.post("/chat/memory/clear")
async def clear_memory_chat(request: Request):
    """Clear conversation memory - chat endpoint"""
    return await clear_memory(request)

@app.post("/confirmation")
async def handle_confirmation(request: Request):
    """Handle preference confirmation and show offers"""
    try:
        body = await request.json()
        preferences = body.get("preferences", {})
        conversation_id = body.get("conversation_id")
        action = body.get("action", "confirm")  # "confirm" or "modify"
        
        logger.info(f"🎯 Handling confirmation: {action}")
        logger.info(f"🎯 Preferences: {preferences}")
        
        # Get pipeline
        pipeline = get_pipeline()
        
        if action == "confirm":
            # User confirmed preferences - generate offers
            user_message = "Je confirme mes préférences, montrez-moi les offres"
            logger.info(f"🎯 Processing confirmation with message: {user_message}")
            result = await pipeline.process_user_input(user_message, conversation_id)
            
            logger.info(f"🎯 Pipeline result: {result}")
            
            # Extract offers and response
            offers = result.get("offers", [])
            response_text = result.get("response", "Voici vos offres personnalisées !")
            
            logger.info(f"🎯 Extracted offers: {offers}")
            logger.info(f"🎯 Response text: {response_text}")
            
            response_data = {
                "status": "success",
                "message": response_text,
                "offers": offers
            }
            
            logger.info(f"🎯 Returning response: {response_data}")
            return response_data
            
        elif action == "modify":
            # User wants to modify preferences - generate new summary and search query
            user_message = "Je veux modifier mes préférences"
            result = await pipeline.process_user_input(user_message, conversation_id)
            
            response_text = result.get("response", "Dites-moi ce que vous souhaitez modifier")
            
            return {
                "status": "success",
                "message": response_text,
                "offers": []  # No offers on modify - wait for new preferences
            }
        
    except Exception as e:
        logger.error(f"❌ Error handling confirmation: {e}")
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
            error_response = create_error_response(
                ValidationError("Message is required")
            )
            return JSONResponse(status_code=400, content=error_response)
        
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
                
                # No confirmation dialog - just stream the response text
                
                # Check if we need to show offers (only after confirmation)
                if isinstance(result, dict) and result.get("offers"):
                    # Send offers data first
                    offers = result["offers"]
                    yield f"data: {json.dumps({'type': 'offers', 'offers': [offer.model_dump() if hasattr(offer, 'model_dump') else offer for offer in offers]})}\n\n"
                    
                    # For offers, send a short intro message only
                    intro_message = "Voici les offres qui correspondent parfaitement à vos critères :"
                    yield f"data: {json.dumps({'type': 'content', 'chunk': intro_message})}\n\n"
                    
                    # Send end marker immediately after offers
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
                error_response = create_error_response(e)
                error_chunk = {
                    "type": "error",
                    "error_data": error_response
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
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
        error_response = create_error_response(e)
        return JSONResponse(status_code=500, content=error_response)

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

@app.get("/status")
async def get_status():
    """Get agent status"""
    return {
        "status": "online",
        "agent": "Layla",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

@app.get("/config")
async def config():
    """Get API configuration"""
    return {
        "api_version": "1.0.0",
        "environment": "development",
        "features": {
            "streaming": True,
            "error_handling": True,
            "memory_service": True
        }
    }

@app.get("/models")
async def get_models():
    """Get model configuration and status"""
    try:
        ai_config = unified_config.get_ai()
        models = ai_config.get('models', {})
        switches = ai_config.get('model_switches', {})
        available_models = ai_config.get('available_models', {})
        
        return {
            "status": "success",
            "models": models,
            "switches": switches,
            "available_models": available_models,
            "provider": ai_config.get('provider', 'groq')
        }
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/switches")
async def get_model_switches():
    """Get current state of all model switches"""
    try:
        ai_config = unified_config.get_ai()
        switches = ai_config.get('model_switches', {})
        
        return {
            "status": "success",
            "switches": switches
        }
    except Exception as e:
        logger.error(f"Error getting model switches: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/validation")
async def validate_models():
    """Validate current model configuration"""
    try:
        ai_config = unified_config.get_ai()
        api_key = ai_config.get('api_key')
        
        validation = {
            "api_key_configured": bool(api_key),
            "provider": ai_config.get('provider', 'groq'),
            "models_configured": len(ai_config.get('models', {})) > 0,
            "switches_configured": len(ai_config.get('model_switches', {})) > 0
        }
        
        return {
            "status": "success",
            "validation": validation
        }
    except Exception as e:
        logger.error(f"Error validating models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# BACKUP MODEL ENDPOINTS
# =============================================================================

@app.get("/models/backup/status")
async def get_backup_model_status():
    """Get status of all backup models"""
    try:
        status = backup_model_service.get_all_model_status()
        return {
            "status": "success",
            "backup_models": status
        }
    except Exception as e:
        logger.error(f"Error getting backup model status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/backup/test")
async def test_backup_models():
    """Test all backup models and return their status"""
    try:
        results = await backup_model_service.test_all_models()
        return {
            "status": "success",
            "test_results": results
        }
    except Exception as e:
        logger.error(f"Error testing backup models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/backup/{model_type}")
async def get_backup_models_for_type(model_type: str):
    """Get backup models for a specific type"""
    try:
        primary_config = backup_model_service.get_model_config(model_type)
        backup_models = backup_model_service.get_backup_models(model_type)
        
        return {
            "status": "success",
            "model_type": model_type,
            "primary": primary_config,
            "backups": backup_models
        }
    except Exception as e:
        logger.error(f"Error getting backup models for {model_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/backup/test/{model_type}")
async def test_specific_model_type(model_type: str):
    """Test a specific model type with all its backup models"""
    try:
        primary_config = backup_model_service.get_model_config(model_type)
        backup_models = backup_model_service.get_backup_models(model_type)
        
        results = {
            "model_type": model_type,
            "primary": await backup_model_service.test_model(primary_config),
            "backups": {}
        }
        
        for backup in backup_models:
            results["backups"][f"backup_{backup.get('priority', 'unknown')}"] = await backup_model_service.test_model(backup)
        
        return {
            "status": "success",
            "test_results": results
        }
    except Exception as e:
        logger.error(f"Error testing model type {model_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
static_dir = Path(__file__).parent.parent.parent / "public"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir)), name="assets")

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get server configuration from unified config
    server_config = unified_config.get_server('backend')
    host = server_config.get('host', '0.0.0.0')
    port = server_config.get('port', 8000)
    
    # Log configuration on startup
    unified_config.log_config()
    
    logger.info(f"🚀 Starting ASIA.fr Agent API on {host}:{port}")
    logger.info(f"🔧 Environment: {unified_config.get_environment()}")
    logger.info(f"🔧 Debug Mode: {unified_config.is_debug()}")
    
    uvicorn.run(app, host=host, port=port, log_level="info") 