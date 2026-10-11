import { NavLink, Outlet } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  Activity,
  CalendarRange,
  FileUp,
  LayoutDashboard,
  LogOut,
  Pill,
  UserRound,
  Bot,
} from 'lucide-react'
import clsx from 'clsx'
import { useAuth } from '../lib/auth'
import { Button } from './ui'

const links = [
  { to: '/', key: 'dashboard', icon: LayoutDashboard },
  { to: '/upload', key: 'upload', icon: FileUp },
  { to: '/copilot', key: 'copilot', icon: Bot },
  { to: '/timeline', key: 'timeline', icon: CalendarRange },
  { to: '/medications', key: 'medications', icon: Pill },
  { to: '/labs', key: 'labs', icon: Activity },
  { to: '/profile', key: 'profile', icon: UserRound },
] as const

export function Layout() {
  const { t, i18n } = useTranslation()
  const { user, logout } = useAuth()

  const setLang = (lng: string) => {
    void i18n.changeLanguage(lng)
    localStorage.setItem('medcare_lang', lng)
  }

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[260px_1fr]">
      <aside className="border-b border-brand-100 bg-white/80 backdrop-blur lg:sticky lg:top-0 lg:h-screen lg:border-b-0 lg:border-r">
        <div className="flex h-full flex-col p-5">
          <div className="mb-8">
            <div className="font-display text-2xl font-bold text-brand-800">{t('appName')}</div>
            <p className="mt-1 text-xs leading-relaxed text-muted">{t('tagline')}</p>
          </div>
          <nav className="flex gap-1 overflow-x-auto lg:flex-col lg:overflow-visible">
            {links.map(({ to, key, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-2 whitespace-nowrap rounded-xl px-3 py-2.5 text-sm font-medium transition',
                    isActive
                      ? 'bg-brand-600 text-white shadow-sm'
                      : 'text-muted hover:bg-brand-50 hover:text-ink',
                  )
                }
              >
                <Icon size={18} />
                {key === 'copilot' ? 'AI Copilot' : t(`nav.${key}`)}
              </NavLink>
            ))}
          </nav>
          <div className="mt-auto space-y-3 pt-6">
            <div className="flex gap-2">
              <Button
                variant={i18n.language.startsWith('hi') ? 'secondary' : 'primary'}
                className="flex-1 !py-2"
                onClick={() => setLang('en')}
              >
                EN
              </Button>
              <Button
                variant={i18n.language.startsWith('hi') ? 'primary' : 'secondary'}
                className="flex-1 !py-2"
                onClick={() => setLang('hi')}
              >
                हिं
              </Button>
            </div>
            <div className="rounded-xl bg-brand-50 px-3 py-2 text-xs text-brand-900">
              {user?.full_name}
              <div className="text-muted">{user?.email}</div>
            </div>
            <Button variant="ghost" className="w-full justify-start" onClick={logout}>
              <LogOut size={16} />
              {t('nav.logout')}
            </Button>
          </div>
        </div>
      </aside>

      <div className="flex min-h-screen flex-col">
        <div className="border-b border-amber-100 bg-amber-50 px-4 py-2 text-center text-xs text-amber-900 sm:px-8">
          {t('disclaimer')}
        </div>
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
