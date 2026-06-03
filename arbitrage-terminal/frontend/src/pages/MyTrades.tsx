import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { AlertTriangle, BellRing, Pencil, Plus, Save, Trash2, X } from "lucide-react"
import { useState } from "react"
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { terminalApi } from "../api/client"
import type { TradeWatch, TradeWatchCreate, TradeWatchUpdate } from "../api/types"
import { PageHeader } from "../components/PageHeader"
import { Badge, Button, Card, CardContent, CardHeader, Input, Select, Skeleton, Switch } from "../components/ui"
import { formatDate, formatPrice, formatSpread } from "../lib/format"

const initialForm: TradeWatchCreate = {
  symbol: "",
  buy_exchange: "Binance",
  sell_exchange: "Bybit",
  notifications_enabled: true,
  buy_entry_price: 0,
  sell_entry_price: 0,
  position_size_coins: 0,
  price_alert_threshold_percent: 0.1,
  funding_alert_threshold_percent: 0.01,
}

export function MyTrades() {
  const queryClient = useQueryClient()
  const [form, setForm] = useState(initialForm)
  const watches = useQuery({
    queryKey: ["trade-watches"],
    queryFn: terminalApi.getTradeWatches,
    refetchInterval: 10_000,
  })
  const exchanges = useQuery({ queryKey: ["exchanges"], queryFn: terminalApi.getExchanges })
  const exchangeNames = exchanges.data?.map((exchange) => exchange.name) ?? []
  const refresh = () => queryClient.invalidateQueries({ queryKey: ["trade-watches"] })
  const create = useMutation({
    mutationFn: terminalApi.createTradeWatch,
    onSuccess: () => {
      setForm(initialForm)
      refresh()
    },
  })
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: TradeWatchUpdate }) =>
      terminalApi.updateTradeWatch(id, payload),
    onSuccess: refresh,
  })
  const remove = useMutation({ mutationFn: terminalApi.deleteTradeWatch, onSuccess: refresh })

  return (
    <>
      <PageHeader title="My Trades" description="Manual perpetual watchlist with live directional price and funding spreads. Monitoring only, no orders are placed." />
      <Card className="mb-4">
        <CardHeader><h2 className="text-sm font-semibold">Add monitored direction</h2></CardHeader>
        <CardContent>
          <form className="grid gap-3 md:grid-cols-2 xl:grid-cols-4" onSubmit={(event) => { event.preventDefault(); create.mutate(form) }}>
            <Field label="Coin"><Input required value={form.symbol} onChange={(event) => setForm({ ...form, symbol: event.target.value })} placeholder="BTC or BTC/USDT" /></Field>
            <Field label="Buy exchange"><ExchangeSelect exchanges={exchangeNames} value={form.buy_exchange} onChange={(buy_exchange) => setForm({ ...form, buy_exchange })} /></Field>
            <Field label="Sell exchange"><ExchangeSelect exchanges={exchangeNames} value={form.sell_exchange} onChange={(sell_exchange) => setForm({ ...form, sell_exchange })} /></Field>
            <Field label="Long entry price"><RequiredNumber value={form.buy_entry_price} onChange={(buy_entry_price) => setForm({ ...form, buy_entry_price })} /></Field>
            <Field label="Short entry price"><RequiredNumber value={form.sell_entry_price} onChange={(sell_entry_price) => setForm({ ...form, sell_entry_price })} /></Field>
            <Field label="Position size, coins"><RequiredNumber value={form.position_size_coins} onChange={(position_size_coins) => setForm({ ...form, position_size_coins })} /></Field>
            <Field label="Price alert %"><OptionalNumber value={form.price_alert_threshold_percent} onChange={(price_alert_threshold_percent) => setForm({ ...form, price_alert_threshold_percent })} /></Field>
            <Field label="Funding alert %"><OptionalNumber value={form.funding_alert_threshold_percent} onChange={(funding_alert_threshold_percent) => setForm({ ...form, funding_alert_threshold_percent })} /></Field>
            <div className="flex items-end gap-3">
              <Switch label="Enable alerts" checked={form.notifications_enabled} onChange={(notifications_enabled) => setForm({ ...form, notifications_enabled })} />
              <Button type="submit" disabled={create.isPending || form.buy_exchange === form.sell_exchange || form.buy_entry_price <= 0 || form.sell_entry_price <= 0 || form.position_size_coins <= 0}><Plus className="mr-1 inline h-3.5 w-3.5" />Add</Button>
            </div>
          </form>
          {form.buy_exchange === form.sell_exchange && <p className="mt-3 text-xs text-amber-300">Choose two different exchanges.</p>}
          {create.isError && <p className="mt-3 text-xs text-rose-300">Unable to add this watch. Check the symbol and selected exchanges.</p>}
        </CardContent>
      </Card>
      {watches.isLoading ? <Skeleton className="h-52" /> : watches.isError ? (
        <Card><CardContent className="text-sm text-rose-300">Unable to load My Trades.</CardContent></Card>
      ) : watches.data?.length ? (
        <div className="grid gap-3 xl:grid-cols-2">
          {watches.data.map((watch) => <WatchCard key={watch.id} watch={watch} exchanges={exchangeNames} onUpdate={(payload) => update.mutate({ id: watch.id, payload })} onDelete={() => remove.mutate(watch.id)} />)}
        </div>
      ) : (
        <Card><CardContent className="py-10 text-center text-sm text-zinc-500">No monitored directions yet. Add a coin and two exchanges above.</CardContent></Card>
      )}
    </>
  )
}

