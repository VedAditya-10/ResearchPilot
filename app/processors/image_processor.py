import logging
from PIL import Image
import pytesseract
from app.processors.document_processor import DocumentProcessor, ProcessingError
from app.models.data_models import ProcessedDocument

logger = logging.getLogger(__name__)


class ImageProcessor(DocumentProcessor):
    
    def can_process(self, file_path: str, file_type: str) -> bool:
        image_types = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
        return file_type.lower() in image_types or file_type.startswith('image/')
    
    def process_document(self, file_path: str, filename: str) -> ProcessedDocument:
        try:
            file_info = self._get_file_info(file_path, filename)
            text_content = self._extract_text_from_image(file_path)
            
            return ProcessedDocument(
                filename=filename,
                file_type=file_info["file_extension"],
                content=text_content,
                file_size=file_info["file_size_bytes"],
                metadata={"processor": "ImageProcessor"}
            )
            
        except Exception as e:
            raise ProcessingError(f"Failed to process image {filename}: {str(e)}")
    
    def _extract_text_from_image(self, file_path: str) -> str:
        try:
            image = Image.open(file_path)
            
            # Simple preprocessing
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Try OCR
            try:
                text = pytesseract.image_to_string(image)
            except Exception as e:
                # Handle TesseractNotFoundError or other pytesseract errors
                logger.warning(f"Tesseract OCR failed: {e}")
                return f"OCR extraction failed: {str(e)}"
            
            if text.strip():
                # Basic cleaning
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                return '\n'.join(lines)
            else:
                return "No readable text found in this image."
                
        except Exception as e:
            logger.warning(f"Image processing failed: {e}")
            raise ProcessingError(f"Failed to process image: {str(e)}")