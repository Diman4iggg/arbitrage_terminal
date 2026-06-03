import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { AlertTriangle, BellRing, Pencil, Plus, Save, Trash2, X } from "lucide-react"
import { useState } from "react"
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { terminalApi } from "../api/client"
import type { AlertCondition, TargetPriceSource, TradeWatch, TradeWatchCreate, TradeWatchUpdate } from "../api/types"
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
  price_alert_condition: "above",
  funding_alert_threshold_percent: 0.01,
  funding_alert_condition: "above",
  target_price_alert_value: null,
  target_price_alert_condition: "above",
  target_price_alert_source: "buy",
}
const TRADE_SPREAD_HISTORY_MINUTES = 1440
type TradeWatchEditForm = {
  buy_exchange: string
  sell_exchange: string
  buy_entry_price: string
  sell_entry_price: string
  position_size_coins: string
  price_alert_threshold_percent: string
  price_alert_condition: AlertCondition
  funding_alert_threshold_percent: string
  funding_alert_condition: AlertCondition
  target_price_alert_value: string
  target_price_alert_condition: AlertCondition
  target_price_alert_source: TargetPriceSource
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
    onSuccess: (updatedWatch) => {
      queryClient.setQueryData<TradeWatch[]>(["trade-watches"], (current) =>
        current?.map((watch) => (watch.id === updatedWatch.id ? updatedWatch : watch)) ?? current,
      )
      refresh()
    },
  })
  const remove = useMutation({ mutationFn: terminalApi.deleteTradeWatch, onSuccess: refresh })

  return (
    <>
      <PageHeader title="My Trades" description="Manual perpetual watchlist with live directional price and funding spreads. Monitoring only, no orders are placed." />
      <Card className="mb-4">
        <CardHeader><h2 className="text-sm font-semibold">Add monitored direction</h2></CardHeader>
        <CardContent>
          <form className="grid gap-4" onSubmit={(event) => { event.preventDefault(); create.mutate(form) }}>
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <Field label="Coin"><Input required value={form.symbol} onChange={(event) => setForm({ ...form, symbol: event.target.value })} placeholder="BTC or BTC/USDT" /></Field>
            <Field label="Buy exchange"><ExchangeSelect exchanges={exchangeNames} value={form.buy_exchange} onChange={(buy_exchange) => setForm({ ...form, buy_exchange })} /></Field>
            <Field label="Sell exchange"><ExchangeSelect exchanges={exchangeNames} value={form.sell_exchange} onChange={(sell_exchange) => setForm({ ...form, sell_exchange })} /></Field>
            <Field label="Long entry price"><RequiredNumber value={form.buy_entry_price} onChange={(buy_entry_price) => setForm({ ...form, buy_entry_price })} /></Field>
            </div>
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <Field label="Short entry price"><RequiredNumber value={form.sell_entry_price} onChange={(sell_entry_price) => setForm({ ...form, sell_entry_price })} /></Field>
            <Field label="Position size, coins"><RequiredNumber value={form.position_size_coins} onChange={(position_size_coins) => setForm({ ...form, position_size_coins })} /></Field>
            <Field className="xl:col-span-2" label="Price alert rule"><AlertRuleInput condition={form.price_alert_condition} value={form.price_alert_threshold_percent} onConditionChange={(price_alert_condition) => setForm({ ...form, price_alert_condition })} onValueChange={(price_alert_threshold_percent) => setForm({ ...form, price_alert_threshold_percent })} /></Field>
            </div>
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <Field className="xl:col-span-2" label="Funding alert rule"><AlertRuleInput condition={form.funding_alert_condition} value={form.funding_alert_threshold_percent} onConditionChange={(funding_alert_condition) => setForm({ ...form, funding_alert_condition })} onValueChange={(funding_alert_threshold_percent) => setForm({ ...form, funding_alert_threshold_percent })} /></Field>
            <Field className="xl:col-span-2" label="Target price alert"><TargetPriceRuleInput source={form.target_price_alert_source} condition={form.target_price_alert_condition} value={form.target_price_alert_value} onSourceChange={(target_price_alert_source) => setForm({ ...form, target_price_alert_source })} onConditionChange={(target_price_alert_condition) => setForm({ ...form, target_price_alert_condition })} onValueChange={(target_price_alert_value) => setForm({ ...form, target_price_alert_value })} /></Field>
            </div>
            <div className="flex flex-wrap items-center justify-end gap-3 border-t border-terminal-700 pt-3">
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
    queryKey: ["trade-watch-spread-history", watch.id, TRADE_SPREAD_HISTORY_MINUTES],
    queryFn: () => terminalApi.getTradeWatchSpreadHistory(watch.id, TRADE_SPREAD_HISTORY_MINUTES),
    refetchInterval: 10_000,
  })
  const chartData = history.data?.points.map((point) => ({
    timestamp: new Date(point.timestamp).toLocaleString([], { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }),
    spread: Number(point.spread_percent),
  })) ?? []
  const editPayload = buildEditPayload(editForm)
  const save = () => {
    if (!editPayload) return
    onUpdate(editPayload)
    setEditing(false)
  }
  const availableExchanges = Array.from(new Set([...exchanges, watch.buy_exchange, watch.sell_exchange]))
  const selectedBuyExchange = editForm.buy_exchange || watch.buy_exchange
  const selectedSellExchange = editForm.sell_exchange || watch.sell_exchange

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
          <Field label="Long entry price"><EditNumber value={editForm.buy_entry_price} onChange={(buy_entry_price) => setEditForm({ ...editForm, buy_entry_price })} required /></Field>
          <Field label="Short entry price"><EditNumber value={editForm.sell_entry_price} onChange={(sell_entry_price) => setEditForm({ ...editForm, sell_entry_price })} required /></Field>
          <Field label="Position size, coins"><EditNumber value={editForm.position_size_coins} onChange={(position_size_coins) => setEditForm({ ...editForm, position_size_coins })} required /></Field>
          <Field className="sm:col-span-3" label="Price alert rule"><EditAlertRuleInput condition={editForm.price_alert_condition} value={editForm.price_alert_threshold_percent} onConditionChange={(price_alert_condition) => setEditForm({ ...editForm, price_alert_condition })} onValueChange={(price_alert_threshold_percent) => setEditForm({ ...editForm, price_alert_threshold_percent })} /></Field>
          <Field className="sm:col-span-3" label="Funding alert rule"><EditAlertRuleInput condition={editForm.funding_alert_condition} value={editForm.funding_alert_threshold_percent} onConditionChange={(funding_alert_condition) => setEditForm({ ...editForm, funding_alert_condition })} onValueChange={(funding_alert_threshold_percent) => setEditForm({ ...editForm, funding_alert_threshold_percent })} /></Field>
          <Field className="sm:col-span-3" label="Target price alert"><EditTargetPriceRuleInput source={editForm.target_price_alert_source} condition={editForm.target_price_alert_condition} value={editForm.target_price_alert_value} onSourceChange={(target_price_alert_source) => setEditForm({ ...editForm, target_price_alert_source })} onConditionChange={(target_price_alert_condition) => setEditForm({ ...editForm, target_price_alert_condition })} onValueChange={(target_price_alert_value) => setEditForm({ ...editForm, target_price_alert_value })} /></Field>
          <div className="flex gap-2 sm:col-span-3"><Button type="button" onClick={save} disabled={!editPayload}><Save className="mr-1 inline h-3.5 w-3.5" />Save changes</Button><Button type="button" onClick={() => setEditing(false)}><X className="mr-1 inline h-3.5 w-3.5" />Cancel</Button></div>
        </div>}
        <div className="mt-4 border-t border-terminal-700 pt-3">
          <p className="mb-2 text-[10px] uppercase tracking-wider text-zinc-600">Spread history, last 24h</p>
          {history.isLoading ? <Skeleton className="h-32" /> : chartData.length ? <TradeSpreadChart data={chartData} /> : <div className="flex h-32 items-center justify-center rounded-md border border-terminal-700 bg-terminal-950 text-xs text-zinc-600">Waiting for spread snapshots from the last 24h...</div>}
        </div>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-terminal-700 pt-3 text-xs">
          <div className="flex flex-wrap gap-3 text-zinc-500">
            <span>Price alert: <b className="text-zinc-300">{formatAlertRule(watch.price_alert_condition, watch.price_alert_threshold_percent)}</b></span>
            <span>Funding alert: <b className="text-zinc-300">{formatAlertRule(watch.funding_alert_condition, watch.funding_alert_threshold_percent)}</b></span>
            <span>Target price alert: <b className="text-zinc-300">{formatTargetPriceRule(watch)}</b></span>
            <span>Updated: <b className="text-zinc-300">{formatDate(watch.last_updated_at)}</b></span>
          </div>
          <div className="flex items-center gap-2 text-zinc-400"><BellRing className="h-3.5 w-3.5" /><Switch label={`Alerts for ${watch.symbol}`} checked={watch.notifications_enabled} onChange={(notifications_enabled) => onUpdate({ notifications_enabled })} /></div>
        </div>
        {watch.last_error && <div className="mt-3 flex gap-2 rounded-md border border-amber-500/20 bg-amber-500/5 p-3 text-[11px] leading-4 text-amber-200"><AlertTriangle className="h-3.5 w-3.5 shrink-0" />{watch.last_error}</div>}
      </CardContent>
    </Card>
  )
}

