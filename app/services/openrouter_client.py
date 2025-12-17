
import logging
import time
from typing import Dict, List, Any
import requests
from config import settings, get_openrouter_api_keys

logger = logging.getLogger(__name__)


class OpenRouterClient:
    
    def __init__(self, model: str = None):
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = model or settings.openrouter_model
        self.timeout = 30
        self.session = requests.Session()
        self.api_keys = get_openrouter_api_keys()
        self.current_key_index = 0
        self.exhausted_keys = set()
    
    def get_current_api_key(self) -> str:
        if not self.api_keys:
            raise OpenRouterError("No OpenRouter API keys configured")
        
        available_keys = [key for key in self.api_keys if key not in self.exhausted_keys]
        if not available_keys:
            logger.warning("All API keys exhausted, resetting exhausted keys list")
            self.exhausted_keys.clear()
            available_keys = self.api_keys
        
        if self.current_key_index >= len(available_keys):
            self.current_key_index = 0
        
        return available_keys[self.current_key_index]
    
    def rotate_api_key(self):
        current_key = self.get_current_api_key()
        self.exhausted_keys.add(current_key)
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.info(f"Rotated to next API key (index: {self.current_key_index})")
    
    def chat_completion(self, messages: List[Dict[str, str]], max_tokens: int = None) -> Dict[str, Any]:
        if not self.api_keys:
            raise OpenRouterError("No OpenRouter API keys configured")
        
        max_key_attempts = len(self.api_keys)
        
        for key_attempt in range(max_key_attempts):
            current_api_key = self.get_current_api_key()
            api_key_preview = current_api_key[:8] + "..." if len(current_api_key) > 8 else "short_key"
            logger.info(f"Using OpenRouter API key: {api_key_preview} (attempt {key_attempt + 1}/{max_key_attempts})")
            
            headers = {
                'Authorization': f'Bearer {current_api_key}',
                'HTTP-Referer': settings.openrouter_site_url,
                'X-Title': settings.openrouter_site_name,
                'Content-Type': 'application/json',
            }
            
            payload = {
                'model': self.model,
                'messages': messages,
                'provider': {'sort': 'throughput'}
            }
            
            if max_tokens:
                payload['max_tokens'] = max_tokens
            
            if settings.openrouter_enable_reasoning and 'grok' in self.model.lower():
                payload['extra_body'] = {"reasoning": {"enabled": True}}
            
            for attempt in range(3):
                try:
                    start_time = time.time()
                    
                    response = self.session.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=self.timeout
                    )
                    
                    processing_time = time.time() - start_time
                    
                    if response.status_code == 429:
                        if attempt < 2:
                            wait_time = (2 ** attempt) * 1
                            logger.warning(f"Rate limited, retrying in {wait_time}s...")
                            time.sleep(wait_time)
                            continue
                        self.rotate_api_key()
                        break
                    
                    if response.status_code == 401:
                        self.rotate_api_key()
                        break
                    
                    response.raise_for_status()
                    
                    result = response.json()
                    result['processing_time'] = processing_time
                    return result
                    
                except requests.exceptions.RequestException as e:
                    if attempt < 2:
                        wait_time = (2 ** attempt) * 1
                        logger.warning(f"Network error, retrying in {wait_time}s: {e}")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Network error after retries with key {api_key_preview}: {e}")
                        break
        
        raise OpenRouterError("All API keys exhausted or failed")
    
    def get_api_key_status(self) -> Dict[str, Any]:
        return {
            "total_keys": len(self.api_keys),
            "current_key_index": self.current_key_index,
            "exhausted_keys": len(self.exhausted_keys),
            "available_keys": len(self.api_keys) - len(self.exhausted_keys),
            "current_key_preview": self.get_current_api_key()[:8] + "..." if self.api_keys else "None"
        }
    
    def reset_exhausted_keys(self):
        self.exhausted_keys.clear()
        logger.info("Reset all exhausted API keys")
    
    def extract_response_content(self, api_response: Dict[str, Any]) -> str:
        try:
            choices = api_response.get('choices', [])
            if not choices:
                raise OpenRouterError("No choices in API response")
            
            message = choices[0].get('message', {})
            content = message.get('content', '')
            
            if not content:
                raise OpenRouterError("Empty content in API response")
            
            reasoning_details = message.get('reasoning_details')
            if reasoning_details and settings.openrouter_enable_reasoning:
                try:
                    if isinstance(reasoning_details, dict):
                        logger.info(f"Model reasoning tokens: {reasoning_details.get('reasoning_tokens', 'N/A')}")
                    elif isinstance(reasoning_details, list) and reasoning_details:
                        logger.info(f"Model reasoning details: {len(reasoning_details)} items")
                except Exception:
                    pass
            
            return content.strip()
            
        except KeyError as e:
            raise OpenRouterError(f"Invalid response structure: {e}")
        except Exception as e:
            raise OpenRouterError(f"Error extracting response content: {e}")
    
    def extract_full_response(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        try:
            choices = api_response.get('choices', [])
            if not choices:
                raise OpenRouterError("No choices in API response")
            
            message = choices[0].get('message', {})
            
            result = {
                'content': message.get('content', '').strip(),
                'reasoning_details': message.get('reasoning_details'),
                'processing_time': api_response.get('processing_time', 0)
            }
            
            return result
            
        except KeyError as e:
            raise OpenRouterError(f"Invalid response structure: {e}")
        except Exception as e:
            raise OpenRouterError(f"Error extracting full response: {e}")


class OpenRouterError(Exception):
    pass