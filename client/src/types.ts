export type Stage = 'Sketch' | 'ClientApproval' | 'Drawings' | 'Done'

export const STAGES: Stage[] = ['Sketch', 'ClientApproval', 'Drawings', 'Done']

export type Role = 'Architect' | 'Designer' | 'Constructor'

export const ROLES: Role[] = ['Architect', 'Designer', 'Constructor']

export type AccessLevel = 'User' | 'Manager' | 'Admin'

export const ACCESS_LEVELS: AccessLevel[] = ['User', 'Manager', 'Admin']

export type Priority = 'Low' | 'Medium' | 'High' | 'Urgent'

export const PRIORITIES: Priority[] = ['Low', 'Medium', 'High', 'Urgent']

export interface Member {
  id: number
  name: string
  role: Role
  username: string
  accessLevel: AccessLevel
}

export interface Attachment {
  id: number
  label: string
  url: string
}

export interface Comment {
  id: number
  author: string
  text: string
  createdAt: string
}

export interface Project {
  id: number
  title: string
  clientName: string
  description?: string | null
  stage: Stage
  priority: Priority
  position: number
  dueDate?: string | null
  createdAt: string
  members: Member[]
  attachments: Attachment[]
  comments: Comment[]
}