function Field({ label, children, className = "" }: { label: string; children: React.ReactNode; className?: string }) {
  return <label className={`block ${className}`}><span className="mb-2 block text-xs text-zinc-500">{label}</span>{children}</label>
}

function ExchangeSelect({ exchanges, value, onChange }: { exchanges: string[]; value: string; onChange: (value: string) => void }) {
  return <Select className="w-full" value={value} onChange={(event) => onChange(event.target.value)}>{exchanges.map((exchange) => <option key={exchange}>{exchange}</option>)}</Select>
}

function OptionalNumber({ value, onChange }: { value: number | null; onChange: (value: number | null) => void }) {
  return <Input type="number" step="any" value={value ?? ""} onChange={(event) => onChange(event.target.value === "" ? null : Number(event.target.value))} placeholder="disabled" />
}

function OptionalPositiveNumber({ value, onChange }: { value: number | null; onChange: (value: number | null) => void }) {
  return <Input type="number" min="0.00000001" step="any" value={value ?? ""} onChange={(event) => onChange(event.target.value === "" ? null : Number(event.target.value))} placeholder="disabled" />
}

function RequiredNumber({ value, onChange }: { value: number; onChange: (value: number) => void }) {
  return <Input required type="number" min="0.00000001" step="any" value={value || ""} onChange={(event) => onChange(Number(event.target.value))} placeholder="Required" />
}

