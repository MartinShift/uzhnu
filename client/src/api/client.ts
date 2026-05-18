import axios from 'axios'
import { authStorage } from '../auth/storage'

const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:5080'

export const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use(config => {
  const token = authStorage.getToken()
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }
  return config
})

api.interceptors.response.use(
  r => r,
  err => {
    if (err?.response?.status === 401) {
      authStorage.clear()
      const here = window.location.pathname
      if (here !== '/login') {
        window.location.assign(`/login?next=${encodeURIComponent(here)}`)
      }
    }
    return Promise.reject(err)
  }
)
