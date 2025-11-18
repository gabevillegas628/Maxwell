let referenceImage = null;
let studentImage = null;
let currentGradingMode = 'fast'; // 'fast', 'detailed', or 'answer_sheet'

// Camera streams
let referenceStream = null;
let studentStream = null;
let referenceFacingMode = 'environment'; // 'user' for front, 'environment' for back
let studentFacingMode = 'environment';

// Get DOM elements
const referenceUpload = document.getElementById('referenceUpload');
const studentUpload = document.getElementById('studentUpload');
const referenceInput = document.getElementById('referenceInput');
const studentInput = document.getElementById('studentInput');
const gradeButton = document.getElementById('gradeButton');
const resultsDiv = document.getElementById('results');
const feedbackDiv = document.getElementById('feedback');
const loadingDiv = document.getElementById('loading');
const modeBadge = document.getElementById('modeBadge');
const modeDescription = document.getElementById('modeDescription');

// Camera elements
const referenceCamera = document.getElementById('referenceCamera');
const studentCamera = document.getElementById('studentCamera');
const referenceVideo = document.getElementById('referenceVideo');
const studentVideo = document.getElementById('studentVideo');
const referenceCanvas = document.getElementById('referenceCanvas');
const studentCanvas = document.getElementById('studentCanvas');
const referenceCaptureBtn = document.getElementById('referenceCaptureBtn');
const studentCaptureBtn = document.getElementById('studentCaptureBtn');
const referenceFlipBtn = document.getElementById('referenceFlipBtn');
const studentFlipBtn = document.getElementById('studentFlipBtn');

// Grading mode button handlers
document.querySelectorAll('.grading-mode-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        // Remove active class from all buttons
        document.querySelectorAll('.grading-mode-btn').forEach(b => b.classList.remove('active'));

        // Add active class to clicked button
        this.classList.add('active');

        // Update current mode
        currentGradingMode = this.dataset.mode;

        // Update description
        const descriptions = {
            'fast': 'Fast mode provides quick scores with brief justification.',
            'detailed': 'Detailed mode includes comprehensive feedback with methodology analysis.',
            'answer_sheet': 'Answer sheet mode compares numbered answers directly and lists incorrect responses. Requires reference image.'
        };
        modeDescription.textContent = descriptions[currentGradingMode];
    });
});

// Image compression function
async function compressImage(base64Image, maxWidth = 1920, quality = 0.8) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            let width = img.width;
            let height = img.height;
            
            // Calculate new dimensions
            if (width > maxWidth) {
                height = (height * maxWidth) / width;
                width = maxWidth;
            }
            
            canvas.width = width;
            canvas.height = height;
            
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);
            
            // Convert to compressed JPEG
            resolve(canvas.toDataURL('image/jpeg', quality));
        };
        img.src = base64Image;
    });
}

// File input handlers
referenceInput.addEventListener('change', async (e) => {
    if (e.target.files[0]) {
        const reader = new FileReader();
        reader.onload = async function(event) {
            referenceImage = await compressImage(event.target.result);
            updateReferencePreview();
            updateGradeButton();
        };
        reader.readAsDataURL(e.target.files[0]);
    }
});

studentInput.addEventListener('change', async (e) => {
    if (e.target.files[0]) {
        const reader = new FileReader();
        reader.onload = async function(event) {
            studentImage = await compressImage(event.target.result);
            updateStudentPreview();
            updateGradeButton();
        };
        reader.readAsDataURL(e.target.files[0]);
    }
});

// Click to upload
referenceUpload.addEventListener('click', () => referenceInput.click());
studentUpload.addEventListener('click', () => studentInput.click());

// Drag and drop handlers
[referenceUpload, studentUpload].forEach(area => {
    area.addEventListener('dragover', (e) => {
        e.preventDefault();
        area.classList.add('dragover');
    });

    area.addEventListener('dragleave', () => {
        area.classList.remove('dragover');
    });
});

referenceUpload.addEventListener('drop', async (e) => {
    e.preventDefault();
    referenceUpload.classList.remove('dragover');
    
    const files = Array.from(e.dataTransfer.files).filter(file => 
        file.type.startsWith('image/')
    );
    
    if (files.length > 0) {
        const reader = new FileReader();
        reader.onload = async function(event) {
            referenceImage = await compressImage(event.target.result);
            updateReferencePreview();
            updateGradeButton();
        };
        reader.readAsDataURL(files[0]);
    }
});

studentUpload.addEventListener('drop', async (e) => {
    e.preventDefault();
    studentUpload.classList.remove('dragover');
    
    const files = Array.from(e.dataTransfer.files).filter(file => 
        file.type.startsWith('image/')
    );
    
    if (files.length > 0) {
        const reader = new FileReader();
        reader.onload = async function(event) {
            studentImage = await compressImage(event.target.result);
            updateStudentPreview();
            updateGradeButton();
        };
        reader.readAsDataURL(files[0]);
    }
});

function updateReferencePreview() {
    const preview = document.getElementById('referencePreview');
    if (referenceImage) {
        preview.innerHTML = `<img src="${referenceImage}" alt="Reference Answer">`;
        preview.classList.add('active');
        referenceUpload.classList.add('has-image');
    }
}

function updateStudentPreview() {
    const preview = document.getElementById('studentPreview');
    if (studentImage) {
        preview.innerHTML = `<img src="${studentImage}" alt="Student Answer">`;
        preview.classList.add('active');
        studentUpload.classList.add('has-image');
    }
}

function updateGradeButton() {
    gradeButton.disabled = !studentImage;
}

