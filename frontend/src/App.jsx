import { AuthProvider } from './context/AuthContext.jsx'
import { PatientsProvider } from './context/PatientsContext.jsx'
import { useAuth } from './hooks/useAuth'
import { Login } from './pages/Login/Login'
import { Dashboard } from './pages/Dashboard/Dashboard'

function AuthGate() {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return <Login />
  }

  return (
    <PatientsProvider>
      <Dashboard />
    </PatientsProvider>
  )
}

function App() {
  return (
    <AuthProvider>
      <AuthGate />
    </AuthProvider>
  )
}

export default App
