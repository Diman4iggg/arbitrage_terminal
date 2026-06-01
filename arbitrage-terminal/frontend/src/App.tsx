import { Activity, BarChart3, Bell, RadioTower } from "lucide-react"

const modules = [
  {
    icon: Activity,
    title: "Perpetual monitoring",
    description: "Binance, Bybit, MEXC, and Hyperliquid adapters are planned for Stage 2.",
  },
  {
    icon: BarChart3,
    title: "Spread analytics",
    description: "Cross-exchange opportunities and historical charts will follow the API layer.",
  },
  {
    icon: Bell,
    title: "Telegram alerts",
    description: "Threshold-based notifications with cooldown protection are configured from env.",
  },
]

export default function App() {
  return (
    <main className="min-h-screen bg-terminal-950 text-zinc-100">
      <header className="border-b border-terminal-700 bg-terminal-900/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="rounded-md border border-emerald-500/30 bg-emerald-500/10 p-2">
              <RadioTower className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-sm font-semibold tracking-wide">ARBITRAGE TERMINAL</p>
              <p className="text-xs text-zinc-500">Perpetual futures monitoring</p>
            </div>
          </div>
          <span className="rounded-full border border-amber-400/30 bg-amber-400/10 px-3 py-1 text-xs font-medium text-amber-300">
            Stage 1 skeleton
          </span>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-6 py-14">
        <p className="mb-3 text-xs font-semibold uppercase tracking-[0.24em] text-emerald-400">
          Monitoring foundation
        </p>
        <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-zinc-50">
          Cross-exchange perpetual arbitrage, built as an operational terminal.
        </h1>
        <p className="mt-4 max-w-2xl text-sm leading-6 text-zinc-400">
          The application shell is running. Market adapters, scheduler jobs, REST endpoints, and
          terminal screens will be added incrementally in the next stages.
        </p>

        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {modules.map(({ icon: Icon, title, description }) => (
            <article
              key={title}
              className="rounded-lg border border-terminal-700 bg-terminal-900 p-5 shadow-sm"
            >
              <Icon className="h-5 w-5 text-emerald-400" />
              <h2 className="mt-5 text-sm font-semibold text-zinc-100">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-zinc-500">{description}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  )
}

