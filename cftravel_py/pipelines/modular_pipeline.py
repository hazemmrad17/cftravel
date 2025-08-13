"""
Modular Pipeline for ASIA.fr Agent
Main pipeline that orchestrates all components
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from .core import Pipeline, PipelineContext, PipelineBuilder
from .components.orchestrator import OrchestratorComponent
from .components.preference_extractor import PreferenceExtractorComponent
from .components.recommendation_engine import RecommendationEngineComponent
from .components.response_generator import ResponseGeneratorComponent
from services.llm_service import LLMService
from services.memory_service import MemoryService
from services.optimized_semantic_service import OptimizedSemanticService
from services.data_service import DataService

logger = logging.getLogger(__name__)

class ASIAModularPipeline:
    """Main modular pipeline for ASIA.fr Agent"""
    
    def __init__(self):
        self.pipeline = None
        self.services = {}
        self.logger = logging.getLogger(f"{__name__}.ASIAModularPipeline")
        self._initialized = False
    
    async def initialize(self):
        """Initialize the pipeline with all services and components"""
        if self._initialized:
            return
        
        try:
            self.logger.info("🚀 Initializing ASIA Modular Pipeline...")
            
            # Initialize services
            await self._initialize_services()
            
            # Build pipeline with components
            self.pipeline = await self._build_pipeline()
            
            self._initialized = True
            self.logger.info("✅ ASIA Modular Pipeline initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize pipeline: {e}")
            raise
    
    async def _initialize_services(self):
        """Initialize all required services"""
        try:
            # Initialize LLM Service
            self.services['llm'] = LLMService()
            
            # Initialize Memory Service
            self.services['memory'] = MemoryService()
            
            # Initialize Semantic Service
            self.services['semantic'] = OptimizedSemanticService()
            
            # Initialize Data Service
            self.services['data'] = DataService()
            
            self.logger.info("✅ All services initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Service initialization failed: {e}")
            raise
    
    async def _build_pipeline(self) -> Pipeline:
        """Build the pipeline with all components"""
        try:
            builder = PipelineBuilder()
            
            # Add components in priority order
            builder.add_component(
                OrchestratorComponent(
                    self.services['llm'],
                    self.services['memory']
                ),
                priority=100
            )
            
            builder.add_component(
                PreferenceExtractorComponent(
                    self.services['llm'],
                    self.services['memory']
                ),
                priority=90
            )
            
            builder.add_component(
                RecommendationEngineComponent(
                    self.services['semantic'],
                    self.services['llm'],
                    self.services['data']
                ),
                priority=80
            )
            
            builder.add_component(
                ResponseGeneratorComponent(
                    self.services['llm'],
                    self.services['memory']
                ),
                priority=70
            )
            
            pipeline = builder.build()
            self.logger.info("✅ Pipeline built successfully")
            return pipeline
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline building failed: {e}")
            raise
    
    async def process_user_input(self, user_input: str, conversation_id: str = "default") -> Dict[str, Any]:
        """Process user input through the modular pipeline"""
        try:
            # Ensure pipeline is initialized
            if not self._initialized:
                await self.initialize()
            
            # Create pipeline context
            context = await self._create_context(user_input, conversation_id)
            
            # Execute pipeline
            result_context = await self.pipeline.execute(context)
            
            # Extract results
            result = self._extract_results(result_context)
            
            self.logger.info(f"✅ Pipeline processing completed for conversation {conversation_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline processing failed: {e}")
            return self._error_response(str(e))
    
    async def _create_context(self, user_input: str, conversation_id: str) -> PipelineContext:
        """Create pipeline context with user input and conversation data"""
        try:
            # Get conversation history and preferences from memory
            memory_service = self.services['memory']
            
            # Get latest preferences
            user_preferences = memory_service.get_latest_preferences(conversation_id)
            
            # Get conversation history
            conversation_history = memory_service.get_conversation_history(conversation_id, max_messages=10)
            
            # Get turn count
            conversation = memory_service.get_conversation(conversation_id)
            turn_count = len(conversation.messages) if conversation else 0
            
            # Create context
            context = PipelineContext(
                conversation_id=conversation_id,
                user_input=user_input,
                user_preferences=user_preferences,
                conversation_history=conversation_history,
                turn_count=turn_count
            )
            
            # Add message to memory
            memory_service.add_message(conversation_id, "user", user_input)
            
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Context creation failed: {e}")
            # Return minimal context
            return PipelineContext(
                conversation_id=conversation_id,
                user_input=user_input,
                user_preferences={},
                conversation_history="",
                turn_count=0
            )
    
    def _extract_results(self, context: PipelineContext) -> Dict[str, Any]:
        """Extract results from pipeline context"""
        try:
            # Get generated response
            generated_response = context.get_metadata('generated_response', {})
            response_text = generated_response.get('text', '')
            
            # Get offers if any
            offers = context.get_metadata('offers', [])
            
            # Get orchestration result
            orchestration_result = context.get_metadata('orchestration_result', {})
            
            # Build result
            result = {
                'response': response_text,
                'offers': offers,
                'intent': orchestration_result.get('intent', 'general'),
                'should_show_offers': context.get_metadata('should_show_offers', False),
                'preferences': context.user_preferences,
                'metadata': {
                    'turn_count': context.turn_count,
                    'conversation_id': context.conversation_id,
                    'execution_stats': self.pipeline.get_execution_stats()
                }
            }
            
            # Add assistant message to memory
            if response_text:
                self.services['memory'].add_message(
                    context.conversation_id, 
                    "assistant", 
                    response_text
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Result extraction failed: {e}")
            return self._error_response("Failed to extract results")
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            'response': f"Je suis désolé, j'ai rencontré une erreur: {error_message}. Pouvez-vous réessayer ?",
            'offers': [],
            'intent': 'error',
            'should_show_offers': False,
            'preferences': {},
            'metadata': {
                'error': error_message
            }
        }
    
    def get_execution_stats(self) -> Dict[str, float]:
        """Get execution statistics"""
        if self.pipeline:
            return self.pipeline.get_execution_stats()
        return {}
    
    def reset_stats(self):
        """Reset execution statistics"""
        if self.pipeline:
            self.pipeline.reset_stats()
    
    def clear_memory(self, conversation_id: str = None):
        """Clear conversation memory"""
        try:
            if conversation_id:
                self.services['memory'].clear_conversation(conversation_id)
                self.logger.info(f"🧹 Cleared memory for conversation {conversation_id}")
            else:
                self.services['memory'].clear_all_conversations()
                self.logger.info("🧹 Cleared all conversation memory")
        except Exception as e:
            self.logger.error(f"❌ Memory clearing failed: {e}")
    
    def get_component_status(self) -> Dict[str, bool]:
        """Get status of all pipeline components"""
        if not self.pipeline:
            return {}
        
        status = {}
        for component in self.pipeline.components:
            status[component.name] = component.enabled
        
        return status
    
    def enable_component(self, component_name: str):
        """Enable a specific component"""
        if self.pipeline:
            for component in self.pipeline.components:
                if component.name == component_name:
                    component.enable()
                    self.logger.info(f"✅ Enabled component: {component_name}")
                    return
        
        self.logger.warning(f"⚠️ Component not found: {component_name}")
    
    def disable_component(self, component_name: str):
        """Disable a specific component"""
        if self.pipeline:
            for component in self.pipeline.components:
                if component.name == component_name:
                    component.disable()
                    self.logger.info(f"❌ Disabled component: {component_name}")
                    return
        
        self.logger.warning(f"⚠️ Component not found: {component_name}") 