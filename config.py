from typing import Optional, List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    
    openrouter_api_key: Optional[str] = None
    openrouter_api_keys: Optional[str] = None
    openrouter_model: str = "x-ai/grok-4.1-fast:free"
    openrouter_enable_reasoning: bool = True
    openrouter_site_url: str = "http://localhost:8000"
    openrouter_site_name: str = "Document Query System"
    
    database_type: str = "supabase"
    max_storage_size: int = 1073741824
    
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    mcp_enabled: bool = True
    
    obsidian_api_url: str = "http://localhost:27123"
    obsidian_api_key: Optional[str] = None
    obsidian_vault_path: Optional[str] = None
    
    debug: bool = False
    log_level: str = "INFO"
    upload_dir: str = "uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


def get_openrouter_api_keys() -> List[str]:
    keys = []
    if settings.openrouter_api_keys:
        keys.extend([key.strip() for key in settings.openrouter_api_keys.split(',') if key.strip()])
    if settings.openrouter_api_key:
        keys.append(settings.openrouter_api_key)
    return list(set(keys))

def validate_settings():
    api_keys = get_openrouter_api_keys()
    if not api_keys:
        raise ValueError("At least one OpenRouter API key is required (OPENROUTER_API_KEY or OPENROUTER_API_KEYS)")
    
    if settings.database_type == "supabase":
        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY are required when using Supabase")
    else:
        raise ValueError("DATABASE_TYPE must be 'supabase'")