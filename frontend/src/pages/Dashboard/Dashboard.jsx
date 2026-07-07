import { useMemo, useState } from 'react'
import { Navbar } from '../../components/Navbar/Navbar'
import { Footer } from '../../components/Footer/Footer'
import { GreetingBanner } from '../../components/GreetingBanner/GreetingBanner'
import { PatientTable } from '../../components/PatientTable/PatientTable'
import { EmptyState } from '../../components/EmptyState/EmptyState'
import { ErrorBanner } from '../../components/ErrorBanner/ErrorBanner'
import { TableSkeleton } from '../../components/TableSkeleton/TableSkeleton'
import { usePatients } from '../../hooks/usePatients'
import styles from './Dashboard.module.css'

function matchesSearch(patient, term) {
  if (!term) return true
  const haystack = `${patient.patient_name} ${patient.phone} ${patient.provider_name}`.toLowerCase()
  return haystack.includes(term.toLowerCase())
}

export function Dashboard() {
  const { patients, loading, error, pendingId, startCall, resetDemo, dismissError } =
    usePatients()
  const [searchTerm, setSearchTerm] = useState('')

  const filteredPatients = useMemo(
    () => patients.filter((patient) => matchesSearch(patient, searchTerm)),
    [patients, searchTerm],
  )

  const activeCount = patients.filter((p) => p.booking_status !== 'booked').length
  const doctorName = patients[0]?.provider_name

  return (
    <div className={styles.page}>
      <Navbar
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        onReset={resetDemo}
        resetting={false}
      />

      <div className={styles.container}>
        <GreetingBanner doctorName={doctorName} activeCount={activeCount} />

        {error && <ErrorBanner message={error} onDismiss={dismissError} />}

        <section className={styles.card}>
          <div className={styles.cardHeader}>
            <h2 className={styles.sectionTitle}>Patients Who Missed Exercises</h2>
            <p className={styles.sectionSubtitle}>Patients requiring immediate outreach</p>
          </div>

          {loading ? (
            <TableSkeleton />
          ) : filteredPatients.length === 0 ? (
            <EmptyState
              title={patients.length === 0 ? 'No patients found' : 'No matches'}
              description={
                patients.length === 0
                  ? 'Patient records will appear here once available.'
                  : 'Try a different name, phone number, or provider.'
              }
            />
          ) : (
            <PatientTable
              patients={filteredPatients}
              pendingId={pendingId}
              onStartCall={startCall}
            />
          )}
        </section>

        <Footer />
      </div>
    </div>
  )
}
