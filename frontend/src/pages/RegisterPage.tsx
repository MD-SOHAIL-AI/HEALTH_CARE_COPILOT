import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../lib/auth'
import { Button, Card, Input, Select } from '../components/ui'

export function RegisterPage() {
  const { t } = useTranslation()
  const { register, user, loading } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [lang, setLang] = useState('en')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  if (!loading && user) return <Navigate to="/" replace />

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await register({
        email,
        password,
        full_name: fullName,
        preferred_language: lang,
      })
      navigate('/')
    } catch {
      setError('Registration failed. Email may already be in use.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <Card className="w-full max-w-md">
        <h2 className="mb-4 font-display text-2xl font-semibold">{t('auth.register')}</h2>
        <form className="space-y-4" onSubmit={onSubmit}>
          <Input
            label={t('auth.fullName')}
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
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
            minLength={6}
            required
          />
          <Select label={t('profile.language')} value={lang} onChange={(e) => setLang(e.target.value)}>
            <option value="en">English</option>
            <option value="hi">हिन्दी</option>
          </Select>
          {error && <p className="text-sm text-danger">{error}</p>}
          <Button className="w-full" disabled={busy}>
            {busy ? t('common.loading') : t('auth.register')}
          </Button>
        </form>
        <p className="mt-4 text-sm text-muted">
          {t('auth.hasAccount')}{' '}
          <Link className="font-semibold text-brand-700" to="/login">
            {t('auth.login')}
          </Link>
        </p>
      </Card>
    </div>
  )
}
