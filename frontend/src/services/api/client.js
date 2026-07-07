// Base HTTP client. Every API call in the app goes through this — no
// component ever calls fetch() directly.

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
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
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message))
  }

  return payload ?? {}
}
