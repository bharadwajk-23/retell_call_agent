import { getBookingStatusMeta } from '../../utils/status'
import styles from './CallActionButton.module.css'

const VARIANT_CLASS = {
  'not-booked': styles.notBooked,
  'in-progress': styles.inProgress,
  booked: styles.booked,
}

export function CallActionButton({ bookingStatus, pending, onClick }) {
  const meta = getBookingStatusMeta(bookingStatus)
  const disabled = meta.disabled || pending

  return (
    <button
      type="button"
      className={`${styles.button} ${VARIANT_CLASS[meta.variant] || ''}`}
      disabled={disabled}
      onClick={onClick}
    >
      {pending ? 'Starting…' : meta.variant === 'not-booked' ? `📞 ${meta.label}` : meta.label}
    </button>
  )
}
