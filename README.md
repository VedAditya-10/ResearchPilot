<p align='center'>
  **Built with ❤️ for efficient document querying**  
</p>

# ResearchPilot

**Deployed App**: https://researchpilot-dozq.onrender.com

A document query system that lets you upload documents (PDF, Word, Markdown, images) and ask questions about them using AI. Upload your files, and get intelligent answers based on your content with automatic source citations.

---

## 🎯 How It Works

1. **Configure Your API** (First Time Setup)
   - Open the app and click on "API Settings"
   - Enter your **OpenRouter API Key** (get one free at [openrouter.ai](https://openrouter.ai))
   - Enter a **Model Name** (e.g., `mistralai/mistral-7b-instruct:free` for free tier)
   - Click "Save Settings" - these are stored in your browser session

2. **Upload Your Documents**
   - Drag and drop or click to upload PDF, Word, images, or text files
   - Files are processed and stored securely in your session

3. **Ask Questions**
   - Type any question about your documents
   - Get AI-powered answers with source citations
   - Responses are beautifully formatted with markdown

4. **Save Your Work** (Optional)
   - Export conversations to **Obsidian** or **Notion**
   - Configure integration in API Settings if needed

> **Note**: Your API key and model settings are stored in your browser's session storage and are never sent to our servers. Each browser session is isolated for privacy.

---

## ✨ Features

### Document Processing
- **Multi-format support**: PDF, DOCX, DOC, TXT, MD, PNG, JPG, JPEG, TIFF, BMP, GIF
- **Smart text extraction**: 
  - PDFs with fallback OCR for scanned documents
  - Images with Tesseract OCR
  - Automatic text cleaning (removes null bytes and problematic characters)
- **Session-based isolation**: Documents are isolated by browser session for privacy

### Intelligent Querying
- **Natural language questions**: Ask anything about your documents
- **AI-powered answers**: Uses OpenRouter models (e.g., Mistral, Grok, Claude)
- **Source citations**: Every answer includes source document references
- **Markdown formatting**: Responses are beautifully formatted with bold, italic, code blocks, and lists

### Integration Options
- **Obsidian**: Save conversations as markdown notes (optional)
- **Notion**: Export Q&A sessions (optional)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Tesseract OCR (for image/PDF OCR)
- Supabase account (free tier works)
- OpenRouter API key

### Installation

1. **Clone and setup**
   ```bash
   git clone <your-repo-url>
   cd ResearchPilot
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or: source .venv/bin/activate  # macOS/Linux
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment** (create `.env` file)
   ```env
   # Required
   DATABASE_TYPE=supabase
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   
   # Optional (can be set via UI)
   OPENROUTER_API_KEY=your_openrouter_key
   
   # Optional integrations
   OBSIDIAN_API_URL=http://localhost:27123
   OBSIDIAN_API_KEY=your_obsidian_key
   ```

4. **Setup database**
   - Create a Supabase project
   - Run the migration in SQL Editor:
   ```sql
   CREATE TABLE documents (
       id TEXT PRIMARY KEY,
       filename TEXT,
       file_type TEXT,
       content TEXT,
       upload_date TIMESTAMP,
       file_size INTEGER,
       metadata JSONB,
       session_id TEXT
   );
   
   CREATE INDEX idx_documents_session_id ON documents(session_id);
   ```

5. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

6. **Open in browser**
   - Navigate to `http://localhost:8000`
   - Configure API settings in the UI
   - Upload documents and start asking questions!

---

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenRouter API
- **Document Processing**:
  - PDFs: `pdfplumber`, `PyPDF2`, `pdf2image` + `pytesseract`
  - Images: `Pillow` + `pytesseract`
  - Word: `python-docx`, `docx2txt`

### Frontend
- **Stack**: Vanilla HTML, CSS, JavaScript
- **Features**: 
  - Session management (UUID-based)
  - Markdown rendering
  - Drag-and-drop upload
  - Real-time API configuration

---

## 📝 Usage

1. **Configure API Settings**
   - Click "API Settings" to expand
   - Enter your OpenRouter API key
   - Enter model name (e.g., `mistralai/mistral-7b-instruct:free`)
   - Click "Save Settings"

2. **Upload Documents**
   - Drag and drop files or click to browse
   - Supports batch uploads
   - Files are processed and stored automatically

3. **Ask Questions**
   - Type your question in the query box
   - Click "Search" or press Ctrl+Enter
   - View formatted answers with source citations

4. **Session Management**
   - Each browser session has a unique ID
   - Only documents from your current session are queried
   - Refresh page: session persists
   - Close tab: new session on reopen

---

## 🔧 Configuration

### API Settings (via UI)
- **OpenRouter API Key**: Required for AI queries
- **Model Name**: Choose your preferred model
- **Obsidian API** (Optional): For saving conversations

### Environment Variables
See `.env` file for all configuration options. Most settings can be configured through the web UI.

---

## 🛠️ Development

### Project Structure
```
ResearchPilot/
├── app/
│   ├── models/          # Data models
│   ├── processors/      # Document processors
│   └── services/        # Business logic
├── static/              # Frontend files
├── migrations/          # Database migrations
├── main.py             # FastAPI application
└── config.py           # Configuration
```

### Key Components
- **Session Management**: UUID-based session isolation
- **Text Cleaning**: Removes null bytes and control characters
- **Markdown Rendering**: Client-side markdown-to-HTML conversion
- **Error Handling**: Comprehensive error messages and logging

---

## 📄 License

MIT License - feel free to use and modify as needed.

---

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

---

