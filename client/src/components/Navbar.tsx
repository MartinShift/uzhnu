import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { changeLanguage } from '../i18n'
import { useAuth } from '../auth/AuthContext'

export function Navbar() {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const current = i18n.resolvedLanguage ?? i18n.language ?? 'uk'

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="sticky top-0 z-20 bg-white/90 backdrop-blur border-b border-slate-200">
      <div className="mx-auto max-w-7xl px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link
            to="/"
            className="flex items-center gap-2 rounded-md -mx-2 px-2 py-1 hover:bg-slate-100 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400"
          >
            <div className="w-8 h-8 rounded-md bg-brand-600 flex items-center justify-center text-white font-bold">
              A
            </div>
            <div className="leading-tight text-left">
              <div className="font-semibold text-slate-900">{t('app.title')}</div>
              <div className="text-xs text-slate-500">{t('app.subtitle')}</div>
            </div>
          </Link>

          <nav className="flex items-center gap-1">
            <TabLink to="/">{t('nav.board')}</TabLink>
            {user && <TabLink to="/members">{t('nav.members')}</TabLink>}
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <LanguageButton active={current === 'uk'} onClick={() => changeLanguage('uk')}>
              UK
            </LanguageButton>
            <LanguageButton active={current === 'en'} onClick={() => changeLanguage('en')}>
              EN
            </LanguageButton>
          </div>

          {user ? (
            <div className="flex items-center gap-2 pl-4 border-l border-slate-200">
              <div className="w-8 h-8 rounded-full bg-brand-100 text-brand-700 text-xs font-semibold flex items-center justify-center">
                {initials(user.name)}
              </div>
              <div className="leading-tight text-right hidden sm:block">
                <div className="text-sm font-medium text-slate-800">{user.name}</div>
                <div className="text-[10px] uppercase tracking-wide text-slate-500">
                  {t(`access.${user.accessLevel}`)}
                </div>
              </div>
              <button
                type="button"
                onClick={handleLogout}
                title={t('nav.logout')}
                className="ml-2 text-xs font-medium text-slate-500 hover:text-red-600 px-2 py-1 rounded-md hover:bg-red-50"
              >
                {t('nav.logout')}
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2 pl-4 border-l border-slate-200">
              <span className="text-xs text-slate-500 hidden sm:inline">{t('nav.guest')}</span>
              <Link
                to="/login"
                className="px-3 py-1.5 text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-md shadow-sm"
              >
                {t('nav.login')}
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

function TabLink({ to, children }: { to: string; children: React.ReactNode }) {
  return (
    <NavLink
      to={to}
      end
      className={({ isActive }) =>
        `px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
          isActive
            ? 'bg-brand-50 text-brand-700'
            : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
        }`
      }
    >
      {children}
    </NavLink>
  )
}

function LanguageButton({
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

function initials(name: string) {
  return name
    .split(' ')
    .map(s => s[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase()
}
