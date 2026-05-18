import type { Member } from '../types'

const TOKEN_KEY = 'archkanban.token'
const USER_KEY = 'archkanban.user'

export interface StoredAuth {
  token: string
  user: Member
}

export const authStorage = {
  load(): StoredAuth | null {
    if (typeof window === 'undefined') return null
    const token = localStorage.getItem(TOKEN_KEY)
    const userRaw = localStorage.getItem(USER_KEY)
    if (!token || !userRaw) return null
    try {
      return { token, user: JSON.parse(userRaw) as Member }
    } catch {
      return null
    }
  },
  save(token: string, user: Member) {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },
  getToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(TOKEN_KEY)
  },
}
