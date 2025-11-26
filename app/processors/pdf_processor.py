
import logging
import io
import PyPDF2
import pdfplumber
import pytesseract
from PIL import Image
from app.processors.document_processor import DocumentProcessor, ProcessingError
from app.models.data_models import ProcessedDocument

logger = logging.getLogger(__name__)


class PDFProcessor(DocumentProcessor):
    
    def can_process(self, file_path: str, file_type: str) -> bool:
        return file_type.lower() in ['.pdf', 'application/pdf']
    
    def process_document(self, file_path: str, filename: str) -> ProcessedDocument:
        try:
            file_info = self._get_file_info(file_path, filename)
            text_content = self._extract_text_from_pdf(file_path)
            
            return ProcessedDocument(
                filename=filename,
                file_type=file_info["file_extension"],
                content=text_content,
                file_size=file_info["file_size_bytes"],
                metadata={"processor": "PDFProcessor"}
            )
            
        except Exception as e:
            raise ProcessingError(f"Failed to process PDF {filename}: {str(e)}")
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        # Try pdfplumber first
        text = self._extract_with_pdfplumber(file_path)
        if text.strip():
            return text
        
        # Try PyPDF2 as fallback
        text = self._extract_with_pypdf2(file_path)
        if text.strip():
            return text
        
        # Try OCR as last resort
        text = self._extract_with_ocr(file_path)
        if text.strip():
            return text
        
        return "No readable text content found in this PDF."
    
    def _extract_with_pdfplumber(self, file_path: str) -> str:
        try:
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return '\n\n'.join(text_parts)
        except Exception:
            return ""
    
    def _extract_with_pypdf2(self, file_path: str) -> str:
        try:
            text_parts = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return '\n\n'.join(text_parts)
        except Exception:
            return ""
    
    def _extract_with_ocr(self, file_path: str) -> str:
        try:
            import fitz  # PyMuPDF
            
            text_parts = []
            pdf_document = fitz.open(file_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                
                ocr_text = pytesseract.image_to_string(image)
                if ocr_text.strip():
                    text_parts.append(ocr_text)
            
            pdf_document.close()
            return '\n\n'.join(text_parts)
            
        except ImportError:
            logger.warning("PyMuPDF not available for OCR")
            return ""
        except Exception as e:
            logger.warning(f"OCR extraction failed: {e}")
            return ""