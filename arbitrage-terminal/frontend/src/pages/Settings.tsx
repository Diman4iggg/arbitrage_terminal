import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import axios from "axios"
import { useEffect, useState } from "react"

import { terminalApi } from "../api/client"
import type { RuntimeSettings } from "../api/types"
import { PageHeader } from "../components/PageHeader"
import { Badge, Button, Card, CardContent, CardHeader, Input, Skeleton, Switch } from "../components/ui"

export function Settings() {
  const queryClient = useQueryClient()
  const settings = useQuery({ queryKey: ["settings"], queryFn: terminalApi.getSettings })
  const pairs = useQuery({ queryKey: ["pairs"], queryFn: terminalApi.getPairs })
  const exchanges = useQuery({ queryKey: ["exchanges"], queryFn: terminalApi.getExchanges })
  const [form, setForm] = useState<RuntimeSettings | null>(null)
  const [newPair, setNewPair] = useState("")
  const [pairSearch, setPairSearch] = useState("")
  const [toast, setToast] = useState<{ tone: "success" | "danger"; message: string } | null>(null)

  useEffect(() => { if (settings.data) setForm(settings.data) }, [settings.data])

  const save = useMutation({
    mutationFn: terminalApi.updateSettings,
    onSuccess: (data) => {
      setForm(data)
      showToast("success", "Settings saved successfully.")
      queryClient.invalidateQueries({ queryKey: ["settings"] })
    },
  })
  const testTelegram = useMutation({
    mutationFn: terminalApi.testTelegram,
    onSuccess: (data) => showToast("success", data.message),
    onError: (error) => {
      const detail = axios.isAxiosError(error) ? error.response?.data?.detail : null
      showToast("danger", detail ?? "Unable to send Telegram test notification.")
    },
  })
  const updateTelegramEnabled = useMutation({
    mutationFn: (enabled: boolean) => terminalApi.updateSettings({ telegram_notifications_enabled: enabled }),
    onSuccess: (data) => {
      setForm(data)
      showToast("success", data.telegram_notifications_enabled ? "Telegram alerts enabled." : "Telegram alerts disabled.")
      queryClient.invalidateQueries({ queryKey: ["settings"] })
    },
    onError: () => showToast("danger", "Unable to update Telegram alert state."),
  })
  const updateOpportunityAlertsEnabled = useMutation({
    mutationFn: (enabled: boolean) => terminalApi.updateSettings({ opportunity_notifications_enabled: enabled }),
    onSuccess: (data) => {
      setForm(data)
      showToast("success", data.opportunity_notifications_enabled ? "Opportunity alerts enabled." : "Opportunity alerts disabled.")
      queryClient.invalidateQueries({ queryKey: ["settings"] })
    },
    onError: () => showToast("danger", "Unable to update opportunity alert state."),
  })
  const updatePair = useMutation({ mutationFn: ({ id, enabled }: { id: number; enabled: boolean }) => terminalApi.updatePair(id, enabled), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pairs"] }) })
  const deletePair = useMutation({
    mutationFn: terminalApi.deletePair,
    onSuccess: () => {
      showToast("success", "Pair deleted from monitoring.")
      queryClient.invalidateQueries({ queryKey: ["pairs"] })
    },
    onError: () => showToast("danger", "Unable to delete pair."),
  })
  const createPair = useMutation({
    mutationFn: terminalApi.createPair,
    onSuccess: () => {
      setNewPair("")
      showToast("success", "Perpetual pair added and enabled.")
      queryClient.invalidateQueries({ queryKey: ["pairs"] })
    },
    onError: (error) => {
      const detail = axios.isAxiosError(error) ? error.response?.data?.detail : null
      showToast("danger", detail ?? "Unable to add perpetual pair.")
    },
  })
  const updateExchange = useMutation({ mutationFn: ({ id, enabled }: { id: number; enabled: boolean }) => terminalApi.updateExchange(id, enabled), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["exchanges"] }) })

  if (!form || settings.isLoading) return <Skeleton className="h-96" />
  const filteredPairs = pairs.data?.filter((item) => item.symbol.toLowerCase().includes(pairSearch.trim().toLowerCase()))
  const normalizedNewPair = normalizePairInput(newPair)
  const newPairIsValid = normalizedNewPair === "" || isPairInputValid(normalizedNewPair)

  function showToast(tone: "success" | "danger", message: string) {
    setToast({ tone, message })
    setTimeout(() => setToast(null), 3500)
  }

  return (
    <>
      <PageHeader title="Settings" description="Runtime monitoring configuration. Changes are applied without restarting the backend." actions={<Button onClick={() => save.mutate(form)} disabled={save.isPending}>{save.isPending ? "Saving..." : "Save settings"}</Button>} />
      {toast && <div role="status" className={`fixed right-5 top-20 z-30 rounded-md border bg-terminal-900 px-4 py-3 text-xs shadow-xl ${toast.tone === "success" ? "border-emerald-500/30 text-emerald-300" : "border-rose-500/30 text-rose-300"}`}>{toast.message}</div>}
      <div className="grid gap-4 xl:grid-cols-2">
        <SettingsCard title="Monitoring">
          <Field label="Default spread threshold %"><Input type="number" min="0" step="0.1" value={form.default_spread_threshold_percent} onChange={(e) => setForm({ ...form, default_spread_threshold_percent: Number(e.target.value) })} /></Field>
          <Field label="Update interval seconds"><Input type="number" min="1" value={form.update_interval_seconds} onChange={(e) => setForm({ ...form, update_interval_seconds: Number(e.target.value) })} /></Field>
          <Field label="Notification cooldown seconds"><Input type="number" min="0" value={form.notification_cooldown_seconds} onChange={(e) => setForm({ ...form, notification_cooldown_seconds: Number(e.target.value) })} /></Field>
        </SettingsCard>
        <SettingsCard title="Telegram notifications">
          <div className="flex items-center justify-between gap-4">
            <Badge tone={form.telegram_notifications_enabled ? "success" : "warning"}>
              {form.telegram_notifications_enabled ? "Alerts active" : "Alerts disabled"}
            </Badge>
            <Switch
              label="Enable Telegram alerts"
              checked={form.telegram_notifications_enabled}
              onChange={(enabled) => updateTelegramEnabled.mutate(enabled)}
            />
          </div>
          <div className="flex items-center justify-between gap-4 rounded-md border border-terminal-700 bg-terminal-950 p-3">
            <div>
              <p className="text-sm font-medium text-zinc-200">Opportunity alerts</p>
              <p className="mt-1 text-xs leading-5 text-zinc-500">Disable this to receive Telegram notifications only from My Trades.</p>
            </div>
            <Switch
              label="Enable opportunity alerts"
              checked={form.opportunity_notifications_enabled}
              onChange={(enabled) => updateOpportunityAlertsEnabled.mutate(enabled)}
            />
          </div>
          <Field label="Telegram chat ID"><Input value={form.telegram_chat_id} onChange={(e) => setForm({ ...form, telegram_chat_id: e.target.value })} placeholder="Configured in Stage 6" /></Field>
          <Button onClick={() => testTelegram.mutate()} disabled={testTelegram.isPending}>{testTelegram.isPending ? "Sending..." : "Send test notification"}</Button>
          <p className="text-xs leading-5 text-zinc-500">The alert switch is applied immediately. The bot token is loaded from the backend environment. No exchange private keys are required.</p>
        </SettingsCard>
        <SettingsCard title="Enabled exchanges">
          {exchanges.data?.map((item) => <ToggleRow key={item.id} label={item.name} checked={item.enabled} onChange={(enabled) => updateExchange.mutate({ id: item.id, enabled })} />)}
        </SettingsCard>
        <SettingsCard title="Tracked perpetual pairs">
          <form className="flex gap-2" onSubmit={(event) => { event.preventDefault(); if (newPairIsValid) createPair.mutate(normalizedNewPair) }}>
            <Input value={newPair} onChange={(event) => setNewPair(event.target.value)} placeholder="Add coin, e.g. SEI or TAO/USDT" required />
            <Button type="submit" disabled={createPair.isPending || !newPairIsValid || !normalizedNewPair}>{createPair.isPending ? "Adding..." : "Add pair"}</Button>
          </form>
          {!newPairIsValid && <p className="text-xs leading-5 text-rose-300">Use a coin ticker like SEI or a USDT pair like TAO/USDT. Letters and digits only, 2-20 chars.</p>}
          <p className="text-xs leading-5 text-zinc-500">Add any USDT perpetual symbol. Unsupported markets are skipped per exchange without stopping monitoring.</p>
          <Input value={pairSearch} onChange={(event) => setPairSearch(event.target.value)} placeholder="Search existing pairs, e.g. BTC or PEPE" />
          {filteredPairs?.length ? filteredPairs.map((item) => <PairRow key={item.id} label={item.symbol} checked={item.enabled} onToggle={(enabled) => updatePair.mutate({ id: item.id, enabled })} onDelete={() => { if (window.confirm(`Delete ${item.symbol} from monitoring?`)) deletePair.mutate(item.id) }} />) : <p className="py-3 text-center text-xs text-zinc-500">No matching pairs.</p>}
        </SettingsCard>
      </div>
    </>
  )
}

