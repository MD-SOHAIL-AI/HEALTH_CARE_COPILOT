import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import {
  confirmDocument,
  fetchDocumentBlob,
  getDocument,
  reprocessDocument,
} from '../lib/api'
import {
  Badge,
  Button,
  Card,
  ConfidenceBadge,
  EmptyState,
  InterpBadge,
  PageHeader,
} from '../components/ui'

export function DocumentDetailPage() {
  const { id } = useParams()
  const documentId = Number(id)
  const { t, i18n } = useTranslation()
  const qc = useQueryClient()
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)

  const { data: doc, isLoading } = useQuery({
    queryKey: ['document', documentId],
    queryFn: () => getDocument(documentId),
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === 'uploaded' || status === 'processing' ? 1500 : false
    },
  })

  useEffect(() => {
    let objectUrl: string | null = null
    if (!doc) return
    void fetchDocumentBlob(doc.id).then((blob) => {
      objectUrl = URL.createObjectURL(blob)
      setPreviewUrl(objectUrl)
    })
    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [doc?.id, doc?.status])

  const confirmMut = useMutation({
    mutationFn: () => confirmDocument(documentId),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['document', documentId] })
      void qc.invalidateQueries({ queryKey: ['dashboard'] })
      void qc.invalidateQueries({ queryKey: ['timeline'] })
    },
  })

  const reprocessMut = useMutation({
    mutationFn: () => reprocessDocument(documentId),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['document', documentId] }),
  })

  const lang = i18n.language.startsWith('hi') ? 'hi' : 'en'
  const summary = useMemo(
    () => doc?.summaries.find((s) => s.language === lang) || doc?.summaries[0],
    [doc, lang],
  )

  if (isLoading || !doc) {
    return <p className="text-muted">{t('common.loading')}</p>
  }

  const processing = doc.status === 'uploaded' || doc.status === 'processing'

  return (
    <div>
      <PageHeader
        title={doc.original_filename}
        subtitle={`${doc.doc_type.replace('_', ' ')} · ${doc.status}`}
        action={
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => reprocessMut.mutate()} disabled={processing}>
              {t('document.reprocess')}
            </Button>
            {(doc.status === 'needs_review' || doc.status === 'confirmed') && (
              <Button onClick={() => confirmMut.mutate()} disabled={confirmMut.isPending}>
                {t('document.confirm')}
              </Button>
            )}
          </div>
        }
      />

      <div className="mb-4 flex flex-wrap gap-2">
        <Badge tone="brand">{t('document.status')}: {doc.status}</Badge>
        {doc.ocr_confidence != null && <ConfidenceBadge value={doc.ocr_confidence} />}
        {doc.source_facility && <Badge>{doc.source_facility}</Badge>}
        {doc.record_date && <Badge>{doc.record_date}</Badge>}
      </div>

      {processing && (
        <Card className="mb-5 border-brand-200 bg-brand-50">
          <p className="text-sm font-medium text-brand-900">{t('document.processing')}</p>
        </Card>
      )}

      {doc.status === 'failed' && (
        <Card className="mb-5 border-red-200 bg-red-50">
          <p className="text-sm text-danger">
            {t('document.failed')}: {doc.error_message}
          </p>
        </Card>
      )}

      <div className="grid gap-5 lg:grid-cols-2">
        <Card title={t('document.preview')}>
          {previewUrl ? (
            doc.mime_type.startsWith('image/') ? (
              <img src={previewUrl} alt="Document preview" className="max-h-[560px] w-full rounded-xl object-contain" />
            ) : doc.mime_type === 'application/pdf' ? (
              <iframe title="pdf" src={previewUrl} className="h-[560px] w-full rounded-xl border" />
            ) : (
              <pre className="max-h-[560px] overflow-auto whitespace-pre-wrap rounded-xl bg-slate-50 p-3 text-xs">
                {doc.ocr_text || 'Preview available after processing.'}
              </pre>
            )
          ) : (
            <EmptyState>{t('common.loading')}</EmptyState>
          )}
          {doc.ocr_text && (
            <details className="mt-4">
              <summary className="cursor-pointer text-sm font-semibold text-brand-700">OCR text</summary>
              <pre className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap rounded-xl bg-slate-50 p-3 text-xs">
                {doc.ocr_text}
              </pre>
            </details>
          )}
        </Card>

        <div className="space-y-5">
          <Card title={t('document.summary')}>
            {summary ? (
              <>
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{summary.plain_text}</p>
                <p className="mt-3 text-xs font-medium text-amber-800">{summary.disclaimer}</p>
              </>
            ) : (
              <EmptyState>{processing ? t('document.processing') : 'No summary yet.'}</EmptyState>
            )}
          </Card>

          <Card title={t('document.abnormal')}>
            {!summary?.abnormal_explanations?.length ? (
              <EmptyState>No abnormal explanations for this document.</EmptyState>
            ) : (
              <ul className="space-y-3">
                {summary.abnormal_explanations.map((item, idx) => (
                  <li key={idx} className="rounded-xl border border-slate-100 p-3">
                    <div className="mb-1 flex items-center justify-between gap-2">
                      <span className="font-semibold">
                        {item.test_name}: {item.value} {item.unit}
                      </span>
                      {item.interpretation && (
                        <InterpBadge value={item.interpretation as 'H' | 'L' | 'N' | 'unknown'} />
                      )}
                    </div>
                    <p className="text-sm text-muted">{item.explanation}</p>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>

        <Card title={t('document.medications')} className="lg:col-span-2">
          {!doc.medications.length ? (
            <EmptyState>—</EmptyState>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase text-muted">
                  <tr>
                    <th className="py-2">Name</th>
                    <th>Dose</th>
                    <th>Frequency</th>
                    <th>{t('document.confidence')}</th>
                  </tr>
                </thead>
                <tbody>
                  {doc.medications.map((m) => (
                    <tr key={m.id} className="border-t border-slate-100">
                      <td className="py-3 font-medium">
                        {m.name} {m.strength}
                        {m.confidence < 0.8 && (
                          <span className="ml-2 text-xs text-warn">{t('document.lowConfidence')}</span>
                        )}
                      </td>
                      <td>{m.dosage}</td>
                      <td>{m.frequency}</td>
                      <td>
                        <ConfidenceBadge value={m.confidence} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card title={t('document.observations')} className="lg:col-span-2">
          {!doc.observations.length ? (
            <EmptyState>—</EmptyState>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase text-muted">
                  <tr>
                    <th className="py-2">Test</th>
                    <th>Value</th>
                    <th>Ref</th>
                    <th>Flag</th>
                    <th>{t('document.confidence')}</th>
                  </tr>
                </thead>
                <tbody>
                  {doc.observations.map((o) => (
                    <tr key={o.id} className="border-t border-slate-100">
                      <td className="py-3 font-medium">{o.test_name}</td>
                      <td>
                        {o.value} {o.unit}
                      </td>
                      <td className="text-muted">
                        {o.ref_low ?? '—'} – {o.ref_high ?? '—'}
                      </td>
                      <td>
                        <InterpBadge value={o.interpretation} />
                      </td>
                      <td>
                        <ConfidenceBadge value={o.confidence} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card title={t('document.conditions')} className="lg:col-span-2">
          {!doc.conditions.length ? (
            <EmptyState>—</EmptyState>
          ) : (
            <ul className="space-y-2">
              {doc.conditions.map((c) => (
                <li key={c.id} className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2">
                  <span>
                    {c.name}
                    {c.icd10_code ? ` (${c.icd10_code})` : ''}
                  </span>
                  <ConfidenceBadge value={c.confidence} />
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <p className="mt-6 text-sm">
        <Link className="font-semibold text-brand-700" to="/timeline">
          ← {t('nav.timeline')}
        </Link>
      </p>
    </div>
  )
}
