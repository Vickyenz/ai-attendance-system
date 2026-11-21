import { useState } from 'react'
import { Button } from '@/components/ui/button'

type ColorToken = {
  name: string
  dark: string
  light: string
  variable: string
}

const colorTokens: ColorToken[] = [
  { name: 'Background', dark: '#0F1620', light: '#FAFAF8', variable: '--background' },
  { name: 'Surface', dark: '#161F2C', light: '#FFFFFF', variable: '--surface' },
  { name: 'Border', dark: '#2A3542', light: '#E2E0D8', variable: '--border' },
  { name: 'Accent', dark: '#0F6E56', light: '#0F6E56', variable: '--accent' },
  { name: 'Accent foreground', dark: '#4FD1B0', light: '#0F6E56', variable: '--accent-fg' },
  { name: 'Success / marked', dark: '#10B981', light: '#047857', variable: '--success' },
  { name: 'Warning / already marked', dark: '#D97706', light: '#B45309', variable: '--warning' },
  { name: 'Danger', dark: '#DC2626', light: '#B91C1C', variable: '--danger' },
  { name: 'Danger foreground', dark: '#F87171', light: '#B91C1C', variable: '--danger-fg' },
]

const statuses = [
  { label: 'Marked', color: 'var(--success)', description: 'Attendance confirmed' },
  { label: 'Already marked', color: 'var(--warning)', description: 'Previously checked in' },
  { label: 'Needs attention', color: 'var(--danger)', description: 'Spoof, unknown, or not enrolled' },
]

export function PalettePage() {
  const [isLight, setIsLight] = useState(false)

  return (
    <main className={isLight ? 'light min-h-screen bg-background text-foreground' : 'min-h-screen bg-background text-foreground'}>
      <div className="mx-auto max-w-6xl px-6 py-10 sm:px-8">
        <header className="mb-10 flex flex-wrap items-start justify-between gap-6 border-b border-border pb-6">
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-accent-fg">AI Attendance System · UI foundation</p>
            <h1 className="font-heading text-3xl font-semibold tracking-tight sm:text-4xl">Design tokens</h1>
            <p className="mt-2 max-w-xl text-sm text-muted-foreground">A practical palette and component preview for the lecturer workspace.</p>
          </div>
          <Button variant="outline" onClick={() => setIsLight((theme) => !theme)} aria-pressed={isLight}>
            Switch to {isLight ? 'dark' : 'light'} theme
          </Button>
        </header>

        <section aria-labelledby="palette-heading" className="mb-10">
          <SectionHeading id="palette-heading" eyebrow="01 / Color" title="Interface palette" />
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {colorTokens.map((token) => (
              <article key={token.variable} className="overflow-hidden rounded-card border border-border bg-surface">
                <div className="h-16 border-b border-border" style={{ backgroundColor: `var(${token.variable})` }} />
                <div className="flex items-start justify-between gap-4 p-4">
                  <div>
                    <h3 className="font-medium">{token.name}</h3>
                    <p className="mt-1 font-mono text-xs text-muted-foreground">{token.variable}</p>
                  </div>
                  <code className="text-xs text-muted-foreground">{isLight ? token.light : token.dark}</code>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section aria-labelledby="type-heading" className="mb-10">
          <SectionHeading id="type-heading" eyebrow="02 / Typography" title="Type scale" />
          <div className="rounded-card border border-border bg-surface p-5 sm:p-6">
            <div className="grid gap-x-8 gap-y-5 sm:grid-cols-[140px_1fr]">
              <TypeSample label="Display / 36" className="font-heading text-4xl font-semibold tracking-tight">Attendance</TypeSample>
              <TypeSample label="Heading / 28" className="font-heading text-3xl font-semibold tracking-tight">Course overview</TypeSample>
              <TypeSample label="Title / 20" className="font-heading text-xl font-medium">MCE 301 · Engineering Mathematics</TypeSample>
              <TypeSample label="Body / 14" className="text-sm">Manage enrolments and review attendance with a clear, compact workspace.</TypeSample>
              <TypeSample label="Caption / 12" className="text-xs text-muted-foreground">Last updated today · 09:42 AM</TypeSample>
              <TypeSample label="Stat / 32" className="font-heading text-3xl font-semibold tabular-nums">128</TypeSample>
            </div>
          </div>
        </section>

        <section aria-labelledby="button-heading" className="mb-10">
          <SectionHeading id="button-heading" eyebrow="03 / Controls" title="Button variants" />
          <div className="flex flex-wrap items-center gap-3 rounded-card border border-border bg-surface p-5">
            <Button>Default</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="link">Link</Button>
          </div>
        </section>

        <section aria-labelledby="status-heading">
          <SectionHeading id="status-heading" eyebrow="04 / Attendance" title="Status colors" />
          <div className="grid gap-3 md:grid-cols-3">
            {statuses.map((status) => (
              <article key={status.label} className="flex items-center gap-3 rounded-card border border-border bg-surface p-4">
                <span className="h-3 w-3 shrink-0 rounded-full" style={{ backgroundColor: status.color }} aria-hidden="true" />
                <div>
                  <h3 className="font-medium">{status.label}</h3>
                  <p className="text-xs text-muted-foreground">{status.description}</p>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  )
}

type SectionHeadingProps = {
  id: string
  eyebrow: string
  title: string
}

function SectionHeading({ id, eyebrow, title }: SectionHeadingProps) {
  return (
    <div className="mb-4">
      <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-accent-fg">{eyebrow}</p>
      <h2 id={id} className="font-heading text-xl font-semibold">{title}</h2>
    </div>
  )
}

type TypeSampleProps = {
  label: string
  className: string
  children: React.ReactNode
}

function TypeSample({ label, className, children }: TypeSampleProps) {
  return (
    <>
      <span className="pt-1 text-xs text-muted-foreground">{label}</span>
      <p className={className}>{children}</p>
    </>
  )
}
