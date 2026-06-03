export type ExchangeHealth = "unknown" | "online" | "offline" | "error"
export type OpportunityStatus = "active" | "expired"
export type AlertCondition = "above" | "below"
export type TargetPriceSource = "buy" | "sell"

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
  buy_funding_rate_percent: string | null
  sell_funding_rate_percent: string | null
  funding_spread_percent: string | null
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
  opportunity_notifications_enabled: boolean
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

export interface TradeWatch {
  id: number
  symbol: string
  buy_exchange: string
  sell_exchange: string
  enabled: boolean
  notifications_enabled: boolean
  buy_entry_price: string | null
  sell_entry_price: string | null
  position_size_coins: string | null
  entry_spread_percent: string | null
  price_alert_threshold_percent: string | null
  price_alert_condition: AlertCondition
  funding_alert_threshold_percent: string | null
  funding_alert_condition: AlertCondition
  target_price_alert_value: string | null
  target_price_alert_condition: AlertCondition
  target_price_alert_source: TargetPriceSource
  buy_price: string | null
  sell_price: string | null
  price_spread_percent: string | null
  buy_funding_rate_percent: string | null
  sell_funding_rate_percent: string | null
  funding_spread_percent: string | null
  pnl_usdt: string | null
  pnl_percent: string | null
  last_updated_at: string | null
  last_error: string | null
  created_at: string
  updated_at: string
}

export interface TradeWatchCreate {
  symbol: string
  buy_exchange: string
  sell_exchange: string
  notifications_enabled: boolean
  buy_entry_price: number
  sell_entry_price: number
  position_size_coins: number
  price_alert_threshold_percent: number | null
  price_alert_condition: AlertCondition
  funding_alert_threshold_percent: number | null
  funding_alert_condition: AlertCondition
  target_price_alert_value: number | null
  target_price_alert_condition: AlertCondition
  target_price_alert_source: TargetPriceSource
}

export interface TradeWatchUpdate {
  buy_exchange?: string
  sell_exchange?: string
  enabled?: boolean
  notifications_enabled?: boolean
  buy_entry_price?: number
  sell_entry_price?: number
  position_size_coins?: number
  price_alert_threshold_percent?: number | null
  price_alert_condition?: AlertCondition
  funding_alert_threshold_percent?: number | null
  funding_alert_condition?: AlertCondition
  target_price_alert_value?: number | null
  target_price_alert_condition?: AlertCondition
  target_price_alert_source?: TargetPriceSource
}

export interface TradeWatchSpreadHistory {
  trade_watch_id: number
  symbol: string
  buy_exchange: string
  sell_exchange: string
  points: Array<{
    timestamp: string
    spread_percent: string
  }>
}
