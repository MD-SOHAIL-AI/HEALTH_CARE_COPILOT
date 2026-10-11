import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowRight, FileUp } from 'lucide-react'
import { getDashboard } from '../lib/api'
import { useAuth } from '../lib/auth'
import { Badge, Button, Card, EmptyState, InterpBadge, PageHeader } from '../components/ui'

export function DashboardPage() {
  const { t, i18n } = useTranslation()
  const { user } = useAuth()
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
  })

  if (isLoading || !data) {
    return <p className="text-muted">{t('common.loading')}</p>
  }

  const summary =
    data.latest_summary &&
    (data.latest_summary.language === (i18n.language.startsWith('hi') ? 'hi' : 'en')
      ? data.latest_summary
      : data.latest_summary)

  return (
    <div>
      <PageHeader
        title={`${t('dashboard.welcome')}, ${user?.full_name?.split(' ')[0] || ''}`}
        subtitle={t('tagline')}
        action={
          <Link to="/upload">
            <Button>
              <FileUp size={16} />
              {t('dashboard.uploadCta')}
            </Button>
          </Link>
        }
      />

      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        {Object.entries(data.document_counts).map(([status, count]) => (
          <Card key={status} className="!p-4">
            <div className="text-xs uppercase tracking-wide text-muted">{status.replace('_', ' ')}</div>
            <div className="mt-1 font-display text-3xl font-semibold text-brand-800">{count}</div>
          </Card>
        ))}
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <Card title={t('dashboard.activeMeds')}>
          {data.active_medications.length === 0 ? (
            <EmptyState>{t('dashboard.noData')}</EmptyState>
          ) : (
            <ul className="space-y-3">
              {data.active_medications.map((m) => (
                <li key={m.id} className="flex items-start justify-between gap-3 rounded-xl bg-brand-50/60 px-3 py-2">
                  <div>
                    <div className="font-semibold">
                      {m.name} {m.strength}
                    </div>
                    <div className="text-xs text-muted">
                      {[m.dosage, m.frequency].filter(Boolean).join(' · ')}
                    </div>
                  </div>
                  {m.document_id && (
                    <Link className="text-xs font-semibold text-brand-700" to={`/documents/${m.document_id}`}>
                      {t('common.source')}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title={t('dashboard.abnormal')}>
          {data.recent_abnormal.length === 0 ? (
            <EmptyState>{t('dashboard.noData')}</EmptyState>
          ) : (
            <ul className="space-y-3">
              {data.recent_abnormal.map((o) => (
                <li key={o.id} className="flex items-center justify-between gap-3 rounded-xl border border-slate-100 px-3 py-2">
                  <div>
                    <div className="font-semibold">{o.test_name}</div>
                    <div className="text-xs text-muted">
                      {o.value} {o.unit}
                      {o.effective_date ? ` · ${o.effective_date}` : ''}
                    </div>
                  </div>
                  <InterpBadge value={o.interpretation} />
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card
          title={t('dashboard.latestSummary')}
          className="lg:col-span-2"
          action={
            summary ? (
              <Link to={`/documents/${summary.document_id}`}>
                <Button variant="secondary" className="!py-1.5 text-xs">
                  {t('common.view')} <ArrowRight size={14} />
                </Button>
              </Link>
            ) : null
          }
        >
          {!summary ? (
            <EmptyState>{t('dashboard.noData')}</EmptyState>
          ) : (
            <div>
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-ink">{summary.plain_text}</p>
              <p className="mt-3 text-xs font-medium text-amber-800">{summary.disclaimer}</p>
            </div>
          )}
        </Card>

        <Card title={t('dashboard.recentDocs')} className="lg:col-span-2">
          {data.recent_documents.length === 0 ? (
            <EmptyState>{t('dashboard.noData')}</EmptyState>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase text-muted">
                  <tr>
                    <th className="py-2">File</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {data.recent_documents.map((d) => (
                    <tr key={d.id} className="border-t border-slate-100">
                      <td className="py-3 font-medium">{d.original_filename}</td>
                      <td>{d.doc_type.replace('_', ' ')}</td>
                      <td>
                        <Badge
                          tone={
                            d.status === 'confirmed'
                              ? 'ok'
                              : d.status === 'needs_review'
                                ? 'warn'
                                : d.status === 'failed'
                                  ? 'danger'
                                  : 'brand'
                          }
                        >
                          {d.status}
                        </Badge>
                      </td>
                      <td className="text-right">
                        <Link className="font-semibold text-brand-700" to={`/documents/${d.id}`}>
                          {t('common.view')}
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
