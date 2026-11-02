/**
 * SmartAttend - Medical Records & Certificate Verification
 */

document.addEventListener('DOMContentLoaded', () => {
  initMedicalForm();
  initCertificatePreviews();
});

function initMedicalForm() {
  const startDate = document.getElementById('startDate');
  const endDate = document.getElementById('endDate');
  const durationLabel = document.getElementById('leaveDurationText');
  const certInput = document.getElementById('certificateInput');

  function updateDuration() {
    if (startDate && endDate && startDate.value && endDate.value) {
      const start = new Date(startDate.value);
      const end = new Date(endDate.value);
      const diffTime = end - start;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

      if (diffDays <= 0) {
        if (durationLabel) {
          durationLabel.textContent = 'End date cannot be earlier than start date!';
          durationLabel.style.color = 'var(--danger)';
        }
      } else {
        if (durationLabel) {
          durationLabel.textContent = `Duration: ${diffDays} day(s)`;
          durationLabel.style.color = 'var(--primary)';
        }
      }
    }
  }

  if (startDate) startDate.addEventListener('change', updateDuration);
  if (endDate) endDate.addEventListener('change', updateDuration);

  // File size validation client-side
  if (certInput) {
    certInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        const maxSize = 16 * 1024 * 1024; // 16 MB
        if (file.size > maxSize) {
          alert('File size exceeds the 16MB limit. Please upload a smaller document.');
          certInput.value = '';
        }
      }
    });
  }
}

function initCertificatePreviews() {
  document.querySelectorAll('[data-preview-cert]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const url = btn.getAttribute('data-preview-cert');
      const filename = btn.getAttribute('data-filename') || 'Certificate';
      
      const modal = document.getElementById('certPreviewModal');
      const container = document.getElementById('certPreviewContainer');
      const title = document.getElementById('certPreviewTitle');

      if (modal && container) {
        if (title) title.textContent = filename;

        if (url.toLowerCase().endsWith('.pdf')) {
          container.innerHTML = `<iframe src="${url}" width="100%" height="550px" style="border:none; border-radius: 8px;"></iframe>`;
        } else {
          container.innerHTML = `<img src="${url}" alt="Medical Certificate" style="max-width:100%; max-height:550px; border-radius:8px; display:block; margin:0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />`;
        }
        openModal('certPreviewModal');
      }
    });
  });
}