function SettingsCard({ title, children }: { title: string; children: React.ReactNode }) {
  return <Card><CardHeader><h2 className="text-sm font-semibold">{title}</h2></CardHeader><CardContent className="space-y-4">{children}</CardContent></Card>
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <label className="block"><span className="mb-2 block text-xs text-zinc-500">{label}</span>{children}</label>
}

function ToggleRow({ label, checked, onChange }: { label: string; checked: boolean; onChange: (checked: boolean) => void }) {
  return <div className="flex items-center justify-between gap-4 text-sm text-zinc-300"><span>{label}</span><Switch checked={checked} onChange={onChange} label={`Toggle ${label}`} /></div>
}

function PairRow({ label, checked, onToggle, onDelete }: { label: string; checked: boolean; onToggle: (checked: boolean) => void; onDelete: () => void }) {
  return (
    <div className="flex items-center justify-between gap-4 text-sm text-zinc-300">
      <span>{label}</span>
      <div className="flex items-center gap-3">
        <Switch checked={checked} onChange={onToggle} label={`Toggle ${label}`} />
        <Button onClick={onDelete} className="border-rose-500/30 text-rose-300 hover:bg-rose-500/10">Delete</Button>
      </div>
    </div>
  )
}

function normalizePairInput(value: string) {
  const symbol = value.trim().toUpperCase()
  return symbol && !symbol.includes("/") ? `${symbol}/USDT` : symbol
}

function isPairInputValid(symbol: string) {
  const parts = symbol.split("/")
  if (parts.length !== 2) return false
  const [baseAsset, quoteAsset] = parts
  return /^[A-Z0-9]{2,20}$/.test(baseAsset ?? "") && quoteAsset === "USDT"
}
