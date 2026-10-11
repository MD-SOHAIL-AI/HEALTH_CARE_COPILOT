import clsx from 'clsx'
import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, SelectHTMLAttributes } from 'react'
import type { Interpretation } from '../lib/types'

export function Card({
  children,
  className,
  title,
  action,
}: {
  children: ReactNode
  className?: string
  title?: string
  action?: ReactNode
}) {
  return (
    <section
      className={clsx(
        'rounded-2xl border border-brand-100/80 bg-card p-5 shadow-[0_10px_40px_-24px_rgba(15,28,36,0.45)]',
        className,
      )}
    >
      {(title || action) && (
        <div className="mb-4 flex items-start justify-between gap-3">
          {title ? <h2 className="font-display text-lg font-semibold text-ink">{title}</h2> : <span />}
          {action}
        </div>
      )}
      {children}
    </section>
  )
}

export function Button({
  variant = 'primary',
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
}) {
  return (
    <button
      className={clsx(
        'inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50',
        variant === 'primary' && 'bg-brand-600 text-white hover:bg-brand-700',
        variant === 'secondary' && 'border border-brand-200 bg-white text-brand-800 hover:bg-brand-50',
        variant === 'ghost' && 'text-muted hover:bg-brand-50 hover:text-ink',
        variant === 'danger' && 'bg-danger text-white hover:bg-red-700',
        className,
      )}
      {...props}
    />
  )
}

export function Input({
  label,
  className,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & { label?: string }) {
  return (
    <label className="block space-y-1.5 text-sm">
      {label && <span className="font-medium text-ink">{label}</span>}
      <input
        className={clsx(
          'w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-ink outline-none ring-brand-400 focus:ring-2',
          className,
        )}
        {...props}
      />
    </label>
  )
}

export function Select({
  label,
  className,
  children,
  ...props
}: SelectHTMLAttributes<HTMLSelectElement> & { label?: string; children: ReactNode }) {
  return (
    <label className="block space-y-1.5 text-sm">
      {label && <span className="font-medium text-ink">{label}</span>}
      <select
        className={clsx(
          'w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-ink outline-none ring-brand-400 focus:ring-2',
          className,
        )}
        {...props}
      >
        {children}
      </select>
    </label>
  )
}

export function Badge({
  children,
  tone = 'neutral',
}: {
  children: ReactNode
  tone?: 'neutral' | 'ok' | 'warn' | 'danger' | 'brand'
}) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
        tone === 'neutral' && 'bg-slate-100 text-slate-700',
        tone === 'ok' && 'bg-emerald-50 text-ok',
        tone === 'warn' && 'bg-amber-50 text-warn',
        tone === 'danger' && 'bg-red-50 text-danger',
        tone === 'brand' && 'bg-brand-100 text-brand-800',
      )}
    >
      {children}
    </span>
  )
}

export function ConfidenceBadge({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const low = value < 0.8
  return <Badge tone={low ? 'warn' : 'ok'}>{low ? `⚠ ${pct}%` : `${pct}%`}</Badge>
}

export function InterpBadge({ value }: { value: Interpretation }) {
  if (value === 'H') return <Badge tone="danger">High</Badge>
  if (value === 'L') return <Badge tone="warn">Low</Badge>
  if (value === 'N') return <Badge tone="ok">Normal</Badge>
  return <Badge>Unknown</Badge>
}

export function EmptyState({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50/80 px-4 py-8 text-center text-sm text-muted">
      {children}
    </div>
  )
}

export function PageHeader({
  title,
  subtitle,
  action,
}: {
  title: string
  subtitle?: string
  action?: ReactNode
}) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-muted">{subtitle}</p>}
      </div>
      {action}
    </div>
  )
}
