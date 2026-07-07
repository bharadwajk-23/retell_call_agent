import styles from './TableSkeleton.module.css'

export function TableSkeleton({ rows = 4 }) {
  return (
    <div className={styles.wrap}>
      {Array.from({ length: rows }).map((_, i) => (
        <div className={styles.row} key={i}>
          <span className={styles.bar} style={{ width: '22%' }} />
          <span className={styles.bar} style={{ width: '18%' }} />
          <span className={styles.bar} style={{ width: '12%' }} />
          <span className={styles.bar} style={{ width: '10%' }} />
          <span className={styles.bar} style={{ width: '18%' }} />
          <span className={styles.pill} />
        </div>
      ))}
    </div>
  )
}
