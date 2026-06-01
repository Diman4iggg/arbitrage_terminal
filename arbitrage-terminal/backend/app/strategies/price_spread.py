from collections import defaultdict
from decimal import Decimal

from app.db.models import OpportunityStatus
from app.schemas.opportunity import Opportunity
from app.schemas.ticker import Ticker
from app.strategies.base import Strategy


class PriceSpreadStrategy(Strategy):
    name = "price_spread"

    async def find_opportunities(
        self,
        tickers: list[Ticker],
        default_threshold_percent: Decimal,
        threshold_per_pair: dict[str, Decimal] | None = None,
    ) -> list[Opportunity]:
        grouped_tickers: dict[str, list[Ticker]] = defaultdict(list)
        for ticker in tickers:
            grouped_tickers[ticker.symbol].append(ticker)

        opportunities: list[Opportunity] = []
        pair_thresholds = threshold_per_pair or {}
        for symbol, symbol_tickers in grouped_tickers.items():
            opportunity = self.calculate_opportunity(symbol_tickers)
            threshold = pair_thresholds.get(symbol, default_threshold_percent)
            if opportunity is not None and opportunity.spread_percent >= threshold:
                opportunities.append(opportunity)

        return sorted(opportunities, key=lambda item: item.spread_percent, reverse=True)

    @staticmethod
    def calculate_opportunity(tickers: list[Ticker]) -> Opportunity | None:
        if len(tickers) < 2:
            return None

        buy_ticker = min(tickers, key=lambda ticker: ticker.last_price)
        sell_ticker = max(tickers, key=lambda ticker: ticker.last_price)
        if buy_ticker.exchange == sell_ticker.exchange or buy_ticker.last_price <= 0:
            return None

        spread_percent = (
            (sell_ticker.last_price - buy_ticker.last_price) / buy_ticker.last_price
        ) * Decimal("100")
        return Opportunity(
            symbol=buy_ticker.symbol,
            market_type=buy_ticker.market_type,
            buy_exchange=buy_ticker.exchange,
            sell_exchange=sell_ticker.exchange,
            buy_price=buy_ticker.last_price,
            sell_price=sell_ticker.last_price,
            spread_percent=spread_percent,
            detected_at=max(ticker.timestamp for ticker in tickers),
            status=OpportunityStatus.ACTIVE,
        )

