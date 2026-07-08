import { PatientsProvider } from './context/PatientsContext.jsx'
import { Dashboard } from './pages/Dashboard/Dashboard'

function App() {
  return (
    <PatientsProvider>
      <Dashboard />
    </PatientsProvider>
  )
}

export default App
