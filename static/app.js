// Document Query System JavaScript

class DocumentQueryApp {
    constructor() {
        this.currentConversation = null;
        this.init();
    }

    init() {
        this.setupFileUpload();
        this.setupQuery();
        this.setupCharacterCount();
        this.setupSaveConversation();
        this.setupNewDocumentButton();
        this.setupClearSearchButtons();
        this.updateQueryButtonState();
    }

    setupNewDocumentButton() {
        const newDocButton = document.getElementById('newDocument');
        const fileInput = document.getElementById('fileInput');
        
        if (newDocButton && fileInput) {
            newDocButton.addEventListener('click', () => {
                fileInput.click();
            });
        }
    }

    setupClearSearchButtons() {
        const clearSearch1 = document.getElementById('clearSearch');
        const clearSearch2 = document.getElementById('clearSearch2');
        const uploadStatus = document.getElementById('uploadStatus');
        const uploadedFiles = document.getElementById('uploadedFiles');
        const queryResults = document.getElementById('queryResults');
        
        const clearAll = () => {
            if (uploadStatus) uploadStatus.innerHTML = '';
            if (uploadedFiles) uploadedFiles.innerHTML = '';
            if (queryResults) queryResults.innerHTML = '';
            this.updateQueryButtonState();
        };
        
        if (clearSearch1) {
            clearSearch1.addEventListener('click', clearAll);
        }
        if (clearSearch2) {
            clearSearch2.addEventListener('click', clearAll);
        }
    }

    // File Upload Functionality
    setupFileUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const uploadStatus = document.getElementById('uploadStatus');

