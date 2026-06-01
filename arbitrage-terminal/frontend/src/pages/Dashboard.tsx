import { useQuery } from "@tanstack/react-query"
import { Activity, AlertTriangle, RadioTower, TrendingUp, WalletCards } from "lucide-react"

import { terminalApi } from "../api/client"
import { OpportunityTable } from "../components/OpportunityTable"
import { PageHeader } from "../components/PageHeader"
import { Badge, Card, CardContent, CardHeader, Skeleton } from "../components/ui"
import { formatDate, formatSpread } from "../lib/format"

export function Dashboard() {
  const dashboard = useQuery({ queryKey: ["dashboard"], queryFn: terminalApi.getDashboard })

  if (dashboard.isLoading) return <DashboardSkeleton />
  if (dashboard.isError || !dashboard.data) return <ErrorState />

  const data = dashboard.data
  const metrics = [
    { label: "Active exchanges", value: data.active_exchanges, icon: WalletCards },
    { label: "Tracked pairs", value: data.tracked_pairs, icon: RadioTower },
    { label: "Live opportunities", value: data.current_opportunities, icon: Activity },
    { label: "Maximum spread", value: formatSpread(data.max_spread_percent), icon: TrendingUp },
  ]
  const cycleErrors = Object.entries(data.monitoring.cycle_errors)

  return (
    <>
      <PageHeader title="Dashboard" description="Live perpetual futures arbitrage overview." />
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map(({ label, value, icon: Icon }) => (
          <Card key={label}>
            <CardContent className="flex items-center justify-between">
              <div>
                <p className="text-[11px] uppercase tracking-wider text-zinc-500">{label}</p>
                <p className="mt-2 text-2xl font-semibold text-zinc-100">{value}</p>
              </div>
              <Icon className="h-5 w-5 text-emerald-400" />
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-[1fr_320px]">
        <Card>
          <CardHeader>
            <h2 className="text-sm font-semibold">Recent opportunities</h2>
          </CardHeader>
          <OpportunityTable opportunities={data.recent_opportunities} />
        </Card>
        <Card>
          <CardHeader className="flex items-center justify-between">
            <h2 className="text-sm font-semibold">Monitoring status</h2>
            <Badge tone={data.monitoring.scheduler_running ? "success" : "danger"}>
              {data.monitoring.scheduler_running ? "Scheduler active" : "Scheduler offline"}
            </Badge>
          </CardHeader>
          <CardContent className="space-y-4 text-xs">
            <StatusLine label="Cycle state" value={data.monitoring.cycle_running ? "Fetching markets" : "Idle"} />
            <StatusLine label="Last completed" value={formatDate(data.monitoring.last_completed_at)} />
            <StatusLine label="Cycle warnings" value={String(cycleErrors.length)} />
            {cycleErrors.slice(0, 3).map(([key, value]) => (
              <div key={key} className="rounded-md border border-amber-500/20 bg-amber-500/5 p-3">
                <div className="flex gap-2 text-amber-300"><AlertTriangle className="h-3.5 w-3.5 shrink-0" />{key}</div>
                <p className="mt-1 break-words text-[11px] leading-4 text-zinc-500">{value}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </>
  )
}

function StatusLine({ label, value }: { label: string; value: string }) {
  return <div className="flex justify-between gap-4"><span className="text-zinc-500">{label}</span><span className="text-right text-zinc-300">{value}</span></div>
}

function DashboardSkeleton() {
  return <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">{Array.from({ length: 4 }).map((_, index) => <Skeleton key={index} className="h-24" />)}</div>
}

function ErrorState() {
  return <Card><CardContent className="py-12 text-center text-sm text-rose-300">Unable to load dashboard data. Check the backend connection.</CardContent></Card>
}
