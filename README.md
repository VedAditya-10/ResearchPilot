## ResearchPilot 
link: https://researchpilot-dozq.onrender.com

A small web app that lets you **upload documents** (PDF, Word, Markdown, images) and then **ask questions** about them using an LLM via OpenRouter. It extracts text from your files, stores it in a database, and answers queries based only on your uploaded content.


---

## What It Does

- Upload documents (drag-and-drop or file picker).
- Extracts text from:
  - PDFs (including OCR fallback),
  - Images (OCR via Tesseract),
  - Markdown files,
  - Word documents (`.doc` / `.docx`).
- Stores processed text in **Supabase**.
- Lets you type questions in the web UI and:
  - Finds relevant documents,
  - Sends context + question to an **OpenRouter** model (e.g. Grok),
  - Returns an answer with a list of source documents.
- Optional: save the last Q&A as a markdown note in **Obsidian** (via its local REST API).

---

## Tech Stack

- **Backend**
  - Python, FastAPI
  - Supabase (Postgres + `supabase-py`)
  - OpenRouter API client for LLM calls
  - PDF processing: `pdfplumber`, `PyPDF2`, `PyMuPDF` + `pytesseract` (OCR)
  - Image OCR: `Pillow`, `pytesseract`
  - Word / Markdown: `python-docx`, `docx2txt`

- **Frontend**
  - Plain HTML, CSS, and vanilla JavaScript
  - Simple single-page UI served by FastAPI (`/static`)

---

## Installation & Setup

1. **Clone the repo & enter the folder**
  
   git clone <your-repo-url>
   cd <your-repo-name>
   2. **Create and activate a virtual environment (recommended)**
  
   python -m venv .venv
   .venv\Scripts\activate  # on Windows
   # or: source .venv/bin/activate  # on macOS/Linux
   3. **Install dependencies**
  
   pip install -r requirements.txt
   4. **Configure environment variables** (in a `.env` file or your shell):
   - OpenRouter:
     - `OPENROUTER_API_KEY` or `OPENROUTER_API_KEYS`
   - Supabase:
     - `DATABASE_TYPE=supabase`
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
   - Optional Obsidian:
     - `OBSIDIAN_API_URL` (default `http://localhost:27123`)
     - `OBSIDIAN_API_KEY`

5. **Run the app**
  
   python main.py
   6. **Open in your browser**
   - Go to `http://localhost:8000/` to upload documents and ask questions.
