"""
Core Pipeline Architecture for ASIA.fr Agent
Defines the base classes and interfaces for the modular pipeline system
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class PipelineState(Enum):
    """Pipeline execution states"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class PipelineContext:
    """Context object passed between pipeline components"""
    conversation_id: str
    user_input: str
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    conversation_history: str = ""
    turn_count: int = 0
    state: PipelineState = PipelineState.IDLE
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def update_preferences(self, new_preferences: Dict[str, Any]):
        """Update user preferences"""
        self.user_preferences.update(new_preferences)
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to context"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from context"""
        return self.metadata.get(key, default)

class PipelineComponent(ABC):
    """Base class for all pipeline components"""
    
    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.enabled = True
    
    @abstractmethod
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process the context and return updated context"""
        pass
    
    @abstractmethod
    def is_required(self, context: PipelineContext) -> bool:
        """Determine if this component should run for the given context"""
        pass
    
    def log_start(self, context: PipelineContext):
        """Log component start"""
        self.logger.info(f"🚀 Starting {self.name}")
    
    def log_complete(self, context: PipelineContext):
        """Log component completion"""
        self.logger.info(f"✅ Completed {self.name}")
    
    def log_error(self, context: PipelineContext, error: Exception):
        """Log component error"""
        self.logger.error(f"❌ Error in {self.name}: {error}")
    
    def disable(self):
        """Disable this component"""
        self.enabled = False
    
    def enable(self):
        """Enable this component"""
        self.enabled = True

class Pipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self, components: List[PipelineComponent] = None):
        self.components = components or []
        self.logger = logging.getLogger(f"{__name__}.Pipeline")
        self.execution_stats = {}
    
    def add_component(self, component: PipelineComponent):
        """Add a component to the pipeline"""
        self.components.append(component)
        # Sort by priority (higher priority first)
        self.components.sort(key=lambda x: x.priority, reverse=True)
    
    def remove_component(self, component_name: str):
        """Remove a component from the pipeline"""
        self.components = [c for c in self.components if c.name != component_name]
    
    async def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute the pipeline with the given context"""
        start_time = datetime.utcnow()
        self.logger.info(f"🎯 Starting pipeline execution for conversation {context.conversation_id}")
        
        try:
            context.state = PipelineState.PROCESSING
            
            # Execute components in priority order
            for component in self.components:
                if not component.enabled:
                    self.logger.debug(f"⏭️ Skipping {component.name} - disabled")
                    continue
                    
                if component.is_required(context):
                    component_start = datetime.utcnow()
                    component.log_start(context)
                    
                    try:
                        context = await component.process(context)
                        component.log_complete(context)
                        
                        # Record execution time
                        execution_time = (datetime.utcnow() - component_start).total_seconds()
                        self.execution_stats[component.name] = execution_time
                        
                    except Exception as e:
                        component.log_error(context, e)
                        # Continue with next component instead of failing entire pipeline
                        continue
                else:
                    self.logger.debug(f"⏭️ Skipping {component.name} - not required")
            
            context.state = PipelineState.COMPLETED
            total_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.info(f"✅ Pipeline execution completed in {total_time:.2f}s")
            
        except Exception as e:
            context.state = PipelineState.ERROR
            self.logger.error(f"❌ Pipeline execution failed: {e}")
            raise
        
        return context
    
    def get_execution_stats(self) -> Dict[str, float]:
        """Get execution statistics for all components"""
        return self.execution_stats.copy()
    
    def reset_stats(self):
        """Reset execution statistics"""
        self.execution_stats.clear()

class PipelineBuilder:
    """Builder pattern for creating pipeline configurations"""
    
    def __init__(self):
        self.components = []
    
    def add_component(self, component: PipelineComponent, priority: int = 0):
        """Add a component with priority"""
        component.priority = priority
        self.components.append(component)
        return self
    
    def build(self) -> Pipeline:
        """Build the pipeline"""
        pipeline = Pipeline(self.components)
        return pipeline 