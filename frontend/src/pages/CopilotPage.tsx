import { useState } from 'react'
import { Link } from 'react-router-dom'
import { askCopilot, type CopilotAnswer } from '../lib/api'
import { Button, Card, PageHeader } from '../components/ui'

export function CopilotPage() {
  const [question, setQuestion] = useState('')
  const [language, setLanguage] = useState<'en' | 'hi' | 'ta'>('en')
  const [result, setResult] = useState<CopilotAnswer | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  async function ask(e: React.FormEvent) {
    e.preventDefault()
    if (question.trim().length < 3) return
    setLoading(true)
    setError('')
    try { setResult(await askCopilot(question, language)) }
    catch { setError('Copilot request failed. Check the server and your login.') }
    finally { setLoading(false) }
  }
  return <div className="space-y-6">
    <PageHeader title="Evidence Copilot" subtitle="Ask questions grounded in your confirmed health records" />
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">For education and record organization only. No diagnosis or medication changes. Only reviewed and confirmed records are included.</div>
    <Card title="Ask your health records">
      <form className="space-y-4" onSubmit={e => { void ask(e) }}>
        <label htmlFor="health-question" className="block text-sm font-medium">Question</label>
        <textarea id="health-question" className="w-full rounded-xl border border-slate-200 p-3 text-sm" rows={4} maxLength={1000} required value={question} onChange={e => setQuestion(e.target.value)} placeholder="How has my hemoglobin changed across reports?" />
        <div className="flex flex-wrap items-center justify-between gap-3">
          <select aria-label="Answer language" className="rounded-xl border border-slate-200 p-2 text-sm" value={language} onChange={e => setLanguage(e.target.value as 'en' | 'hi' | 'ta')}>
            <option value="en">English</option><option value="hi">Hindi</option><option value="ta">Tamil</option>
          </select>
          <Button type="submit" disabled={loading || question.trim().length < 3}>{loading ? 'Searching…' : 'Ask Copilot'}</Button>
        </div>
      </form>
      {error && <p role="alert" className="mt-4 text-sm text-red-700">{error}</p>}
    </Card>
    {result && <Card title="Answer with evidence">
      <p className="whitespace-pre-wrap text-sm leading-relaxed">{result.answer}</p>
      <div className="mt-5 border-t border-slate-200 pt-4">
        <h3 className="text-sm font-semibold">Document evidence ({result.citations.length})</h3>
        {result.citations.map((c,i) => <div key={i} className="my-3 rounded-xl bg-slate-50 p-3 text-sm">
          <Link className="font-semibold text-brand-700" to={'/documents/' + c.document_id}>{c.title}</Link>
          <p className="mt-1 whitespace-pre-wrap text-xs text-muted">{c.excerpt}</p>
        </div>)}
        <p className="text-xs text-muted">Laya: {result.decision.status} · Generation: {result.generation.status}</p>
        <p className="mt-2 text-xs text-muted">{result.disclaimer}</p>
      </div>
    </Card>}
  </div>
}
