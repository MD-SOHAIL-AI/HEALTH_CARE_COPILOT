import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { getMe, getPatient, login as apiLogin, register as apiRegister } from './api'
import type { Patient, User } from './types'

interface AuthState {
  user: User | null
  patient: Patient | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: {
    email: string
    password: string
    full_name: string
    preferred_language?: string
  }) => Promise<void>
  logout: () => void
  refreshPatient: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [patient, setPatient] = useState<Patient | null>(null)
  const [loading, setLoading] = useState(true)

  const bootstrap = useCallback(async () => {
    const token = localStorage.getItem('medcare_token')
    if (!token) {
      setLoading(false)
      return
    }
    try {
      const [u, p] = await Promise.all([getMe(), getPatient()])
      setUser(u)
      setPatient(p)
    } catch {
      localStorage.removeItem('medcare_token')
      setUser(null)
      setPatient(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void bootstrap()
  }, [bootstrap])

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await apiLogin(email, password)
    localStorage.setItem('medcare_token', access_token)
    const [u, p] = await Promise.all([getMe(), getPatient()])
    setUser(u)
    setPatient(p)
  }, [])

  const register = useCallback(
    async (data: {
      email: string
      password: string
      full_name: string
      preferred_language?: string
    }) => {
      const { access_token } = await apiRegister(data)
      localStorage.setItem('medcare_token', access_token)
      const [u, p] = await Promise.all([getMe(), getPatient()])
      setUser(u)
      setPatient(p)
    },
    [],
  )

  const logout = useCallback(() => {
    localStorage.removeItem('medcare_token')
    setUser(null)
    setPatient(null)
  }, [])

  const refreshPatient = useCallback(async () => {
    const p = await getPatient()
    setPatient(p)
  }, [])

  const value = useMemo(
    () => ({ user, patient, loading, login, register, logout, refreshPatient }),
    [user, patient, loading, login, register, logout, refreshPatient],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
