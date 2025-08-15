"""
Enhanced Modular Pipeline for ASIA.fr Agent
Enhanced version that inherits from original ASIAModularPipeline
Adds advanced AI intelligence while preserving original functionality
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from .modular_pipeline import ASIAModularPipeline
from services.optimized_semantic_service import OptimizedSemanticService
from .components.travel_orchestrator import TravelOrchestrator

logger = logging.getLogger(__name__)

class EnhancedASIAModularPipeline(ASIAModularPipeline):
    """Enhanced modular pipeline that inherits from original and adds advanced features"""
    
    def __init__(self):
        # Call parent constructor to preserve original functionality
        super().__init__()
        
        # Add enhanced features
        self.semantic_service = None
        self.logger = logging.getLogger(f"{__name__}.EnhancedASIAModularPipeline")
    
    async def initialize(self):
        """Initialize the enhanced pipeline with all services and components"""
        if self._initialized:
            return
        
        try:
            self.logger.info("🚀 Initializing Enhanced ASIA Modular Pipeline...")
            
            # Initialize services (including enhanced semantic service)
            await self._initialize_enhanced_services()
            
            # Build pipeline with enhanced components
            self.pipeline = await self._build_enhanced_pipeline()
            
            self._initialized = True
            self.logger.info("✅ Enhanced ASIA Modular Pipeline initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize enhanced pipeline: {e}")
            raise
    
    async def _initialize_enhanced_services(self):
        """Initialize all required services including enhanced ones"""
        try:
            # Initialize original services first
            await super()._initialize_services()
            
            # Initialize enhanced semantic service
            self.semantic_service = OptimizedSemanticService()
            
            # Ensure data service is properly loaded
            if self.services.get('data'):
                try:
                    # Test data service by loading some data
                    test_offers = self.services['data'].get_offers()
                    self.logger.info(f"✅ Data service test successful - loaded {len(test_offers)} offers")
                except Exception as e:
                    self.logger.error(f"❌ Data service test failed: {e}")
                    # Try to reinitialize data service
                    from services.data_service import DataService
                    self.services['data'] = DataService()
                    test_offers = self.services['data'].get_offers()
                    self.logger.info(f"✅ Data service reinitialized - loaded {len(test_offers)} offers")
            
            self.logger.info("✅ All enhanced services initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced service initialization failed: {e}")
            raise
    
    async def _build_enhanced_pipeline(self):
        """Build the enhanced pipeline with intelligent components"""
        try:
            from .core import PipelineBuilder
            from .components.enhanced_preference_extractor import EnhancedPreferenceExtractorComponent
            from .components.enhanced_recommendation_engine import EnhancedRecommendationEngineComponent
            from .components.response_generator import ResponseGeneratorComponent
            
            builder = PipelineBuilder()
            
            # Add enhanced components in priority order
            builder.add_component(
                TravelOrchestrator(
                    self.services['llm'],
                    self.services['data']
                ),
                priority=100
            )
            
            builder.add_component(
                EnhancedPreferenceExtractorComponent(
                    self.services['llm'],
                    self.services['memory']
                ),
                priority=90
            )
            
            builder.add_component(
                EnhancedRecommendationEngineComponent(
                    self.semantic_service,
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
            self.logger.info("✅ Enhanced pipeline built successfully")
            return pipeline
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced pipeline building failed: {e}")
            raise
    
    async def process_user_input(self, user_input: str, conversation_id: str = "default") -> Dict[str, Any]:
        """Process user input through the enhanced modular pipeline with travel orchestrator"""
        try:
            # Ensure pipeline is initialized
            if not self._initialized:
                await self.initialize()
            
            # Get conversation context from memory
            conversation_context = {}
            if conversation_id and self.services.get('memory'):
                try:
                    conversation_context = await self.services['memory'].get_conversation_context(conversation_id)
                    self.logger.info(f"📝 Retrieved conversation context: {len(conversation_context)} items")
                    self.logger.info(f"📝 Conversation context content: {conversation_context}")
                    
                    # If we have stored preferences, update the orchestrator's current preferences
                    if orchestrator_key in self._orchestrators and conversation_context:
                        orchestrator = self._orchestrators[orchestrator_key]
                        # Update orchestrator preferences from memory
                        for key, value in conversation_context.items():
                            if hasattr(orchestrator.current_preferences, key) and value is not None:
                                setattr(orchestrator.current_preferences, key, value)
                        self.logger.info(f"🔄 Updated orchestrator preferences from memory: {orchestrator.current_preferences}")
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to get conversation context: {e}")
                    conversation_context = {}
            
            # Use the travel orchestrator directly
            # Ensure data service is properly initialized
            if not self.services.get('data'):
                self.logger.error("❌ Data service not found in services")
                return self._error_response("Data service not available")
            
            self.logger.info(f"🔧 Creating TravelOrchestrator with data service: {type(self.services['data'])}")
            
            # Create orchestrator instance or reuse existing one for this conversation
            orchestrator_key = f"orchestrator_{conversation_id}"
            if not hasattr(self, '_orchestrators'):
                self._orchestrators = {}
            
            if orchestrator_key not in self._orchestrators:
                self._orchestrators[orchestrator_key] = TravelOrchestrator(
                    self.services['llm'],
                    self.services['data']
                )
                self.logger.info(f"🆕 Created new orchestrator for conversation {conversation_id}")
            else:
                self.logger.info(f"🔄 Reusing existing orchestrator for conversation {conversation_id}")
            
            orchestrator = self._orchestrators[orchestrator_key]
            
            # Process through orchestrator
            result = await orchestrator.process_user_input(user_input, conversation_context)
            
            # Update memory with new context
            if conversation_id and self.services.get('memory'):
                try:
                    # Get current preferences from orchestrator
                    current_preferences = {}
                    if hasattr(orchestrator, 'current_preferences'):
                        current_preferences = {
                            'destination': orchestrator.current_preferences.destination,
                            'duration': orchestrator.current_preferences.duration,
                            'budget_amount': orchestrator.current_preferences.budget_amount,
                            'group_size': orchestrator.current_preferences.group_size,
                            'style': orchestrator.current_preferences.style,
                            'travel_dates': orchestrator.current_preferences.travel_dates,
                            'special_requirements': orchestrator.current_preferences.special_requirements
                        }
                        # Remove None values
                        current_preferences = {k: v for k, v in current_preferences.items() if v is not None}
                    
                    # Check if the method is async or sync
                    if asyncio.iscoroutinefunction(self.services['memory'].update_conversation_context):
                        await self.services['memory'].update_conversation_context(
                            conversation_id, 
                            current_preferences
                        )
                    else:
                        # Sync method
                        self.services['memory'].update_conversation_context(
                            conversation_id, 
                            current_preferences
                        )
                    
                    self.logger.info(f"📝 Updated memory with preferences: {current_preferences}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to update conversation context: {e}")
            
            # Format response for API
            response_data = {
                'response': result.get('text', ''),
                'conversation_id': conversation_id,
                'status': 'success',
                'enhanced': True,
                'intent': result.get('type', 'general'),
                'metadata': {
                    'orchestrator_used': True,
                    'confirmation_pending': result.get('type') == 'confirmation_request',
                    'offers_available': result.get('type') == 'offers'
                }
            }
            
            # Add current preferences to response
            if hasattr(orchestrator, 'current_preferences'):
                current_preferences = {
                    'destination': orchestrator.current_preferences.destination,
                    'duration': orchestrator.current_preferences.duration,
                    'budget_amount': orchestrator.current_preferences.budget_amount,
                    'group_size': orchestrator.current_preferences.group_size,
                    'style': orchestrator.current_preferences.style,
                    'travel_dates': orchestrator.current_preferences.travel_dates,
                    'special_requirements': orchestrator.current_preferences.special_requirements
                }
                # Remove None values
                current_preferences = {k: v for k, v in current_preferences.items() if v is not None}
                response_data['preferences'] = current_preferences
            
            # Add offers if present
            if result.get('type') == 'offers' and result.get('offers'):
                response_data['offers'] = result['offers']
                response_data['match_scores'] = result.get('match_scores', [])
                response_data['budget_indicators'] = result.get('budget_indicators', [])
                response_data['llm_selected'] = result.get('llm_selected', False)
                response_data['confidence'] = result.get('confidence', 'medium')
            
            self.logger.info(f"✅ Travel orchestrator processing completed for conversation {conversation_id}")
            return response_data
            
        except Exception as e:
            self.logger.error(f"❌ Travel orchestrator processing failed: {e}")
            return self._error_response(str(e))
    
    async def _create_enhanced_context(self, user_input: str, conversation_id: str):
        """Create enhanced pipeline context with user input and conversation data"""
        try:
            # Use parent context creation
            context = await super()._create_context(user_input, conversation_id)
            
            # Add enhanced metadata
            context.add_metadata('enhanced_pipeline', True)
            context.add_metadata('semantic_service_available', self.semantic_service is not None)
            
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced context creation failed: {e}")
            # Return minimal context
            from .core import PipelineContext
            return PipelineContext(
                conversation_id=conversation_id,
                user_input=user_input,
                user_preferences={},
                conversation_history="",
                turn_count=0
            )
    
    def _extract_enhanced_results(self, context) -> Dict[str, Any]:
        """Extract enhanced results from pipeline context"""
        try:
            # Get base results from parent
            base_result = super()._extract_results(context)
            
            # Add enhanced metadata
            enhanced_metadata = {
                'enhanced_pipeline': True,
                'semantic_search_enabled': context.get_metadata('semantic_search_enabled', False),
                'search_query': context.get_metadata('search_query', ''),
                'semantic_results_count': context.get_metadata('semantic_results_count', 0),
                'recommendation_strategy': context.get_metadata('recommendation_strategy', 'traditional'),
                'enhanced_components': [
                    'IntelligentOrchestrator',
                    'EnhancedPreferenceExtractor',
                    'EnhancedRecommendationEngine',
                    'ResponseGenerator'
                ]
            }
            
            # Merge enhanced metadata with base metadata
            if 'metadata' in base_result:
                base_result['metadata'].update(enhanced_metadata)
            else:
                base_result['metadata'] = enhanced_metadata
            
            return base_result
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced result extraction failed: {e}")
            return self._error_response("Failed to extract enhanced results")
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            'response': f"Je suis désolé, j'ai rencontré une erreur: {error_message}. Pouvez-vous réessayer ?",
            'offers': [],
            'intent': 'error',
            'should_show_offers': False,
            'preferences': {},
            'enhanced_metadata': {
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
    
    async def clear_memory(self, conversation_id: str = None):
        """Clear conversation memory"""
        try:
            # Ensure pipeline is initialized
            if not self._initialized:
                await self.initialize()
            
            if conversation_id:
                self.services['memory'].clear_conversation(conversation_id)
                # Also clear the orchestrator instance for this conversation
                orchestrator_key = f"orchestrator_{conversation_id}"
                if hasattr(self, '_orchestrators') and orchestrator_key in self._orchestrators:
                    del self._orchestrators[orchestrator_key]
                    self.logger.info(f"🧹 Cleared orchestrator for conversation {conversation_id}")
                self.logger.info(f"🧹 Cleared memory for conversation {conversation_id}")
            else:
                self.services['memory'].clear_all_conversations()
                # Clear all orchestrator instances
                if hasattr(self, '_orchestrators'):
                    self._orchestrators.clear()
                    self.logger.info("🧹 Cleared all orchestrator instances")
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
    
    async def get_semantic_search_capabilities(self) -> Dict[str, Any]:
        """Get semantic search capabilities"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Test semantic search with a simple query
            test_results = await self.semantic_service.search_offers("beach destinations", top_k=3)
            
            return {
                'available': len(test_results) > 0,
                'test_results_count': len(test_results),
                'model_name': self.semantic_service.model_name if hasattr(self.semantic_service, 'model_name') else 'unknown'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Semantic search capability check failed: {e}")
            return {
                'available': False,
                'error': str(e)
            }
    
    async def get_ai_intelligence_status(self) -> Dict[str, Any]:
        """Get AI intelligence status"""
        try:
            if not self._initialized:
                await self.initialize()
            
            return {
                'llm_service': 'available',
                'semantic_service': 'available' if self.semantic_service else 'unavailable',
                'memory_service': 'available',
                'data_service': 'available',
                'enhanced_components': [
                    'IntelligentOrchestrator',
                    'EnhancedPreferenceExtractor', 
                    'EnhancedRecommendationEngine',
                    'ResponseGenerator'
                ]
            }
            
        except Exception as e:
            self.logger.error(f"❌ AI intelligence status check failed: {e}")
            return {
                'error': str(e)
            } 