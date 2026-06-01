import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"

import { terminalApi } from "../api/client"
import type { RuntimeSettings } from "../api/types"
import { PageHeader } from "../components/PageHeader"
import { Button, Card, CardContent, CardHeader, Input, Skeleton, Switch } from "../components/ui"

export function Settings() {
  const queryClient = useQueryClient()
  const settings = useQuery({ queryKey: ["settings"], queryFn: terminalApi.getSettings })
  const pairs = useQuery({ queryKey: ["pairs"], queryFn: terminalApi.getPairs })
  const exchanges = useQuery({ queryKey: ["exchanges"], queryFn: terminalApi.getExchanges })
  const [form, setForm] = useState<RuntimeSettings | null>(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => { if (settings.data) setForm(settings.data) }, [settings.data])

  const save = useMutation({
    mutationFn: terminalApi.updateSettings,
    onSuccess: (data) => {
      setForm(data)
      setSaved(true)
      setTimeout(() => setSaved(false), 2500)
      queryClient.invalidateQueries({ queryKey: ["settings"] })
    },
  })
  const updatePair = useMutation({ mutationFn: ({ id, enabled }: { id: number; enabled: boolean }) => terminalApi.updatePair(id, enabled), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pairs"] }) })
  const updateExchange = useMutation({ mutationFn: ({ id, enabled }: { id: number; enabled: boolean }) => terminalApi.updateExchange(id, enabled), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["exchanges"] }) })

  if (!form || settings.isLoading) return <Skeleton className="h-96" />

  return (
    <>
      <PageHeader title="Settings" description="Runtime monitoring configuration. Changes are applied without restarting the backend." actions={<Button onClick={() => save.mutate(form)} disabled={save.isPending}>{save.isPending ? "Saving..." : "Save settings"}</Button>} />
      {saved && <div role="status" className="fixed right-5 top-20 z-30 rounded-md border border-emerald-500/30 bg-terminal-900 px-4 py-3 text-xs text-emerald-300 shadow-xl">Settings saved successfully.</div>}
      <div className="grid gap-4 xl:grid-cols-2">
        <SettingsCard title="Monitoring">
          <Field label="Default spread threshold %"><Input type="number" min="0" step="0.1" value={form.default_spread_threshold_percent} onChange={(e) => setForm({ ...form, default_spread_threshold_percent: Number(e.target.value) })} /></Field>
          <Field label="Update interval seconds"><Input type="number" min="1" value={form.update_interval_seconds} onChange={(e) => setForm({ ...form, update_interval_seconds: Number(e.target.value) })} /></Field>
          <Field label="Notification cooldown seconds"><Input type="number" min="0" value={form.notification_cooldown_seconds} onChange={(e) => setForm({ ...form, notification_cooldown_seconds: Number(e.target.value) })} /></Field>
        </SettingsCard>
        <SettingsCard title="Telegram notifications">
          <ToggleRow label="Enable Telegram alerts" checked={form.telegram_notifications_enabled} onChange={(value) => setForm({ ...form, telegram_notifications_enabled: value })} />
          <Field label="Telegram chat ID"><Input value={form.telegram_chat_id} onChange={(e) => setForm({ ...form, telegram_chat_id: e.target.value })} placeholder="Configured in Stage 6" /></Field>
          <p className="text-xs leading-5 text-zinc-500">Telegram delivery and the test button are connected in Stage 6. No exchange private keys are required.</p>
        </SettingsCard>
        <SettingsCard title="Enabled exchanges">
          {exchanges.data?.map((item) => <ToggleRow key={item.id} label={item.name} checked={item.enabled} onChange={(enabled) => updateExchange.mutate({ id: item.id, enabled })} />)}
        </SettingsCard>
        <SettingsCard title="Tracked perpetual pairs">
          {pairs.data?.map((item) => <ToggleRow key={item.id} label={item.symbol} checked={item.enabled} onChange={(enabled) => updatePair.mutate({ id: item.id, enabled })} />)}
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
