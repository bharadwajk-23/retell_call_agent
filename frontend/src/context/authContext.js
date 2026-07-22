// Plain (non-component) module holding the context object itself, kept
// separate from the Provider component file for React Fast Refresh.
import { createContext } from 'react'

export const AuthContext = createContext(null)
