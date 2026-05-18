import type { Priority } from '../types'

export const priorityStyles: Record<Priority, string> = {
  Low:    'bg-slate-100 text-slate-600 border-slate-300',
  Medium: 'bg-sky-50 text-sky-700 border-sky-300',
  High:   'bg-amber-50 text-amber-700 border-amber-300',
  Urgent: 'bg-red-50 text-red-700 border-red-300',
}

export const priorityDot: Record<Priority, string> = {
  Low:    'bg-slate-400',
  Medium: 'bg-sky-500',
  High:   'bg-amber-500',
  Urgent: 'bg-red-500',
}
