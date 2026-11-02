/**
 * SmartAttend - Interactive Attendance Calculator & Recovery Planner
 * Live reactive recalculation without page refresh
 */

document.addEventListener('DOMContentLoaded', () => {
  initCalculator();
});

function initCalculator() {
  const totalInput = document.getElementById('calcTotal');
  const attendedInput = document.getElementById('calcAttended');
  const medicalInput = document.getElementById('calcMedical');
  const upcomingInput = document.getElementById('calcUpcoming');
  const targetInput = document.getElementById('calcTarget');

  if (!totalInput || !attendedInput) return;

  const inputs = [totalInput, attendedInput, medicalInput, upcomingInput, targetInput];
  inputs.forEach(input => {
    if (input) {
      input.addEventListener('input', runCalculations);
      input.addEventListener('change', runCalculations);
    }
  });

  // Quick subject selector buttons
  document.querySelectorAll('.btn-load-subject').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      totalInput.value = btn.dataset.total || 0;
      attendedInput.value = btn.dataset.attended || 0;
      medicalInput.value = btn.dataset.medical || 0;
      if (upcomingInput) upcomingInput.value = 10;
      runCalculations();

      showToast('Subject Loaded', `Populated ${btn.dataset.code} values into calculator`, 'info', 2500);
    });
  });

  // Initial run
  runCalculations();
}

function runCalculations() {
  const total = parseInt(document.getElementById('calcTotal')?.value) || 0;
  const attended = parseInt(document.getElementById('calcAttended')?.value) || 0;
  const medical = parseInt(document.getElementById('calcMedical')?.value) || 0;
  const upcoming = parseInt(document.getElementById('calcUpcoming')?.value) || 0;
  const targetPct = parseFloat(document.getElementById('calcTarget')?.value) || 75.0;

  // Validation
  const errBox = document.getElementById('calcError');
  if (attended > total) {
    if (errBox) {
      errBox.textContent = 'Attended classes cannot exceed total classes conducted.';
      errBox.style.display = 'block';
    }
    return;
  } else if (errBox) {
    errBox.style.display = 'none';
  }

  // Calculate regular attendance percentage
  const regularPct = total > 0 ? ((attended / total) * 100).toFixed(1) : '100.0';
  const medicalPct = total > 0 ? ((medical / total) * 100).toFixed(1) : '0.0';

  // Effective attended with medical addition
  const effAttended = attended + medical;
  const adjustedPctVal = total > 0 ? Math.min(100.0, (effAttended / total) * 100) : 100.0;
  const adjustedPct = adjustedPctVal.toFixed(1);

  // Recovery: Required classes to reach target
  const p = targetPct / 100.0;
  let requiredClasses = 0;
  if (p < 1.0) {
    if (total > 0 && (effAttended / total) >= p) {
      requiredClasses = 0;
    } else {
      const numerator = (p * total) - effAttended;
      const denominator = 1.0 - p;
      requiredClasses = Math.max(0, Math.ceil(numerator / denominator));
    }
  }

  // Max bunkable classes without falling below target
  let maxBunks = 0;
  if (total > 0 && (effAttended / total) >= p) {
    maxBunks = Math.max(0, Math.floor((effAttended / p) - total));
  }

  // Projected attendance after attending upcoming classes
  const projTotal = total + upcoming;
  const projAttended = effAttended + upcoming;
  const projectedPct = projTotal > 0 ? Math.min(100.0, (projAttended / projTotal) * 100).toFixed(1) : '100.0';

  // Update UI Elements
  updateText('outRegularPct', `${regularPct}%`);
  updateText('outAdjustedPct', `${adjustedPct}%`);
  updateText('outProjectedPct', `${projectedPct}%`);
  updateText('outRequiredClasses', requiredClasses === 0 ? '0 (Target Met!)' : `${requiredClasses} Classes`);
  updateText('outMaxBunks', `${maxBunks} Classes`);

  // Target recovery status callout
  const statusBadge = document.getElementById('calcStatusBadge');
  const statusDesc = document.getElementById('calcStatusDesc');
  if (statusBadge && statusDesc) {
    if (adjustedPctVal >= targetPct) {
      statusBadge.className = 'badge badge-safe';
      statusBadge.innerHTML = '<i class="fa-solid fa-circle-check"></i> Safe Zone';
      statusDesc.textContent = `You are currently above ${targetPct}%. You can afford to miss up to ${maxBunks} classes.`;
    } else if (adjustedPctVal >= 65.0) {
      statusBadge.className = 'badge badge-warning';
      statusBadge.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Warning Zone';
      statusDesc.textContent = `You are below ${targetPct}%. Attend the next ${requiredClasses} consecutive classes to recover eligibility!`;
    } else {
      statusBadge.className = 'badge badge-danger';
      statusBadge.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i> Critical Shortage';
      statusDesc.textContent = `Critical shortage! Immediate action required: Attend next ${requiredClasses} classes without absence.`;
    }
  }
}

function updateText(elemId, val) {
  const el = document.getElementById(elemId);
  if (el) el.textContent = val;
}
