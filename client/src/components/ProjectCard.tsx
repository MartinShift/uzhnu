import { useTranslation } from 'react-i18next'
import type { Project, Role } from '../types'
import { priorityStyles } from './priority'

const roleStyles: Record<Role, string> = {
  Architect:   'bg-brand-50 text-brand-700 border-brand-200',
  Designer:    'bg-amber-50 text-amber-700 border-amber-200',
  Constructor: 'bg-slate-100 text-slate-700 border-slate-200',
}

interface Props {
  project: Project
  onClick: () => void
  isDragging?: boolean
}

export function ProjectCard({ project, onClick, isDragging = false }: Props) {
  const { t, i18n } = useTranslation()

  const due = project.dueDate ? new Date(project.dueDate) : null
  const overdue = due && due.getTime() < Date.now() && project.stage !== 'Done'

  const dueText = due
    ? due.toLocaleDateString(i18n.resolvedLanguage === 'en' ? 'en-GB' : 'uk-UA', {
        day: '2-digit',
        month: 'short',
      })
    : null

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onClick()
        }
      }}
      className={`group relative w-full text-left bg-white rounded-lg border shadow-sm hover:shadow-md hover:border-brand-300 transition-all p-3 space-y-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400 ${
        isDragging
          ? 'cursor-grabbing border-brand-400'
          : 'cursor-grab active:cursor-grabbing border-slate-200'
      }`}
    >
      <span
        aria-hidden
        className="absolute top-2 right-2 text-slate-300 group-hover:text-slate-400 text-xs leading-none select-none"
      >
        ⋮⋮
      </span>

      <div className="flex items-start gap-2 pr-4">
        <span
          className={`shrink-0 mt-0.5 text-[10px] uppercase tracking-wide font-semibold px-1.5 py-0.5 rounded border ${priorityStyles[project.priority]}`}
          title={t('card.priority')}
        >
          {t(`priority.${project.priority}`)}
        </span>
        <div className="font-semibold text-slate-900 leading-snug">
          {project.title}
        </div>
      </div>

      <div className="text-xs text-slate-500">
        {project.clientName || t('card.noClient')}
      </div>

      {project.members.length > 0 && (
        <div className="flex flex-wrap gap-1 pt-1">
          {project.members.slice(0, 4).map(m => (
            <span
              key={m.id}
              className={`text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded border ${roleStyles[m.role]}`}
              title={`${m.name} — ${t(`role.${m.role}`)}`}
            >
              {m.name.split(' ')[0]}
            </span>
          ))}
          {project.members.length > 4 && (
            <span className="text-[10px] text-slate-400">+{project.members.length - 4}</span>
          )}
        </div>
      )}

      <div className="flex items-center justify-between text-xs pt-1">
        <span className="text-slate-400">
          {project.attachments.length > 0
            ? `${t('card.attachments')}: ${project.attachments.length}`
            : ''}
        </span>
        {dueText && (
          <span className={overdue ? 'text-red-600 font-medium' : 'text-slate-500'}>
            {dueText}
          </span>
        )}
      </div>
    </div>
  )
}
