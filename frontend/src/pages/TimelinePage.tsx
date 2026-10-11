import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { getTimeline } from '../lib/api'
import { Badge, Button, Card, EmptyState, PageHeader } from '../components/ui'

const kinds = ['', 'prescription', 'lab', 'discharge', 'diagnosis'] as const

export function TimelinePage() {
  const { t } = useTranslation()
  const [kind, setKind] = useState('')
  const { data = [], isLoading } = useQuery({
    queryKey: ['timeline', kind],
    queryFn: () => getTimeline(kind || undefined),
  })

  return (
    <div>
      <PageHeader title={t('timeline.title')} />
      <div className="mb-5 flex flex-wrap gap-2">
        {kinds.map((k) => (
          <Button
            key={k || 'all'}
            variant={kind === k ? 'primary' : 'secondary'}
            className="!py-1.5"
            onClick={() => setKind(k)}
          >
            {k ? k : t('timeline.all')}
          </Button>
        ))}
      </div>

      <Card>
        {isLoading ? (
          <p className="text-muted">{t('common.loading')}</p>
        ) : data.length === 0 ? (
          <EmptyState>{t('timeline.empty')}</EmptyState>
        ) : (
          <ol className="relative space-y-6 border-l-2 border-brand-200 pl-6">
            {data.map((event) => (
              <li key={event.id} className="relative">
                <span className="absolute -left-[1.95rem] top-1.5 h-3 w-3 rounded-full border-2 border-white bg-brand-600 shadow" />
                <div className="flex flex-wrap items-center gap-2">
                  <time className="text-xs font-semibold text-muted">{event.event_date}</time>
                  <Badge tone="brand">{event.kind}</Badge>
                </div>
                <h3 className="mt-1 font-semibold text-ink">{event.title}</h3>
                {event.description && <p className="text-sm text-muted">{event.description}</p>}
                {event.document_id && (
                  <Link
                    className="mt-1 inline-block text-xs font-semibold text-brand-700"
                    to={`/documents/${event.document_id}`}
                  >
                    {t('common.source')} →
                  </Link>
                )}
              </li>
            ))}
          </ol>
        )}
      </Card>
    </div>
  )
}
