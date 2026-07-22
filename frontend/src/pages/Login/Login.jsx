import { useState } from 'react'
import { useAuth } from '../../hooks/useAuth'
import styles from './Login.module.css'

export function Login() {
  const { login, error, dismissError } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  function handleSubmit(event) {
    event.preventDefault()
    login(username, password)
  }

  return (
    <div className={styles.page}>
      <form className={styles.card} onSubmit={handleSubmit}>
        <div className={styles.brand}>
          <span className={styles.logo} aria-hidden="true">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2a1 1 0 0 1 1.02-.24c1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1.02l-2.2 2.2Z"
                fill="#ffffff"
              />
            </svg>
          </span>
          <div>
            <p className={styles.brandName}>MediCare</p>
            <p className={styles.brandSubtitle}>AI Call Assistant</p>
          </div>
        </div>

        <h1 className={styles.heading}>Sign in</h1>
        <p className={styles.subtext}>Use your staff credentials to access the dashboard.</p>

        {error && (
          <div className={styles.error} role="alert">
            <span>{error}</span>
            <button type="button" className={styles.errorDismiss} onClick={dismissError} aria-label="Dismiss">
              ×
            </button>
          </div>
        )}

        <label className={styles.label} htmlFor="login-username">
          Username
        </label>
        <input
          id="login-username"
          className={styles.input}
          type="text"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          autoComplete="username"
          autoFocus
          required
        />

        <label className={styles.label} htmlFor="login-password">
          Password
        </label>
        <input
          id="login-password"
          className={styles.input}
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          required
        />

        <button type="submit" className={styles.submitButton}>
          Sign in
        </button>
      </form>
    </div>
  )
}
