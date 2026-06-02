from decimal import Decimal

import httpx

from app.exchanges.variational_omni import VariationalOmniAdapter


async def test_variational_omni_adapter_normalizes_public_listing() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "listings": [
                    {
                        "ticker": "BTC",
                        "mark_price": "67000.5",
                        "funding_rate": "0.0001",
                        "quotes": {
                            "updated_at": "2026-06-03T10:00:00Z",
                            "size_1k": {"bid": "66999.5", "ask": "67001.5"},
                        },
                    }
                ]
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://omni.test",
    ) as client:
        adapter = VariationalOmniAdapter(client=client)
        ticker = await adapter.get_ticker("BTC/USDT")
        funding = await adapter.get_funding_rate("BTC/USDT")
        markets = await adapter.get_markets()

    assert ticker.last_price == Decimal("67000.5")
    assert ticker.bid_price == Decimal("66999.5")
    assert ticker.ask_price == Decimal("67001.5")
    assert funding is not None
    assert funding.rate == Decimal("0.0001")
    assert markets[0].symbol == "BTC/USDT"
