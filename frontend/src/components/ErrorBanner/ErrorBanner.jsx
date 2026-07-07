import styles from './ErrorBanner.module.css'

export function ErrorBanner({ message, onDismiss }) {
  if (!message) return null

  return (
    <div className={styles.banner} role="alert">
      <span>{message}</span>
      <button type="button" className={styles.dismiss} onClick={onDismiss} aria-label="Dismiss">
        ×
      </button>
    </div>
  )
}
