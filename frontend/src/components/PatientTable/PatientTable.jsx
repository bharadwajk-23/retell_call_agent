import { CallActionButton } from '../CallActionButton/CallActionButton'
import { SeverityPill } from '../SeverityPill/SeverityPill'
import { formatPatientCode, getInitials, getMissedDaysSeverity } from '../../utils/severity'
import styles from './PatientTable.module.css'

const COLUMNS = ['Patient', 'Contact', 'DOB', 'Days Missed', 'Provider', 'Action']

export function PatientTable({ patients, pendingId, onStartCall }) {
  return (
    <div className={styles.tableContainer}>
      <table className={styles.table}>
        <thead>
          <tr>
            {COLUMNS.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {patients.map((patient) => {
            const severity = getMissedDaysSeverity(patient.exercise_missed_days)
            const patientName = patient.patient_name || 'Unknown patient'

            return (
              <tr key={patient.id}>
                <td data-label="Patient">
                  <div className={styles.patientCell}>
                    <span className={styles.avatar}>{getInitials(patientName)}</span>
                    <div>
                      <p className={styles.patientName}>{patientName}</p>
                      <p className={styles.patientCode}>{formatPatientCode(patient.id)}</p>
                    </div>
                  </div>
                </td>
                <td data-label="Contact">
                  <span className={styles.contact}>📞 {patient.phone}</span>
                </td>
                <td data-label="DOB">{patient.dob || '—'}</td>
                <td data-label="Days Missed">
                  <SeverityPill level={severity.level}>
                    {patient.exercise_missed_days ?? 0}d
                  </SeverityPill>
                </td>
                <td data-label="Provider">
                  <span className={styles.provider}>👤 {patient.provider_name}</span>
                </td>
                <td data-label="Action" className={styles.actionCell}>
                  <CallActionButton
                    bookingStatus={patient.booking_status}
                    pending={pendingId === patient.id}
                    onClick={() => onStartCall(patient.id)}
                  />
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
