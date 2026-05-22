/**
 * Frontend for AI Physiotherapy Call Agent (served from /frontend).
 */

const API_BASE = window.location.origin;

let patients = [];
let activeCallPhone = null;
let transcriptInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    loadPatients();
    loadRecentCalls();
});

async function loadPatients() {
    try {
        const response = await fetch(`${API_BASE}/patients`);
        patients = await response.json();
        renderPatients();
    } catch (error) {
        console.error   ('Error loading patients:', error);
        showError('Failed to load patients');
    }
}

function missedDaysBadgeClass(days) {
    const n = Number(days) || 0;
    if (n >= 5) return 'status-missed';
    if (n >= 3) return 'status-high';
    return 'status-low';
}

function renderPatients() {
    const tbody = document.getElementById('patient-table-body');
    tbody.innerHTML = '';

    patients.forEach((patient) => {
        const row = document.createElement('tr');
        const phone = patient.phone;
        const missed = patient.exercise_missed_days ?? 0;
        const badgeClass = missedDaysBadgeClass(missed);
        const disabled =
            activeCallPhone !== null && activeCallPhone === phone;

        row.innerHTML = `
            <td>${escapeHtml(patient.patient_name)}</td>
            <td>${escapeHtml(phone)}</td>
            <td>${escapeHtml(patient.dob || '—')}</td>
            <td><span class="status-badge ${badgeClass}">${escapeHtml(String(missed))} days</span></td>
            <td>${escapeHtml(patient.provider_name)}</td>
            <td>
                <button
                    type="button"
                    class="start-call-btn"
                    data-phone="${escapeAttr(phone)}"
                    ${disabled ? 'disabled' : ''}
                >
                    ${disabled ? 'Calling...' : 'Start Call'}
                </button>
            </td>
        `;
        const btn = row.querySelector('.start-call-btn');
        btn.addEventListener('click', () => startCall(patient));
        tbody.appendChild(row);
    });
}

function escapeHtml(s) {
    return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, '&#39;');
}

async function startCall(patient) {
    try {
        if (!patient || patient.id == null) {
            showError('Patient not found');
            return;
        }

        const phone = patient.phone;
        activeCallPhone = phone;
        updateCallStatus('Calling...', 'calling');
        updateBookingStatus('Pending', 'pending');
        clearTranscript();
        renderPatients();

        const response = await fetch(`${API_BASE}/start-call`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ patient_id: patient.id }),
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || 'Failed to start call');
        }

        const data = await response.json();
        console.log('Call started:', data);

        startTranscriptPolling(phone);
        simulateDemoConversation(patient);
    } catch (error) {
        console.error('Error starting call:', error);
        showError(error.message || 'Failed to start call');
        activeCallPhone = null;
        updateCallStatus('Call Failed', 'completed');
        renderPatients();
    }
}

function startTranscriptPolling(phone) {
    if (transcriptInterval) {
        clearInterval(transcriptInterval);
    }

    const params = new URLSearchParams({ phone });
    transcriptInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/call-status?${params}`);
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'completed') {
                    clearInterval(transcriptInterval);
                    updateCallStatus('Call Completed', 'completed');
                    activeCallPhone = null;
                    renderPatients();
                    loadRecentCalls();
                }
            }
        } catch (error) {
            console.error('Error polling call status:', error);
        }
    }, 3000);
}

function simulateDemoConversation(patient) {
    const transcriptContent = document.getElementById('transcript-content');
    transcriptContent.innerHTML = '';

    const name = patient.patient_name;
    const provider = patient.provider_name;
    const missed = patient.exercise_missed_days ?? 0;

    const conversation = [
        {
            speaker: 'agent',
            text: `Hi ${name}, this is CarePhysio assistant. We see ${missed} days of missed exercises. Are you facing any issue?`,
        },
        { speaker: 'patient', text: 'I have shoulder pain.' },
        {
            speaker: 'agent',
            text: "I'm sorry to hear that. Would you like to schedule an appointment?",
        },
        { speaker: 'patient', text: 'Yes.' },
        {
            speaker: 'agent',
            text: `${provider} has openings tomorrow at 11 AM or 4 PM. Which time works best?`,
        },
        { speaker: 'patient', text: '11 AM.' },
        {
            speaker: 'agent',
            text: 'Your appointment has been confirmed for tomorrow at 11 AM. Thank you and take care.',
        },
    ];

    let delay = 0;
    conversation.forEach((line, index) => {
        setTimeout(() => {
            addTranscriptLine(line.speaker, line.text);

            if (index === conversation.length - 1) {
                setTimeout(() => {
                    updateBookingStatus(
                        'Appointment Confirmed - Tomorrow 11 AM',
                        'confirmed'
                    );
                    updateCallStatus('Call Completed', 'completed');
                    activeCallPhone = null;
                    renderPatients();
                    loadRecentCalls();
                    if (transcriptInterval) {
                        clearInterval(transcriptInterval);
                    }
                }, 1000);
            }
        }, delay);
        delay += 2000;
    });
}

function addTranscriptLine(speaker, text) {
    const transcriptContent = document.getElementById('transcript-content');
    const placeholder = transcriptContent.querySelector('.transcript-placeholder');
    if (placeholder) {
        placeholder.remove();
    }

    const line = document.createElement('div');
    line.className = `transcript-line ${speaker}`;
    line.innerHTML = `<span class="speaker">${speaker.charAt(0).toUpperCase() + speaker.slice(1)}:</span> ${escapeHtml(text)}`;
    transcriptContent.appendChild(line);
    transcriptContent.scrollTop = transcriptContent.scrollHeight;
}

function clearTranscript() {
    const transcriptContent = document.getElementById('transcript-content');
    transcriptContent.innerHTML =
        '<p class="transcript-placeholder">Call transcript will appear here...</p>';
}

function updateCallStatus(status, className) {
    const statusElement = document.getElementById('call-status');
    statusElement.textContent = status;
    statusElement.className = `status-value ${className}`;
}

function updateBookingStatus(status, className) {
    const bookingElement = document.getElementById('booking-status');
    bookingElement.textContent = status;
    bookingElement.className = `booking-value ${className}`;
}

async function loadRecentCalls() {
    try {
        const response = await fetch(`${API_BASE}/transcripts`);
        const data = await response.json();
        renderRecentCalls(data.transcripts);
    } catch (error) {
        console.error('Error loading recent calls:', error);
    }
}

function renderRecentCalls(calls) {
    const container = document.getElementById('call-logs-container');

    if (!calls || calls.length === 0) {
        container.innerHTML =
            '<p class="logs-placeholder">No recent calls...</p>';
        return;
    }

    const recentCalls = calls.slice(-5).reverse();
    container.innerHTML = '';
    recentCalls.forEach((call) => {
        const entry = document.createElement('div');
        entry.className = 'log-entry';

        const timestamp = new Date(call.timestamp).toLocaleString();
        const patientName = call.patient_name || 'Unknown';
        const event = call.event || 'Unknown event';

        entry.innerHTML = `
            <div class="timestamp">${escapeHtml(timestamp)}</div>
            <div class="patient-name">${escapeHtml(patientName)}</div>
            <div class="event">${escapeHtml(event)}</div>
        `;
        container.appendChild(entry);
    });
}

function showError(message) {
    alert(message);
}

setInterval(loadRecentCalls, 30000);
