#!/usr/bin/env python3
"""
CFTravel Semantic Search API
FastAPI application for high-performance semantic search
"""

import sys
import time
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
import os

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global semantic service
semantic_service = None


class KeywordSearchService:
    """
    Lightweight keyword-based search fallback.
    Provides the same interface as the semantic service so endpoints remain unchanged.
    """

    def __init__(self):
        from data.data_processor import DataProcessor
        from pathlib import Path as _Path

        # Default to asia data file; gracefully handle absence
        default_json = _Path(__file__).parent.parent / "data" / "asia" / "data.json"
        self.data_processor = DataProcessor(str(default_json)) if default_json.exists() else DataProcessor()
        if default_json.exists():
            try:
                self.data_processor.load_offers(str(default_json))
            except Exception:
                pass

    def search(self, query: str, top_k: int = 10, threshold: float = 0.0) -> List[Dict[str, Any]]:
        results = self.data_processor._basic_text_search(query, top_k)
        if threshold:
            results = [r for r in results if r.get("similarity_score", 0.0) >= threshold]
        return results

    def search_with_context(self, query: str, context: str = "", top_k: int = 10) -> List[Dict[str, Any]]:
        enhanced_query = f"{query} {context}".strip()
        return self.search(enhanced_query, top_k)

    def get_similar_offers(self, offer_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return self.data_processor.get_similar_offers(offer_id, top_k)

    def get_search_statistics(self) -> Dict[str, Any]:
        stats = self.data_processor.get_statistics()
        stats.update({
            "model_name": "keyword",
            "indexed_offers": stats.get("total_offers", 0),
        })
        return stats

    def clear_cache(self):
        # Nothing to clear for keyword engine
        return

    def rebuild_index(self, force: bool = False):
        # Reload offers if available
        return

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app"""
    global semantic_service
    
    # Startup
    try:
        # Allow forcing keyword engine via env
        if os.getenv("SEARCH_ENGINE", "semantic").lower() == "keyword":
            logger.info("🚀 Initializing Keyword Search Service (fallback mode)...")
            semantic_service = KeywordSearchService()
            logger.info("✅ Keyword Search Service initialized successfully")
        else:
            logger.info("🚀 Initializing Optimized Semantic Search Service...")
            from services.optimized_semantic_service import OptimizedSemanticService
            semantic_service = OptimizedSemanticService()
            logger.info("✅ Semantic Search Service initialized successfully")
    except Exception as e:
        # Fallback to keyword engine instead of failing to start
        logger.error(f"❌ Failed to initialize Semantic Search Service: {e}")
        logger.info("🔄 Falling back to Keyword Search Service...")
        semantic_service = KeywordSearchService()
        logger.info("✅ Keyword Search Service initialized successfully")
    
    yield
    
    # Shutdown
    if semantic_service:
        logger.info("🔄 Shutting down Semantic Search Service...")
        semantic_service.clear_cache()

# Create FastAPI app with lifespan
app = FastAPI(
    title="CFTravel Semantic Search API",
    description="High-performance semantic search for travel offers using Sentence Transformers and FAISS",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS to allow frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10
    threshold: Optional[float] = 0.1
    context: Optional[str] = ""

class ChatMessageRequest(BaseModel):
    message: str
    top_k: Optional[int] = 10
    context: Optional[str] = ""

class SearchResponse(BaseModel):
    success: bool
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    search_time: float
    message: str

class HealthResponse(BaseModel):
    status: str
    service: str
    model: str
    offers_indexed: int
    uptime: float

class StatisticsResponse(BaseModel):
    success: bool
    statistics: Dict[str, Any]
    message: str

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if not semantic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        stats = semantic_service.get_search_statistics()
        return HealthResponse(
            status="healthy",
            service="semantic_search",
            model=stats.get('model_name', 'unknown'),
            offers_indexed=stats.get('indexed_offers', 0),
            uptime=0.0
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")

# Simple status endpoint for frontend compatibility
@app.get("/status")
async def status():
    if not semantic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    stats = semantic_service.get_search_statistics()
    return {"ok": True, "model": stats.get("model_name"), "indexed": stats.get("indexed_offers", 0)}

# Main search endpoint
@app.post("/search", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """Perform semantic search for travel offers"""
    if not semantic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        start_time = time.time()
        
        # Perform search
        if request.context:
            results = semantic_service.search_with_context(
                request.query, 
                request.context, 
                request.top_k
            )
        else:
            results = semantic_service.search(
                request.query, 
                request.top_k, 
                request.threshold
            )
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            success=True,
            query=request.query,
            results=results,
            total_results=len(results),
            search_time=search_time,
            message=f"Found {len(results)} results"
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

# Compatibility chat endpoint - maps message -> query
@app.post("/chat", response_model=SearchResponse)
async def chat(request: ChatMessageRequest):
    if not semantic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        start_time = time.time()
        if request.context:
            results = semantic_service.search_with_context(request.message, request.context, request.top_k)
        else:
            results = semantic_service.search(request.message, request.top_k)
        search_time = time.time() - start_time
        return SearchResponse(
            success=True,
            query=request.message,
            results=results,
            total_results=len(results),
            search_time=search_time,
            message=f"Found {len(results)} results"
        )
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")

# GET search endpoint for convenience
@app.get("/search", response_model=SearchResponse)
async def search_get(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(10, description="Number of results to return"),
    threshold: float = Query(0.1, description="Similarity threshold"),
    context: str = Query("", description="Additional context for search")
):
    """GET endpoint for semantic search (convenience)"""
    if not semantic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        start_time = time.time()
        
        # Perform search
        if context:
            results = semantic_service.search_with_context(query, context, top_k)
        else:
            results = semantic_service.search(query, top_k, threshold)
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            success=True,
            query=query,
            results=results,
            total_results=len(results),
            search_time=search_time,
            message=f"Found {len(results)} results"
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

# Similar offers endpoint
@app.get("/similar/{offer_id}", response_model=SearchResponse)
async def find_similar_offers(
    offer_id: str,
    top_k: int = Query(5, description="Number of similar offers to return")
):
    """Find offers similar to a specific offer"""
    if not semantic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        start_time = time.time()
        
        # Find similar offers
        results = semantic_service.get_similar_offers(offer_id, top_k)
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            success=True,
            query=f"similar to {offer_id}",
            results=results,
            total_results=len(results),
            search_time=search_time,
            message=f"Found {len(results)} similar offers"
        )
        
    except Exception as e:
        logger.error(f"Similar offers search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Similar offers search failed: {e}")

# Statistics endpoint
@app.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """Get service statistics and performance metrics"""
    if not semantic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        stats = semantic_service.get_search_statistics()
        
        return StatisticsResponse(
            success=True,
            statistics=stats,
            message="Statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {e}")

# Rebuild index endpoint
@app.post("/rebuild-index")
async def rebuild_index(force: bool = Query(False, description="Force rebuild even if index exists")):
    """Rebuild the semantic search index"""
    if not semantic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info("🔨 Rebuilding semantic search index...")
        semantic_service.rebuild_index(force=force)
        
        return {
            "success": True,
            "message": "Index rebuilt successfully",
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Failed to rebuild index: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rebuild index: {e}")

# Clear cache endpoint
@app.post("/clear-cache")
async def clear_cache():
    """Clear performance cache"""
    if not semantic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        semantic_service.clear_cache()
        
        return {
            "success": True,
            "message": "Cache cleared successfully",
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {e}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "CFTravel Semantic Search API",
        "version": "1.0.0",
        "description": "High-performance semantic search for travel offers",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "search": "/search",
            "chat": "/chat",
            "similar_offers": "/similar/{offer_id}",
            "statistics": "/statistics",
            "rebuild_index": "/rebuild-index",
            "clear_cache": "/clear-cache"
        },
        "model": "Sentence Transformers (all-MiniLM-L6-v2)",
        "vector_store": "FAISS"
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting CFTravel Semantic Search API...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    ) 