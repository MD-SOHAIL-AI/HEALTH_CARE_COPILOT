import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { listMedications } from '../lib/api'
import { Card, EmptyState, PageHeader } from '../components/ui'

export function MedicationsPage() {
  const { t } = useTranslation()
  const { data = [], isLoading } = useQuery({
    queryKey: ['medications'],
    queryFn: () => listMedications(false),
  })

  const active = data.filter((m) => m.is_active)
  const past = data.filter((m) => !m.is_active)

  return (
    <div>
      <PageHeader title={t('medications.title')} />
      {isLoading ? (
        <p className="text-muted">{t('common.loading')}</p>
      ) : (
        <div className="grid gap-5 lg:grid-cols-2">
          <Card title={t('medications.active')}>
            {!active.length ? (
              <EmptyState>{t('medications.empty')}</EmptyState>
            ) : (
              <ul className="space-y-3">
                {active.map((m) => (
                  <li key={m.id} className="rounded-xl border border-brand-100 bg-brand-50/40 p-3">
                    <div className="font-semibold">
                      {m.name} {m.strength}
                    </div>
                    <div className="text-sm text-muted">
                      {[m.dosage, m.frequency, m.route].filter(Boolean).join(' · ')}
                    </div>
                    {m.instructions && <div className="mt-1 text-xs text-muted">{m.instructions}</div>}
                    {m.document_id && (
                      <Link
                        className="mt-2 inline-block text-xs font-semibold text-brand-700"
                        to={`/documents/${m.document_id}`}
                      >
                        {t('common.source')}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </Card>
          <Card title={t('medications.past')}>
            {!past.length ? (
              <EmptyState>—</EmptyState>
            ) : (
              <ul className="space-y-3">
                {past.map((m) => (
                  <li key={m.id} className="rounded-xl border border-slate-100 p-3 opacity-80">
                    <div className="font-semibold">
                      {m.name} {m.strength}
                    </div>
                    <div className="text-sm text-muted">{m.frequency}</div>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      )}
    </div>
  )
}
