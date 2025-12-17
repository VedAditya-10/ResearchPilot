# Tesseract OCR Setup Guide

This guide will help you set up Tesseract OCR for the ResearchPilot application to enable text extraction from images and scanned PDFs.

## Installation Steps

### Windows

1. **Download the Tesseract installer**:
   - Go to [UB Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki)
   - Download the latest `.exe` installer (e.g., `tesseract-ocr-w64-setup-v5.x.x.exe`)

2. **Install Tesseract**:
   - Run the installer
   - Choose installation path (default: `C:\Program Files\Tesseract-OCR`)
   - Complete the installation

3. **Configure in your application** (if Tesseract is not in PATH):
   - Open `app/processors/image_processor.py`
   - Uncomment and set the path:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

### macOS

1. **Install using Homebrew**:
   ```bash
   brew install tesseract
   ```

2. **Verify installation**:
   ```bash
   tesseract --version
   ```

### Linux (Ubuntu/Debian)

1. **Install Tesseract**:
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr
   ```

2. **Verify installation**:
   ```bash
   tesseract --version
   ```

## Python Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- `pytesseract` - Python wrapper for Tesseract
- `pdf2image` - Convert PDF pages to images for OCR

## Testing the Setup

1. **Start the application**:
   ```bash
   uvicorn main:app --reload
   ```

2. **Upload an image with text**:
   - Go to `http://localhost:8000`
   - Upload a PNG or JPG image containing text
   - The system should now extract and index the text

3. **Query the image**:
   - Ask a question about the text in the image
   - The AI should be able to answer based on the extracted text

## Troubleshooting

### "pytesseract.TesseractNotFoundError"

**Solution**: Tesseract is not installed or not in PATH
- Windows: Set the path in `image_processor.py` (see above)
- macOS/Linux: Ensure Tesseract is installed and in PATH

### "pdf2image: convert: command not found" (Linux)

**Solution**: Install ImageMagick
```bash
sudo apt-get install imagemagick
```

### OCR is slow

**Solution**: This is normal for large images. Consider:
- Reducing image resolution before uploading
- Limiting the number of PDF pages processed (currently set to 10)

### Poor OCR accuracy

**Solution**: Improve image quality:
- Ensure good lighting and contrast
- Use high-resolution images (300+ DPI recommended)
- Avoid skewed or rotated text

## Features Enabled

After setup, the following features will work:

✅ **Image OCR**: Extract text from PNG, JPG, JPEG, TIFF, BMP images
✅ **Scanned PDF OCR**: Extract text from image-based PDFs
✅ **Text Indexing**: Extracted text is indexed and searchable
✅ **Query Support**: Ask questions about extracted text

## Performance Notes

- Image processing: ~1-2 seconds per image
- PDF OCR: ~2-5 seconds per page (limited to 10 pages)
- Text extraction is cached in the database for faster queries
