import logging
import re
import PyPDF2
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
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
            
            # Clean the text to remove null bytes and other problematic characters
            text_content = self._clean_text(text_content)
            
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
            logger.info("Attempting OCR extraction for scanned PDF")
            text_parts = []
            
            images = convert_from_path(file_path, first_page=1, last_page=20)
            
            for page_num, image in enumerate(images, 1):
                try:
                    if image.mode != 'L':
                        image = image.convert('L')
                    
                    text = pytesseract.image_to_string(image)
                    if text.strip():
                        text_parts.append(f"--- Page {page_num} ---\n{text}")
                except Exception as e:
                    logger.warning(f"OCR failed for page {page_num}: {e}")
                    continue
            
            return '\n\n'.join(text_parts) if text_parts else ""
            
        except Exception as e:
            logger.warning(f"OCR extraction failed: {e}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text to remove characters that PostgreSQL cannot store.
        Removes null bytes and other problematic Unicode characters.
        """
        if not text:
            return ""
        
        # Remove null bytes (\x00 or \u0000)
        text = text.replace('\x00', '')
        
        # Remove other control characters except newlines and tabs
        cleaned_chars = []
        for char in text:
            # Keep printable characters, newlines, tabs, and carriage returns
            if char.isprintable() or char in ['\n', '\t', '\r']:
                cleaned_chars.append(char)
            # Replace other control characters with space
            elif ord(char) < 32:
                cleaned_chars.append(' ')
        
        cleaned_text = ''.join(cleaned_chars)
        
        # Remove excessive whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        cleaned_text = re.sub(r'\n\s+\n', '\n\n', cleaned_text)
        
        return cleaned_text.strip()