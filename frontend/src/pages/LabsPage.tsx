import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceArea,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { getTrends } from '../lib/api'
import { Card, EmptyState, PageHeader } from '../components/ui'

export function LabsPage() {
  const { t } = useTranslation()
  const { data = [], isLoading } = useQuery({
    queryKey: ['trends'],
    queryFn: getTrends,
  })

  return (
    <div>
      <PageHeader title={t('labs.title')} />
      {isLoading ? (
        <p className="text-muted">{t('common.loading')}</p>
      ) : data.length === 0 ? (
        <EmptyState>{t('labs.empty')}</EmptyState>
      ) : (
        <div className="grid gap-5">
          {data.map((trend) => {
            const chartData = trend.points.map((p) => ({
              date: p.effective_date || '—',
              value: p.value,
              document_id: p.document_id,
            }))
            const low = trend.ref_low ?? undefined
            const high = trend.ref_high ?? undefined
            return (
              <Card
                key={trend.test_name}
                title={`${trend.test_name}${trend.unit ? ` (${trend.unit})` : ''}`}
                action={
                  low != null && high != null ? (
                    <span className="text-xs text-muted">
                      {t('labs.refRange')}: {low}–{high}
                    </span>
                  ) : null
                }
              >
                <div className="h-64 w-full">
                  <ResponsiveContainer>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} domain={['auto', 'auto']} />
                      <Tooltip />
                      {low != null && high != null && (
                        <ReferenceArea y1={low} y2={high} fill="#d5f2f1" fillOpacity={0.5} />
                      )}
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke="#1b767c"
                        strokeWidth={2.5}
                        dot={{ r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-2 flex flex-wrap gap-3 text-xs">
                  {trend.points.map((p, idx) =>
                    p.document_id ? (
                      <Link
                        key={`${p.document_id}-${idx}`}
                        to={`/documents/${p.document_id}`}
                        className="font-semibold text-brand-700"
                      >
                        {p.effective_date}: {p.value} {t('common.source')}
                      </Link>
                    ) : null,
                  )}
                </div>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
