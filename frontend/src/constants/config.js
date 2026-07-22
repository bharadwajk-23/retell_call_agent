// App-wide constants — the single place magic numbers/strings live.

export const POLL_INTERVAL_MS = 2000
export const URGENT_MISSED_DAYS_THRESHOLD = 10

export const BOOKING_STATUS = {
  NOT_BOOKED: 'not booked',
  IN_PROGRESS: 'in progress',
  BOOKED: 'booked',
}

// Static demo login — no real auth, just a client-side gate in front of the
// dashboard. Credentials live in the bundled JS, so this is not a security
// boundary; don't rely on it to protect anything sensitive.
export const AUTH_USERNAME = 'admin'
export const AUTH_PASSWORD = 'admin123'
export const AUTH_STORAGE_KEY = 'medicare_authenticated'
