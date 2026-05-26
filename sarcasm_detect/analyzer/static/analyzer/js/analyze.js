// analyze.js — Form submit with AJAX, loading overlay, toasts, emoji preview

// ── Toast helper ─────────────────────────────────────────────────────────────
function showToast(msg, type = 'danger') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const id = 'toast-' + Date.now();
  container.insertAdjacentHTML('beforeend', `
    <div id="${id}" class="toast align-items-center text-bg-${type} border-0 show mb-2" role="alert">
      <div class="d-flex">
        <div class="toast-body">${msg}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto"
                onclick="document.getElementById('${id}').remove()"></button>
      </div>
    </div>`);
  setTimeout(() => { const el = document.getElementById(id); if (el) el.remove(); }, 6000);
}

// ── Loading overlay ──────────────────────────────────────────────────────────
const LOADING_STEPS = [
  '😏 Extracting emojis...',
  '📝 Running text analysis (RoBERTa + Rules)...',
  '🌐 Detecting language signals...',
  '🖼️ Analyzing image (CLIP ViT-B/32)...',
  '🤖 Consulting Claude AI...',
  '⚡ Fusing multimodal scores...',
  '✅ Finalizing results...',
];

let stepIdx = 0, stepInterval = null, progressInterval = null;

function createLoadingOverlay() {
  if (document.getElementById('loadingOverlay')) return;
  document.body.insertAdjacentHTML('beforeend', `
    <div id="loadingOverlay">
      <div class="loading-content">
        <div class="spinner-grow text-warning mb-3" style="width:3.5rem;height:3.5rem;" role="status"></div>
        <div id="loadingStepText">${LOADING_STEPS[0]}</div>
        <div class="progress mt-3" id="loadingProgress">
          <div id="loadingBar" class="progress-bar bg-warning progress-bar-striped progress-bar-animated" style="width:0%;"></div>
        </div>
        <small class="text-muted mt-3 d-block">This may take 5–15 seconds</small>
      </div>
    </div>`);
}

function startLoading() {
  createLoadingOverlay();
  stepIdx = 0;
  let pct = 5;
  const bar = document.getElementById('loadingBar');
  const text = document.getElementById('loadingStepText');

  stepInterval = setInterval(() => {
    stepIdx = Math.min(stepIdx + 1, LOADING_STEPS.length - 1);
    if (text) text.textContent = LOADING_STEPS[stepIdx];
  }, 2500);

  progressInterval = setInterval(() => {
    pct = Math.min(pct + 2, 90);
    if (bar) bar.style.width = pct + '%';
  }, 500);
}

function stopLoading() {
  clearInterval(stepInterval);
  clearInterval(progressInterval);
  const overlay = document.getElementById('loadingOverlay');
  const bar = document.getElementById('loadingBar');
  if (bar) bar.style.width = '100%';
  setTimeout(() => { if (overlay) overlay.remove(); }, 400);
}

// ── Emoji live preview ───────────────────────────────────────────────────────
const textInput = document.getElementById('textInput');
const emojiPreview = document.getElementById('emojiPreview');
const emojiList = document.getElementById('emojiList');
const charCount = document.getElementById('charCount');

if (textInput) {
  textInput.addEventListener('input', () => {
    const text = textInput.value;
    if (charCount) charCount.textContent = text.length;
    const emojis = [...text.matchAll(/\p{Emoji_Presentation}|\p{Extended_Pictographic}/gu)].map(m => m[0]);
    if (emojis.length > 0) {
      emojiList.textContent = [...new Set(emojis)].join(' ');
      emojiPreview.classList.remove('d-none');
    } else {
      emojiPreview.classList.add('d-none');
    }
  });
}

// ── Image preview + remove ───────────────────────────────────────────────────
const imageInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');
const imagePreviewContainer = document.getElementById('imagePreviewContainer');
const removeImageBtn = document.getElementById('removeImage');

if (imageInput) {
  imageInput.addEventListener('change', () => {
    const file = imageInput.files[0];
    if (!file) return;
    imagePreview.src = URL.createObjectURL(file);
    imagePreviewContainer.classList.remove('d-none');
  });
}

if (removeImageBtn) {
  removeImageBtn.addEventListener('click', () => {
    imageInput.value = '';
    imagePreviewContainer.classList.add('d-none');
    imagePreview.src = '';
  });
}

// ── Drag & drop (image only) ─────────────────────────────────────────────────
const imageDropZone = document.getElementById('imageDropZone');
if (imageDropZone && imageInput) {
  imageDropZone.addEventListener('dragover', e => { e.preventDefault(); imageDropZone.classList.add('dragover'); });
  imageDropZone.addEventListener('dragleave', () => imageDropZone.classList.remove('dragover'));
  imageDropZone.addEventListener('drop', e => {
    e.preventDefault();
    imageDropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
      imageInput.files = e.dataTransfer.files;
      imageInput.dispatchEvent(new Event('change'));
    }
  });
  imageDropZone.addEventListener('click', e => { if (e.target.tagName !== 'BUTTON') imageInput.click(); });
}

// ── Example buttons ──────────────────────────────────────────────────────────
document.querySelectorAll('.example-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const text = btn.getAttribute('data-text');
    if (textInput && text) {
      textInput.value = text;
      textInput.dispatchEvent(new Event('input'));
      textInput.focus();
    }
  });
});

// ── Reset button ─────────────────────────────────────────────────────────────
const resetBtn = document.getElementById('resetBtn');
if (resetBtn) {
  resetBtn.addEventListener('click', () => {
    if (imagePreviewContainer) imagePreviewContainer.classList.add('d-none');
    if (emojiPreview) emojiPreview.classList.add('d-none');
    if (charCount) charCount.textContent = '0';
  });
}

// ── Form submit ──────────────────────────────────────────────────────────────
document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const submitBtn = document.getElementById('submitBtn');

  const formData = new FormData(e.target);
  const text = (formData.get('text') || '').trim();
  const image = formData.get('image');

  if (!text && (!image || !image.size)) {
    showToast('Please enter some text or upload an image.', 'warning');
    return;
  }

  submitBtn.disabled = true;
  startLoading();

  try {
    const resp = await fetch('/api/analyze/', { method: 'POST', body: formData });
    const data = await resp.json();
    stopLoading();
    if (!resp.ok) {
      submitBtn.disabled = false;
      const errMsg = typeof data.error === 'object'
        ? Object.values(data.error).flat().join(' ')
        : (data.error || 'Analysis failed.');
      showToast('Error: ' + errMsg);
      return;
    }
    window.location.href = `/result/${data.id}/`;
  } catch (err) {
    stopLoading();
    submitBtn.disabled = false;
    showToast('Network error: ' + err.message);
  }
});
