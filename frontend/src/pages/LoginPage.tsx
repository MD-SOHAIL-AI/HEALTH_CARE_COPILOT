import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../lib/auth'
import { Button, Card, Input } from '../components/ui'

export function LoginPage() {
  const { t } = useTranslation()
  const { login, user, loading } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('demo@medcare.app')
  const [password, setPassword] = useState('demo1234')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  if (!loading && user) return <Navigate to="/" replace />

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await login(email, password)
      navigate('/')
    } catch {
      setError('Login failed. Check email and password.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="grid w-full max-w-4xl gap-6 lg:grid-cols-2">
        <div className="flex flex-col justify-center px-2">
          <h1 className="font-display text-4xl font-semibold text-brand-900">{t('appName')}</h1>
          <p className="mt-3 text-lg text-muted">{t('tagline')}</p>
          <p className="mt-6 text-sm leading-relaxed text-muted">
            Upload prescriptions, lab reports, and discharge summaries. Get plain-language summaries,
            a unified timeline, and an ABDM-ready health profile.
          </p>
          <p className="mt-4 text-xs text-brand-700">{t('auth.demoHint')}</p>
        </div>
        <Card>
          <h2 className="mb-4 font-display text-2xl font-semibold">{t('auth.login')}</h2>
          <form className="space-y-4" onSubmit={onSubmit}>
            <Input
              label={t('auth.email')}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              label={t('auth.password')}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            {error && <p className="text-sm text-danger">{error}</p>}
            <Button className="w-full" disabled={busy}>
              {busy ? t('common.loading') : t('auth.login')}
            </Button>
          </form>
          <p className="mt-4 text-sm text-muted">
            {t('auth.noAccount')}{' '}
            <Link className="font-semibold text-brand-700" to="/register">
              {t('auth.register')}
            </Link>
          </p>
        </Card>
      </div>
    </div>
  )
}
