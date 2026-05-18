import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../auth/AuthContext'
import { changeLanguage } from '../i18n'

export function LoginPage() {
  const { t, i18n } = useTranslation()
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const next = params.get('next') || '/'

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (user) navigate(next, { replace: true })
  }, [user, next, navigate])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!username.trim() || !password) return
    setSubmitting(true)
    setError(null)
    try {
      await login(username.trim(), password)
      navigate(next, { replace: true })
    } catch {
      setError(t('login.error'))
    } finally {
      setSubmitting(false)
    }
  }

  const current = i18n.resolvedLanguage ?? i18n.language ?? 'uk'

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-md bg-brand-600 flex items-center justify-center text-white font-bold text-lg">
              A
            </div>
            <div className="leading-tight">
              <div className="font-semibold text-slate-900">{t('app.title')}</div>
              <div className="text-xs text-slate-500">{t('app.subtitle')}</div>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <LangBtn active={current === 'uk'} onClick={() => changeLanguage('uk')}>UK</LangBtn>
            <LangBtn active={current === 'en'} onClick={() => changeLanguage('en')}>EN</LangBtn>
          </div>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 space-y-4"
        >
          <div>
            <h1 className="text-xl font-semibold text-slate-900">{t('login.title')}</h1>
            <p className="text-sm text-slate-500 mt-1">{t('login.subtitle')}</p>
          </div>

          <Field label={t('login.username')}>
            <input
              autoFocus
              value={username}
              onChange={e => setUsername(e.target.value)}
              autoComplete="username"
              className="login-input"
            />
          </Field>

          <Field label={t('login.password')}>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete="current-password"
              className="login-input"
            />
          </Field>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-2">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting || !username.trim() || !password}
            className="w-full px-4 py-2 text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-md disabled:opacity-50"
          >
            {submitting ? t('login.submitting') : t('login.submit')}
          </button>

          <div className="text-center pt-1">
            <Link
              to="/"
              className="text-xs font-medium text-slate-500 hover:text-brand-700"
            >
              {t('login.continueAsGuest')}
            </Link>
          </div>
        </form>

        <div className="mt-6 text-xs text-slate-500 bg-white border border-dashed border-slate-300 rounded-lg p-4">
          <div className="font-medium text-slate-700 mb-1">{t('login.demoHint')}</div>
          <ul className="space-y-0.5 font-mono">
            <li>{t('login.demoAdmin')}</li>
            <li>{t('login.demoManager')}</li>
            <li>{t('login.demoUser')}</li>
          </ul>
        </div>
      </div>

      <style>{`
        .login-input {
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
        .login-input:focus {
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

function LangBtn({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-2.5 py-1 text-xs font-semibold rounded-md border transition-colors ${
        active
          ? 'bg-brand-600 text-white border-brand-600'
          : 'bg-white text-slate-600 border-slate-200 hover:border-brand-400 hover:text-brand-700'
      }`}
    >
      {children}
    </button>
  )
}
