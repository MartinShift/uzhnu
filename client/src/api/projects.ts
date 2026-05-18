import { api } from './client'
import type { Attachment, Comment, Priority, Project, Stage } from '../types'

export interface CreateProjectInput {
  title: string
  clientName: string
  description?: string | null
  stage: Stage
  priority?: Priority
  dueDate?: string | null
}

export interface UpdateProjectInput {
  title: string
  clientName: string
  description?: string | null
  priority: Priority
  dueDate?: string | null
}

export const projectsApi = {
  list: () => api.get<Project[]>('/api/projects').then(r => r.data),

  get: (id: number) => api.get<Project>(`/api/projects/${id}`).then(r => r.data),

  create: (input: CreateProjectInput) =>
    api.post<Project>('/api/projects', input).then(r => r.data),

  update: (id: number, input: UpdateProjectInput) =>
    api.put<Project>(`/api/projects/${id}`, input).then(r => r.data),

  remove: (id: number) => api.delete(`/api/projects/${id}`),

  move: (id: number, stage: Stage, position: number) =>
    api.patch(`/api/projects/${id}/move`, { stage, position }),

  assignMember: (projectId: number, memberId: number) =>
    api.post(`/api/projects/${projectId}/members/${memberId}`),

  unassignMember: (projectId: number, memberId: number) =>
    api.delete(`/api/projects/${projectId}/members/${memberId}`),

  addAttachment: (projectId: number, label: string, url: string) =>
    api.post<Attachment>(`/api/projects/${projectId}/attachments`, { label, url }).then(r => r.data),

  removeAttachment: (attachmentId: number) =>
    api.delete(`/api/attachments/${attachmentId}`),

  addComment: (projectId: number, text: string) =>
    api.post<Comment>(`/api/projects/${projectId}/comments`, { text }).then(r => r.data),

  removeComment: (commentId: number) =>
    api.delete(`/api/projects/comments/${commentId}`),
}
