import { useQuery } from "@tanstack/react-query"
import { useState } from "react"

import { terminalApi } from "../api/client"
import { OpportunityTable } from "../components/OpportunityTable"
import { PageHeader } from "../components/PageHeader"
import { Card, Input, Select, Skeleton } from "../components/ui"

export function Opportunities() {
  const [symbol, setSymbol] = useState("")
  const [exchange, setExchange] = useState("")
  const [minSpread, setMinSpread] = useState("0")
  const opportunities = useQuery({
    queryKey: ["opportunities", symbol, exchange, minSpread],
    queryFn: () => terminalApi.getOpportunities({ ...(symbol && { symbol }), ...(exchange && { exchange }), min_spread: minSpread || 0 }),
  })

  return (
    <>
      <PageHeader title="Arbitrage Opportunities" description="Spreads above your configured threshold, sorted by profitability." />
      <Card>
        <div className="grid gap-3 border-b border-terminal-700 p-4 md:grid-cols-3">
          <Input value={symbol} onChange={(event) => setSymbol(event.target.value)} placeholder="Filter symbol, e.g. BTC or BNB" />
          <Select value={exchange} onChange={(event) => setExchange(event.target.value)}>
            <option value="">All exchanges</option>
            {["Binance", "Bybit", "MEXC", "Hyperliquid"].map((item) => <option key={item}>{item}</option>)}
          </Select>
          <Input value={minSpread} onChange={(event) => setMinSpread(event.target.value)} type="number" min="0" step="0.1" placeholder="Minimum spread %" />
        </div>
        {opportunities.isLoading ? <Skeleton className="m-4 h-40" /> : opportunities.isError ? <div className="p-8 text-center text-sm text-rose-300">Unable to load opportunities.</div> : <OpportunityTable opportunities={opportunities.data ?? []} />}
      </Card>
    </>
  )
}
