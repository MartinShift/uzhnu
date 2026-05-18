import { useCallback, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { membersApi } from '../api/members'
import { useAuth } from '../auth/AuthContext'
import type { AccessLevel, Member, Role } from '../types'
import { ACCESS_LEVELS, ROLES } from '../types'

const roleAccent: Record<Role, string> = {
  Architect:   'bg-brand-50 text-brand-700 border-brand-200',
  Designer:    'bg-amber-50 text-amber-700 border-amber-200',
  Constructor: 'bg-slate-100 text-slate-700 border-slate-200',
}

const accessAccent: Record<AccessLevel, string> = {
  User:    'bg-slate-100 text-slate-600 border-slate-300',
  Manager: 'bg-sky-50 text-sky-700 border-sky-300',
  Admin:   'bg-red-50 text-red-700 border-red-300',
}

export function MembersPage() {
  const { t } = useTranslation()
  const { isManagerOrAdmin } = useAuth()
  const [members, setMembers] = useState<Member[]>([])
  const [loading, setLoading] = useState(true)

  const [name, setName] = useState('')
  const [role, setRole] = useState<Role>('Architect')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [accessLevel, setAccessLevel] = useState<AccessLevel>('User')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      setMembers(await membersApi.list())
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim() || !username.trim() || !password) return
    setSubmitting(true)
    setError(null)
    try {
      await membersApi.create({
        name: name.trim(),
        role,
        username: username.trim(),
        password,
        accessLevel,
      })
      setName('')
      setUsername('')
      setPassword('')
      setAccessLevel('User')
      await load()
    } catch (err: unknown) {
      const e = err as { response?: { status?: number; data?: { message?: string } } }
      if (e?.response?.status === 409) {
        setError(e.response?.data?.message ?? 'Username already taken')
      } else {
        setError(String(err))
      }
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(m: Member) {
    if (!confirm(t('members.deleteConfirm', { name: m.name }))) return
    await membersApi.remove(m.id)
    await load()
  }

  return (
    <div className="flex-1 px-6 py-6">
      <div className="mx-auto max-w-3xl">
        <h1 className="text-xl font-semibold text-slate-800 mb-4">
          {t('members.title')}
        </h1>

        {isManagerOrAdmin ? (
          <form
            onSubmit={handleAdd}
            className="bg-white border border-slate-200 rounded-xl p-4 mb-6 shadow-sm space-y-3"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Field label={t('members.name')}>
                <input
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder={t('members.placeholderName')}
                  className="m-input"
                />
              </Field>
              <Field label={t('members.role')}>
                <select
                  value={role}
                  onChange={e => setRole(e.target.value as Role)}
                  className="m-input"
                >
                  {ROLES.map(r => (
                    <option key={r} value={r}>{t(`role.${r}`)}</option>
                  ))}
                </select>
              </Field>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <Field label={t('members.username')}>
                <input
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  placeholder={t('members.placeholderUsername')}
                  autoComplete="off"
                  className="m-input"
                />
              </Field>
              <Field label={t('members.password')}>
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder={t('members.placeholderPassword')}
                  autoComplete="new-password"
                  className="m-input"
                />
              </Field>
              <Field label={t('members.access')}>
                <select
                  value={accessLevel}
                  onChange={e => setAccessLevel(e.target.value as AccessLevel)}
                  className="m-input"
                >
                  {ACCESS_LEVELS.map(a => (
                    <option key={a} value={a}>{t(`access.${a}`)}</option>
                  ))}
                </select>
              </Field>
            </div>

            {error && (
              <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-2">
                {error}
              </div>
            )}

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={submitting || !name.trim() || !username.trim() || password.length < 4}
                className="px-4 py-2 text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-md disabled:opacity-50"
              >
                {t('members.add')}
              </button>
            </div>
          </form>
        ) : (
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 mb-6 text-sm text-slate-500">
            {t('members.onlyManagersCanAdd')}
          </div>
        )}

        {loading ? (
          <div className="text-sm text-slate-500">{t('board.loading')}</div>
        ) : members.length === 0 ? (
          <div className="text-sm text-slate-500 italic">{t('members.empty')}</div>
        ) : (
          <ul className="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100 shadow-sm overflow-hidden">
            {members.map(m => (
              <li key={m.id} className="flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-9 h-9 rounded-full bg-brand-100 text-brand-700 font-semibold flex items-center justify-center text-sm shrink-0">
                    {initials(m.name)}
                  </div>
                  <div className="min-w-0">
                    <div className="font-medium text-slate-900 text-sm truncate">
                      {m.name}
                      <span className="ml-2 text-xs text-slate-400 font-normal">@{m.username}</span>
                    </div>
                    <div className="flex items-center gap-1 mt-0.5 flex-wrap">
                      <span className={`text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded border ${roleAccent[m.role]}`}>
                        {t(`role.${m.role}`)}
                      </span>
                      <span className={`text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded border ${accessAccent[m.accessLevel]}`}>
                        {t(`access.${m.accessLevel}`)}
                      </span>
                    </div>
                  </div>
                </div>
                {isManagerOrAdmin && (
                  <button
                    onClick={() => handleDelete(m)}
                    className="text-xs text-slate-400 hover:text-red-600 font-medium ml-3 shrink-0"
                  >
                    {t('common.delete')}
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>

      <style>{`
        .m-input {
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
        .m-input:focus {
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

function initials(name: string) {
  return name
    .split(' ')
    .map(s => s[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase()
}
