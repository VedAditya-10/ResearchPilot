
from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.data_models import ProcessedDocument


class DatabaseService(ABC):
    
    @abstractmethod
    def connect(self) -> None:
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def store_document(self, document: ProcessedDocument) -> str:
        pass
    
    @abstractmethod
    def get_all_documents(self, session_id: Optional[str] = None) -> List[ProcessedDocument]:
        pass
    
    @abstractmethod
    def search_documents(self, query: str, session_id: Optional[str] = None) -> List[ProcessedDocument]:
        pass