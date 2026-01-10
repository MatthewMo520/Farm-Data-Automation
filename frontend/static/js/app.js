// Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// State
let currentClient = null;
let mediaRecorder = null;
let audioChunks = [];
let recordingStartTime = null;
let recordingInterval = null;
let currentAudioBlob = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    // Setup event listeners
    setupEventListeners();

    // Check if already logged in (session)
    checkSession();
}

// Event Listeners
function setupEventListeners() {
    // Login
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);

    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', handleTabSwitch);
    });

    // Upload
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    document.getElementById('uploadBtn').addEventListener('click', handleFileUpload);

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    uploadArea.addEventListener('drop', handleFileDrop);

    // Recording
    document.getElementById('startRecordBtn').addEventListener('click', startRecording);
    document.getElementById('stopRecordBtn').addEventListener('click', stopRecording);
    document.getElementById('submitRecordBtn').addEventListener('click', submitRecording);

    // Refresh
    document.getElementById('refreshBtn').addEventListener('click', loadRecordings);

    // Missing fields modal
    document.querySelectorAll('.close-modal, .close-btn').forEach(btn => {
        btn.addEventListener('click', closeMissingFieldsModal);
    });
}

// Client Management
function checkSession() {
    const savedClient = localStorage.getItem('currentClient');
    if (savedClient) {
        currentClient = JSON.parse(savedClient);
        showDashboard();
    }
}

async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        // Authenticate with backend
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        currentClient = data.client;

        // Save to session
        localStorage.setItem('currentClient', JSON.stringify(currentClient));

        showDashboard();
        showToast(`Welcome to ${currentClient.name}!`, 'success');

    } catch (error) {
        showToast('Login failed: ' + error.message, 'error');
        console.error(error);
    }
}

function showDashboard() {
    document.getElementById('loginModal').classList.add('hidden');
    document.getElementById('dashboard').classList.remove('hidden');
    document.getElementById('clientName').textContent = currentClient.name;
    loadRecordings();
}

function handleLogout() {
    currentClient = null;
    localStorage.removeItem('currentClient');
    document.getElementById('dashboard').classList.add('hidden');
    document.getElementById('loginModal').classList.remove('hidden');

    // Clear form
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
}

