"""
Response Generator Component for ASIA.fr Agent
Handles text generation and response formatting
"""

import json
from typing import Dict, Any, List
from ..core import PipelineComponent, PipelineContext, PipelineState
from services.llm_service import LLMService
from services.memory_service import MemoryService

class ResponseGeneratorComponent(PipelineComponent):
    """Generates intelligent responses based on pipeline context"""
    
    def __init__(self, llm_service: LLMService, memory_service: MemoryService):
        super().__init__("ResponseGenerator", priority=70)
        self.llm_service = llm_service
        self.memory_service = memory_service
    
    def is_required(self, context: PipelineContext) -> bool:
        """Always required to generate a response"""
        return True
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Generate appropriate response based on context"""
        try:
            # Determine response type and generate accordingly
            response_type = context.get_metadata('response_type', 'question')
            intent = context.get_metadata('intent', 'general')
            
            if context.get_metadata('should_show_offers', False):
                # Check if we should show preference summary first
                if context.get_metadata('show_preference_summary', True):
                    # Generate preference summary response
                    response = await self._generate_preference_summary_response(context)
                else:
                    # Generate offer presentation response
                    response = await self._generate_offer_response(context)
            elif intent == 'confirmation':
                # Generate confirmation response and show offers
                response = await self._generate_confirmation_response(context)
                # Set flag to show offers directly next time
                context.add_metadata('show_preference_summary', False)
            elif intent == 'modification':
                # Generate modification response
                response = await self._generate_modification_response(context)
            else:
                # Generate general conversation response
                response = await self._generate_general_response(context)
            
            # Store response in context
            context.add_metadata('generated_response', response)
            context.add_metadata('response_text', response.get('text', ''))
            
            return context
            
        except Exception as e:
            self.log_error(context, e)
            # Fallback response
            context.add_metadata('generated_response', self._fallback_response())
            return context
    
    async def _generate_offer_response(self, context: PipelineContext) -> Dict[str, Any]:
        """Generate response when showing offers"""
        offers = context.get_metadata('offers', [])
        
        if not offers:
            return {
                'text': "Je n'ai pas trouvé d'offres correspondant exactement à vos critères. Pouvez-vous préciser vos préférences ?",
                'type': 'no_offers',
                'offers': []
            }
        
        # Generate personalized introduction
        intro = await self._generate_offer_intro(context, offers)
        
        return {
            'text': intro,
            'type': 'offers',
            'offers': offers,
            'offer_count': len(offers)
        }
    
    async def _generate_offer_intro(self, context: PipelineContext, offers: List[Dict]) -> str:
        """Generate personalized introduction for offers"""
        try:
            prompt = f"""
You are ASIA.fr Agent, a French travel specialist. Generate a personalized introduction for the offers you're about to present.

USER PREFERENCES: {json.dumps(context.user_preferences, indent=2, ensure_ascii=False)}
OFFER COUNT: {len(offers)}

Generate a warm, personalized introduction in French that:
1. Acknowledges their preferences
2. Mentions the number of offers found
3. Invites them to explore the offers
4. Is friendly and professional

Keep it concise (2-3 sentences maximum).

RESPOND ONLY WITH THE INTRODUCTION TEXT:
"""
            
            response = await self.llm_service.generate_text(prompt, model="generator")
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate offer intro: {e}")
            return f"Voici {len(offers)} offres qui correspondent parfaitement à vos critères :"
    
    async def _generate_confirmation_response(self, context: PipelineContext) -> Dict[str, Any]:
        """Generate response for user confirmations"""
        try:
            prompt = f"""
You are ASIA.fr Agent, a friendly and enthusiastic French travel specialist with a warm personality like Layla.ai. The user has confirmed their preferences and you're excited to show them amazing offers!

USER PREFERENCES: {json.dumps(context.user_preferences, indent=2, ensure_ascii=False)}

Generate a warm, enthusiastic confirmation response in French that:
1. 🌟 Acknowledges their confirmation with genuine excitement
2. ✨ Shows enthusiasm about preparing their personalized offers
3. Uses emojis naturally to express your happiness
4. Sounds like you're genuinely excited to help them

Keep it warm and encouraging (1-2 sentences).

RESPOND ONLY WITH THE CONFIRMATION TEXT:
"""
            
            response = await self.llm_service.generate_text(prompt, model="generator")
            return {
                'text': response.strip(),
                'type': 'confirmation'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate confirmation response: {e}")
            return {
                'text': "Parfait ! Je prépare vos offres personnalisées.",
                'type': 'confirmation'
            }
    
    async def _generate_modification_response(self, context: PipelineContext) -> Dict[str, Any]:
        """Generate response for modification requests"""
        try:
            prompt = f"""
You are ASIA.fr Agent, a friendly and enthusiastic French travel specialist with a warm personality like Layla.ai. The user wants to modify their preferences and you're happy to help them get it perfect!

CURRENT PREFERENCES: {json.dumps(context.user_preferences, indent=2, ensure_ascii=False)}
USER INPUT: {context.user_input}

Generate a warm, helpful response in French that:
1. 🌟 Acknowledges their desire to modify preferences with understanding
2. ✨ Shows enthusiasm about helping them get their perfect trip
3. Asks what they'd like to change with genuine interest
4. Uses emojis naturally to keep it friendly
5. Sounds like you're genuinely happy to help them adjust

Keep it conversational, warm and encouraging.

