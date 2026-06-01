# Arbitrage Terminal

Production-oriented MVP foundation for monitoring cross-exchange perpetual futures arbitrage.

The first release is intentionally read-only: it collects public market data, calculates price
spreads, displays opportunities, and sends Telegram notifications. It does not place orders, use
private exchange API keys, or perform automated trading.

## Stage 2 Status

This repository currently contains the Stage 1 foundation and Stage 2 backend core:

- FastAPI backend skeleton with async SQLAlchemy PostgreSQL connection.
- `GET /api/health` endpoint with database availability status.
- SQLAlchemy models and an initial Alembic migration for exchanges, pairs, settings, opportunities,
  notifications, exchange statuses, and price snapshots.
- Seed data for Binance, Bybit, MEXC, Hyperliquid, and the seven default perpetual pairs.
- Exchange adapter interface with ccxt-based CEX adapters and a public HTTP Hyperliquid adapter.
- Normalized perpetual market ticker, market, and funding-rate schemas.
- Market data service with graceful degradation when an exchange or pair is unavailable.
- Extensible strategy interface with the MVP `PriceSpreadStrategy`.
- Runtime settings service backed by PostgreSQL with environment defaults.
- React, TypeScript, Vite, and Tailwind CSS frontend skeleton.
- Dockerfiles for backend and frontend development/production builds.
- Docker Compose services for `postgres`, `backend`, and `frontend`.
- Environment variable template for database, monitoring, and Telegram configuration.

Scheduler jobs, API resources, full terminal pages, Telegram sending, and tests are implemented in
the following stages.

## Repository Layout

```text
arbitrage-terminal/
  backend/
    app/
      api/
      core/
      db/
      exchanges/
      notifications/
      schemas/
      services/
      strategies/
      main.py
    tests/
    alembic.ini
    Dockerfile
    requirements.txt
  frontend/
    src/
      api/
      components/
      pages/
      App.tsx
      main.tsx
    Dockerfile
    package.json
  .env.example
  docker-compose.yml
```

## Local Start

Requirements:

- Docker Engine with Docker Compose.

Create the local environment file:

```bash
cp .env.example .env
```

On PowerShell:

```powershell
Copy-Item .env.example .env
```

Update `POSTGRES_PASSWORD` and `DATABASE_URL` together if you change the default password.

Start the development stack:

```bash
docker compose up --build
```

Open:

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend health: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- OpenAPI JSON: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Database Migrations

The Alembic environment and initial monitoring schema migration are available.

Apply available migrations from the running backend container:

```bash
docker compose exec backend alembic upgrade head
```

Create a migration after model changes:

```bash
docker compose exec backend alembic revision --autogenerate -m "describe change"
```

## Telegram Configuration

Telegram sending is implemented in Stage 6. The required environment variables are already reserved:

```env
TELEGRAM_NOTIFICATIONS_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
NOTIFICATION_COOLDOWN_SECONDS=300
```

Only a bot token and destination chat ID are needed. Exchange private API keys are not part of this
project.

## Planned Extension Points

### Add an exchange

A new exchange should be added as an adapter inside `backend/app/exchanges/`, then registered in
`backend/app/exchanges/registry.py`. Data retrieval and symbol normalization remain isolated from
opportunity calculations.

### Add a strategy

Future strategies should implement the strategy interface in `backend/app/strategies/` and consume
normalized market data rather than exchange-specific payloads.

## Deployment

The intended first deployment target is a VPS with Docker Compose:

1. Provision a Linux VPS and install Docker Engine with the Compose plugin.
2. Copy the repository and create a production `.env` file outside version control.
3. Use a strong PostgreSQL password and keep the PostgreSQL volume persistent.
4. Build the frontend production image from the `production` Dockerfile target.
5. Run the backend without `--reload`.
6. Put Nginx or Caddy in front of the frontend and backend for TLS termination and routing.
7. Back up the PostgreSQL volume and review container logs regularly.

A production Compose override and reverse proxy configuration can be added after the MVP feature
stages are complete.
