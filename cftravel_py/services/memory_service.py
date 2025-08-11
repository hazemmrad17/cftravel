"""
Memory service for ASIA.fr Agent
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.exceptions import MemoryError
from models.llm_models import Conversation, ConversationMessage

logger = logging.getLogger(__name__)

class MemoryService:
    """Service for managing conversation memory"""
    
    def __init__(self):
        self._conversations: Dict[str, Conversation] = {}
        self._user_preferences: Dict[str, Dict[str, Any]] = {}
        
    def create_conversation(self, conversation_id: str, user_id: Optional[str] = None) -> Conversation:
        """Create a new conversation"""
        try:
            now = datetime.utcnow().isoformat()
            conversation = Conversation(
                id=conversation_id,
                messages=[],
                user_preferences={},
                created_at=now,
                updated_at=now
            )
            
            self._conversations[conversation_id] = conversation
            logger.info(f"✅ Created conversation: {conversation_id}")
            return conversation
            
        except Exception as e:
            raise MemoryError(f"Failed to create conversation: {e}")
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        return self._conversations.get(conversation_id)
    
    def add_message(self, conversation_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> ConversationMessage:
        """Add a message to conversation"""
        try:
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                conversation = self.create_conversation(conversation_id)
            
            message = ConversationMessage(
                role=role,
                content=content,
                timestamp=datetime.utcnow().isoformat(),
                metadata=metadata or {}
            )
            
            conversation.messages.append(message)
            conversation.updated_at = datetime.utcnow().isoformat()
            
            logger.debug(f"✅ Added {role} message to conversation {conversation_id}")
            return message
            
        except Exception as e:
            raise MemoryError(f"Failed to add message: {e}")
    
    def get_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[ConversationMessage]:
        """Get messages from conversation"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        messages = conversation.messages
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear a conversation"""
        try:
            if conversation_id in self._conversations:
                del self._conversations[conversation_id]
                logger.info(f"✅ Cleared conversation: {conversation_id}")
                return True
            return False
            
        except Exception as e:
            raise MemoryError(f"Failed to clear conversation: {e}")
    
    def clear_all_conversations(self) -> bool:
        """Clear all conversations"""
        try:
            self._conversations.clear()
            logger.info("✅ Cleared all conversations")
            return True
            
        except Exception as e:
            raise MemoryError(f"Failed to clear conversations: {e}")
    
    def set_user_preference(self, conversation_id: str, key: str, value: Any) -> bool:
        """Set user preference for conversation"""
        try:
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                conversation = self.create_conversation(conversation_id)
            
            if not conversation.user_preferences:
                conversation.user_preferences = {}
            
            conversation.user_preferences[key] = value
            conversation.updated_at = datetime.utcnow().isoformat()
            
            logger.debug(f"✅ Set preference {key}={value} for conversation {conversation_id}")
            return True
            
        except Exception as e:
            raise MemoryError(f"Failed to set preference: {e}")
    
    def get_user_preferences(self, conversation_id: str) -> Dict[str, Any]:
        """Get user preferences for conversation"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return {}
        
        return conversation.user_preferences or {}
    
    def get_user_preference(self, conversation_id: str, key: str, default: Any = None) -> Any:
        """Get specific user preference"""
        preferences = self.get_user_preferences(conversation_id)
        return preferences.get(key, default)
    
    def clear_user_preferences(self, conversation_id: str) -> bool:
        """Clear user preferences for conversation"""
        try:
            conversation = self.get_conversation(conversation_id)
            if conversation:
                conversation.user_preferences = {}
                conversation.updated_at = datetime.utcnow().isoformat()
                logger.info(f"✅ Cleared preferences for conversation {conversation_id}")
                return True
            return False
            
        except Exception as e:
            raise MemoryError(f"Failed to clear preferences: {e}")
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation summary"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return {}
        
        return {
            'id': conversation.id,
            'message_count': len(conversation.messages),
            'created_at': conversation.created_at,
            'updated_at': conversation.updated_at,
            'user_preferences': conversation.user_preferences,
            'last_message': conversation.messages[-1].content if conversation.messages else None
        }
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """Get all conversations summary"""
        return [self.get_conversation_summary(conv_id) for conv_id in self._conversations.keys()]
    
    def get_conversation_history(self, conversation_id: str, max_messages: int = 10) -> str:
        """Get conversation history as formatted string"""
        messages = self.get_messages(conversation_id, max_messages)
        
        history = []
        for msg in messages:
            role = "User" if msg.role == "user" else "Assistant"
            history.append(f"{role}: {msg.content}")
        
        return "\n".join(history) 