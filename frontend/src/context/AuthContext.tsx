import React, { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../api/client'

interface User {
  id: string
  email: string
  rol: string
  empresa_id?: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType>(null!)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
    }
    setLoading(false)
  }, [])

  async function login(email: string, password: string) {
    const form = new FormData()
    form.append('username', email)
    form.append('password', password)
    const { data } = await api.post('/auth/login', form)
    localStorage.setItem('token', data.access_token)
    setToken(data.access_token)
    const { data: me } = await api.get('/auth/me', {
      headers: { Authorization: `Bearer ${data.access_token}` },
    })
    localStorage.setItem('user', JSON.stringify(me))
    setUser(me)
  }

  function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('espacio')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
