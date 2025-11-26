
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid


@dataclass
class ProcessedDocument:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    file_type: str = ""
    content: str = ""
    upload_date: datetime = field(default_factory=datetime.now)
    file_size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "file_type": self.file_type,
            "content": self.content,
            "upload_date": self.upload_date.isoformat(),
            "file_size": self.file_size,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessedDocument":
        # Handle datetime conversion
        upload_date = data.get("upload_date")
        if isinstance(upload_date, str):
            upload_date = datetime.fromisoformat(upload_date)
        elif upload_date is None:
            upload_date = datetime.now()
            
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            filename=data.get("filename", ""),
            file_type=data.get("file_type", ""),
            content=data.get("content", ""),
            upload_date=upload_date,
            file_size=data.get("file_size", 0),
            metadata=data.get("metadata", {})
        )


@dataclass
class QueryResponse:
    answer: str = ""
    source_documents: List[str] = field(default_factory=list)
    confidence_score: Optional[float] = None
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "source_documents": self.source_documents,
            "confidence_score": self.confidence_score,
            "processing_time": self.processing_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QueryResponse":
        return cls(
            answer=data.get("answer", ""),
            source_documents=data.get("source_documents", []),
            confidence_score=data.get("confidence_score"),
            processing_time=data.get("processing_time", 0.0)
        )


@dataclass
class Conversation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query: str = ""
    response: QueryResponse = field(default_factory=QueryResponse)
    timestamp: datetime = field(default_factory=datetime.now)
    source_documents: List[str] = field(default_factory=list)
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "query": self.query,
            "response": self.response.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "source_documents": self.source_documents,
            "session_id": self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        # Handle datetime conversion
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()
        
        # Handle QueryResponse conversion
        response_data = data.get("response", {})
        if isinstance(response_data, dict):
            response = QueryResponse.from_dict(response_data)
        else:
            response = QueryResponse()
            
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            query=data.get("query", ""),
            response=response,
            timestamp=timestamp,
            source_documents=data.get("source_documents", []),
            session_id=data.get("session_id")
        )
    
    def format_for_notion(self) -> Dict[str, Any]:
        return {
            "title": f"Query: {self.query[:50]}..." if len(self.query) > 50 else f"Query: {self.query}",
            "content": {
                "query": self.query,
                "answer": self.response.answer,
                "source_documents": self.source_documents,
                "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "processing_time": f"{self.response.processing_time:.2f}s"
            }
        }
    
    def format_for_obsidian(self) -> Dict[str, Any]:
        # Create markdown content
        markdown_content = f"""# Query Session - {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}

## Query
{self.query}

## Answer
{self.response.answer}

## Source Documents
{chr(10).join(f"- {doc}" for doc in self.source_documents)}

## Metadata
- Processing Time: {self.response.processing_time:.2f}s
- Session ID: {self.session_id or "N/A"}
- Confidence Score: {self.response.confidence_score or "N/A"}
"""
        
        return {
            "filename": f"query-{self.timestamp.strftime('%Y%m%d-%H%M%S')}.md",
            "content": markdown_content
        }