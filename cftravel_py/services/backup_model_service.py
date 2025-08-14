"""
Backup Model Service
===================
Handles priority-based backup models with automatic fallback and retry logic.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from groq import Groq, GroqError
from core.unified_config import unified_config

logger = logging.getLogger(__name__)

class BackupModelService:
    """
    Priority-based backup model service with automatic fallback
    """
    
    def __init__(self):
        self.config = unified_config.get_ai()
        api_key = self.config.get('api_key')
        
        if not api_key:
            logger.warning("⚠️ No API key found. Some features may not work properly.")
            self.client = None
        else:
            # Initialize Groq client - Groq client handles the base URL internally
            # Don't pass base_url as it causes URL duplication
            self.client = Groq(api_key=api_key)
            logger.info("🔧 Initialized Groq client")
        
        self.models = self.config.get('models', {})
        
    def get_model_config(self, model_type: str) -> Dict[str, Any]:
        """Get primary model configuration for a given type"""
        model_config = self.models.get(model_type, {})
        return {
            'name': model_config.get('name'),
            'temperature': model_config.get('temperature', 0.7),
            'max_tokens': model_config.get('max_tokens', 2048),
            'top_p': model_config.get('top_p', 0.95),
            'reasoning_effort': model_config.get('reasoning_effort', 'default'),
            'enabled': model_config.get('enabled', True)
        }
    
    def get_backup_models(self, model_type: str) -> List[Dict[str, Any]]:
        """Get sorted backup models by priority for a given type"""
        model_config = self.models.get(model_type, {})
        backup_models = model_config.get('backup_models', [])
        
        # Sort by priority (lower number = higher priority)
        return sorted(backup_models, key=lambda x: x.get('priority', 999))
    
    async def create_completion_with_fallback(
        self,
        model_type: str,
        messages: List[Dict[str, str]],
        stream: bool = False,  # Changed default to False for simple API calls
        **kwargs
    ):
        """
        Create completion with automatic fallback to backup models
        
        Args:
            model_type: Type of model (reasoning, generation, matcher, extractor)
            messages: List of message dictionaries
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the completion
        
        Returns:
            Completion response or generator
        """
        
        # Get primary model configuration
        primary_config = self.get_model_config(model_type)
        if not primary_config.get('enabled'):
            raise ValueError(f"Model type {model_type} is disabled")
        
        # Get backup models sorted by priority
        backup_models = self.get_backup_models(model_type)
        
        # Try primary model first
        try:
            logger.info(f"🔄 Trying primary model: {primary_config['name']} for {model_type}")
            return await self._create_completion(primary_config, messages, stream, **kwargs)
            
        except Exception as e:
            logger.warning(f"⚠️ Primary model {primary_config['name']} failed: {e}")
            
            # Try backup models in priority order
            for backup_model in backup_models:
                try:
                    logger.info(f"🔄 Trying backup model: {backup_model['name']} (priority {backup_model.get('priority')}) for {model_type}")
                    return await self._create_completion(backup_model, messages, stream, **kwargs)
                    
                except Exception as backup_error:
                    logger.warning(f"⚠️ Backup model {backup_model['name']} failed: {backup_error}")
                    continue
            
            # All models failed
            raise Exception(f"All models failed for {model_type}. Last error: {e}")
    
    async def _create_completion(
        self,
        model_config: Dict[str, Any],
        messages: List[Dict[str, str]],
        stream: bool = False,  # Changed default to False for simple API calls
        **kwargs
    ):
        """Create completion with specific model configuration"""
        
        # Prepare completion parameters
        completion_params = {
            'model': model_config['name'],
            'messages': messages,
            'temperature': model_config.get('temperature', 0.7),
            'max_tokens': model_config.get('max_tokens', 2048),
            'top_p': model_config.get('top_p', 0.95),
            'stream': stream,
            'stop': None
        }
        
        # Add reasoning_effort if specified and model supports it
        if 'reasoning_effort' in model_config:
            # Only add reasoning_effort for models that support it
            supported_models = ['openai/gpt-oss-120b', 'llama-3.1-70b-versatile', 'llama-3.1-8b-versatile']
            if model_config['name'] in supported_models:
                completion_params['reasoning_effort'] = model_config['reasoning_effort']
        
        # Override with any additional kwargs
        completion_params.update(kwargs)
        
        logger.info(f"📡 Creating completion with {model_config['name']}: {completion_params}")
        
        if not self.client:
            raise Exception("No API client available. Please set GROQ_API_KEY environment variable.")
        
        try:
            completion = self.client.chat.completions.create(**completion_params)
            
            if stream:
                return completion
            else:
                return completion.choices[0].message.content
                
        except GroqError as e:
            logger.error(f"❌ Groq API error with {model_config['name']}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error with {model_config['name']}: {e}")
            raise
    
    def get_model_status(self, model_type: str) -> Dict[str, Any]:
        """Get status of all models for a given type"""
        primary_config = self.get_model_config(model_type)
        backup_models = self.get_backup_models(model_type)
        
        return {
            'type': model_type,
            'primary': {
                'name': primary_config['name'],
                'enabled': primary_config['enabled'],
                'temperature': primary_config['temperature'],
                'max_tokens': primary_config['max_tokens'],
                'top_p': primary_config.get('top_p'),
                'reasoning_effort': primary_config.get('reasoning_effort')
            },
            'backups': [
                {
                    'name': backup['name'],
                    'priority': backup.get('priority'),
                    'temperature': backup.get('temperature'),
                    'max_tokens': backup.get('max_tokens'),
                    'top_p': backup.get('top_p'),
                    'reasoning_effort': backup.get('reasoning_effort')
                }
                for backup in backup_models
            ],
            'total_models': 1 + len(backup_models)
        }
    
    def get_all_model_status(self) -> Dict[str, Any]:
        """Get status of all model types"""
        model_types = ['reasoning', 'generation', 'matcher', 'extractor']
        
        return {
            model_type: self.get_model_status(model_type)
            for model_type in model_types
        }
    
    async def test_model(self, model_config: Dict[str, Any]) -> bool:
        """Test if a model is working"""
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            await self._create_completion(model_config, test_messages, stream=False)
            return True
        except Exception as e:
            logger.error(f"❌ Model test failed for {model_config['name']}: {e}")
            return False
    
    async def test_all_models(self) -> Dict[str, Dict[str, bool]]:
        """Test all models and return their status"""
        results = {}
        
        for model_type in ['reasoning', 'generation', 'matcher', 'extractor']:
            results[model_type] = {}
            
            # Test primary model
            primary_config = self.get_model_config(model_type)
            results[model_type]['primary'] = await self.test_model(primary_config)
            
            # Test backup models
            backup_models = self.get_backup_models(model_type)
            for backup in backup_models:
                results[model_type][f"backup_{backup.get('priority', 'unknown')}"] = await self.test_model(backup)
        
        return results

# Global instance
backup_model_service = BackupModelService() 