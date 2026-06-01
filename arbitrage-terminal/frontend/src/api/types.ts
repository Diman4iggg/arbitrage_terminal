export type ExchangeHealth = "unknown" | "online" | "offline" | "error"
export type OpportunityStatus = "active" | "expired"

export interface MonitoringStatus {
  scheduler_enabled: boolean
  scheduler_running: boolean
  cycle_running: boolean
  last_started_at: string | null
  last_completed_at: string | null
  last_error: string | null
  cycle_errors: Record<string, string>
}

export interface Opportunity {
  id: number
  symbol: string
  market_type: string
  buy_exchange: string
  sell_exchange: string
  buy_price: string
  sell_price: string
  spread_percent: string
  detected_at: string
  status: OpportunityStatus
}

export interface DashboardData {
  active_exchanges: number
  tracked_pairs: number
  current_opportunities: number
  max_spread_percent: string | null
  monitoring: MonitoringStatus
  recent_opportunities: Opportunity[]
}

export interface Exchange {
  id: number
  name: string
  slug: string
  exchange_type: "cex" | "perp_dex"
  enabled: boolean
  status: ExchangeHealth
  last_success_at: string | null
  last_error_at: string | null
  last_error_message: string | null
}

export interface TradingPair {
  id: number
  symbol: string
  base_asset: string
  quote_asset: string
  market_type: string
  enabled: boolean
}

export interface RuntimeSettings {
  default_spread_threshold_percent: number
  threshold_per_pair: Record<string, number>
  update_interval_seconds: number
  telegram_notifications_enabled: boolean
  telegram_chat_id: string
  notification_cooldown_seconds: number
}

export interface PricePoint {
  exchange: string
  timestamp: string
  bid_price: string | null
  ask_price: string | null
  last_price: string
}

export interface SpreadPoint {
  timestamp: string
  buy_exchange: string
  sell_exchange: string
  buy_price: string
  sell_price: string
  spread_percent: string
}

export interface PriceChart {
  symbol: string
  points: PricePoint[]
}

export interface SpreadChart {
  symbol: string
  points: SpreadPoint[]
}

export interface TopSpread {
  symbol: string
  buy_exchange: string
  sell_exchange: string
  spread_percent: string
  detected_at: string
}

export interface NotificationTestResult {
  delivered: boolean
  message: string
}
