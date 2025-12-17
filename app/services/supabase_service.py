
import logging
from typing import List
from supabase import create_client, Client
from app.models.data_models import ProcessedDocument
from config import settings

logger = logging.getLogger(__name__)


class SupabaseService:
    
    def __init__(self):
        self.client = None
    
    def connect(self):
        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError("Supabase URL and key are required")
        
        try:
            self.client = create_client(settings.supabase_url, settings.supabase_key)
            logger.info("Connected to Supabase")
            
        except Exception as e:
            raise ValueError(f"Supabase connection failed: {e}")
    
    def disconnect(self):
        self.client = None
    
    def store_document(self, document: ProcessedDocument) -> str:
        if not self.client:
            raise ValueError("Not connected to Supabase")
        
        try:
            document_data = document.to_dict()
            document_data["upload_date"] = document.upload_date.isoformat()
            
            result = self.client.table("documents").insert(document_data).execute()
            
            if not result.data:
                raise ValueError("Failed to insert document")
            
            return document.id
            
        except Exception as e:
            raise ValueError(f"Failed to store document: {e}")
    
    def get_all_documents(self) -> List[ProcessedDocument]:
        if not self.client:
            raise ValueError("Not connected to Supabase")
        
        try:
            result = self.client.table("documents").select("*").order("upload_date", desc=True).execute()
            return [ProcessedDocument.from_dict(doc) for doc in result.data]
            
        except Exception as e:
            raise ValueError(f"Failed to retrieve documents: {e}")
    
    def search_documents(self, query: str) -> List[ProcessedDocument]:
        if not self.client:
            raise ValueError("Not connected to Supabase")
        
        try:
            result = (self.client.table("documents")
                     .select("*")
                     .ilike("content", f"%{query}%")
                     .limit(10)
                     .execute())
            
            if not result.data:
                result = (self.client.table("documents")
                         .select("*")
                         .ilike("filename", f"%{query}%")
                         .limit(10)
                         .execute())
            
            return [ProcessedDocument.from_dict(doc) for doc in result.data]
            
        except Exception as e:
            raise ValueError(f"Search failed: {e}")