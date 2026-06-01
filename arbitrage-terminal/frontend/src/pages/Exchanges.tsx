import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { AlertTriangle, CheckCircle2, Server } from "lucide-react"

import { terminalApi } from "../api/client"
import type { ExchangeHealth } from "../api/types"
import { PageHeader } from "../components/PageHeader"
import { Badge, Card, CardContent, Skeleton, Switch } from "../components/ui"
import { formatDate } from "../lib/format"

export function Exchanges() {
  const queryClient = useQueryClient()
  const exchanges = useQuery({ queryKey: ["exchanges"], queryFn: terminalApi.getExchanges })
  const update = useMutation({
    mutationFn: ({ id, enabled }: { id: number; enabled: boolean }) => terminalApi.updateExchange(id, enabled),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["exchanges"] }),
  })

  return (
    <>
      <PageHeader title="Exchanges" description="Public perpetual market data connections and their latest health state." />
      <div className="grid gap-3 lg:grid-cols-2">
        {exchanges.isLoading && Array.from({ length: 4 }).map((_, index) => <Skeleton key={index} className="h-48" />)}
        {exchanges.data?.map((exchange) => (
          <Card key={exchange.id}>
            <CardContent>
              <div className="flex items-start justify-between gap-4">
                <div className="flex gap-3">
                  <div className="rounded-md border border-terminal-700 bg-terminal-800 p-2.5"><Server className="h-4 w-4 text-emerald-400" /></div>
                  <div>
                    <h2 className="text-sm font-semibold">{exchange.name}</h2>
                    <p className="mt-1 text-xs uppercase tracking-wider text-zinc-500">{exchange.exchange_type}</p>
                  </div>
                </div>
                <Switch label={`Enable ${exchange.name}`} checked={exchange.enabled} onChange={(enabled) => update.mutate({ id: exchange.id, enabled })} />
              </div>
              <div className="mt-5 grid gap-3 text-xs sm:grid-cols-2">
                <div><p className="text-zinc-500">Connection</p><div className="mt-1"><HealthBadge status={exchange.status} /></div></div>
                <div><p className="text-zinc-500">Last successful update</p><p className="mt-1 text-zinc-300">{formatDate(exchange.last_success_at)}</p></div>
              </div>
              {exchange.last_error_message && <div className="mt-4 flex gap-2 rounded-md border border-amber-500/20 bg-amber-500/5 p-3 text-[11px] leading-4 text-amber-200"><AlertTriangle className="h-3.5 w-3.5 shrink-0" />{exchange.last_error_message}</div>}
            </CardContent>
          </Card>
        ))}
      </div>
    </>
  )
}

function HealthBadge({ status }: { status: ExchangeHealth }) {
  const tone = status === "online" ? "success" : status === "unknown" ? "neutral" : "danger"
  return <Badge tone={tone}><CheckCircle2 className="mr-1 h-3 w-3" />{status}</Badge>
}
