
import os
import logging
import shutil
from typing import List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from config import settings
from app.services.database_factory import get_database_service
from app.services.query_engine import QueryEngine, QueryEngineError
from app.services.notion import NotionService
from app.services.obsidian import ObsidianService
from app.processors.document_processor import DocumentProcessorFactory, ProcessingError
from app.processors.pdf_processor import PDFProcessor
from app.processors.image_processor import ImageProcessor
from app.processors.markdown_processor import MarkdownProcessor
from app.processors.doc_processor import DocProcessor
from app.models.data_models import Conversation

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Document Query System...")
    query_engine.validate_setup()
    logger.info(" System ready ")
    yield

app = FastAPI(
    title="Document Query System",
    description="Upload documents and query them using AI",
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
db_service = get_database_service()
query_engine = QueryEngine()
processor_factory = DocumentProcessorFactory()
processor_factory.register_processor(PDFProcessor())
processor_factory.register_processor(ImageProcessor())
processor_factory.register_processor(MarkdownProcessor())
processor_factory.register_processor(DocProcessor())
class QueryRequest(BaseModel):
    question: str
    api_key: Optional[str] = None
    model: Optional[str] = None
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    source_documents: List[str]
    processing_time: float

class SaveConversationRequest(BaseModel):
    platform: str
    conversation: dict


async def send_to_integration(platform: str, conversation_data: dict) -> bool:
    result = conversation_data["result"]
    query_response = QueryResponse(
        answer=result["answer"],
        source_documents=result.get("source_documents", []),
        processing_time=result.get("processing_time", 0.0)
    )
    
    conversation = Conversation(
        query=conversation_data["query"],
        response=query_response,
        source_documents=result.get("source_documents", [])
    )
    service_class = NotionService if platform == "notion" else ObsidianService
    service = service_class()
    return service.save_conversation(conversation)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.post("/upload")
def upload_file(file: UploadFile = File(...), session_id: Optional[str] = Form(None)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    processor = processor_factory.get_processor("", file_extension)
    if not processor:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
    
    file_path = os.path.join(settings.upload_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        processed_doc = processor.process_document(file_path, file.filename)
        # Set session_id on the document
        processed_doc.session_id = session_id
        logger.info(f"Uploading document with session_id: {session_id}")
        document_id = db_service.store_document(processed_doc)
        
        return {
            "message": "File uploaded and processed successfully",
            "document_id": document_id,
            "filename": file.filename,
            "content_length": len(processed_doc.content)
        }
    except ProcessingError as e:
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except PermissionError:
                import time
                time.sleep(0.1)
                try:
                    os.remove(file_path)
                except PermissionError:
                    logger.warning(f"Could not delete temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Error deleting temporary file {file_path}: {e}")


@app.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Validate that API credentials are provided
    if not request.api_key or not request.model:
        raise HTTPException(status_code=400, detail="API Key and Model Name are required. Please configure them in Settings.")
    
    try:
        logger.info(f"Processing query with session_id: {request.session_id}")
        result = query_engine.process_query(
            request.question, 
            api_key=request.api_key, 
            model=request.model,
            session_id=request.session_id
        )
        return QueryResponse(
            answer=result.answer,
            source_documents=result.source_documents,
            processing_time=result.processing_time
        )
    except QueryEngineError as e:
        # Return specific error message from query engine
        error_message = str(e)
        
        # Make error messages more user-friendly
        if "Invalid OpenRouter API Key" in error_message or "401" in error_message:
            raise HTTPException(status_code=401, detail="Invalid API Key. Please check your OpenRouter API key.")
        elif "All API keys exhausted" in error_message:
            raise HTTPException(status_code=429, detail="API key exhausted or rate limited. Please wait or use a different key.")
        elif "No documents available" in error_message:
            raise HTTPException(status_code=404, detail="No documents found. Please upload documents first.")
        else:
            # Return the original error message for other cases
            raise HTTPException(status_code=500, detail=error_message)
    except Exception as e:
        logger.error(f"Unexpected error in query endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/api-status")
def get_api_status():
    try:
        api_key_status = query_engine.openrouter_client.get_api_key_status()
        return {
            "openrouter_status": api_key_status,
            "message": f"{api_key_status['available_keys']} of {api_key_status['total_keys']} API keys available"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get API status: {str(e)}")

@app.post("/reset-api-keys")
def reset_api_keys():
    try:
        query_engine.openrouter_client.reset_exhausted_keys()
        return {"message": "All API keys have been reset and are now available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset API keys: {str(e)}")

@app.post("/save-conversation")
async def save_conversation(request: SaveConversationRequest):
    if not settings.mcp_enabled:
        raise HTTPException(status_code=400, detail="Saving conversations is not enabled")
    
    platform = request.platform.lower()
    if platform not in ["notion", "obsidian"]:
        raise HTTPException(status_code=400, detail="Platform must be 'notion' or 'obsidian'")
    
    success = await send_to_integration(platform, request.conversation)
    if success:
        return {"message": f"Conversation saved to {platform.title()} successfully"}
    else:
        raise HTTPException(status_code=422, detail=f"Failed to save to {platform.title()}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug
    )