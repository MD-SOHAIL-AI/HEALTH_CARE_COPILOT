import { useEffect, useState, type FormEvent } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import {
  exportFhirBundle,
  importAbhaSample,
  linkAbha,
  listConditions,
  updatePatient,
} from '../lib/api'
import { useAuth } from '../lib/auth'
import { Badge, Button, Card, EmptyState, Input, PageHeader, Select } from '../components/ui'

export function ProfilePage() {
  const { t, i18n } = useTranslation()
  const { patient, refreshPatient } = useAuth()
  const qc = useQueryClient()
  const { data: conditions = [] } = useQuery({
    queryKey: ['conditions'],
    queryFn: listConditions,
  })

  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [dob, setDob] = useState('')
  const [gender, setGender] = useState('unknown')
  const [allergies, setAllergies] = useState('')
  const [lang, setLang] = useState('en')
  const [abhaNumber, setAbhaNumber] = useState('')
  const [otp, setOtp] = useState('123456')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!patient) return
    setName(patient.name || '')
    setPhone(patient.phone || '')
    setDob(patient.date_of_birth || '')
    setGender(patient.gender || 'unknown')
    setAllergies(patient.allergies || '')
    setLang(patient.preferred_language || 'en')
  }, [patient])

  const saveProfile = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setMessage('')
    try {
      await updatePatient({
        name,
        phone,
        date_of_birth: dob || null,
        gender,
        allergies,
        preferred_language: lang,
      } as never)
      await refreshPatient()
      void i18n.changeLanguage(lang)
      localStorage.setItem('medcare_lang', lang)
      setMessage('Profile saved.')
    } catch {
      setMessage('Could not save profile.')
    } finally {
      setBusy(false)
    }
  }

  const onLinkAbha = async () => {
    setBusy(true)
    setMessage('')
    try {
      const res = await linkAbha(abhaNumber, otp)
      await refreshPatient()
      setMessage(res.message)
    } catch {
      setMessage('ABHA link failed. Use OTP 123456.')
    } finally {
      setBusy(false)
    }
  }

  const onImport = async () => {
    setBusy(true)
    try {
      await importAbhaSample()
      await refreshPatient()
      void qc.invalidateQueries({ queryKey: ['conditions'] })
      void qc.invalidateQueries({ queryKey: ['medications'] })
      void qc.invalidateQueries({ queryKey: ['dashboard'] })
      setMessage('Sample FHIR bundle imported.')
    } catch {
      setMessage('Import failed.')
    } finally {
      setBusy(false)
    }
  }

  const onExport = async () => {
    try {
      const bundle = await exportFhirBundle()
      const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `medcare-fhir-${patient?.id || 'me'}.json`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      setMessage('Export failed.')
    }
  }

  if (!patient) return <p className="text-muted">{t('common.loading')}</p>

  return (
    <div>
      <PageHeader title={t('profile.title')} />
      <div className="grid gap-5 lg:grid-cols-2">
        <Card title={t('profile.demographics')}>
          <form className="space-y-3" onSubmit={saveProfile}>
            <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} />
            <Input label="Phone" value={phone} onChange={(e) => setPhone(e.target.value)} />
            <Input label="Date of birth" type="date" value={dob} onChange={(e) => setDob(e.target.value)} />
            <Select label="Gender" value={gender} onChange={(e) => setGender(e.target.value)}>
              <option value="female">Female</option>
              <option value="male">Male</option>
              <option value="other">Other</option>
              <option value="unknown">Unknown</option>
            </Select>
            <Select
              label={t('profile.language')}
              value={lang}
              onChange={(e) => setLang(e.target.value)}
            >
              <option value="en">English</option>
              <option value="hi">हिन्दी</option>
            </Select>
            <Input
              label={t('profile.allergies')}
              value={allergies}
              onChange={(e) => setAllergies(e.target.value)}
            />
            <Button disabled={busy}>{t('profile.save')}</Button>
          </form>
        </Card>

        <Card title={t('profile.abha')}>
          {patient.abha_number ? (
            <div className="mb-4 space-y-2">
              <Badge tone="ok">{t('profile.linked')}</Badge>
              <p className="text-sm">
                <span className="font-semibold">ABHA:</span> {patient.abha_number}
              </p>
              <p className="text-sm">
                <span className="font-semibold">Address:</span> {patient.abha_address}
              </p>
            </div>
          ) : (
            <p className="mb-3 text-sm text-muted">
              Mock ABHA linking for ABDM readiness. OTP for demo is <strong>123456</strong>.
            </p>
          )}
          <div className="space-y-3">
            <Input
              label={t('profile.abhaNumber')}
              placeholder="12-3456-7890-1234"
              value={abhaNumber}
              onChange={(e) => setAbhaNumber(e.target.value)}
            />
            <Input label={t('profile.otp')} value={otp} onChange={(e) => setOtp(e.target.value)} />
            <div className="flex flex-wrap gap-2">
              <Button onClick={onLinkAbha} disabled={busy}>
                {t('profile.link')}
              </Button>
              <Button variant="secondary" onClick={onImport} disabled={busy}>
                {t('profile.import')}
              </Button>
              <Button variant="secondary" onClick={onExport}>
                {t('profile.export')}
              </Button>
            </div>
          </div>
          <p className="mt-3 text-xs text-muted">FHIR Patient id: {patient.fhir_id}</p>
        </Card>

        <Card title={t('profile.conditions')} className="lg:col-span-2">
          {!conditions.length ? (
            <EmptyState>—</EmptyState>
          ) : (
            <ul className="grid gap-2 sm:grid-cols-2">
              {conditions.map((c) => (
                <li key={c.id} className="rounded-xl border border-slate-100 px-3 py-2 text-sm">
                  <div className="font-semibold">{c.name}</div>
                  <div className="text-xs text-muted">
                    {c.icd10_code || '—'} · {c.clinical_status}
                    {c.onset_date ? ` · ${c.onset_date}` : ''}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
      {message && <p className="mt-4 text-sm text-brand-800">{message}</p>}
    </div>
  )
}
