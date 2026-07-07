// Thin wrappers around the existing FastAPI endpoints (app/main_new.py).
// Contracts are reused exactly as-is — no new endpoints, no shape changes.

const API_BASE = import.meta.env.VITE_API_BASE || window.location.origin

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  const contentType = response.headers.get('content-type') || ''
  const isJson = contentType.includes('application/json')
  const payload = isJson
    ? await response.json().catch(() => null)
    : await response.text().catch(() => '')

  if (!response.ok) {
    const message = payload?.detail || payload || `Request failed (${response.status})`
    throw new Error(message)
  }

  return payload ?? {}
}

export function getPatients() {
  return request('/patients')
}

export function startCall(patientId) {
  return request('/start-call', {
    method: 'POST',
    body: JSON.stringify({ patient_id: patientId }),
  })
}

export function resetDemo() {
  return request('/reset-patients', { method: 'POST' })
}