RESPOND ONLY WITH THE MODIFICATION RESPONSE:
"""
            
            response = await self.llm_service.generate_text(prompt, model="generator")
            return {
                'text': response.strip(),
                'type': 'modification'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate modification response: {e}")
            return {
                'text': "Bien sûr ! Que souhaitez-vous modifier dans vos préférences ?",
                'type': 'modification'
            }
    
    async def _generate_general_response(self, context: PipelineContext) -> Dict[str, Any]:
        """Generate general conversation response"""
        try:
            # Check if we need more information
            preference_count = len(context.user_preferences)
            
            if preference_count < 2:
                # Need more preferences
                prompt = f"""
You are ASIA.fr Agent, a friendly and enthusiastic French travel specialist with a warm personality like Layla.ai. You're passionate about helping people discover amazing Asian destinations and you show genuine excitement about their travel dreams.

CURRENT PREFERENCES: {json.dumps(context.user_preferences, indent=2, ensure_ascii=False)}
USER INPUT: {context.user_input}

Generate a warm, friendly response in French that:
• Uses emojis naturally to express enthusiasm and warmth 🌟✨
• Acknowledges their input with genuine interest
• Asks for missing preferences using bullet points (•) with line breaks
• Shows excitement about helping them plan their dream trip
• Uses a conversational, friendly tone like talking to a friend
• Provides helpful examples with enthusiasm

IMPORTANT FORMATTING RULES:
• Use bullet points (•) instead of numbers
• Add line breaks after each bullet point
• Make each bullet point on its own line
• Include relevant emojis to make it more engaging
• Keep it conversational, warm and encouraging

Example format:
• 🌍 Première question avec ligne de retour

• ⏱️ Deuxième question avec ligne de retour

• 💰 Troisième question avec ligne de retour

RESPOND ONLY WITH THE RESPONSE TEXT:
"""
            else:
                # Have enough preferences, ask for confirmation
                prompt = f"""
You are ASIA.fr Agent, a friendly and enthusiastic French travel specialist with a warm personality like Layla.ai. You're excited to help them find their perfect Asian adventure!

CURRENT PREFERENCES: {json.dumps(context.user_preferences, indent=2, ensure_ascii=False)}
USER INPUT: {context.user_input}

Generate a warm, enthusiastic response in French that:
1. 🌟 Summarizes their preferences with excitement
2. ✨ Shows genuine enthusiasm about finding them the perfect offers
3. 🎯 Asks for confirmation to show offers with warmth
4. Uses emojis naturally to express your excitement
5. Sounds like you're genuinely happy to help them

Keep it friendly, warm and encouraging - like talking to a friend!

RESPOND ONLY WITH THE RESPONSE TEXT:
"""
            
            response = await self.llm_service.generate_text(prompt, model="generator")
            formatted_response = self._format_with_bullet_points(response.strip())
            return {
                'text': formatted_response,
                'type': 'general'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate general response: {e}")
            return self._fallback_response()
    
    def _fallback_response(self) -> Dict[str, Any]:
        """Fallback response when generation fails"""
        return {
            'text': "Je suis désolé, j'ai rencontré une difficulté. Pouvez-vous reformuler votre demande ?",
            'type': 'error'
        }
    
    def _format_with_bullet_points(self, text: str) -> str:
        """Format text to ensure proper bullet points with line breaks"""
        import re
        
        # Replace "1. ", "2. ", "3. ", "4. " etc. with "• "
        text = re.sub(r'^\d+\.\s*', '• ', text, flags=re.MULTILINE)
        
        # Split text into lines and process each line
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('•'):
                # This is a bullet point line
                # Ensure the bullet point content is properly formatted
                content = line[1:].strip()
                formatted_lines.append(f"• {content}")
                formatted_lines.append("")  # Add empty line after each bullet point
            elif line:
                # Regular text line
                formatted_lines.append(line)
        
        # Join lines and clean up
        result = '\n'.join(formatted_lines)
        
        # Remove multiple consecutive empty lines
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result.strip()
    
    async def _generate_preference_summary_response(self, context: PipelineContext) -> Dict[str, Any]:
        """Generate preference summary response"""
        offers = context.get_metadata('offers', [])
        
        # Create a detailed preference summary text
        summary_text = self._create_preference_summary_text(context.user_preferences)
        
        return {
            'text': f"J'ai bien noté vos préférences de voyage. Voici un récapitulatif de ce que j'ai compris :\n\n{summary_text}\n\nSi ces préférences vous conviennent, je vais vous montrer les meilleures offres. Si vous souhaitez modifier quelque chose, dites-moi simplement ce que vous voulez changer.",
            'type': 'preference_summary',
            'offers': offers,
            'show_preference_summary': True
        }
    
    def _create_preference_summary_text(self, preferences: Dict[str, Any]) -> str:
        """Create preference summary text"""
        parts = []
        
        if preferences.get('destination'):
            parts.append(f"🌍 Destination : {preferences['destination']}")
        if preferences.get('duration'):
            parts.append(f"⏱️ Durée : {preferences['duration']}")
        if preferences.get('budget'):
            parts.append(f"💰 Budget : {preferences['budget']}")
        if preferences.get('style'):
            parts.append(f"🎯 Style : {preferences['style']}")
        if preferences.get('group_size'):
            parts.append(f"👥 Groupe : {preferences['group_size']}")
        if preferences.get('timing'):
            parts.append(f"📅 Période : {preferences['timing']}")
        
        return "\n".join(parts) if parts else "Aucune préférence spécifique détectée" 