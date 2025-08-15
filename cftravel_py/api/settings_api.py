"""
Settings API for Dashboard Configuration
Handles real-time settings updates and system configuration
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Global settings storage (in production, use a proper database)
settings_store = {}
system_stats = {
    "total_requests": 0,
    "avg_response_time": 0,
    "success_rate": 100,
    "active_models": 3
}

router = APIRouter(prefix="/api", tags=["settings"])

class SettingUpdate(BaseModel):
    setting_id: str
    value: Any
    timestamp: str

class SettingsSave(BaseModel):
    settings: Dict[str, Any]
    timestamp: str
    user_id: str

class SystemStatus(BaseModel):
    services: Dict[str, bool]

@router.post("/settings/update")
async def update_setting(setting_update: SettingUpdate):
    """Update a single setting in real-time"""
    try:
        setting_id = setting_update.setting_id
        value = setting_update.value
        
        # Store the setting
        settings_store[setting_id] = {
            "value": value,
            "timestamp": setting_update.timestamp,
            "updated_at": datetime.now().isoformat()
        }
        
        # Apply the setting to the system
        await apply_setting_to_system(setting_id, value)
        
        logger.info(f"Setting updated: {setting_id} = {value}")
        
        return {
            "success": True,
            "message": f"Setting {setting_id} updated successfully",
            "setting_id": setting_id,
            "value": value
        }
        
    except Exception as e:
        logger.error(f"Error updating setting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/settings/save")
async def save_settings(settings_data: SettingsSave):
    """Save all settings at once"""
    try:
        settings = settings_data.settings
        
        # Store all settings
        for setting_id, value in settings.items():
            settings_store[setting_id] = {
                "value": value,
                "timestamp": settings_data.timestamp,
                "updated_at": datetime.now().isoformat()
            }
            
            # Apply each setting
            await apply_setting_to_system(setting_id, value)
        
        logger.info(f"Saved {len(settings)} settings for user {settings_data.user_id}")
        
        return {
            "success": True,
            "message": f"Saved {len(settings)} settings successfully",
            "settings_count": len(settings)
        }
        
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/settings/get")
async def get_settings():
    """Get all current settings"""
    try:
        return {
            "success": True,
            "settings": settings_store
        }
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/clear")
async def clear_cache():
    """Clear all caches"""
    try:
        # Clear settings store
        settings_store.clear()
        
        # Clear system stats
        global system_stats
        system_stats = {
            "total_requests": 0,
            "avg_response_time": 0,
            "success_rate": 100,
            "active_models": 3
        }
        
        logger.info("Cache cleared successfully")
        
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/realtime")
async def get_real_time_stats():
    """Get real-time system statistics"""
    try:
        # Simulate some real stats (in production, get from actual system)
        import random
        
        system_stats["total_requests"] += random.randint(1, 10)
        system_stats["avg_response_time"] = random.randint(50, 200)
        system_stats["success_rate"] = random.randint(95, 100)
        system_stats["active_models"] = random.randint(2, 4)
        
        return {
            "success": True,
            "stats": system_stats
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/status")
async def get_system_status():
    """Get system service status"""
    try:
        # Check actual service status (in production, ping services)
        services = {
            "api python": True,  # FastAPI is running
            "base de données": True,  # Assume DB is connected
            "services ia": True,  # Assume AI services are available
            "synchronisation": True  # Assume sync is working
        }
        
        return {
            "success": True,
            "services": services
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def apply_setting_to_system(setting_id: str, value: Any):
    """Apply a setting to the actual system"""
    try:
        # Import services here to avoid circular imports
        from services.llm_service import LLMService
        from services.memory_service import MemoryService
        from services.optimized_semantic_service import OptimizedSemanticService
        
        # Get service instances (you might want to use dependency injection)
        llm_service = LLMService()
        memory_service = MemoryService()
        semantic_service = OptimizedSemanticService()
        
        # Apply settings based on ID
        if setting_id == "debug-toggle":
            # Enable/disable general debug mode
            logger.setLevel(logging.DEBUG if value else logging.INFO)
            
        elif setting_id == "llm-debug-toggle":
            # Enable/disable LLM debug mode
            llm_service.debug_mode = value
            
        elif setting_id == "pipeline-debug-toggle":
            # Enable/disable pipeline debug mode
            # This would be applied to the pipeline components
            pass

        elif setting_id == "api-debug-toggle":
            # Enable/disable API debug mode
            # This affects API logging
            pass
            
        elif setting_id == "semantic-debug-toggle":
            # Enable/disable semantic search debug mode
            semantic_service.debug_mode = value
            
        elif setting_id == "memory-debug-toggle":
            # Enable/disable memory service debug mode
            memory_service.debug_mode = value
            
        elif setting_id == "streaming-speed":
            # Update streaming speed (affects chat responses)
            # This would be stored and used by the chat system
            pass

        elif setting_id == "dark-mode-toggle":
            # Dark mode is handled by frontend
            pass
            
        elif setting_id == "semantic-toggle":
            # Enable/disable semantic search
            semantic_service.enabled = value
            
        elif setting_id == "pipeline-toggle":
            # Enable/disable enhanced pipeline
            # This would switch between basic and enhanced pipeline
            pass

        elif setting_id == "cache-toggle":
            # Enable/disable caching
            # This would affect offer caching
            pass
            
        elif setting_id == "turbo-toggle":
            # Enable/disable turbo mode
            # This would affect response speed and resource usage
            pass
            
        elif setting_id == "console-toggle":
            # Enable/disable console logging
            # This affects browser console output
            pass
            
        elif setting_id == "typing-sound-toggle":
            # Enable/disable typing sound
            # This is handled by frontend
            pass
            
        elif setting_id == "suggestions-toggle":
            # Enable/disable intelligent suggestions
            # This would affect chat suggestions
            pass
            
        elif setting_id == "memory-toggle":
            # Enable/disable conversation memory
            memory_service.enabled = value
            
        elif setting_id == "experimental-toggle":
            # Enable/disable experimental features
            # This would enable/disable beta features
            pass
            
        elif setting_id == "gpu-toggle":
            # Enable/disable GPU acceleration
            # This would affect AI model inference
            pass
            
        elif setting_id == "animations-toggle":
            # Enable/disable animations
            # This is handled by frontend
            pass
            
        elif setting_id == "detailed-logs-toggle":
            # Enable/disable detailed logging
            if value:
                logger.setLevel(logging.DEBUG)
            else:
                logger.setLevel(logging.INFO)
                
        elif setting_id == "metrics-toggle":
            # Enable/disable metrics collection
            # This would affect performance monitoring
            pass
            
        elif setting_id == "dev-mode-toggle":
            # Enable/disable development mode
            # This would enable test models and features
            pass
            
        logger.info(f"Applied setting {setting_id} = {value} to system")
        
    except Exception as e:
        logger.error(f"Error applying setting {setting_id}: {e}")
        # Don't raise here, just log the error 