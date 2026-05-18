import { api } from './client'
import type { Member } from '../types'

export interface LoginResponse {
  token: string
  user: Member
}

export const authApi = {
  login: (username: string, password: string) =>
    api.post<LoginResponse>('/api/auth/login', { username, password }).then(r => r.data),
}
