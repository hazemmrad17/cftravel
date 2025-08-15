"""
Intelligent Orchestrator Component for ASIA.fr Agent
Enhanced version that inherits from original OrchestratorComponent
Adds advanced AI orchestration while preserving original functionality
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .orchestrator import OrchestratorComponent
from services.optimized_semantic_service import OptimizedSemanticService

class IntelligentOrchestratorComponent(OrchestratorComponent):
    """Enhanced orchestrator that inherits from original and adds advanced features"""
    
    def __init__(self, llm_service, memory_service, semantic_service: OptimizedSemanticService):
        # Call parent constructor to preserve original functionality
        super().__init__(llm_service, memory_service)
        
        # Add enhanced features
        self.semantic_service = semantic_service
        self.current_date = datetime.now()
        
        # Override component name and priority
        self.name = "IntelligentOrchestrator"
        self.priority = 100
    
    async def process(self, context):
        """Enhanced process that uses original logic + semantic capabilities"""
        try:
            self.logger.info(f"🧠 Intelligent orchestration for: {context.user_input}")
            
            # First, use the original orchestration logic
            original_context = await super().process(context)
            
            # Then enhance with semantic search capabilities
            enhanced_result = await self._enhance_with_semantic_capabilities(original_context)
            
            # Update context with enhanced results
            context.add_metadata('semantic_search_enabled', enhanced_result.get('semantic_search_enabled', False))
            context.add_metadata('search_query', enhanced_result.get('search_query', ''))
            context.add_metadata('semantic_results_count', enhanced_result.get('semantic_results_count', 0))
            
            return context
            
        except Exception as e:
            self.log_error(context, e)
            # Fallback to original orchestration
            return await super().process(context)
    
    async def _enhance_with_semantic_capabilities(self, context) -> Dict[str, Any]:
        """Enhance orchestration result with semantic search capabilities"""
        try:
            orchestration_result = context.get_metadata('orchestration_result', {})
            user_input = context.user_input
            
            # Check if semantic search should be enabled
            semantic_enabled = self._should_enable_semantic_search(user_input, orchestration_result)
            
            if semantic_enabled:
                # Generate search query
                search_query = self._generate_semantic_search_query(user_input, context.user_preferences)
                
                # Test semantic search capability
                test_results = await self.semantic_service.search_offers(search_query, top_k=3)
                
                return {
                    'semantic_search_enabled': len(test_results) > 0,
                    'search_query': search_query if len(test_results) > 0 else '',
                    'semantic_results_count': len(test_results)
                }
            
            return {
                'semantic_search_enabled': False,
                'search_query': '',
                'semantic_results_count': 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Semantic enhancement failed: {e}")
            return {
                'semantic_search_enabled': False,
                'search_query': '',
                'semantic_results_count': 0
            }
    
    def _should_enable_semantic_search(self, user_input: str, orchestration_result: Dict[str, Any]) -> bool:
        """Determine if semantic search should be enabled"""
        # Enable semantic search for vague preferences and activity-based requests
        vague_keywords = [
            'plage', 'beach', 'culture', 'aventure', 'adventure', 'détente', 'relaxation',
            'gastronomie', 'cuisine', 'nature', 'montagne', 'mountain', 'tropical',
            'luxe', 'luxury', 'authentique', 'traditionnel', 'moderne', 'urbain',
            'rural', 'île', 'island', 'désert', 'desert', 'neige', 'snow'
        ]
        
        # Check for vague preferences
        user_input_lower = user_input.lower()
        has_vague_preferences = any(keyword in user_input_lower for keyword in vague_keywords)
        
        # Check if user is asking for recommendations or suggestions
        is_recommendation_request = orchestration_result.get('intent') in ['recommendation_request', 'suggestion_request']
        
        return has_vague_preferences or is_recommendation_request
    
    def _generate_semantic_search_query(self, user_input: str, user_preferences: Dict[str, Any]) -> str:
        """Generate semantic search query from user input and preferences"""
        query_parts = []
        
        # Add user input terms
        query_parts.append(user_input)
        
        # Add destination if available
        if user_preferences.get('destination'):
            query_parts.append(f"voyage {user_preferences['destination']}")
            query_parts.append(f"circuit {user_preferences['destination']}")
        
        # Add trip type if available
        if user_preferences.get('trip_type'):
            query_parts.append(f"{user_preferences['trip_type']} asie")
        
        # Add activities if available
        if user_preferences.get('activities'):
            for activity in user_preferences['activities']:
                query_parts.append(f"{activity} asie")
        
        # Join and return
        return " ".join(query_parts) 