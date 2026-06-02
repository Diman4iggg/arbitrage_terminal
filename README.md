# Arbitrage Terminal

Production-oriented MVP for monitoring cross-exchange perpetual futures arbitrage.

The application collects public market prices, normalizes perpetual markets, detects price spreads,
stores recent history, renders a dark trading terminal UI, and sends Telegram notifications. It does
not place orders, use exchange private API keys, or perform automated trading.

## Features

- Perpetual futures monitoring for Binance USD-M, Bybit USDT, MEXC USDT, and Hyperliquid.
- Modular exchange adapter layer: async ccxt adapters for CEX exchanges and an httpx adapter for
  Hyperliquid.
- Extensible strategy layer with the MVP `PriceSpreadStrategy`.
- Configurable global threshold and per-pair thresholds.
- APScheduler monitoring cycle with graceful degradation when an exchange or pair is unavailable.
- Telegram Bot API notifications with cooldown protection.
- PostgreSQL persistence for exchanges, pairs, settings, opportunities, notification logs, exchange
  statuses, and price snapshots.
- Snapshot retention window for chart history.
- React terminal UI with Dashboard, Opportunities, Exchanges, Charts, and Settings pages.
- FastAPI Swagger documentation and pytest coverage for critical business logic.

## Supported Markets

The MVP monitors `market_type = perpetual` only:

```text
BTC/USDT
ETH/USDT
SOL/USDT
BNB/USDT
XRP/USDT
DOGE/USDT
TON/USDT
```

Pairs and exchanges can be enabled or disabled from Settings. Some exchanges do not expose every
pair. For example, MEXC may report `TON/USDT` as unsupported; the remaining markets continue to run.

## Architecture

```text
arbitrage-terminal/
  backend/
    app/
      api/routes/          # FastAPI REST endpoints
      core/                # config, logging, APScheduler lifecycle
      db/                  # SQLAlchemy models and Alembic migrations
      exchanges/           # exchange adapters and registry
      notifications/       # Telegram Bot API sender
      schemas/             # Pydantic domain and API schemas
      services/            # monitoring, persistence, settings, cooldown
      strategies/          # arbitrage strategy interface
      main.py
    tests/
    Dockerfile
    requirements.txt
  frontend/
    src/
      api/
      components/
      pages/
    Dockerfile
  docker-compose.yml       # local development
  docker-compose.prod.yml  # VPS deployment baseline
  .env.example
```

The monitoring flow is:

```text
APScheduler -> enabled exchanges and pairs -> normalized tickers
            -> PriceSpreadStrategy -> opportunities -> PostgreSQL
            -> cooldown check -> Telegram Bot API
```

## Quick Start

Requirements:

- Docker Desktop on Windows or Docker Engine with the Compose plugin on Linux.

Create the local environment file:

```powershell
Copy-Item .env.example .env
```

On Linux or macOS:

```bash
cp .env.example .env
```

Start the development stack:

```bash
docker compose up --build
```

Open:

