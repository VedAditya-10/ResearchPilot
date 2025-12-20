
import logging
import time
from typing import List, Optional
from app.services.openrouter_client import OpenRouterClient, OpenRouterError
from app.services.database_factory import get_database_service
from app.models.data_models import ProcessedDocument, QueryResponse

logger = logging.getLogger(__name__)


class QueryEngine:
    
    def __init__(self):
        self.openrouter_client = OpenRouterClient()
        self.max_tokens = 4000
        self.max_documents = 5
        self.db_service = None
    
    def process_query(self, question: str, api_key: Optional[str] = None, model: Optional[str] = None, session_id: Optional[str] = None) -> QueryResponse:
        start_time = time.time()
        
        try:
            relevant_docs = self._get_relevant_documents(question, session_id=session_id)
            
            if not relevant_docs:
                raise QueryEngineError("No documents available to search")
            
            context = self._build_context(relevant_docs)
            ai_response = self._generate_ai_response(question, context, api_key=api_key, model=model)
            source_docs = [doc.filename for doc in relevant_docs]
            
            return QueryResponse(
                answer=ai_response,
                source_documents=source_docs,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise QueryEngineError(f"Failed to process query: {str(e)}")
    
    def _get_relevant_documents(self, question: str, session_id: Optional[str] = None) -> List[ProcessedDocument]:
        try:
            if not self.db_service:
                self.db_service = get_database_service()
            
            search_results = self.db_service.search_documents(question, session_id=session_id)
            
            if search_results:
                return search_results[:self.max_documents]
            
            logger.info("No specific search results found, using all available documents")
            all_docs = self.db_service.get_all_documents(session_id=session_id)
            return all_docs[:self.max_documents]
                
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            logger.error("Database unavailable - please upload documents first or check your connection")
            raise QueryEngineError("No documents available to search. Please upload documents first or check your database connection.")
    
    def _build_context(self, documents: List[ProcessedDocument]) -> str:
        if not documents:
            return "No documents available."
        
        context_parts = []
        current_tokens = 0
        
        for doc in documents:
            doc_section = f"\n--- Document: {doc.filename} ---\n{doc.content}\n"
            estimated_tokens = len(doc_section) // 4
            
            if current_tokens + estimated_tokens <= self.max_tokens:
                context_parts.append(doc_section)
                current_tokens += estimated_tokens
            else:
                break
        
        return "".join(context_parts)
    
    def _generate_ai_response(self, question: str, context: str, api_key: Optional[str] = None, model: Optional[str] = None) -> str:
        try:
            system_prompt = """You are a helpful AI assistant that answers questions based on provided documents. 

Instructions:
- Answer using only information from the provided documents
- If the answer is not in the documents, say so clearly
- Be concise but comprehensive
- Simplify topics or give easy to understand explainations, if user ask for it
- Quote relevant parts when helpful"""
            
            user_prompt = f"""Documents:
{context}

Question: {question}

Answer based on the documents above:"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Use runtime credentials if provided
            api_response = self.openrouter_client.chat_completion(
                messages, 
                max_tokens=1000,
                api_key=api_key,
                model=model
            )
            return self.openrouter_client.extract_response_content(api_response)
            
        except OpenRouterError as e:
            raise QueryEngineError(f"AI service error: {str(e)}")
        except Exception as e:
            raise QueryEngineError(f"Response generation failed: {str(e)}")
    
    def validate_setup(self) -> bool:
        errors = []
        
        from config import get_openrouter_api_keys
        api_keys = get_openrouter_api_keys()
        if not api_keys:
            errors.append("OpenRouter API key not configured")
        
        try:
            if not self.db_service:
                self.db_service = get_database_service()
            self.db_service.get_all_documents()
            logger.info("Database connection successful")
        except Exception as e:
            logger.warning(f"Database connection failed: {str(e)}")
            logger.warning("Application will start but database features may not work")
        
        if errors:
            raise QueryEngineError(f"Setup validation failed: {'; '.join(errors)}")
        
        return True


class QueryEngineError(Exception):
    pass