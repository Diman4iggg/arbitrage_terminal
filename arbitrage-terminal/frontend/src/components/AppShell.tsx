import { Activity, BarChart3, CandlestickChart, RadioTower, Settings, SquareChartGantt, WalletCards } from "lucide-react"
import type { ReactNode } from "react"
import { NavLink } from "react-router-dom"

import { cn } from "./ui"

const navItems = [
  { to: "/", label: "Dashboard", icon: Activity },
  { to: "/opportunities", label: "Opportunities", icon: CandlestickChart },
  { to: "/my-trades", label: "My Trades", icon: SquareChartGantt },
  { to: "/exchanges", label: "Exchanges", icon: WalletCards },
  { to: "/charts", label: "Charts", icon: BarChart3 },
  { to: "/settings", label: "Settings", icon: Settings },
]

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-terminal-950 text-zinc-100">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-60 border-r border-terminal-700 bg-terminal-900 md:block">
        <div className="flex h-16 items-center gap-3 border-b border-terminal-700 px-4">
          <div className="rounded-md border border-emerald-500/30 bg-emerald-500/10 p-2">
            <RadioTower className="h-4 w-4 text-emerald-400" />
          </div>
          <div>
            <p className="text-xs font-bold tracking-[0.18em]">ARBITRAGE</p>
            <p className="text-[10px] uppercase tracking-[0.2em] text-zinc-500">Terminal</p>
          </div>
        </div>
        <nav className="space-y-1 p-3">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                cn("flex items-center gap-3 rounded-md px-3 py-2.5 text-sm text-zinc-500 transition hover:bg-terminal-800 hover:text-zinc-200", isActive && "bg-emerald-500/10 text-emerald-300")
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="absolute bottom-0 w-full border-t border-terminal-700 p-4">
          <p className="text-[10px] uppercase tracking-wider text-zinc-600">Market type</p>
          <p className="mt-1 text-xs font-medium text-zinc-300">Perpetual futures</p>
        </div>
      </aside>
      <div className="min-w-0 md:pl-60">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-terminal-700 bg-terminal-900/95 px-4 backdrop-blur md:px-6">
          <div>
            <p className="text-xs font-semibold tracking-wide text-zinc-200">MARKET MONITOR</p>
            <p className="text-[11px] text-zinc-500">Cross-exchange perpetual spreads</p>
          </div>
          <div className="flex items-center gap-2 text-xs text-emerald-300">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            Live monitoring
          </div>
        </header>
        <nav className="flex gap-1 overflow-x-auto border-b border-terminal-700 bg-terminal-900 px-3 py-2 md:hidden">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                cn("flex shrink-0 items-center gap-2 rounded-md px-3 py-2 text-xs text-zinc-500", isActive && "bg-emerald-500/10 text-emerald-300")
              }
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
            </NavLink>
          ))}
        </nav>
        <main className="min-w-0 p-4 md:p-6">{children}</main>
      </div>
    </div>
  )
}
