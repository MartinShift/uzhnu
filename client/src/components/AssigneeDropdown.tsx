import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import type { Member } from '../types'

interface Props {
  available: Member[]
  onPick: (memberId: number) => void
  disabled?: boolean
}

export function AssigneeDropdown({ available, onPick, disabled }: Props) {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (!ref.current?.contains(e.target as Node)) setOpen(false)
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', onDocClick)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onDocClick)
      document.removeEventListener('keydown', onKey)
    }
  }, [])

  return (
    <div ref={ref} className="relative inline-block">
      <button
        type="button"
        onClick={() => setOpen(v => !v)}
        disabled={disabled || available.length === 0}
        className="text-xs font-medium px-2.5 py-1 rounded-full border border-dashed border-slate-400 text-slate-600 hover:border-brand-500 hover:text-brand-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {t('detail.addAssignee')}
      </button>

      {open && available.length > 0 && (
        <div className="absolute left-0 mt-1 z-10 w-56 bg-white border border-slate-200 rounded-lg shadow-lg max-h-64 overflow-y-auto">
          {available.map(m => (
            <button
              key={m.id}
              type="button"
              onClick={() => {
                onPick(m.id)
                setOpen(false)
              }}
              className="w-full text-left px-3 py-2 text-sm hover:bg-brand-50 flex items-center justify-between gap-2"
            >
              <span className="text-slate-800 truncate">{m.name}</span>
              <span className="text-[10px] uppercase tracking-wide text-slate-400 shrink-0">
                {t(`role.${m.role}`)}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
