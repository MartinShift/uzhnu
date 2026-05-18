import { api } from './client'
import type { AccessLevel, Member, Role } from '../types'

export interface CreateMemberInput {
  name: string
  role: Role
  username: string
  password: string
  accessLevel: AccessLevel
}

export const membersApi = {
  list: () => api.get<Member[]>('/api/members').then(r => r.data),

  create: (input: CreateMemberInput) =>
    api.post<Member>('/api/members', input).then(r => r.data),

  remove: (id: number) => api.delete(`/api/members/${id}`),
}
