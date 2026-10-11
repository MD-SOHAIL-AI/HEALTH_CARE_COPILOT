import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { FileUp } from 'lucide-react'
import { uploadDocument } from '../lib/api'
import type { DocumentType } from '../lib/types'
import { Button, Card, Input, PageHeader, Select } from '../components/ui'

export function UploadPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [files, setFiles] = useState<File[]>([])
  const [docType, setDocType] = useState<DocumentType>('prescription')
  const [recordDate, setRecordDate] = useState('')
  const [facility, setFacility] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const onDrop = useCallback((accepted: File[]) => {
    setFiles(accepted)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
    accept: {
      'image/*': [],
      'application/pdf': [],
      'text/plain': [],
    },
  })

  const submit = async () => {
    if (!files.length) {
      setError('Please choose at least one file.')
      return
    }
    setBusy(true)
    setError('')
    try {
      let lastId = 0
      for (const file of files) {
        const doc = await uploadDocument({
          file,
          doc_type: docType,
          record_date: recordDate || undefined,
          source_facility: facility || undefined,
        })
        lastId = doc.id
      }
      navigate(`/documents/${lastId}`)
    } catch {
      setError('Upload failed. Is the API running?')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <PageHeader title={t('upload.title')} subtitle={t('disclaimer')} />
      <Card className="max-w-2xl">
        <div
          {...getRootProps()}
          className={`mb-5 cursor-pointer rounded-2xl border-2 border-dashed px-6 py-12 text-center transition ${
            isDragActive ? 'border-brand-500 bg-brand-50' : 'border-brand-200 bg-slate-50/70'
          }`}
        >
          <input {...getInputProps()} />
          <FileUp className="mx-auto mb-3 text-brand-600" />
          <p className="text-sm font-medium text-ink">{t('upload.drop')}</p>
          {files.length > 0 && (
            <ul className="mt-3 space-y-1 text-xs text-muted">
              {files.map((f) => (
                <li key={f.name}>{f.name}</li>
              ))}
            </ul>
          )}
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Select
            label={t('upload.type')}
            value={docType}
            onChange={(e) => setDocType(e.target.value as DocumentType)}
          >
            {(
              ['prescription', 'lab_report', 'discharge_summary', 'diagnostic_report'] as DocumentType[]
            ).map((type) => (
              <option key={type} value={type}>
                {t(`upload.types.${type}`)}
              </option>
            ))}
          </Select>
          <Input
            label={t('upload.date')}
            type="date"
            value={recordDate}
            onChange={(e) => setRecordDate(e.target.value)}
          />
          <div className="sm:col-span-2">
            <Input
              label={t('upload.facility')}
              value={facility}
              onChange={(e) => setFacility(e.target.value)}
            />
          </div>
        </div>

        {error && <p className="mt-3 text-sm text-danger">{error}</p>}
        <Button className="mt-5" onClick={submit} disabled={busy}>
          {busy ? t('common.loading') : t('upload.submit')}
        </Button>
      </Card>
    </div>
  )
}
