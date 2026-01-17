// Content Factory Frontend Script

const form = document.getElementById('contentForm');
const brandTextarea = document.getElementById('brand');
const charCount = document.getElementById('charCount');
const submitBtn = document.getElementById('submitBtn');
const loadingDiv = document.getElementById('loading');
const resultDiv = document.getElementById('result');
const errorDiv = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');
const tryAgainBtn = document.getElementById('tryAgain');
const createNewBtn = document.getElementById('createNew');

let currentPosts = null;

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

        // Get the JSON data with posts
        const data = await response.json();
        currentPosts = data.posts;

        // Show success with posts
        showSuccess(currentPosts);

    } catch (error) {
        showError(error.message);
    }
});

// Try again button
tryAgainBtn.addEventListener('click', () => {
    resetForm();
});

// Create new button
createNewBtn.addEventListener('click', () => {
    resetForm();
});

function showLoading() {
    form.classList.add('hidden');
    loadingDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');
    submitBtn.disabled = true;
}

function showSuccess(posts) {
    form.classList.add('hidden');
    loadingDiv.classList.add('hidden');
    resultDiv.classList.remove('hidden');
    errorDiv.classList.add('hidden');
    
    // Render the posts
    renderPosts(posts);
}

function renderPosts(posts) {
    const postsContainer = document.getElementById('postsContainer');
    postsContainer.innerHTML = '';
    
    posts.forEach((post, index) => {
        const postCard = document.createElement('div');
        postCard.className = 'post-card';
        
        postCard.innerHTML = `
            <div class="post-header">
                <h3>Post ${post.post_number} - ${post.day}</h3>
                <span class="post-time">${post.best_time_to_post}</span>
            </div>
            <div class="post-image">
                <img src="${post.image_url}" alt="${post.topic}" loading="lazy" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22%3E%3Crect fill=%22%23e1e1e1%22 width=%22400%22 height=%22300%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 font-family=%22sans-serif%22 font-size=%2218%22 fill=%22%23999%22%3EImage not available%3C/text%3E%3C/svg%3E'">
            </div>
            <div class="post-content">
                <h4 class="post-topic">${post.topic}</h4>
                <p class="post-copy">${post.post_copy}</p>
                <div class="post-hashtags">${post.hashtags}</div>
            </div>
            <div class="post-footer">
                <button class="copy-btn" onclick="copyPost(${index})">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M13.5 5.5H6.5C5.67157 5.5 5 6.17157 5 7V14C5 14.8284 5.67157 15.5 6.5 15.5H13.5C14.3284 15.5 15 14.8284 15 14V7C15 6.17157 14.3284 5.5 13.5 5.5Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M3 10.5H2.5C2.10218 10.5 1.72064 10.342 1.43934 10.0607C1.15804 9.77936 1 9.39782 1 9V2C1 1.60218 1.15804 1.22064 1.43934 0.93934C1.72064 0.658035 2.10218 0.5 2.5 0.5H9.5C9.89782 0.5 10.2794 0.658035 10.5607 0.93934C10.842 1.22064 11 1.60218 11 2V2.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Copy Text
                </button>
            </div>
        `;
        
        postsContainer.appendChild(postCard);
    });
}

function copyPost(index) {
    const post = currentPosts[index];
    const textToCopy = `${post.post_copy}\n\n${post.hashtags}`;
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        // Show feedback
        const btn = event.target.closest('.copy-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span style="color: #10b981;">✓ Copied!</span>';
        setTimeout(() => {
            btn.innerHTML = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy text. Please try again.');
    });
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
