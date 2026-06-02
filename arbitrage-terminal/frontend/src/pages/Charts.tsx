import { useQuery } from "@tanstack/react-query"
import { useMemo, useState } from "react"
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { terminalApi } from "../api/client"
import { PageHeader } from "../components/PageHeader"
import { Card, CardContent, CardHeader, Select, Skeleton } from "../components/ui"
import { formatSpread } from "../lib/format"

const colors: Record<string, string> = { Binance: "#34d399", Bybit: "#60a5fa", MEXC: "#f59e0b", Hyperliquid: "#c084fc", Aster: "#fb7185", "Variational Omni": "#22d3ee", BingX: "#a3e635", Bitget: "#f472b6", OKX: "#e4e4e7", "Gate.io": "#f97316" }

export function Charts() {
  const [symbol, setSymbol] = useState("BTC/USDT")
  const [minutes, setMinutes] = useState(30)
  const pairs = useQuery({ queryKey: ["pairs"], queryFn: terminalApi.getPairs })
  const prices = useQuery({ queryKey: ["prices", symbol, minutes], queryFn: () => terminalApi.getPrices(symbol, minutes) })
  const spreads = useQuery({ queryKey: ["spreads", symbol, minutes], queryFn: () => terminalApi.getSpreads(symbol, minutes) })
  const top = useQuery({ queryKey: ["top-spreads", minutes], queryFn: () => terminalApi.getTopSpreads(minutes) })

  const priceData = useMemo(() => {
    const buckets: Record<string, Record<string, string | number>> = {}
    prices.data?.points.forEach((point) => {
      const timestamp = new Date(point.timestamp).toLocaleTimeString()
      buckets[timestamp] ??= { timestamp }
      buckets[timestamp][point.exchange] = Number(point.last_price)
    })
    return Object.values(buckets)
  }, [prices.data])
  const spreadData = spreads.data?.points.map((point) => ({ timestamp: new Date(point.timestamp).toLocaleTimeString(), spread: Number(point.spread_percent) })) ?? []

  return (
    <>
      <PageHeader title="Charts" description="Recent normalized perpetual prices and cross-exchange spread history." actions={<div className="flex gap-2"><Select value={symbol} onChange={(event) => setSymbol(event.target.value)}>{pairs.data?.map((pair) => <option key={pair.id}>{pair.symbol}</option>)}</Select><Select value={minutes} onChange={(event) => setMinutes(Number(event.target.value))}>{[15, 30, 60, 180].map((value) => <option key={value} value={value}>{value} min</option>)}</Select></div>} />
      <div className="grid gap-4">
        <ChartCard title={`${symbol} price by exchange`}>{prices.isLoading ? <Skeleton className="h-72" /> : <PriceChart data={priceData} />}</ChartCard>
        <div className="grid gap-4 xl:grid-cols-[1fr_360px]">
          <ChartCard title={`${symbol} spread history`}>{spreads.isLoading ? <Skeleton className="h-64" /> : <SpreadChart data={spreadData} />}</ChartCard>
          <Card><CardHeader><h2 className="text-sm font-semibold">Top spreads</h2></CardHeader><CardContent className="space-y-3">{top.data?.length ? top.data.map((item, index) => <div key={`${item.symbol}-${item.detected_at}-${index}`} className="flex items-center justify-between gap-3 border-b border-terminal-700 pb-3 text-xs last:border-0 last:pb-0"><div><p className="font-semibold text-zinc-200">{item.symbol}</p><p className="mt-1 text-zinc-500">{item.buy_exchange} / {item.sell_exchange}</p></div><span className="font-mono font-semibold text-emerald-300">{formatSpread(item.spread_percent)}</span></div>) : <p className="py-8 text-center text-sm text-zinc-500">No recorded spreads in this window.</p>}</CardContent></Card>
        </div>
      </div>
    </>
  )
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return <Card><CardHeader><h2 className="text-sm font-semibold">{title}</h2></CardHeader><CardContent>{children}</CardContent></Card>
}

function PriceChart({ data }: { data: Array<Record<string, string | number>> }) {
  return <div className="h-72"><ResponsiveContainer width="100%" height="100%"><LineChart data={data}><CartesianGrid stroke="#272a31" vertical={false} /><XAxis dataKey="timestamp" tick={{ fill: "#71717a", fontSize: 10 }} minTickGap={30} /><YAxis domain={["auto", "auto"]} tick={{ fill: "#71717a", fontSize: 10 }} width={75} /><Tooltip contentStyle={{ background: "#101114", border: "1px solid #272a31", fontSize: 12 }} /><Legend />{Object.entries(colors).map(([exchange, color]) => <Line key={exchange} type="monotone" dataKey={exchange} stroke={color} dot={false} connectNulls strokeWidth={1.5} />)}</LineChart></ResponsiveContainer></div>
}

function SpreadChart({ data }: { data: Array<{ timestamp: string; spread: number }> }) {
  return <div className="h-64"><ResponsiveContainer width="100%" height="100%"><LineChart data={data}><CartesianGrid stroke="#272a31" vertical={false} /><XAxis dataKey="timestamp" tick={{ fill: "#71717a", fontSize: 10 }} minTickGap={30} /><YAxis tick={{ fill: "#71717a", fontSize: 10 }} width={55} /><Tooltip contentStyle={{ background: "#101114", border: "1px solid #272a31", fontSize: 12 }} formatter={(value) => `${Number(value).toFixed(3)}%`} /><Line type="monotone" dataKey="spread" name="Spread %" stroke="#34d399" dot={false} strokeWidth={1.5} /></LineChart></ResponsiveContainer></div>
}
