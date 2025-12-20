// Document Query System JavaScript

class DocumentQueryApp {
    constructor() {
        this.currentConversation = null;
        this.sessionId = this.getOrCreateSessionId();
        this.init();
    }

    init() {
        this.setupSettings();
        this.setupFileUpload();
        this.setupQuery();
        this.setupCharacterCount();
        this.setupSaveConversation();
        this.updateQueryButtonState();
        console.log('Session ID:', this.sessionId);
    }

    // Session Management
    getOrCreateSessionId() {
        // Check if session_id exists in sessionStorage
        let sessionId = sessionStorage.getItem('session_id');
        
        if (!sessionId) {
            // Generate a new session ID (UUID v4)
            sessionId = this.generateUUID();
            sessionStorage.setItem('session_id', sessionId);
            console.log('Created new session ID:', sessionId);
        } else {
            console.log('Using existing session ID:', sessionId);
        }
        
        return sessionId;
    }

    generateUUID() {
        // Simple UUID v4 generator
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    // Settings Functionality
    setupSettings() {
        const settingsToggle = document.getElementById('settingsToggle');
        const settingsContent = document.getElementById('settingsContent');
        const toggleIcon = document.getElementById('toggleIcon');
        const saveSettingsBtn = document.getElementById('saveSettingsBtn');
        const settingsStatus = document.getElementById('settingsStatus');

        // Load saved settings from sessionStorage
        this.loadSettings();

        // Toggle settings visibility
        if (settingsToggle) {
            settingsToggle.addEventListener('click', () => {
                settingsContent.classList.toggle('show');
                toggleIcon.classList.toggle('collapsed');
            });
        }

        // Save settings button
        if (saveSettingsBtn) {
            saveSettingsBtn.addEventListener('click', () => {
                this.saveSettings();
            });
        }

        // Password visibility toggles
        document.querySelectorAll('.toggle-visibility').forEach(btn => {
            btn.addEventListener('click', () => {
                const targetId = btn.getAttribute('data-target');
                const input = document.getElementById(targetId);
                const icon = btn.querySelector('i');
                
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        });
    }

    loadSettings() {
        const apiKeyInput = document.getElementById('apiKeyInput');
        const modelNameInput = document.getElementById('modelNameInput');
        const obsidianKeyInput = document.getElementById('obsidianKeyInput');
        const obsidianUrlInput = document.getElementById('obsidianUrlInput');

        if (apiKeyInput) apiKeyInput.value = sessionStorage.getItem('openrouter_api_key') || '';
        if (modelNameInput) modelNameInput.value = sessionStorage.getItem('openrouter_model') || '';
        if (obsidianKeyInput) obsidianKeyInput.value = sessionStorage.getItem('obsidian_api_key') || '';
        if (obsidianUrlInput) obsidianUrlInput.value = sessionStorage.getItem('obsidian_api_url') || 'http://localhost:27123';
    }

    saveSettings() {
        const apiKeyInput = document.getElementById('apiKeyInput');
        const modelNameInput = document.getElementById('modelNameInput');
        const obsidianKeyInput = document.getElementById('obsidianKeyInput');
        const obsidianUrlInput = document.getElementById('obsidianUrlInput');
        const settingsStatus = document.getElementById('settingsStatus');

        console.log('Save Settings - Input elements found:', {
            apiKeyInput: !!apiKeyInput,
            modelNameInput: !!modelNameInput,
            apiKeyValue: apiKeyInput?.value?.substring(0, 10) + '...',
            modelValue: modelNameInput?.value
        });

        const apiKey = apiKeyInput?.value?.trim() || '';
        const modelName = modelNameInput?.value?.trim() || '';

        // Validate required fields
        if (!apiKey || !modelName) {
            this.showStatus(settingsStatus, 'API Key and Model Name are required', 'error');
            return;
        }

        // Save to sessionStorage
        sessionStorage.setItem('openrouter_api_key', apiKey);
        sessionStorage.setItem('openrouter_model', modelName);
        sessionStorage.setItem('obsidian_api_key', obsidianKeyInput?.value?.trim() || '');
        sessionStorage.setItem('obsidian_api_url', obsidianUrlInput?.value?.trim() || 'http://localhost:27123');

        console.log('Settings saved to sessionStorage:', {
            api_key: sessionStorage.getItem('openrouter_api_key')?.substring(0, 10) + '...',
            model: sessionStorage.getItem('openrouter_model')
        });

        this.showStatus(settingsStatus, 'Settings saved successfully!', 'success');
        this.updateQueryButtonState();

        // Auto-hide success message
        setTimeout(() => {
            settingsStatus.style.display = 'none';
        }, 3000);
    }

    getSettings() {
        const settings = {
            api_key: sessionStorage.getItem('openrouter_api_key') || '',
            model: sessionStorage.getItem('openrouter_model') || '',
            obsidian_api_key: sessionStorage.getItem('obsidian_api_key') || '',
            obsidian_api_url: sessionStorage.getItem('obsidian_api_url') || 'http://localhost:27123'
        };
        console.log('getSettings called:', {
            api_key: settings.api_key ? settings.api_key.substring(0, 10) + '...' : 'EMPTY',
            model: settings.model || 'EMPTY'
        });
        return settings;
    }

    hasRequiredSettings() {
        const settings = this.getSettings();
        return settings.api_key && settings.model;
    }



    setupCharacterCount() {
        const queryInput = document.getElementById('queryInput');
        const charCount = document.getElementById('charCount');
        if (!queryInput || !charCount) return;
        const update = () => {
            charCount.textContent = queryInput.value.length;
        };
        queryInput.addEventListener('input', update);
        update();
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
        formData.append('session_id', this.sessionId);

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

            const settings = this.getSettings();

            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    question,
                    api_key: settings.api_key,
                    model: settings.model,
                    session_id: this.sessionId
                }),
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

        // Convert markdown to HTML (basic patterns)
        let formatted = safeAnswer;
        
        // Bold: **text** -> <strong>text</strong>
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Italic: *text* -> <em>text</em> (but not ** which is already handled)
        formatted = formatted.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
        
        // Code: `code` -> <code>code</code>
        formatted = formatted.replace(/`(.+?)`/g, '<code>$1</code>');
        
        // Numbered lists: 1. item -> <ol><li>item</li></ol>
        formatted = formatted.replace(/^(\d+)\.\s+(.+)$/gm, '<li-num data-num="$1">$2</li-num>');
        
        // Bullet lists: - item or * item -> <ul><li>item</li></ul>
        formatted = formatted.replace(/^[\-\*]\s+(.+)$/gm, '<li-bullet>$1</li-bullet>');
        
        // Convert line breaks and paragraphs
        formatted = formatted
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
        
        // Wrap consecutive list items in proper list tags
        formatted = formatted.replace(/(<li-num[^>]*>.*?<\/li-num>(\s|<br>)*)+/g, (match) => {
            const items = match.replace(/<li-num data-num="\d+">/g, '<li>').replace(/<\/li-num>/g, '</li>').replace(/<br>/g, '');
            return `<ol>${items}</ol>`;
        });
        
        formatted = formatted.replace(/(<li-bullet>.*?<\/li-bullet>(\s|<br>)*)+/g, (match) => {
            const items = match.replace(/<li-bullet>/g, '<li>').replace(/<\/li-bullet>/g, '</li>').replace(/<br>/g, '');
            return `<ul>${items}</ul>`;
        });

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

        // Check if files were successfully uploaded AND settings are configured
        const hasUploadedFiles = uploadStatus.textContent.includes('Successfully uploaded');
        const hasSettings = this.hasRequiredSettings();

        queryButton.disabled = !(hasUploadedFiles && hasSettings);

        if (!hasSettings) {
            queryButton.title = 'Please configure API settings first';
        } else if (!hasUploadedFiles) {
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