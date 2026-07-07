import styles from './SeverityPill.module.css'

export function SeverityPill({ level, children }) {
  return (
    <span className={`${styles.pill} ${level === 'urgent' ? styles.urgent : styles.followUp}`}>
      {children}
    </span>
  )
}
