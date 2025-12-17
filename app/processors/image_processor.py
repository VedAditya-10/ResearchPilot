import logging
import os
import pytesseract
from PIL import Image
from app.processors.document_processor import DocumentProcessor, ProcessingError
from app.models.data_models import ProcessedDocument

logger = logging.getLogger(__name__)

# Set Tesseract path - update this to your Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ImageProcessor(DocumentProcessor):
    
    def can_process(self, file_path: str, file_type: str) -> bool:
        image_types = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
        return file_type.lower() in image_types or file_type.startswith('image/')
    
    def process_document(self, file_path: str, filename: str) -> ProcessedDocument:
        try:
            file_info = self._get_file_info(file_path, filename)
            text_content = self._extract_metadata_from_image(file_path, filename)
            
            return ProcessedDocument(
                filename=filename,
                file_type=file_info["file_extension"],
                content=text_content,
                file_size=file_info["file_size_bytes"],
                metadata={"processor": "ImageProcessor", "note": "OCR not available in cloud deployment"}
            )
            
        except Exception as e:
            raise ProcessingError(f"Failed to process image {filename}: {str(e)}")
    
    def _extract_metadata_from_image(self, file_path: str, filename: str) -> str:
        try:
            image = Image.open(file_path)
            width, height = image.size
            mode = image.mode
            format_name = image.format or "Unknown"
            file_size = self._format_file_size(self._get_file_info(file_path, filename)['file_size_bytes'])
            
            # Try to extract text using Tesseract OCR
            extracted_text = self._extract_text_with_ocr(image)
            
            if extracted_text:
                metadata_text = f"""Image File: {filename}
Format: {format_name}
Dimensions: {width} x {height} pixels
Color Mode: {mode}
File Size: {file_size}

--- Extracted Text (OCR) ---
{extracted_text}
--- End of Text ---

Note: Text was extracted using OCR and may contain inaccuracies."""
                logger.info(f"Successfully extracted text from {filename} using OCR")
            else:
                metadata_text = f"""Image File: {filename}
Format: {format_name}
Dimensions: {width} x {height} pixels
Color Mode: {mode}
File Size: {file_size}

Note: No text could be extracted from this image using OCR."""
                logger.info(f"No text found in image {filename}")
            
            return metadata_text
                
        except Exception as e:
            logger.warning(f"Could not process image {filename}: {e}")
            return f"""Image File: {filename}

Error: The image could not be processed. Please check if the file is a valid image."""
    
    def _extract_text_with_ocr(self, image: Image.Image) -> str:
        try:
            if image.mode != 'L':
                image = image.convert('L')
            
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.warning(f"OCR extraction failed: {e}")
            return ""
    
    def _format_file_size(self, size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"