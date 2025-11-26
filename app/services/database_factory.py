
from typing import Optional
from app.services.supabase_service import SupabaseService
from config import settings


class DatabaseFactory:
    
    @staticmethod
    def create_database_service():
        database_type = settings.database_type.lower()
        
        if database_type == "supabase":
            return SupabaseService()
        else:
            raise ValueError(f"Unsupported database type: {database_type}. Only 'supabase' is supported.")


_db_service = None


def get_database_service():
    global _db_service
    
    if _db_service is None:
        _db_service = DatabaseFactory.create_database_service()
        _db_service.connect()
    
    return _db_service


def close_database_service():
    global _db_service
    
    if _db_service is not None:
        _db_service.disconnect()
        _db_service = None