import axios from "axios"

import type {
  DashboardData,
  Exchange,
  Opportunity,
  NotificationTestResult,
  PriceChart,
  RuntimeSettings,
  SpreadChart,
  TopSpread,
  TradeWatch,
  TradeWatchCreate,
  TradeWatchSpreadHistory,
  TradeWatchUpdate,
  TradingPair,
} from "./types"

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api",
  timeout: 10_000,
})

export const terminalApi = {
  getDashboard: async () => (await api.get<DashboardData>("/dashboard")).data,
  getExchanges: async () => (await api.get<Exchange[]>("/exchanges")).data,
  updateExchange: async (id: number, enabled: boolean) =>
    (await api.patch<Exchange>(`/exchanges/${id}`, { enabled })).data,
  getPairs: async () => (await api.get<TradingPair[]>("/pairs")).data,
  updatePair: async (id: number, enabled: boolean) =>
    (await api.patch<TradingPair>(`/pairs/${id}`, { enabled })).data,
  createPair: async (symbol: string) =>
    (await api.post<TradingPair>("/pairs", { symbol })).data,
  deletePair: async (id: number) => {
    await api.delete(`/pairs/${id}`)
  },
  getOpportunities: async (params?: Record<string, string | number>) =>
    (await api.get<Opportunity[]>("/opportunities", { params })).data,
  getSettings: async () => (await api.get<RuntimeSettings>("/settings")).data,
  updateSettings: async (settings: Partial<RuntimeSettings>) =>
    (await api.patch<RuntimeSettings>("/settings", settings)).data,
  getPrices: async (symbol: string, minutes = 30) =>
    (await api.get<PriceChart>("/charts/prices", { params: { symbol, minutes } })).data,
  getSpreads: async (symbol: string, minutes = 30) =>
    (await api.get<SpreadChart>("/charts/spreads", { params: { symbol, minutes } })).data,
  getTopSpreads: async (minutes = 30) =>
    (await api.get<TopSpread[]>("/charts/top-spreads", { params: { minutes } })).data,
  testTelegram: async () =>
    (await api.post<NotificationTestResult>("/notifications/test-telegram")).data,
  getTradeWatches: async () => (await api.get<TradeWatch[]>("/trade-watches")).data,
  createTradeWatch: async (payload: TradeWatchCreate) =>
    (await api.post<TradeWatch>("/trade-watches", payload)).data,
  updateTradeWatch: async (id: number, payload: TradeWatchUpdate) =>
    (await api.patch<TradeWatch>(`/trade-watches/${id}`, payload)).data,
  getTradeWatchSpreadHistory: async (id: number, minutes = 1440) =>
    (await api.get<TradeWatchSpreadHistory>(`/trade-watches/${id}/spread-history`, { params: { minutes } })).data,
  deleteTradeWatch: async (id: number) => {
    await api.delete(`/trade-watches/${id}`)
  },
}
