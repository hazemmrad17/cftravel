"""
Enhanced Preference Extractor Component for ASIA.fr Agent
Enhanced version that inherits from original PreferenceExtractorComponent
Adds date and budget intelligence while preserving original functionality
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .preference_extractor import PreferenceExtractorComponent

class EnhancedPreferenceExtractorComponent(PreferenceExtractorComponent):
    """Enhanced preference extractor that inherits from original and adds advanced features"""
    
    def __init__(self, llm_service, memory_service):
        # Call parent constructor to preserve original functionality
        super().__init__(llm_service, memory_service)
        
        # Add enhanced features
        self.current_date = datetime.now()
        
        # Override component name and priority
        self.name = "EnhancedPreferenceExtractor"
        self.priority = 90
        
        # Enhanced patterns for better extraction
        self.destination_patterns = [
            r'\b(japon|japan|japanese|nippon)\b',
            r'\b(philippines|philippine)\b',
            r'\b(thailand|thaïlande|thaï|siam)\b',
            r'\b(vietnam|vietnamien)\b',
            r'\b(china|chine|chinois)\b',
            r'\b(india|inde|indien)\b',
            r'\b(indonesia|indonésie|indonésien)\b',
            r'\b(malaysia|malaisie|malaisien)\b',
            r'\b(singapore|singapour|singapourien)\b',
            r'\b(cambodia|cambodge|cambodgien)\b',
            r'\b(laos|laotien)\b',
            r'\b(myanmar|myanmarais|birmanie)\b',
            r'\b(sri lanka|sri lankais|ceylan)\b',
            r'\b(nepal|népal|népalais)\b',
            r'\b(bhutan|bhoutan|bhoutanais)\b',
            r'\b(mongolia|mongolie|mongol)\b',
            r'\b(maldives|maldive)\b',
            r'\b(australia|australie)\b'
        ]
        
        # Activity and experience patterns for semantic matching
        self.activity_patterns = [
            r'\b(plage|beach|bord de mer)\b',
            r'\b(culture|culturel|temple|monument)\b',
            r'\b(aventure|adventure|trek|randonnée)\b',
            r'\b(détente|relaxation|spa|bien-être)\b',
            r'\b(gastronomie|cuisine|food|restaurant)\b',
            r'\b(sport|activité|yoga|plongée)\b',
            r'\b(visite|découverte|exploration)\b',
            r'\b(shopping|achats|marché)\b',
            r'\b(nature|paysage|montagne|jungle)\b',
            r'\b(ville|urbain|métropole)\b',
            r'\b(campagne|rural|village)\b',
            r'\b(île|island|tropical)\b',
            r'\b(désert|desert)\b',
            r'\b(neige|snow|ski)\b'
        ]
        
        # Accommodation patterns
        self.accommodation_patterns = [
            r'\b(hôtel|hotel)\b',
            r'\b(resort|station)\s+balnéaire\b',
            r'\b(bungalow|villa|suite|chalet)\b',
            r'\b(5\s*étoiles?|5\s*stars?|luxe)\b',
            r'\b(4\s*étoiles?|4\s*stars?)\b',
            r'\b(3\s*étoiles?|3\s*stars?)\b',
            r'\b(luxe|premium|standard|économique)\s+(hôtel|hotel)\b',
            r'\b(lodge|auberge|guesthouse)\b'
        ]
    
    async def process(self, context):
        """Enhanced process that uses original logic + date/budget intelligence"""
        try:
            self.logger.info(f"🔍 Enhanced preference extraction for: {context.user_input}")
            
            # First, use the original preference extraction logic
            original_context = await super().process(context)
            
            # Then enhance with date and budget intelligence
            enhanced_preferences = await self._enhance_preferences_with_intelligence(original_context)
            
            # Update context with enhanced preferences
            context.user_preferences = enhanced_preferences
            
            # Store in memory
            self.memory_service.update_preferences(
                context.conversation_id, 
                enhanced_preferences
            )
            
            self.logger.info(f"🔍 Enhanced preferences: {enhanced_preferences}")
            
            return context
            
        except Exception as e:
            self.log_error(context, e)
            # Fallback to original preference extraction
            return await super().process(context)
    
    async def _enhance_preferences_with_intelligence(self, context) -> Dict[str, Any]:
        """Enhance preferences with date and budget intelligence"""
        try:
            preferences = context.user_preferences.copy()
            
            # Process dates intelligently if present
            if 'travel_dates' in preferences and preferences['travel_dates']:
                processed_dates = self._process_dates_intelligently(preferences['travel_dates'])
                if processed_dates:
                    preferences['travel_dates'] = processed_dates
            
            # Process budget intelligently if present
            if 'budget_amount' in preferences and preferences['budget_amount']:
                processed_budget = self._process_budget_intelligently(preferences['budget_amount'])
                if processed_budget:
                    preferences['budget_amount'] = processed_budget
            
            # Extract additional preferences from user input
            additional_preferences = self._extract_additional_preferences(context.user_input)
            
            # Merge additional preferences
            for key, value in additional_preferences.items():
                if value and value != "":
                    if key == "activities" and isinstance(value, list):
                        # Merge activities lists
                        existing_activities = preferences.get("activities", [])
                        preferences["activities"] = list(set(existing_activities + value))
                    else:
                        preferences[key] = value
            
            return preferences
            
        except Exception as e:
            self.logger.error(f"❌ Preference enhancement failed: {e}")
            return context.user_preferences
    
    def _extract_additional_preferences(self, user_input: str) -> Dict[str, Any]:
        """Extract additional preferences using enhanced patterns"""
        additional_preferences = {}
        
        # Extract activities
        activities = []
        for pattern in self.activity_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                activity = re.search(pattern, user_input, re.IGNORECASE).group(1)
                activities.append(activity)
        
        if activities:
            additional_preferences['activities'] = activities
        
        # Extract accommodation preferences
        for pattern in self.accommodation_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                accommodation = re.search(pattern, user_input, re.IGNORECASE).group(1)
                additional_preferences['accommodation_type'] = accommodation
                break
        
        return additional_preferences
    
    def _process_dates_intelligently(self, date_input: str) -> Optional[str]:
        """Process dates intelligently with current date awareness"""
        try:
            if not date_input:
                return None
            
            current_date = self.current_date
            current_year = current_date.year
            
            # Handle relative dates
            if "prochain" in date_input.lower() or "next" in date_input.lower():
                if "mois" in date_input.lower() or "month" in date_input.lower():
                    next_month = current_date + timedelta(days=30)
                    return next_month.strftime("%m/%Y")
                elif "semaine" in date_input.lower() or "week" in date_input.lower():
                    next_week = current_date + timedelta(weeks=1)
                    return next_week.strftime("%d/%m/%Y")
            
            # Handle seasons
            season_mapping = {
                "printemps": "03-05",
                "spring": "03-05",
                "été": "06-08",
                "summer": "06-08",
                "automne": "09-11",
                "fall": "09-11",
                "autumn": "09-11",
                "hiver": "12-02",
                "winter": "12-02"
            }
            
            for season, months in season_mapping.items():
                if season in date_input.lower():
                    return f"{season} {current_year}"
            
            # Handle specific months
            month_mapping = {
                "janvier": "01", "january": "01",
                "février": "02", "february": "02",
                "mars": "03", "march": "03",
                "avril": "04", "april": "04",
                "mai": "05", "may": "05",
                "juin": "06", "june": "06",
                "juillet": "07", "july": "07",
                "août": "08", "august": "08",
                "septembre": "09", "september": "09",
                "octobre": "10", "october": "10",
                "novembre": "11", "november": "11",
                "décembre": "12", "december": "12"
            }
            
            for month_name, month_num in month_mapping.items():
                if month_name in date_input.lower():
                    return f"{month_num}/{current_year}"
            
            # Handle specific date formats
            date_patterns = [
                r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/YYYY or MM/DD/YYYY
                r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY or MM-DD-YYYY
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_input)
                if match:
                    return match.group(0)
            
            # If no specific processing, return as is
            return date_input
            
        except Exception as e:
            self.logger.error(f"❌ Date processing failed: {e}")
            return date_input
    
    def _process_budget_intelligently(self, budget_input: str) -> Optional[str]:
        """Process budget intelligently - returns numeric amount"""
        try:
            if not budget_input:
                return None
            
            # If it's already a numeric value, return as is
            if isinstance(budget_input, (int, float)):
                return str(budget_input)
            
            budget_input_str = str(budget_input)
            
            # Handle numeric amounts
            amount_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:€|euros?)', budget_input_str)
            if amount_match:
                amount = float(amount_match.group(1).replace(',', '.'))
                return str(amount)
            
            # Handle pure numeric values
            if budget_input_str.replace('.', '').replace(',', '').isdigit():
                amount = float(budget_input_str.replace(',', '.'))
                return str(amount)
            
            return budget_input_str
            
        except Exception as e:
            self.logger.error(f"❌ Budget processing failed: {e}")
            return budget_input 