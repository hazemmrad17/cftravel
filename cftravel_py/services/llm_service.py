"""
LLM Service with Backup Model Support
====================================
Enhanced LLM service that uses priority-based backup models with automatic fallback.
"""

import logging
from typing import Dict, List, Optional, Any, Generator
from groq import Groq, GroqError
from core.unified_config import unified_config
from services.backup_model_service import backup_model_service

logger = logging.getLogger(__name__)

class LLMService:
    """
    Enhanced LLM service with backup model support
    """
    
    def __init__(self):
        self.config = unified_config.get_ai()
        api_key = self.config.get('api_key')
        if not api_key:
            logger.warning("⚠️ No API key found in LLMService. Some features may not work properly.")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
        self.models = self.config.get('models', {})
        
        # Log model configuration on startup
        self._log_model_configuration()
    
    def _log_model_configuration(self):
        """Log the current model configuration"""
        logger.info("🤖 LLM Service Configuration:")
        
        for model_type in ['reasoning', 'generation', 'matcher', 'extractor']:
            model_config = self.models.get(model_type, {})
            primary_name = model_config.get('name', 'N/A')
            backup_count = len(model_config.get('backup_models', []))
            
            logger.info(f"  {model_type.upper()}:")
            logger.info(f"    Primary: {primary_name}")
            logger.info(f"    Backups: {backup_count} models")
            
            # Log backup models
            for backup in model_config.get('backup_models', []):
                logger.info(f"      Backup {backup.get('priority')}: {backup.get('name')}")
    
    async def create_completion(
        self,
        model_type: str,
        messages: List[Dict[str, str]],
        stream: bool = True,
        **kwargs
    ) -> Any:
        """
        Create completion with automatic backup model fallback
        
        Args:
            model_type: Type of model (reasoning, generation, matcher, extractor)
            messages: List of message dictionaries
            stream: Whether to stream the response
            **kwargs: Additional parameters
        
        Returns:
            Completion response or generator
        """
        try:
            return await backup_model_service.create_completion_with_fallback(
                model_type=model_type,
                messages=messages,
                stream=stream,
                **kwargs
            )
        except Exception as e:
            logger.error(f"❌ All models failed for {model_type}: {e}")
            raise
    
    async def create_reasoning_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True,
        **kwargs
    ) -> Any:
        """Create completion using reasoning model with backup fallback"""
        return await self.create_completion('reasoning', messages, stream, **kwargs)
    
    async def create_generation_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True,
        **kwargs
    ) -> Any:
        """Create completion using generation model with backup fallback"""
        return await self.create_completion('generation', messages, stream, **kwargs)
    
    async def create_matcher_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True,
        **kwargs
    ) -> Any:
        """Create completion using matcher model with backup fallback"""
        return await self.create_completion('matcher', messages, stream, **kwargs)
    
    async def create_extractor_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True,
        **kwargs
    ) -> Any:
        """Create completion using extractor model with backup fallback"""
        return await self.create_completion('extractor', messages, stream, **kwargs)
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        return backup_model_service.get_all_model_status()
    
    async def test_all_models(self) -> Dict[str, Dict[str, bool]]:
        """Test all models and return their status"""
        return await backup_model_service.test_all_models()
    
    def get_model_config(self, model_type: str) -> Dict[str, Any]:
        """Get model configuration for a given type"""
        return backup_model_service.get_model_config(model_type)
    
    def get_backup_models(self, model_type: str) -> List[Dict[str, Any]]:
        """Get backup models for a given type"""
        return backup_model_service.get_backup_models(model_type)
    
    async def stream_response(
        self,
        model_type: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Stream response from model with backup fallback
        
        Args:
            model_type: Type of model to use
            messages: List of message dictionaries
            **kwargs: Additional parameters
        
        Yields:
            Response chunks as strings
        """
        try:
            completion = await self.create_completion(model_type, messages, stream=True, **kwargs)
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"❌ Streaming failed for {model_type}: {e}")
            raise
    
    async def get_single_response(
        self,
        model_type: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Get single response from model with backup fallback
        
        Args:
            model_type: Type of model to use
            messages: List of message dictionaries
            **kwargs: Additional parameters
        
        Returns:
            Complete response as string
        """
        try:
            return await self.create_completion(model_type, messages, stream=False, **kwargs)
        except Exception as e:
            logger.error(f"❌ Single response failed for {model_type}: {e}")
            raise

# Global instance
llm_service = LLMService() 