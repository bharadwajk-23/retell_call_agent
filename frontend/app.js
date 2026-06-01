/**
 * Frontend patient details and booking status only.
 */
console.log('Js loaded from Frontend');
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
        const booked = patient.booking_status ? 'Booked' : 'Not booked';
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(patient.patient_name)}</td>
            <td>${escapeHtml(patient.phone)}</td>
            <td>${escapeHtml(patient.dob || '—')}</td>
            <td>${escapeHtml(String(patient.exercise_missed_days ?? 0))}</td>
            <td>${escapeHtml(patient.provider_name)}</td>
            <td>${escapeHtml(booked)}</td>
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
