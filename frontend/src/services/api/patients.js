import { apiRequest } from './client'

export function getPatients() {
  return apiRequest('/patients')
}

export function resetPatients() {
  return apiRequest('/patients/reset', { method: 'POST' })
}
