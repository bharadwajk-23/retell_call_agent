/**
 * Backend patient details and booking status UI.
 */
console.log('Js loaded from Backend');
const API_BASE = window.location.origin;
let patients = [];

document.addEventListener('DOMContentLoaded', () => {
    loadPatients();
});

async function loadPatients() {
    try {
        const response = await fetch(`${API_BASE}/patients`);
        patients = await response.json();
        renderPatients();
    } catch (error) {
        console.error('Error loading patients:', error);
        showError('Failed to load patients');
    }
}

function renderPatients() {
    const tbody = document.getElementById('patient-table-body');
    tbody.innerHTML = '';

    patients.forEach((patient) => {
        const bookingStatus = patient.booking_status || 'not booked';
        const disabled = bookingStatus !== 'not booked';
        
        let btnText = 'Start Call';
        let btnClass = 'status-not-booked';
        
        if (bookingStatus === 'in progress') {
            btnText = 'Calling...';
            btnClass = 'status-in-progress';
        } else if (bookingStatus === 'booked') {
            btnText = 'Booked';
            btnClass = 'status-booked';
        }
        
        const actionBtn = `<button class="start-call-btn ${btnClass}" data-id="${patient.id}" ${disabled ? 'disabled' : ''} onclick="startCall(${patient.id})">${btnText}</button>`;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(patient.patient_name)}</td>
            <td>${escapeHtml(patient.phone)}</td>
            <td>${escapeHtml(patient.dob || '—')}</td>
            <td>${escapeHtml(String(patient.exercise_missed_days ?? 0))}</td>
            <td>${escapeHtml(patient.provider_name)}</td>
            <td>${actionBtn}</td>
        `;

        tbody.appendChild(row);
    });
}

function escapeHtml(s) {
    return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function showError(message) {
    alert(message);
}

async function startCall(patientId) {
    try {
        const patient = patients.find((p) => p.id === patientId);
        if (!patient) {
            showError('Patient not found');
            return;
        }

        const response = await fetch(`${API_BASE}/start-call`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ patient_id: patientId }),
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || 'Failed to start call');
        }

        // Refresh patients to see "in progress" status set by backend
        await loadPatients();
    } catch (error) {
        console.error('Error starting call:', error);
        showError(error.message || 'Failed to start call');
    }
}

// Poll patients every 2 seconds to pick up booking status changes
setInterval(() => {
    loadPatients().catch((e) => console.error('Error polling patients:', e));
}, 2000);