- Frontend: [http://localhost:5173](http://localhost:5173)
- Health endpoint: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- OpenAPI JSON: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

Stop the stack:

```bash
docker compose down
```

PostgreSQL data remains in the `postgres_data` volume.

## Environment Variables

Copy `.env.example` to `.env`. Never commit `.env`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | local Compose PostgreSQL | SQLAlchemy async connection URL |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed frontend origins |
| `VITE_API_URL` | `http://localhost:8000/api` | Browser-visible backend API URL embedded in frontend build |
| `MARKET_TYPE` | `perpetual` | MVP market type |
| `SCHEDULER_ENABLED` | `true` | Enable periodic market monitoring |
| `MONITORING_INTERVAL_SECONDS` | `10` | Scheduler interval |
| `PERSIST_PRICE_SNAPSHOTS` | `true` | Store normalized chart snapshots |
| `PRICE_SNAPSHOT_RETENTION_HOURS` | `24` | Remove older snapshots |
| `DEFAULT_SPREAD_THRESHOLD_PERCENT` | `0.5` | Global opportunity threshold |
| `NOTIFICATION_COOLDOWN_SECONDS` | `300` | Suppress duplicate Telegram alerts |
| `TELEGRAM_NOTIFICATIONS_ENABLED` | `false` | Default notification state |
| `TELEGRAM_BOT_TOKEN` | empty | Telegram bot token from BotFather |
| `TELEGRAM_CHAT_ID` | empty | Destination user or group chat ID |

Runtime values such as threshold, interval, enabled exchanges, enabled pairs, Telegram state, and
chat ID can be changed in the Settings page. The bot token remains environment-only.

## Telegram Setup

1. Open the official [@BotFather](https://t.me/BotFather) account in Telegram.
2. Run `/newbot`, choose a name and a username ending in `bot`, then copy the token.
3. Open your new bot, press Start, and send a message.
4. Open `https://api.telegram.org/botYOUR_TOKEN/getUpdates`.
5. Read `result[].message.chat.id` from the JSON response.
6. Add the values to `.env`:

```env
TELEGRAM_BOT_TOKEN=replace_with_bot_token
TELEGRAM_CHAT_ID=replace_with_chat_id
```

Restart backend after editing `.env`:

```bash
docker compose restart backend
```

Open Settings and click `Send test notification`. Enable Telegram alerts and save settings when the
test succeeds.

Treat the bot token as a secret. If it appears in a screenshot, URL history shared with others, or
logs, revoke it through BotFather and issue a new token.

## Database Migrations

Apply migrations:

```bash
docker compose exec backend alembic upgrade head
```

Create a migration after model changes:

```bash
docker compose exec backend alembic revision --autogenerate -m "describe change"
```

Production Compose applies available migrations automatically before backend startup.

## REST API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Application and database health |
| `GET` | `/api/dashboard` | Terminal metrics and monitoring status |
| `GET` | `/api/exchanges` | Exchanges with health status |
| `PATCH` | `/api/exchanges/{exchange_id}` | Enable or disable an exchange |
| `GET` | `/api/pairs` | Trading pairs |
| `PATCH` | `/api/pairs/{pair_id}` | Enable or disable a pair |
| `GET` | `/api/opportunities` | Filtered current opportunities |
| `GET` | `/api/settings` | Runtime settings |
| `PATCH` | `/api/settings` | Update runtime settings |
| `GET` | `/api/charts/prices` | Price history by exchange |
| `GET` | `/api/charts/spreads` | Spread history |
| `GET` | `/api/charts/top-spreads` | Highest recorded spreads |
| `POST` | `/api/notifications/test-telegram` | Send a Telegram test message |

## Tests

The backend test suite uses an isolated async SQLite database. It does not modify the PostgreSQL
volume or call real exchange APIs.

Build backend after dependency changes and run tests:

```bash
docker compose build backend
docker compose run --rm -e SCHEDULER_ENABLED=false backend pytest -q
```

Build frontend:

```bash
docker compose exec frontend npm run build
```

## Add an Exchange

1. Implement `ExchangeAdapter` from `backend/app/exchanges/base.py`.
2. Return normalized `Ticker`, `Market`, and optional `FundingRate` schemas.
3. Keep exchange-specific symbol mapping inside the adapter.
4. Register the factory in `backend/app/exchanges/registry.py`.
5. Add seed data through an Alembic migration.
6. Add a mock-backed adapter test.

For ccxt exchanges, enable rate limiting and select linear perpetual swap markets. For perp DEX
exchanges, use their official public API and normalize payloads before strategy evaluation.

## Add a Strategy

1. Implement `Strategy` from `backend/app/strategies/base.py`.
2. Accept normalized market data rather than exchange-specific payloads.
3. Return `Opportunity` schemas.
4. Wire the strategy through the service layer.
5. Add focused business-logic tests.

Planned strategies include funding-rate arbitrage, spot-perp spread, DEX-CEX spread, and triangular
arbitrage.

## Deployment

The included `docker-compose.prod.yml` is a VPS baseline:

```bash
cp .env.example .env
# Set a strong POSTGRES_PASSWORD and update DATABASE_URL accordingly.
# Set production CORS_ORIGINS, VITE_API_URL, and Telegram values.
docker compose -f docker-compose.prod.yml up -d --build
```

Production services:

- PostgreSQL with a persistent `postgres_data` volume.
- FastAPI backend without `--reload`; migrations run before startup.
- Nginx frontend image serving the compiled Vite application.

Place Caddy or Nginx in front of the exposed ports for HTTPS and host routing. A typical routing plan
is:

```text
https://terminal.example.com      -> frontend:80
https://terminal.example.com/api  -> backend:8000/api
https://terminal.example.com/docs -> backend:8000/docs
```

Operational checklist:

- Store `.env` outside version control.
- Restrict PostgreSQL from public access.
- Back up the Docker volume.
- Enable TLS.
- Monitor disk usage because snapshots are persisted.
- Rotate Telegram bot tokens if exposed.
- Review logs regularly; HTTP library request URLs are suppressed to avoid credential leakage.

## MVP Scope

Implemented:

- Read-only perpetual monitoring.
- Spread detection by normalized `last_price`.
- Dashboard, tables, settings, charts, Telegram notifications, cooldown, tests, and Docker setup.

Intentionally excluded:

- Order placement and auto-trading.
- Private exchange API keys.
- Authentication and multi-user management.
- Order-book depth, liquidity, slippage, fees, and funding strategy execution.
