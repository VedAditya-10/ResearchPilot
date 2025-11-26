import logging
import requests
from datetime import datetime
from app.models.data_models import Conversation
from config import settings

logger = logging.getLogger(__name__)


class ObsidianService:
    
    def __init__(self):
        self.api_url = getattr(settings, 'obsidian_api_url', 'http://127.0.0.1:27123')
        self.api_key = getattr(settings, 'obsidian_api_key', None)
        self.vault_path = getattr(settings, 'obsidian_vault_path', None)
    
    def connect(self) -> bool:
        if not settings.mcp_enabled or not self.api_key:
            logger.warning("Obsidian integration not enabled or API key missing")
            return False
        
        try:
            # Test API connection - try Bearer token format
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Test with a simple endpoint
            # Test connection to HTTP API
            response = requests.get(f"{self.api_url}/", headers=headers, timeout=5)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Obsidian API connection failed: {e}")
            return False
    
    def disconnect(self):
        pass
    
    def save_conversation(self, conversation: Conversation) -> bool:
        if not self.api_key:
            logger.error("Obsidian API key not configured")
            return False
        
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"Document Query - {timestamp}.md"
            
            # Create markdown content
            content = f"""# Document Query - {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Question
{conversation.query}

## Answer
{conversation.response.answer}

## Source Documents
{chr(10).join(f"- {doc}" for doc in conversation.source_documents) if conversation.source_documents else "- None"}

---
*Processing time: {conversation.response.processing_time:.2f}s*
*Saved from Document Query System*
"""
            
            # API request to create note using Obsidian Local REST API format
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'text/plain'  # Obsidian expects plain text content
            }
            
            # Use the correct endpoint format for creating files
            response = requests.put(
                f"{self.api_url}/vault/{filename}",
                headers=headers,
                data=content,  # Send content as plain text, not JSON
                timeout=10
            )
            
            if response.status_code in [200, 201, 204]:  # 204 = No Content (success)
                logger.info(f"Successfully saved conversation to Obsidian: {filename}")
                return True
            else:
                logger.error(f"Failed to save to Obsidian: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Error saving conversation to Obsidian: {e}")
            return False


