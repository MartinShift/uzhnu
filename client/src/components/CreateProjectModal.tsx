import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { projectsApi } from '../api/projects'
import type { Priority, Stage } from '../types'
import { PRIORITIES, STAGES } from '../types'
import { priorityDot } from './priority'

interface Props {
  defaultStage?: Stage
  onClose: () => void
}

export function CreateProjectModal({ defaultStage = 'Sketch', onClose }: Props) {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const [title, setTitle] = useState('')
  const [stage, setStage] = useState<Stage>(defaultStage)
  const [priority, setPriority] = useState<Priority>('Medium')
  const [dueDate, setDueDate] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim()) return
    setSaving(true)
    setError(null)
    try {
      const created = await projectsApi.create({
        title: title.trim(),
        clientName: '',
        stage,
        priority,
        dueDate: dueDate ? new Date(dueDate).toISOString() : null,
      })
      navigate(`/projects/${created.id}`)
    } catch (err) {
      console.error(err)
      setError(String(err))
      setSaving(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-30 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={onClose}
    >
      <form
        onSubmit={handleSubmit}
        onClick={e => e.stopPropagation()}
        className="bg-white w-full max-w-md rounded-xl shadow-2xl overflow-hidden"
      >
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">{t('create.title')}</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 text-2xl leading-none"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <div className="px-6 py-5 space-y-4">
          <Field label={t('create.titleLabel')}>
            <input
              autoFocus
              value={title}
              onChange={e => setTitle(e.target.value)}
              className="modal-input"
              required
            />
          </Field>

          <div className="grid grid-cols-2 gap-4">
            <Field label={t('create.stageLabel')}>
              <select
                value={stage}
                onChange={e => setStage(e.target.value as Stage)}
                className="modal-input"
              >
                {STAGES.map(s => (
                  <option key={s} value={s}>{t(`stage.${s}`)}</option>
                ))}
              </select>
            </Field>

            <Field label={t('card.priority')}>
              <select
                value={priority}
                onChange={e => setPriority(e.target.value as Priority)}
                className="modal-input"
              >
                {PRIORITIES.map(p => (
                  <option key={p} value={p}>{t(`priority.${p}`)}</option>
                ))}
              </select>
            </Field>
          </div>

          <Field label={t('detail.dueDate')}>
            <input
              type="date"
              value={dueDate}
              onChange={e => setDueDate(e.target.value)}
              className="modal-input"
            />
          </Field>

          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className={`w-2 h-2 rounded-full ${priorityDot[priority]}`} />
            <span>{t(`priority.${priority}`)}</span>
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-2">
              {error}
            </div>
          )}
        </div>

        <div className="px-6 py-4 border-t border-slate-200 flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            disabled={saving}
            className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-md disabled:opacity-50"
          >
            {t('create.cancel')}
          </button>
          <button
            type="submit"
            disabled={saving || !title.trim()}
            className="px-4 py-2 text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-md disabled:opacity-50"
          >
            {t('create.create')}
          </button>
        </div>
      </form>

      <style>{`
        .modal-input {
          display: block;
          width: 100%;
          border-radius: 0.5rem;
          border: 1px solid rgb(203 213 225);
          background-color: white;
          padding: 0.5rem 0.75rem;
          font-size: 0.875rem;
          color: rgb(15 23 42);
          outline: none;
        }
        .modal-input:focus {
          border-color: rgb(13 148 136);
          box-shadow: 0 0 0 3px rgb(204 251 241);
        }
      `}</style>
    </div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="block text-xs font-medium uppercase tracking-wide text-slate-500 mb-1">
        {label}
      </span>
      {children}
    </label>
  )
}
