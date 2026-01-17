// Content Factory Frontend Script

const form = document.getElementById('contentForm');
const brandTextarea = document.getElementById('brand');
const charCount = document.getElementById('charCount');
const submitBtn = document.getElementById('submitBtn');
const loadingDiv = document.getElementById('loading');
const resultDiv = document.getElementById('result');
const errorDiv = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');
const downloadAgainBtn = document.getElementById('downloadAgain');
const tryAgainBtn = document.getElementById('tryAgain');

let lastBlobUrl = null;
let lastFilename = null;

// Update character count
brandTextarea.addEventListener('input', () => {
    const count = brandTextarea.value.length;
    charCount.textContent = count;

    // Visual feedback for minimum length
    if (count < 50) {
        charCount.parentElement.style.color = '#ef4444';
    } else {
        charCount.parentElement.style.color = '#888';
    }
});

// Form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const brandDescription = brandTextarea.value.trim();

    // Validate
    if (brandDescription.length < 50) {
        showError('Please provide a more detailed brand description (at least 50 characters).');
        return;
    }

    // Show loading state
    showLoading();

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ brand_description: brandDescription }),
        });

        if (!response.ok) {
            let errorDetail = 'An error occurred during content generation.';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail?.detail || errorData.detail || errorDetail;
            } catch {
                // Response wasn't JSON
            }
            throw new Error(errorDetail);
        }

        // Get the blob and filename
        const blob = await response.blob();
        const contentDisposition = response.headers.get('Content-Disposition');
        lastFilename = 'social_content.zip';

        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?([^"]+)"?/);
            if (match) {
                lastFilename = match[1];
            }
        }

        // Create download link
        if (lastBlobUrl) {
            URL.revokeObjectURL(lastBlobUrl);
        }
        lastBlobUrl = URL.createObjectURL(blob);

        // Trigger download
        triggerDownload(lastBlobUrl, lastFilename);

        // Show success
        showSuccess();

    } catch (error) {
        showError(error.message);
    }
});

// Download again button
downloadAgainBtn.addEventListener('click', () => {
    if (lastBlobUrl && lastFilename) {
        triggerDownload(lastBlobUrl, lastFilename);
    }
});

// Try again button
tryAgainBtn.addEventListener('click', () => {
    resetForm();
});

function triggerDownload(url, filename) {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function showLoading() {
    form.classList.add('hidden');
    loadingDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');
    submitBtn.disabled = true;
}

function showSuccess() {
    form.classList.add('hidden');
    loadingDiv.classList.add('hidden');
    resultDiv.classList.remove('hidden');
    errorDiv.classList.add('hidden');
}

function showError(message) {
    form.classList.add('hidden');
    loadingDiv.classList.add('hidden');
    resultDiv.classList.add('hidden');
    errorDiv.classList.remove('hidden');
    errorMessage.textContent = message;
}

function resetForm() {
    form.classList.remove('hidden');
    loadingDiv.classList.add('hidden');
    resultDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');
    submitBtn.disabled = false;
}

// Initialize character count on page load
charCount.textContent = brandTextarea.value.length;
