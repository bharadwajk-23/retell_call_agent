import { apiRequest } from './client'

export function startCall(patientId) {
  return apiRequest('/calls/start', {
    method: 'POST',
    body: JSON.stringify({ patient_id: patientId }),
  })
}
