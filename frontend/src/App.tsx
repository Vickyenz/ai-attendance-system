import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";

const palette = [
  { name: "Background", token: "--background" },
  { name: "Surface", token: "--surface" },
  { name: "Border", token: "--border" },
  { name: "Accent", token: "--accent" },
  { name: "Accent foreground", token: "--accent-fg" },
  { name: "Marked", token: "--success" },
  { name: "Already marked", token: "--warning" },
  { name: "Danger", token: "--danger" },
  { name: "Danger foreground", token: "--danger-fg" },
];

const buttonVariants = ["default", "outline", "secondary", "ghost", "link"] as const;

function App() {
  const [isLight, setIsLight] = useState(false);

  function toggleTheme() {
    const nextIsLight = !isLight;
    document.documentElement.classList.toggle("light", nextIsLight);
    setIsLight(nextIsLight);
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-6xl px-6 py-10 sm:px-8">
        <header className="mb-10 flex flex-wrap items-start justify-between gap-5 border-b border-border pb-6">
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-accent-fg">
              Attendance
            </p>
            <h1 className="font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
              Design system
            </h1>
            <p className="mt-2 max-w-xl text-sm text-muted">
              A compact preview of the tokens and components used in the lecturer workspace.
            </p>
          </div>
          <Button variant="outline" onClick={toggleTheme} aria-pressed={isLight}>
            Switch to {isLight ? "dark" : "light"} theme
          </Button>
        </header>

        <div className="space-y-10">
          <section aria-labelledby="palette-heading">
            <SectionHeading
              id="palette-heading"
              eyebrow="Foundation"
              title="Colour palette"
            />
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {palette.map(({ name, token }) => (
                <div
                  key={token}
                  className="flex items-center gap-3 rounded-md border border-border bg-surface p-3"
                >
                  <span
                    className="h-10 w-10 shrink-0 rounded border border-border"
                    style={{ backgroundColor: `var(${token})` }}
                    aria-hidden="true"
                  />
                  <span>
                    <span className="block text-sm font-medium">{name}</span>
                    <code className="text-xs text-muted">{token}</code>
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section aria-labelledby="type-heading">
            <SectionHeading
              id="type-heading"
              eyebrow="Typography"
              title="Type scale"
            />
            <div className="space-y-4 rounded-md border border-border bg-surface p-5">
              <p className="font-heading text-3xl font-semibold">Space Grotesk / 30</p>
              <p className="font-heading text-2xl font-semibold">Space Grotesk / 24</p>
              <p className="font-heading text-xl font-medium">Space Grotesk / 20</p>
              <p className="text-base">Inter / 16 — Regular body text</p>
              <p className="text-sm">Inter / 14 — Supporting text and labels</p>
              <p className="text-xs text-muted">Inter / 12 — Metadata and helper text</p>
            </div>
          </section>

          <section aria-labelledby="buttons-heading">
            <SectionHeading
              id="buttons-heading"
              eyebrow="Components"
              title="Button variants"
            />
            <div className="flex flex-wrap items-center gap-3 rounded-md border border-border bg-surface p-5">
              {buttonVariants.map((variant) => (
                <Button key={variant} variant={variant}>
                  {variant[0].toUpperCase() + variant.slice(1)}
                </Button>
              ))}
              <Button size="sm">Small</Button>
              <Button size="lg">Large</Button>
            </div>
          </section>

          <section aria-labelledby="status-heading">
            <SectionHeading
              id="status-heading"
              eyebrow="Attendance states"
              title="Status colours"
            />
            <div className="flex flex-wrap items-center gap-3 rounded-md border border-border bg-surface p-5">
              <Badge variant="marked">Marked</Badge>
              <Badge variant="already_marked">Already marked</Badge>
              <Badge variant="danger">Spoof / unknown / not enrolled</Badge>
            </div>
          </section>

          <section aria-labelledby="form-heading">
            <SectionHeading
              id="form-heading"
              eyebrow="Form controls"
              title="Input and label"
            />
            <div className="max-w-sm space-y-2 rounded-md border border-border bg-surface p-5">
              <Label htmlFor="course-code">Course code</Label>
              <Input id="course-code" placeholder="e.g. MCE 301" />
            </div>
          </section>

          <section aria-labelledby="loading-heading">
            <SectionHeading
              id="loading-heading"
              eyebrow="Loading state"
              title="Skeleton"
            />
            <div className="flex max-w-sm items-center gap-3 rounded-md border border-border bg-surface p-5">
              <Skeleton className="h-10 w-10 rounded-full" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-3 w-2/3" />
                <Skeleton className="h-3 w-1/2" />
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}

function SectionHeading({
  id,
  eyebrow,
  title,
}: {
  id: string;
  eyebrow: string;
  title: string;
}) {
  return (
    <div className="mb-4">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-accent-fg">
        {eyebrow}
      </p>
      <h2 id={id} className="mt-1 font-heading text-xl font-semibold">
        {title}
      </h2>
    </div>
  );
}

export default App;