        // Click to select files
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });

        // Drag and drop functionality
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });
    }

    async handleFiles(files) {
        const uploadStatus = document.getElementById('uploadStatus');

        if (files.length === 0) return;

        // Validate file types and sizes
        const validFiles = [];
        const allowedTypes = ['.pdf', '.docx', '.doc', '.txt', '.md', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'];
        const maxFileSize = 50 * 1024 * 1024; // 50MB

        for (const file of files) {
            const fileExt = '.' + file.name.split('.').pop().toLowerCase();

            if (!allowedTypes.includes(fileExt)) {
                this.showStatus(uploadStatus, `File ${file.name} has unsupported type. Allowed: ${allowedTypes.join(', ')}`, 'error');
                return;
            }

            if (file.size > maxFileSize) {
                this.showStatus(uploadStatus, `File ${file.name} is too large. Maximum size: 50MB`, 'error');
                return;
            }

            validFiles.push(file);
        }

        // Show loading status
        this.showStatus(uploadStatus, 'Uploading files...', 'loading');

        try {
            // Upload files in batches to prevent browser crashes
            const results = [];
            const BATCH_SIZE = 3; // Upload 3 at a time

            for (let i = 0; i < validFiles.length; i += BATCH_SIZE) {
                const batch = validFiles.slice(i, i + BATCH_SIZE);
                const batchPromises = batch.map(file => this.uploadFile(file));
                const batchResults = await Promise.all(batchPromises);
                results.push(...batchResults);

                // Show progress
                this.showStatus(uploadStatus, `Uploading... ${i + batch.length}/${validFiles.length}`, 'loading');
            }

            const successCount = results.filter(r => r.success).length;
            const totalCount = results.length;

            if (successCount === totalCount) {
                this.showStatus(uploadStatus, `Successfully uploaded ${successCount} file(s)`, 'success');
                this.updateQueryButtonState();
            } else {
                this.showStatus(uploadStatus, `Uploaded ${successCount}/${totalCount} files. Some uploads failed.`, 'error');
            }
        } catch (error) {
            this.showStatus(uploadStatus, `Upload failed: ${error.message}`, 'error');
        }
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Upload failed');
            }

            const result = await response.json();
            return { success: true, result };
        } catch (error) {
            console.error(`Failed to upload ${file.name}:`, error);
            return { success: false, error: error.message };
        }
    }

    // Query Functionality
    setupQuery() {
        const queryButton = document.getElementById('queryButton');
        const queryInput = document.getElementById('queryInput');
        const queryResults = document.getElementById('queryResults');

        queryButton.addEventListener('click', () => {
            this.submitQuery();
        });

        queryInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                this.submitQuery();
            }
        });
    }

    async submitQuery() {
        const queryInput = document.getElementById('queryInput');
        const queryButton = document.getElementById('queryButton');
        const saveSection = document.getElementById('saveSection');

        const question = queryInput.value.trim();

        // Validate query
        if (!question) {
            alert('Please enter a question');
            return;
        }

        if (question.length < 3) {
            alert('Question is too short (minimum 3 characters)');
            return;
        }

        if (question.length > 1000) {
            alert('Question is too long (maximum 1000 characters)');
            return;
        }

        // Show loading state
        queryButton.disabled = true;
        queryButton.innerHTML = '<span class="loading-spinner"></span>Processing...';

        console.log('Submitting query:', question);

        try {
            // Add timeout to prevent hanging
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 seconds

            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            console.log('Response status:', response.status);

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Query error:', errorData);
                throw new Error(errorData.detail || 'Query failed');
            }

            const result = await response.json();
            console.log('Query result:', result);

            // Store conversation for saving
            this.currentConversation = {
                query: question,
                result: result
            };

            // Display results
            this.displayQueryResult(result);

            // Show save section
            saveSection.style.display = 'block';

        } catch (error) {
            console.error('Query submission error:', error);

            // Better error messages
            let userMessage = 'An error occurred. Please try again.';

            if (error.name === 'AbortError') {
                userMessage = 'Request timed out. Please try again.';
            } else if (error.message.includes('fetch')) {
                userMessage = 'Network error. Check your internet connection.';
            } else if (error.message.includes('timeout')) {
                userMessage = 'Request timed out. The server took too long to respond.';
            } else if (error.message) {
                userMessage = error.message;
            }

            this.showQueryError(userMessage);
        } finally {
            // Reset button
            queryButton.disabled = false;
            queryButton.innerHTML = 'Submit Query';
        }
    }

    displayQueryResult(result) {
        const queryResults = document.getElementById('queryResults');

        const resultDiv = document.createElement('div');
        resultDiv.className = 'query-result';

        // Add timestamp
        const timestamp = new Date().toLocaleString();

        resultDiv.innerHTML = `
            <div class="query-timestamp">${this.escapeHtml(timestamp)}</div>
            <div class="query-question"><strong>Q:</strong> ${this.escapeHtml(this.currentConversation.query)}</div>
            <div class="query-answer"><strong>A:</strong> ${this.formatAnswer(result.answer)}</div>
            <div class="query-sources">
                <h4>Source Documents:</h4>
                <ul class="source-list">
                    ${result.source_documents.map(doc => `<li>${this.escapeHtml(doc)}</li>`).join('')}
                </ul>
            </div>
            <div class="processing-time">Processing time: ${result.processing_time.toFixed(2)}s</div>
        `;

        // Keep previous results, add new one at top
        queryResults.insertBefore(resultDiv, queryResults.firstChild);
    }

    formatAnswer(answer) {
        // SECURITY FIX: Escape HTML first, then format
        const safeAnswer = this.escapeHtml(answer);

        // Now do formatting on the safe text
        const formatted = safeAnswer
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');

        return `<p>${formatted}</p>`;
    }

    escapeHtml(text) {
        // Create safe text by escaping HTML
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showQueryError(message) {
        const queryResults = document.getElementById('queryResults');
        queryResults.innerHTML = `
            <div class="query-result status-error">
                <strong>Error:</strong> ${this.escapeHtml(message)}
            </div>
        `;
    }

    // Save Conversation Functionality
    setupSaveConversation() {
        const saveNotion = document.getElementById('saveNotion');
        const saveObsidian = document.getElementById('saveObsidian');

        saveNotion.addEventListener('click', () => {
            this.saveConversation('notion');
        });

        saveObsidian.addEventListener('click', () => {
            this.saveConversation('obsidian');
        });
    }

    async saveConversation(platform) {
        if (!this.currentConversation) {
            alert('No conversation to save');
            return;
        }

        const saveStatus = document.getElementById('saveStatus');
        const button = document.getElementById(`save${platform.charAt(0).toUpperCase() + platform.slice(1)}`);

        // Show loading state
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<span class="loading-spinner"></span>Saving...';

        try {
            const response = await fetch('/save-conversation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    platform: platform,
                    conversation: this.currentConversation
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Save failed');
            }

            const result = await response.json();
            this.showStatus(saveStatus, result.message, 'success');

        } catch (error) {
            this.showStatus(saveStatus, `Failed to save to ${platform}: ${error.message}`, 'error');
        } finally {
            // Reset button
            button.disabled = false;
            button.innerHTML = originalText;
        }
    }

    updateQueryButtonState() {
        const queryButton = document.getElementById('queryButton');
        const uploadStatus = document.getElementById('uploadStatus');

        // Check if files were successfully uploaded
        const hasUploadedFiles = uploadStatus.textContent.includes('Successfully uploaded');

        queryButton.disabled = !hasUploadedFiles;

        if (!hasUploadedFiles) {
            queryButton.title = 'Please upload files first';
        } else {
            queryButton.title = '';
        }
    }

    // Utility Functions
    showStatus(element, message, type) {
        element.innerHTML = this.escapeHtml(message);
        element.className = `status-${type}`;
        element.style.display = 'block';

        // Auto-hide only save conversation success messages after 5 seconds
        // Keep upload success messages visible
        if (type === 'success' && element.id === 'saveStatus') {
            setTimeout(() => {
                element.style.display = 'none';
            }, 5000);
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DocumentQueryApp();
});