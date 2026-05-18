import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { authApi } from '../api/auth'
import type { Member } from '../types'
import { authStorage } from './storage'

interface AuthContextValue {
  user: Member | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  isManagerOrAdmin: boolean
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<Member | null>(() => authStorage.load()?.user ?? null)

  useEffect(() => {
    const onStorage = () => setUser(authStorage.load()?.user ?? null)
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    const res = await authApi.login(username, password)
    authStorage.save(res.token, res.user)
    setUser(res.user)
  }, [])

  const logout = useCallback(() => {
    authStorage.clear()
    setUser(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      login,
      logout,
      isManagerOrAdmin: user?.accessLevel === 'Admin' || user?.accessLevel === 'Manager',
    }),
    [user, login, logout]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
