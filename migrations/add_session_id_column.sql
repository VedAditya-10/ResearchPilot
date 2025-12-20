-- Migration: Add session_id column to documents table
-- Date: 2025-12-20
-- Purpose: Enable session-based document filtering

-- Add session_id column to documents table
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS session_id TEXT;

-- Create index on session_id for faster queries
CREATE INDEX IF NOT EXISTS idx_documents_session_id 
ON documents(session_id);

-- Optional: Add comment to explain the column
COMMENT ON COLUMN documents.session_id IS 'Session identifier to isolate documents by browser session';