function EditNumber({ value, onChange, required = false, placeholder = "Required" }: { value: string; onChange: (value: string) => void; required?: boolean; placeholder?: string }) {
  return <Input required={required} type="number" min={required ? "0.00000001" : undefined} step="any" value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} />
}

function AlertRuleInput({ condition, value, onConditionChange, onValueChange }: { condition: AlertCondition; value: number | null; onConditionChange: (value: AlertCondition) => void; onValueChange: (value: number | null) => void }) {
  return (
    <div className="grid min-w-0 grid-cols-1 gap-2 sm:grid-cols-[minmax(120px,0.45fr)_minmax(180px,1fr)]">
      <AlertConditionSelect value={condition} onChange={onConditionChange} />
      <OptionalNumber value={value} onChange={onValueChange} />
    </div>
  )
}

function EditAlertRuleInput({ condition, value, onConditionChange, onValueChange }: { condition: AlertCondition; value: string; onConditionChange: (value: AlertCondition) => void; onValueChange: (value: string) => void }) {
  return (
    <div className="grid min-w-0 grid-cols-1 gap-2 sm:grid-cols-[minmax(120px,0.45fr)_minmax(180px,1fr)]">
      <AlertConditionSelect value={condition} onChange={onConditionChange} />
      <EditNumber value={value} onChange={onValueChange} placeholder="disabled" />
    </div>
  )
}

function AlertConditionSelect({ value, onChange }: { value: AlertCondition; onChange: (value: AlertCondition) => void }) {
  return (
    <Select className="w-full" value={value} onChange={(event) => onChange(event.target.value as AlertCondition)}>
      <option value="above">above</option>
      <option value="below">below</option>
    </Select>
  )
}

function TargetPriceRuleInput({ source, condition, value, onSourceChange, onConditionChange, onValueChange }: { source: TargetPriceSource; condition: AlertCondition; value: number | null; onSourceChange: (value: TargetPriceSource) => void; onConditionChange: (value: AlertCondition) => void; onValueChange: (value: number | null) => void }) {
  return (
    <div className="grid min-w-0 grid-cols-1 gap-2 sm:grid-cols-[minmax(120px,0.7fr)_minmax(120px,0.7fr)_minmax(180px,1fr)]">
      <TargetPriceSourceSelect value={source} onChange={onSourceChange} />
      <AlertConditionSelect value={condition} onChange={onConditionChange} />
      <OptionalPositiveNumber value={value} onChange={onValueChange} />
    </div>
  )
}

function EditTargetPriceRuleInput({ source, condition, value, onSourceChange, onConditionChange, onValueChange }: { source: TargetPriceSource; condition: AlertCondition; value: string; onSourceChange: (value: TargetPriceSource) => void; onConditionChange: (value: AlertCondition) => void; onValueChange: (value: string) => void }) {
  return (
    <div className="grid min-w-0 grid-cols-1 gap-2 sm:grid-cols-[minmax(120px,0.7fr)_minmax(120px,0.7fr)_minmax(180px,1fr)]">
      <TargetPriceSourceSelect value={source} onChange={onSourceChange} />
      <AlertConditionSelect value={condition} onChange={onConditionChange} />
      <EditNumber value={value} onChange={onValueChange} placeholder="disabled" />
    </div>
  )
}

