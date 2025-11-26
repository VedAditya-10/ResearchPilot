
import os
from abc import ABC, abstractmethod
from typing import Optional
from app.models.data_models import ProcessedDocument


class DocumentProcessor(ABC):
    
    @abstractmethod
    def can_process(self, file_path: str, file_type: str) -> bool:
        pass
    
    @abstractmethod
    def process_document(self, file_path: str, filename: str) -> ProcessedDocument:
        pass
    
    def _get_file_info(self, file_path: str, filename: str) -> dict:
        try:
            file_size = os.path.getsize(file_path)
            file_extension = os.path.splitext(filename)[1].lower()
            
            return {
                "file_extension": file_extension,
                "file_size_bytes": file_size
            }
        except Exception:
            return {
                "file_extension": "",
                "file_size_bytes": 0
            }


class DocumentProcessorFactory:
    
    def __init__(self):
        self._processors = []
    
    def register_processor(self, processor: DocumentProcessor):
        self._processors.append(processor)
    
    def get_processor(self, file_path: str, file_type: str) -> Optional[DocumentProcessor]:
        for processor in self._processors:
            if processor.can_process(file_path, file_type):
                return processor
        return None


class ProcessingError(Exception):
    pass