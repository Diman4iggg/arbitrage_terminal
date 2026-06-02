import type { Opportunity } from "../api/types"
import { formatDate, formatPrice, formatSpread } from "../lib/format"
import { Badge } from "./ui"

export function OpportunityTable({ opportunities }: { opportunities: Opportunity[] }) {
  if (!opportunities.length) {
    return <div className="px-4 py-12 text-center text-sm text-zinc-500">No spreads currently exceed the configured threshold.</div>
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[1160px] text-left text-xs">
        <thead className="border-b border-terminal-700 bg-terminal-950/50 text-[10px] uppercase tracking-wider text-zinc-500">
          <tr>{["Pair", "Market", "Buy exchange", "Sell exchange", "Buy price", "Sell price", "Spread", "Buy funding", "Sell funding", "Funding delta", "Detected", "Status"].map((item) => <th key={item} className="px-4 py-3 font-medium">{item}</th>)}</tr>
        </thead>
        <tbody>
          {opportunities.map((item) => (
            <tr key={item.id} className="border-b border-terminal-700/70 text-zinc-300 last:border-0">
              <td className="px-4 py-3 font-semibold text-zinc-100">{item.symbol}</td>
              <td className="px-4 py-3 uppercase text-zinc-500">{item.market_type}</td>
              <td className="px-4 py-3">{item.buy_exchange}</td>
              <td className="px-4 py-3">{item.sell_exchange}</td>
              <td className="px-4 py-3 font-mono">{formatPrice(item.buy_price)}</td>
              <td className="px-4 py-3 font-mono">{formatPrice(item.sell_price)}</td>
              <td className="px-4 py-3 font-mono font-semibold text-emerald-300">{formatSpread(item.spread_percent)}</td>
              <td className="px-4 py-3 font-mono">{formatOptionalSpread(item.buy_funding_rate_percent)}</td>
              <td className="px-4 py-3 font-mono">{formatOptionalSpread(item.sell_funding_rate_percent)}</td>
              <td className="px-4 py-3 font-mono font-semibold text-cyan-300">{formatOptionalSpread(item.funding_spread_percent)}</td>
              <td className="px-4 py-3 text-zinc-500">{formatDate(item.detected_at)}</td>
              <td className="px-4 py-3"><Badge tone={item.status === "active" ? "success" : "neutral"}>{item.status}</Badge></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function formatOptionalSpread(value: string | null) {
  return value === null ? "n/a" : formatSpread(value)
}
