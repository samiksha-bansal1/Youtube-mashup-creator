// Form elements
const form = document.getElementById('mashupForm');
const singerInput = document.getElementById('singer');
const countInput = document.getElementById('count');
const durationInput = document.getElementById('duration');
const emailInput = document.getElementById('email');
const submitBtn = document.getElementById('submitBtn');
const spinner = document.getElementById('spinner');
const btnText = document.getElementById('btnText');

// Progress elements
const progressSection = document.getElementById('progressSection');
const progressBar = document.getElementById('progressBar');
const progressMessage = document.getElementById('progressMessage');

// Success elements
const successSection = document.getElementById('successSection');
const audioPlayer = document.getElementById('audioPlayer');
const audioSource = document.getElementById('audioSource');
const downloadBtn = document.getElementById('downloadBtn');
const createAnotherBtn = document.getElementById('createAnotherBtn');

// Current job ID
let currentJobId = null;
let statusCheckInterval = null;

// Real-time validation
singerInput.addEventListener('input', validateSinger);
countInput.addEventListener('input', validateCount);
durationInput.addEventListener('input', validateDuration);
emailInput.addEventListener('input', validateEmail);

function validateSinger() {
    const singerError = document.getElementById('singerError');
    const value = singerInput.value.trim();
    
    if (!value) {
        singerInput.classList.add('error');
        singerError.classList.add('show');
        return false;
    }
    
    singerInput.classList.remove('error');
    singerError.classList.remove('show');
    return true;
}

function validateCount() {
    const countError = document.getElementById('countError');
    const value = parseInt(countInput.value);
    
    if (!value || value <= 10) {
        countInput.classList.add('error');
        countError.classList.add('show');
        return false;
    }
    
    countInput.classList.remove('error');
    countError.classList.remove('show');
    return true;
}

function validateDuration() {
    const durationError = document.getElementById('durationError');
    const value = parseInt(durationInput.value);
    
    if (!value || value <= 20) {
        durationInput.classList.add('error');
        durationError.classList.add('show');
        return false;
    }
    
    durationInput.classList.remove('error');
    durationError.classList.remove('show');
    return true;
}

function validateEmail() {
    const emailError = document.getElementById('emailError');
    const value = emailInput.value.trim();
    
    // Email is optional, so empty is valid
    if (!value) {
        emailInput.classList.remove('error');
        emailError.classList.remove('show');
        return true;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!emailRegex.test(value)) {
        emailInput.classList.add('error');
        emailError.classList.add('show');
        return false;
    }
    
    emailInput.classList.remove('error');
    emailError.classList.remove('show');
    return true;
}

// Form submission
form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const isSingerValid = validateSinger();
    const isCountValid = validateCount();
    const isDurationValid = validateDuration();
    const isEmailValid = validateEmail();
    
    if (!isSingerValid || !isCountValid || !isDurationValid || !isEmailValid) {
        showToast('Please fix all validation errors', 'error');
        return;
    }
    
    // Disable form
    submitBtn.disabled = true;
    btnText.textContent = 'Creating...';
    spinner.style.display = 'inline-block';
    
    // Hide previous results
    successSection.classList.remove('show');
    
    // Prepare data
    const data = {
        singer: singerInput.value.trim(),
        count: parseInt(countInput.value),
        duration: parseInt(durationInput.value),
        email: emailInput.value.trim() || null
    };
    
    try {
        // Submit request
        const response = await fetch('/create-mashup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Failed to create mashup');
        }
        
        // Start tracking progress
        currentJobId = result.job_id;
        startStatusCheck();
        
        // Show progress section
        progressSection.classList.add('show');
        
        // Scroll to progress
        setTimeout(() => {
            progressSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
        
    } catch (error) {
        showToast(error.message, 'error');
        resetForm();
    }
});

function startStatusCheck() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    
    statusCheckInterval = setInterval(checkStatus, 1000);
}

async function checkStatus() {
    if (!currentJobId) return;
    
    try {
        const response = await fetch(`/status/${currentJobId}`);
        const job = await response.json();
        
        if (!response.ok) {
            throw new Error('Failed to get status');
        }
        
        // Update progress
        updateProgress(job);
        
        // Check if completed
        if (job.status === 'completed') {
            clearInterval(statusCheckInterval);
            showSuccess(job);
        } else if (job.status === 'failed') {
            clearInterval(statusCheckInterval);
            showToast(job.error || 'Mashup creation failed', 'error');
            resetForm();
            progressSection.classList.remove('show');
        }
        
    } catch (error) {
        console.error('Status check error:', error);
    }
}

function updateProgress(job) {
    const progress = Math.round(job.progress || 0);
    progressBar.style.width = `${progress}%`;
    progressMessage.textContent = job.current_step || 'Processing...';
}

function showSuccess(job) {
    // Hide progress
    progressSection.classList.remove('show');
    
    // Set audio source and load
    audioSource.src = job.download_url;
    audioPlayer.load();
    
    // Set download URL
    downloadBtn.onclick = () => {
        window.location.href = job.download_url;
    };
    
    // Show success with animation
    successSection.classList.add('show');
    
    // Scroll to success
    setTimeout(() => {
        successSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
    
    // Reset form
    resetForm();
    
    // Show success toast
    setTimeout(() => {
        showToast('Your mashup is ready!', 'success');
    }, 500);
}

function resetForm() {
    submitBtn.disabled = false;
    btnText.textContent = 'Create Mashup';
    spinner.style.display = 'none';
}

// Create another mashup
createAnotherBtn.addEventListener('click', function() {
    // Hide success section
    successSection.classList.remove('show');
    
    // Clear form
    form.reset();
    
    // Remove validation classes
    singerInput.classList.remove('error');
    countInput.classList.remove('error');
    durationInput.classList.remove('error');
    emailInput.classList.remove('error');
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Focus on singer input
    setTimeout(() => {
        singerInput.focus();
    }, 500);
});

// Toast notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}