function TargetPriceSourceSelect({ value, onChange }: { value: TargetPriceSource; onChange: (value: TargetPriceSource) => void }) {
  return (
    <Select className="w-full" value={value} onChange={(event) => onChange(event.target.value as TargetPriceSource)}>
      <option value="buy">buy price</option>
      <option value="sell">sell price</option>
    </Select>
  )
}

function makeEditForm(watch: TradeWatch): TradeWatchEditForm {
  return {
    buy_exchange: watch.buy_exchange,
    sell_exchange: watch.sell_exchange,
    buy_entry_price: watch.buy_entry_price === null ? "" : trimNumericString(watch.buy_entry_price),
    sell_entry_price: watch.sell_entry_price === null ? "" : trimNumericString(watch.sell_entry_price),
    position_size_coins: watch.position_size_coins === null ? "" : trimNumericString(watch.position_size_coins),
    price_alert_threshold_percent: watch.price_alert_threshold_percent === null ? "" : trimNumericString(watch.price_alert_threshold_percent),
    price_alert_condition: watch.price_alert_condition,
    funding_alert_threshold_percent: watch.funding_alert_threshold_percent === null ? "" : trimNumericString(watch.funding_alert_threshold_percent),
    funding_alert_condition: watch.funding_alert_condition,
    target_price_alert_value: watch.target_price_alert_value === null ? "" : trimNumericString(watch.target_price_alert_value),
    target_price_alert_condition: watch.target_price_alert_condition,
    target_price_alert_source: watch.target_price_alert_source,
  }
}

function buildEditPayload(form: TradeWatchEditForm): TradeWatchUpdate | null {
  const buyEntryPrice = parsePositiveNumber(form.buy_entry_price)
  const sellEntryPrice = parsePositiveNumber(form.sell_entry_price)
  const positionSize = parsePositiveNumber(form.position_size_coins)
  const priceAlert = parseOptionalNumber(form.price_alert_threshold_percent)
  const fundingAlert = parseOptionalNumber(form.funding_alert_threshold_percent)
  const targetPriceAlert = parseOptionalPositiveNumber(form.target_price_alert_value)
  if (
    buyEntryPrice === null
    || sellEntryPrice === null
    || positionSize === null
    || priceAlert === undefined
    || fundingAlert === undefined
    || targetPriceAlert === undefined
    || form.buy_exchange === form.sell_exchange
  ) {
    return null
  }
  return {
    buy_exchange: form.buy_exchange,
    sell_exchange: form.sell_exchange,
    buy_entry_price: buyEntryPrice,
    sell_entry_price: sellEntryPrice,
    position_size_coins: positionSize,
    price_alert_threshold_percent: priceAlert,
    price_alert_condition: form.price_alert_condition,
    funding_alert_threshold_percent: fundingAlert,
    funding_alert_condition: form.funding_alert_condition,
    target_price_alert_value: targetPriceAlert,
    target_price_alert_condition: form.target_price_alert_condition,
    target_price_alert_source: form.target_price_alert_source,
  }
}

function parsePositiveNumber(value: string) {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null
}

function parseOptionalNumber(value: string) {
  if (value.trim() === "") return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : undefined
}

function parseOptionalPositiveNumber(value: string) {
  if (value.trim() === "") return null
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : undefined
}

function trimNumericString(value: string) {
  return Number(value).toString()
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

function formatAlertRule(condition: AlertCondition, value: string | null) {
  return value === null ? "disabled" : `${condition} ${formatSpread(value)}`
}

function formatTargetPriceRule(watch: TradeWatch) {
  return watch.target_price_alert_value === null
    ? "disabled"
    : `${watch.target_price_alert_source} price ${watch.target_price_alert_condition} ${formatPrice(watch.target_price_alert_value)}`
}

function Metric({ label, value, accent = false, tone = "neutral" }: { label: string; value: string; accent?: boolean; tone?: "neutral" | "positive" | "negative" }) {
  const color = tone === "positive" ? "text-emerald-300" : tone === "negative" ? "text-rose-300" : accent ? "text-emerald-300" : "text-zinc-200"
  return <div className="rounded-md border border-terminal-700 bg-terminal-950 p-3"><p className="text-[10px] uppercase tracking-wider text-zinc-600">{label}</p><p className={`mt-1 text-sm font-semibold ${color}`}>{value}</p></div>
}