function WatchCard({ watch, exchanges, onUpdate, onDelete }: { watch: TradeWatch; exchanges: string[]; onUpdate: (payload: TradeWatchUpdate) => void; onDelete: () => void }) {
  const [editing, setEditing] = useState(false)
  const [editForm, setEditForm] = useState(() => makeEditForm(watch))
  const history = useQuery({
    queryKey: ["trade-watch-spread-history", watch.id],
    queryFn: () => terminalApi.getTradeWatchSpreadHistory(watch.id),
    refetchInterval: 10_000,
  })
  const chartData = history.data?.points.map((point) => ({
    timestamp: new Date(point.timestamp).toLocaleTimeString(),
    spread: Number(point.spread_percent),
  })) ?? []
  const save = () => {
    onUpdate(editForm)
    setEditing(false)
  }
  const availableExchanges = Array.from(new Set([...exchanges, watch.buy_exchange, watch.sell_exchange]))
  const selectedBuyExchange = editForm.buy_exchange ?? watch.buy_exchange
  const selectedSellExchange = editForm.sell_exchange ?? watch.sell_exchange

  return (
    <Card>
      <CardHeader className="flex items-center justify-between gap-3">
        <div><h2 className="text-sm font-semibold">{watch.symbol} <span className="text-zinc-500">PERP</span></h2><p className="mt-1 text-xs text-zinc-500">{watch.buy_exchange} <span className="text-emerald-400">-&gt;</span> {watch.sell_exchange}</p></div>
        <div className="flex items-center gap-2"><Badge tone={watch.enabled ? "success" : "neutral"}>{watch.enabled ? "live" : "paused"}</Badge><Button onClick={() => { setEditForm(makeEditForm(watch)); setEditing(!editing) }} aria-label={`Edit ${watch.symbol}`}><Pencil className="h-3.5 w-3.5" /></Button><Button onClick={onDelete} aria-label={`Delete ${watch.symbol}`}><Trash2 className="h-3.5 w-3.5" /></Button></div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 sm:grid-cols-3">
          <Metric label="Position size" value={watch.position_size_coins ? `${formatPrice(watch.position_size_coins)} coins` : "Legacy watch"} />
          <Metric label="Long entry" value={watch.buy_entry_price ? formatPrice(watch.buy_entry_price) : "n/a"} />
          <Metric label="Short entry" value={watch.sell_entry_price ? formatPrice(watch.sell_entry_price) : "n/a"} />
          <Metric label="Entry spread" value={formatOptionalSpread(watch.entry_spread_percent)} tone={spreadTone(watch.entry_spread_percent)} />
          <Metric label="Buy price" value={watch.buy_price ? formatPrice(watch.buy_price) : "Waiting..."} />
          <Metric label="Sell price" value={watch.sell_price ? formatPrice(watch.sell_price) : "Waiting..."} />
          <Metric label="Price spread" value={formatSpread(watch.price_spread_percent)} accent />
          <Metric label={`${watch.buy_exchange} funding`} value={formatSpread(watch.buy_funding_rate_percent)} />
          <Metric label={`${watch.sell_exchange} funding`} value={formatSpread(watch.sell_funding_rate_percent)} />
          <Metric label="Funding spread" value={formatOptionalSpread(watch.funding_spread_percent)} tone={spreadTone(watch.funding_spread_percent)} />
          <Metric label="Position PnL" value={formatPnl(watch.pnl_usdt, watch.pnl_percent)} tone={pnlTone(watch.pnl_usdt)} />
        </div>
        {editing && <div className="mt-4 grid gap-3 rounded-md border border-terminal-700 bg-terminal-950 p-3 sm:grid-cols-3">
          <Field label="Buy exchange"><ExchangeSelect exchanges={availableExchanges} value={selectedBuyExchange} onChange={(buy_exchange) => setEditForm({ ...editForm, buy_exchange })} /></Field>
          <Field label="Sell exchange"><ExchangeSelect exchanges={availableExchanges} value={selectedSellExchange} onChange={(sell_exchange) => setEditForm({ ...editForm, sell_exchange })} /></Field>
          <Field label="Position size, coins"><RequiredNumber value={editForm.position_size_coins ?? 0} onChange={(position_size_coins) => setEditForm({ ...editForm, position_size_coins })} /></Field>
          <Field label="Price alert %"><OptionalNumber value={editForm.price_alert_threshold_percent ?? null} onChange={(price_alert_threshold_percent) => setEditForm({ ...editForm, price_alert_threshold_percent })} /></Field>
          <Field label="Funding alert %"><OptionalNumber value={editForm.funding_alert_threshold_percent ?? null} onChange={(funding_alert_threshold_percent) => setEditForm({ ...editForm, funding_alert_threshold_percent })} /></Field>
          <div className="flex gap-2 sm:col-span-3"><Button onClick={save} disabled={!editForm.position_size_coins || editForm.position_size_coins <= 0 || selectedBuyExchange === selectedSellExchange}><Save className="mr-1 inline h-3.5 w-3.5" />Save changes</Button><Button onClick={() => setEditing(false)}><X className="mr-1 inline h-3.5 w-3.5" />Cancel</Button></div>
        </div>}
        <div className="mt-4 border-t border-terminal-700 pt-3">
          <p className="mb-2 text-[10px] uppercase tracking-wider text-zinc-600">Spread history, 30 min</p>
          {history.isLoading ? <Skeleton className="h-32" /> : chartData.length ? <TradeSpreadChart data={chartData} /> : <div className="flex h-32 items-center justify-center rounded-md border border-terminal-700 bg-terminal-950 text-xs text-zinc-600">Waiting for spread snapshots...</div>}
        </div>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-terminal-700 pt-3 text-xs">
          <div className="flex flex-wrap gap-3 text-zinc-500">
            <span>Price alert: <b className="text-zinc-300">{formatSpread(watch.price_alert_threshold_percent)}</b></span>
            <span>Funding alert: <b className="text-zinc-300">{formatSpread(watch.funding_alert_threshold_percent)}</b></span>
            <span>Updated: <b className="text-zinc-300">{formatDate(watch.last_updated_at)}</b></span>
          </div>
          <div className="flex items-center gap-2 text-zinc-400"><BellRing className="h-3.5 w-3.5" /><Switch label={`Alerts for ${watch.symbol}`} checked={watch.notifications_enabled} onChange={(notifications_enabled) => onUpdate({ notifications_enabled })} /></div>
        </div>
        {watch.last_error && <div className="mt-3 flex gap-2 rounded-md border border-amber-500/20 bg-amber-500/5 p-3 text-[11px] leading-4 text-amber-200"><AlertTriangle className="h-3.5 w-3.5 shrink-0" />{watch.last_error}</div>}
      </CardContent>
    </Card>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <label className="block"><span className="mb-2 block text-xs text-zinc-500">{label}</span>{children}</label>
}

function ExchangeSelect({ exchanges, value, onChange }: { exchanges: string[]; value: string; onChange: (value: string) => void }) {
  return <Select className="w-full" value={value} onChange={(event) => onChange(event.target.value)}>{exchanges.map((exchange) => <option key={exchange}>{exchange}</option>)}</Select>
}

function OptionalNumber({ value, onChange }: { value: number | null; onChange: (value: number | null) => void }) {
  return <Input type="number" min="0" step="0.001" value={value ?? ""} onChange={(event) => onChange(event.target.value === "" ? null : Number(event.target.value))} placeholder="disabled" />
}

function RequiredNumber({ value, onChange }: { value: number; onChange: (value: number) => void }) {
  return <Input required type="number" min="0.00000001" step="any" value={value || ""} onChange={(event) => onChange(Number(event.target.value))} placeholder="Required" />
}

function makeEditForm(watch: TradeWatch): TradeWatchUpdate {
  return {
    buy_exchange: watch.buy_exchange,
    sell_exchange: watch.sell_exchange,
    position_size_coins: watch.position_size_coins === null ? 0 : Number(watch.position_size_coins),
    price_alert_threshold_percent: watch.price_alert_threshold_percent === null ? null : Number(watch.price_alert_threshold_percent),
    funding_alert_threshold_percent: watch.funding_alert_threshold_percent === null ? null : Number(watch.funding_alert_threshold_percent),
  }
}

function TradeSpreadChart({ data }: { data: Array<{ timestamp: string; spread: number }> }) {
  return <div className="h-32"><ResponsiveContainer width="100%" height="100%"><LineChart data={data}><CartesianGrid stroke="#272a31" vertical={false} /><XAxis dataKey="timestamp" tick={{ fill: "#71717a", fontSize: 9 }} minTickGap={30} /><YAxis tick={{ fill: "#71717a", fontSize: 9 }} width={48} /><Tooltip contentStyle={{ background: "#101114", border: "1px solid #272a31", fontSize: 11 }} formatter={(value) => `${Number(value).toFixed(3)}%`} /><Line type="monotone" dataKey="spread" name="Spread %" stroke="#34d399" dot={false} strokeWidth={1.5} /></LineChart></ResponsiveContainer></div>
}

function formatPnl(pnlUsdt: string | null, pnlPercent: string | null) {
  if (pnlUsdt === null || pnlPercent === null) return "Waiting..."
  return `${Number(pnlUsdt).toFixed(4)} USDT (${Number(pnlPercent).toFixed(3)}%)`
}

function pnlTone(value: string | null) {
  if (value === null || Number(value) === 0) return "neutral"
  return Number(value) > 0 ? "positive" : "negative"
}

function spreadTone(value: string | null) {
  if (value === null || Number(value) === 0) return "neutral"
  return Number(value) > 0 ? "positive" : "negative"
}

function formatOptionalSpread(value: string | null) {
  return value === null ? "n/a" : formatSpread(value)
}

function Metric({ label, value, accent = false, tone = "neutral" }: { label: string; value: string; accent?: boolean; tone?: "neutral" | "positive" | "negative" }) {
  const color = tone === "positive" ? "text-emerald-300" : tone === "negative" ? "text-rose-300" : accent ? "text-emerald-300" : "text-zinc-200"
  return <div className="rounded-md border border-terminal-700 bg-terminal-950 p-3"><p className="text-[10px] uppercase tracking-wider text-zinc-600">{label}</p><p className={`mt-1 text-sm font-semibold ${color}`}>{value}</p></div>
}