// Tab Management
function handleTabSwitch(e) {
    const targetTab = e.target.dataset.tab;

    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${targetTab}Tab`).classList.add('active');
}

// File Upload
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        updateUploadUI(file);
    }
}

function handleFileDrop(e) {
    e.preventDefault();
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.classList.remove('dragover');

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('audio/')) {
        document.getElementById('fileInput').files = e.dataTransfer.files;
        updateUploadUI(file);
    } else {
        showToast('Please drop an audio file', 'error');
    }
}

function updateUploadUI(file) {
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.innerHTML = `
        <svg width="64" height="64" fill="currentColor" stroke="currentColor" stroke-width="2">
            <path d="M32 8v40M16 24l16-16 16 16"/>
        </svg>
        <p>✓ ${file.name}</p>
        <span>${(file.size / 1024 / 1024).toFixed(2)} MB</span>
    `;
    document.getElementById('uploadBtn').disabled = false;
}

async function handleFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        showToast('No file selected', 'error');
        return;
    }

    if (!currentClient) {
        showToast('Please log in first', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('client_id', currentClient.id);

    try {
        document.getElementById('uploadBtn').disabled = true;
        document.getElementById('uploadBtn').textContent = 'Processing...';

        const response = await fetch(`${API_BASE_URL}/recordings/`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const result = await response.json();
        showToast('Recording uploaded successfully!', 'success');

        // Reset UI
        fileInput.value = '';
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.innerHTML = `
            <svg width="64" height="64" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M32 8v40M16 24l16-16 16 16"/>
            </svg>
            <p>Click to upload or drag and drop</p>
            <span>Supported: MP3, WAV, M4A, OGG</span>
        `;
        document.getElementById('uploadBtn').disabled = true;
        document.getElementById('uploadBtn').textContent = 'Upload & Process';

        // Refresh recordings
        await loadRecordings();

    } catch (error) {
        showToast('Upload failed: ' + error.message, 'error');
        document.getElementById('uploadBtn').disabled = false;
        document.getElementById('uploadBtn').textContent = 'Upload & Process';
    }
}

// Audio Recording
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            currentAudioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            const audioUrl = URL.createObjectURL(currentAudioBlob);
            const audioPlayback = document.getElementById('audioPlayback');
            audioPlayback.src = audioUrl;
            audioPlayback.classList.remove('hidden');
            document.getElementById('submitRecordBtn').classList.remove('hidden');
        };

        mediaRecorder.start();
        recordingStartTime = Date.now();

        // Update UI
        document.getElementById('startRecordBtn').classList.add('hidden');
        document.getElementById('stopRecordBtn').classList.remove('hidden');
        document.getElementById('recordingStatus').classList.remove('hidden');

        // Start timer
        recordingInterval = setInterval(updateRecordingTime, 1000);

        showToast('Recording started', 'success');

    } catch (error) {
        showToast('Microphone access denied', 'error');
        console.error(error);
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());

        // Update UI
        document.getElementById('stopRecordBtn').classList.add('hidden');
        document.getElementById('startRecordBtn').classList.remove('hidden');
        document.getElementById('recordingStatus').classList.add('hidden');

        clearInterval(recordingInterval);
        showToast('Recording stopped', 'success');
    }
}

function updateRecordingTime() {
    const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    document.getElementById('recordingTime').textContent =
        `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

async function submitRecording() {
    if (!currentAudioBlob) {
        showToast('No recording available', 'error');
        return;
    }

    if (!currentClient) {
        showToast('Please log in first', 'error');
        return;
    }

    const formData = new FormData();
    const filename = `recording_${Date.now()}.webm`;
    formData.append('file', currentAudioBlob, filename);
    formData.append('client_id', currentClient.id);

    try {
        document.getElementById('submitRecordBtn').disabled = true;
        document.getElementById('submitRecordBtn').textContent = 'Submitting...';

        const response = await fetch(`${API_BASE_URL}/recordings/`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        showToast('Recording submitted successfully!', 'success');

        // Reset UI
        currentAudioBlob = null;
        document.getElementById('audioPlayback').classList.add('hidden');
        document.getElementById('audioPlayback').src = '';
        document.getElementById('submitRecordBtn').classList.add('hidden');
        document.getElementById('submitRecordBtn').disabled = false;
        document.getElementById('submitRecordBtn').textContent = 'Submit Recording';

        // Refresh recordings
        await loadRecordings();

    } catch (error) {
        showToast('Submission failed: ' + error.message, 'error');
        document.getElementById('submitRecordBtn').disabled = false;
        document.getElementById('submitRecordBtn').textContent = 'Submit Recording';
    }
}

// Recordings List
async function loadRecordings() {
    if (!currentClient) return;

    try {
        const response = await fetch(`${API_BASE_URL}/recordings?client_id=${currentClient.id}`);
        const recordings = await response.json();

        const listContainer = document.getElementById('recordingsList');

        if (recordings.length === 0) {
            listContainer.innerHTML = '<div class="loading">No recordings yet. Upload or record your first animal!</div>';
            return;
        }

        listContainer.innerHTML = recordings.map(recording => createRecordingItem(recording)).join('');

        // Add event listeners for retry buttons and missing fields
        document.querySelectorAll('.retry-btn').forEach(btn => {
            btn.addEventListener('click', () => reprocessRecording(btn.dataset.recordingId));
        });

        document.querySelectorAll('.provide-info-btn').forEach(btn => {
            btn.addEventListener('click', () => showMissingFieldsModal(btn.dataset.recordingId, btn.dataset.error));
        });

    } catch (error) {
        showToast('Error loading recordings', 'error');
        console.error(error);
    }
}

function createRecordingItem(recording) {
    const date = new Date(recording.created_at).toLocaleString();
    const status = recording.status;
    const statusClass = `status-${status}`;

    let errorSection = '';
    if (recording.sync_error) {
        const isMissingFields = recording.sync_error.includes('required information');
        errorSection = `
            <div class="error-message">
                <strong>Error:</strong>
                ${recording.sync_error}
                ${isMissingFields ? `
                    <button class="retry-btn provide-info-btn"
                            data-recording-id="${recording.id}"
                            data-error="${escapeHtml(recording.sync_error)}">
                        Provide Missing Information
                    </button>
                ` : `
                    <button class="retry-btn" data-recording-id="${recording.id}">
                        Retry Processing
                    </button>
                `}
            </div>
        `;
    }

    return `
        <div class="recording-item">
            <div class="recording-info">
                <h4>${recording.filename}</h4>
                <p>Uploaded: ${date}</p>
                ${recording.transcription_text ? `<p>Transcription: ${recording.transcription_text.substring(0, 100)}...</p>` : ''}
                ${recording.entity_type ? `<p>Entity Type: ${recording.entity_type}</p>` : ''}
                ${errorSection}
            </div>
            <span class="status-badge ${statusClass}">${status}</span>
        </div>
    `;
}

async function reprocessRecording(recordingId) {
    try {
        const response = await fetch(`${API_BASE_URL}/recordings/${recordingId}/reprocess`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('Reprocessing failed');
        }

        showToast('Recording queued for reprocessing', 'success');
        await loadRecordings();

    } catch (error) {
        showToast('Reprocessing failed: ' + error.message, 'error');
    }
}

// Missing Fields Modal
function showMissingFieldsModal(recordingId, errorMessage) {
    document.getElementById('missingFieldsMessage').textContent = errorMessage;
    document.getElementById('missingFieldsModal').classList.remove('hidden');

    // Parse missing fields and create form (simplified version)
    // In a real implementation, you would parse the error message and create appropriate inputs
    const container = document.getElementById('missingFieldsContainer');
    container.innerHTML = `
        <div class="form-group">
            <label>Additional Information</label>
            <textarea rows="4" placeholder="Please provide the missing information mentioned above..."></textarea>
        </div>
        <p style="color: #666; font-size: 14px; margin-top: 10px;">
            Note: After providing this information, please record or upload a new recording with all required details.
        </p>
    `;
}

function closeMissingFieldsModal() {
    document.getElementById('missingFieldsModal').classList.add('hidden');
}

// Toast Notifications
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