// Grade button handler
gradeButton.addEventListener('click', async () => {
    const rubric = document.getElementById('rubric').value;
    const context = document.getElementById('context').value;

    // Show loading
    loadingDiv.style.display = 'block';
    resultsDiv.style.display = 'none';
    gradeButton.disabled = true;

    try {
        const response = await fetch('/grade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                rubric: rubric,
                context: context,
                referenceImage: referenceImage,
                studentImage: studentImage,
                gradingMode: currentGradingMode
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Update mode badge
            const modeBadges = {
                'fast': { text: '⚡ Fast Mode', class: 'mode-badge fast' },
                'detailed': { text: '📝 Detailed Mode', class: 'mode-badge detailed' },
                'answer_sheet': { text: '📋 Answer Sheet Mode', class: 'mode-badge answer-sheet' }
            };

            const badge = modeBadges[data.mode] || modeBadges['fast'];
            modeBadge.textContent = badge.text;
            modeBadge.className = badge.class;

            feedbackDiv.textContent = data.feedback;
            resultsDiv.style.display = 'block';
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        loadingDiv.style.display = 'none';
        gradeButton.disabled = false;
    }
});

// ===== CAMERA FUNCTIONALITY =====

// Mode switching (Upload vs Camera)
document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.addEventListener('click', async function() {
        const mode = this.dataset.mode;
        const target = this.dataset.target;

        // Update active button
        this.parentElement.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');

        if (target === 'reference') {
            if (mode === 'camera') {
                referenceUpload.style.display = 'none';
                referenceCamera.style.display = 'block';
                await startCamera('reference');
            } else {
                await stopCamera('reference');
                referenceCamera.style.display = 'none';
                referenceUpload.style.display = 'block';
            }
        } else if (target === 'student') {
            if (mode === 'camera') {
                studentUpload.style.display = 'none';
                studentCamera.style.display = 'block';
                await startCamera('student');
            } else {
                await stopCamera('student');
                studentCamera.style.display = 'none';
                studentUpload.style.display = 'block';
            }
        }
    });
});

// Start camera stream
async function startCamera(target) {
    const video = target === 'reference' ? referenceVideo : studentVideo;
    const flipBtn = target === 'reference' ? referenceFlipBtn : studentFlipBtn;
    const facingMode = target === 'reference' ? referenceFacingMode : studentFacingMode;

    try {
        // Check if device has multiple cameras (mobile)
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');

        // Show flip button if multiple cameras available
        if (videoDevices.length > 1) {
            flipBtn.style.display = 'inline-flex';
        }

        const constraints = {
            video: {
                facingMode: facingMode,
                width: { ideal: 1920 },
                height: { ideal: 1080 }
            }
        };

        const stream = await navigator.mediaDevices.getUserMedia(constraints);

        if (target === 'reference') {
            referenceStream = stream;
        } else {
            studentStream = stream;
        }

        video.srcObject = stream;

    } catch (error) {
        console.error('Camera error:', error);
        let errorMessage = 'Could not access camera. ';

        if (error.name === 'NotAllowedError') {
            errorMessage += 'Please allow camera access in your browser settings.';
        } else if (error.name === 'NotFoundError') {
            errorMessage += 'No camera found on this device.';
        } else {
            errorMessage += error.message;
        }

        alert(errorMessage);

        // Switch back to upload mode
        const uploadBtn = document.querySelector(`.mode-btn[data-mode="upload"][data-target="${target}"]`);
        if (uploadBtn) uploadBtn.click();
    }
}

// Stop camera stream
async function stopCamera(target) {
    const stream = target === 'reference' ? referenceStream : studentStream;
    const video = target === 'reference' ? referenceVideo : studentVideo;
    const flipBtn = target === 'reference' ? referenceFlipBtn : studentFlipBtn;

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;

        if (target === 'reference') {
            referenceStream = null;
        } else {
            studentStream = null;
        }
    }

    flipBtn.style.display = 'none';
}

// Capture photo from camera
async function capturePhoto(target) {
    const video = target === 'reference' ? referenceVideo : studentVideo;
    const canvas = target === 'reference' ? referenceCanvas : studentCanvas;
    const preview = document.getElementById(`${target}Preview`);
    const captureBtn = target === 'reference' ? referenceCaptureBtn : studentCaptureBtn;

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to base64 and compress
    const base64Image = canvas.toDataURL('image/jpeg', 0.95);
    const compressedImage = await compressImage(base64Image);

    // Store the image
    if (target === 'reference') {
        referenceImage = compressedImage;
        updateReferencePreview();
    } else {
        studentImage = compressedImage;
        updateStudentPreview();
    }

    updateGradeButton();

    // Stop camera and switch to upload mode to show preview
    await stopCamera(target);
    const uploadBtn = document.querySelector(`.mode-btn[data-mode="upload"][data-target="${target}"]`);
    if (uploadBtn) {
        uploadBtn.click();
    }
}

// Flip camera (front/back)
async function flipCamera(target) {
    const currentFacingMode = target === 'reference' ? referenceFacingMode : studentFacingMode;
    const newFacingMode = currentFacingMode === 'user' ? 'environment' : 'user';

    if (target === 'reference') {
        referenceFacingMode = newFacingMode;
    } else {
        studentFacingMode = newFacingMode;
    }

    // Restart camera with new facing mode
    await stopCamera(target);
    await startCamera(target);
}

// Capture button event listeners
referenceCaptureBtn.addEventListener('click', () => capturePhoto('reference'));
studentCaptureBtn.addEventListener('click', () => capturePhoto('student'));

// Flip button event listeners
referenceFlipBtn.addEventListener('click', () => flipCamera('reference'));
studentFlipBtn.addEventListener('click', () => flipCamera('student'));

// Clean up camera streams when page unloads
window.addEventListener('beforeunload', () => {
    stopCamera('reference');
    stopCamera('student');
});
