import { AuthProvider, useAuth } from './context/AuthContext'
import { PatientsProvider } from './context/PatientsContext.jsx'
import { Dashboard } from './pages/Dashboard/Dashboard'
import { Login } from './pages/Login/Login'

function AppContent() {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <p>Loading...</p>
      </div>
    )
  }

  return isAuthenticated ? (
    <PatientsProvider>
      <Dashboard />
    </PatientsProvider>
  ) : (
    <Login />
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
