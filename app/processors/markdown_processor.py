
from app.processors.document_processor import DocumentProcessor, ProcessingError
from app.models.data_models import ProcessedDocument


class MarkdownProcessor(DocumentProcessor):
    
    def can_process(self, file_path: str, file_type: str) -> bool:
        markdown_types = ['.md', '.markdown', '.mdown', '.mkd']
        return file_type.lower() in markdown_types or file_type == 'text/markdown'
    
    def process_document(self, file_path: str, filename: str) -> ProcessedDocument:
        try:
            file_info = self._get_file_info(file_path, filename)
            text_content = self._read_markdown_file(file_path)
            
            return ProcessedDocument(
                filename=filename,
                file_type=file_info["file_extension"],
                content=text_content,
                file_size=file_info["file_size_bytes"],
                metadata={"processor": "MarkdownProcessor"}
            )
            
        except Exception as e:
            raise ProcessingError(f"Failed to process Markdown {filename}: {str(e)}")
    
    def _read_markdown_file(self, file_path: str) -> str:
        try:
            for encoding in ['utf-8', 'utf-16', 'latin-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ProcessingError("Could not decode file")
            
            if not content.strip():
                return "Empty Markdown file."
            
            # Basic cleaning
            lines = [line.strip() for line in content.split('\n')]
            cleaned_lines = []
            
            for line in lines:
                if line or (cleaned_lines and cleaned_lines[-1]):
                    cleaned_lines.append(line)
            
            result = '\n'.join(cleaned_lines)
            
            # Remove excessive newlines
            while '\n\n\n' in result:
                result = result.replace('\n\n\n', '\n\n')
            
            return result.strip()
            
        except Exception as e:
            raise ProcessingError(f"Failed to read Markdown file: {str(e)}")