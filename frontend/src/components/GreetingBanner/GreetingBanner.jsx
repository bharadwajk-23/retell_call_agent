import { useTimeOfDay } from '../../hooks/useTimeOfDay'
import styles from './GreetingBanner.module.css'

export function GreetingBanner({ doctorName, activeCount }) {
  const period = useTimeOfDay()

  return (
    <section className={`${styles.banner} ${styles[period.key]}`}>
      <div className={styles.content}>
        <span className={styles.pill}>
          <span className={styles.onlineDot} aria-hidden="true" />
          AI Assistant Online
        </span>
        <h1 className={styles.heading}>
          <span aria-hidden="true">{period.icon}</span> {period.greeting}
          {doctorName ? `, ${doctorName}` : ''}
        </h1>
        <p className={styles.subtext}>
          You have <strong>{activeCount}</strong>{' '}
          {activeCount === 1 ? 'patient' : 'patients'} who missed exercises prescribed. Start
          automated outreach or place a live call.
        </p>
      </div>
    </section>
  )
}
