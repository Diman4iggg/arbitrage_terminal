# Arbitrage Terminal

**Arbitrage Terminal** — production-oriented MVP веб-приложения для мониторинга арбитражных возможностей на perpetual futures / swap markets.

Приложение получает публичные рыночные данные с криптобирж, нормализует цены perpetual markets, считает spread между биржами, показывает данные в dark-mode торговом интерфейсе и отправляет Telegram-уведомления.

Проект **не выполняет торговые операции**:

- не выставляет ордера;
- не использует приватные API-ключи бирж;
- не реализует автотрейдинг;
- не хранит торговые ключи пользователя.

Это read-only терминал для мониторинга рынка.

## Возможности

- Мониторинг perpetual futures / swap markets.
- Поддержка CEX и perp-DEX источников.
- Модульная архитектура exchange adapters.
- Расчёт price spread между биржами.
- Funding context в таблице opportunities.
- Dashboard со статусом мониторинга.
- Таблица arbitrage opportunities с фильтрами.
- Страница Exchanges со статусами бирж.
- Страница Settings:
  - включение и выключение бирж;
  - включение и выключение пар;
  - поиск по уже добавленным парам;
  - ручное добавление новых USDT perpetual пар;
  - настройка threshold;
  - настройка Telegram;
  - настройка cooldown уведомлений.
- Страница Charts:
  - график цены выбранной пары по биржам;
  - график spread во времени;
  - top spreads за период.
- Страница My Trades:
  - ручное создание наблюдаемой позиции;
  - выбор монеты и двух бирж;
  - ввод long entry price;
  - ввод short entry price;
  - ввод размера позиции в монетах;
  - отображение entry spread, включая отрицательный;
  - отображение live spread;
  - отображение funding spread;
  - отображение live PnL;
  - график spread по сделке;
  - редактирование thresholds и размера позиции;
  - Telegram-уведомления по пользовательским порогам.
- Telegram Bot API уведомления с cooldown защитой от спама.
- PostgreSQL persistence.
- Alembic migrations.
- APScheduler background monitoring.
- Graceful degradation: если одна биржа или пара недоступна, остальные продолжают работать.
- Pytest-тесты для ключевой бизнес-логики.
- Docker Compose запуск.

## Поддерживаемые биржи

На текущем этапе добавлены:

| Биржа | Тип | Источник данных |
| --- | --- | --- |
| Binance USD-M Futures | CEX | `ccxt` |
| Bybit USDT Perpetuals | CEX | `ccxt` |
| MEXC USDT Perpetuals | CEX | `ccxt` |
| Hyperliquid | perp-DEX | официальный публичный API |
| Aster | perp-DEX | `ccxt` |
| Variational Omni | perp-DEX | официальный публичный API |
| BingX | CEX | `ccxt` |
| Bitget | CEX | `ccxt` |
| OKX | CEX | `ccxt` |
| Gate.io | CEX | `ccxt` |

Некоторые пары поддерживаются не на всех биржах. Например, `TON/USDT` может отсутствовать на MEXC и BingX. Это нормальное поведение: приложение логирует warning, показывает статус и продолжает мониторинг остальных рынков.

## Торговые пары

Базовый включённый список:

```text
BTC/USDT
ETH/USDT
SOL/USDT
BNB/USDT
XRP/USDT
DOGE/USDT
TON/USDT
```

Также в базе есть дополнительные пары, выключенные по умолчанию:

```text
ADA/USDT
AVAX/USDT
LINK/USDT
DOT/USDT
LTC/USDT
BCH/USDT
TRX/USDT
SUI/USDT
APT/USDT
ARB/USDT
OP/USDT
NEAR/USDT
FIL/USDT
PEPE/USDT
WIF/USDT
```

Через Settings можно добавить почти любую USDT perpetual пару вручную. Например:

```text
SEI
TAO
1000PEPE
```

Ввод `SEI` будет нормализован в `SEI/USDT`.

Важно: добавление пары в терминал не означает, что она есть на всех биржах. Если конкретная биржа не поддерживает пару, она будет пропущена только для этой биржи.

## Архитектура

```text
coursework/
  backend/
    app/
      api/routes/          # REST endpoints FastAPI
      core/                # config, logging, scheduler
      db/                  # SQLAlchemy models и Alembic migrations
      exchanges/           # exchange adapters и registry
      notifications/       # Telegram sender
      schemas/             # Pydantic schemas
      services/            # market data, arbitrage, settings, persistence
      strategies/          # strategy interface и price spread strategy
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
    package.json

  docker-compose.yml
  docker-compose.prod.yml
  .env.example
  README.md
```

Основной pipeline мониторинга:

```text
APScheduler
  -> enabled exchanges + enabled pairs
  -> exchange adapters
  -> normalized tickers
  -> PriceSpreadStrategy
  -> funding enrichment
  -> PostgreSQL persistence
  -> Telegram cooldown check
  -> frontend REST API
```

## Стек

Backend:

- Python 3.12+
- FastAPI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL
- Pydantic Settings
- APScheduler
- ccxt
- httpx
- pytest

Frontend:

- React
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query
- Recharts
- Axios

Infrastructure:

- Docker
- Docker Compose
- PostgreSQL container

## Быстрый запуск

Требования:

- Docker Desktop на Windows или Docker Engine + Docker Compose plugin на Linux.

Создать `.env`:

```powershell
Copy-Item .env.example .env
```

На Linux/macOS:

```bash
cp .env.example .env
```

Запустить проект:

```bash
docker compose up --build
```

Открыть:

- Frontend: [http://localhost:5173](http://localhost:5173)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health endpoint: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- OpenAPI JSON: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

Остановить:

```bash
docker compose down
```

Данные PostgreSQL сохраняются в Docker volume `postgres_data`.

## Переменные окружения

Файл `.env.example` нужно скопировать в `.env`. Сам `.env` нельзя коммитить.

| Переменная | Значение по умолчанию | Описание |
| --- | --- | --- |
| `APP_NAME` | `Arbitrage Terminal API` | Название backend-приложения |
| `APP_ENV` | `development` | Окружение |
| `APP_DEBUG` | `true` | Debug mode |
| `API_PREFIX` | `/api` | Префикс REST API |
| `DATABASE_URL` | Compose PostgreSQL | Async SQLAlchemy URL |
| `CORS_ORIGINS` | `http://localhost:5173` | Разрешённые frontend origins |
| `VITE_API_URL` | `http://localhost:8000/api` | Backend URL для frontend |
| `MARKET_TYPE` | `perpetual` | Market type MVP |
| `SCHEDULER_ENABLED` | `true` | Включить background monitoring |
| `MONITORING_INTERVAL_SECONDS` | `10` | Интервал scheduler cycle |
| `PERSIST_PRICE_SNAPSHOTS` | `true` | Сохранять snapshots для графиков |
| `PRICE_SNAPSHOT_RETENTION_HOURS` | `24` | Retention истории |
| `DEFAULT_SPREAD_THRESHOLD_PERCENT` | `0.5` | Глобальный порог opportunities |
| `NOTIFICATION_COOLDOWN_SECONDS` | `300` | Cooldown одинаковых Telegram-уведомлений |
| `TELEGRAM_NOTIFICATIONS_ENABLED` | `false` | Включены ли Telegram alerts по умолчанию |
| `TELEGRAM_BOT_TOKEN` | пусто | Токен Telegram bot |
| `TELEGRAM_CHAT_ID` | пусто | Chat ID получателя |

Часть настроек можно менять в UI на странице Settings без перезапуска backend:

- spread threshold;
- update interval;
- notification cooldown;
- enabled exchanges;
- enabled pairs;
- Telegram chat ID;
- Telegram notifications enabled/disabled.

Bot token остаётся только в `.env`.

## Telegram

1. Открыть [@BotFather](https://t.me/BotFather).
2. Выполнить `/newbot`.
3. Создать бота и скопировать токен.
4. Открыть созданного бота и отправить ему любое сообщение.
5. Открыть URL:

```text
https://api.telegram.org/botYOUR_TOKEN/getUpdates
```

6. Найти `message.chat.id`.
7. Записать значения в `.env`:

```env
TELEGRAM_BOT_TOKEN=replace_with_bot_token
TELEGRAM_CHAT_ID=replace_with_chat_id
```

8. Перезапустить backend:

```bash
docker compose restart backend
```

9. В Settings нажать `Send test notification`.
10. Включить Telegram alerts.

Если токен попал в скриншот, историю браузера или публичный репозиторий, его нужно перевыпустить через BotFather.

## Notification cooldown

`Notification cooldown seconds` защищает от спама одинаковыми уведомлениями.

Например, если cooldown равен `300`, то одинаковое уведомление по одной паре и одной связке бирж не будет отправляться чаще одного раза в 5 минут.

Cooldown применяется к:

- обычным arbitrage opportunities;
- price alerts в My Trades;
- funding alerts в My Trades.

Если поставить `0`, уведомления могут приходить почти каждый scheduler cycle.

## REST API

| Method | Endpoint | Описание |
| --- | --- | --- |
| `GET` | `/api/health` | Health check приложения и БД |
| `GET` | `/api/dashboard` | Метрики dashboard |
| `GET` | `/api/exchanges` | Список бирж со статусом |
| `PATCH` | `/api/exchanges/{exchange_id}` | Включить или выключить биржу |
| `GET` | `/api/pairs` | Список торговых пар |
| `POST` | `/api/pairs` | Добавить новую USDT perpetual пару |
| `PATCH` | `/api/pairs/{pair_id}` | Включить или выключить пару |
| `GET` | `/api/opportunities` | Таблица текущих opportunities |
| `GET` | `/api/settings` | Runtime settings |
| `PATCH` | `/api/settings` | Обновить runtime settings |
| `GET` | `/api/charts/prices` | История цены по биржам |
| `GET` | `/api/charts/spreads` | История spread |
| `GET` | `/api/charts/top-spreads` | Top spreads |
| `GET` | `/api/trade-watches` | Список My Trades |
| `POST` | `/api/trade-watches` | Создать наблюдаемую сделку |
| `PATCH` | `/api/trade-watches/{id}` | Обновить сделку |
| `DELETE` | `/api/trade-watches/{id}` | Удалить сделку |
| `GET` | `/api/trade-watches/{id}/spread-history` | График spread по сделке |
| `POST` | `/api/notifications/test-telegram` | Тестовое Telegram-сообщение |

Swagger доступен по адресу:

[http://localhost:8000/docs](http://localhost:8000/docs)

## My Trades

Страница My Trades предназначена для ручного отслеживания позиции, которую пользователь открыл самостоятельно на биржах.

При создании указывается:

- монета;
- биржа long / buy;
- биржа short / sell;
- long entry price;
- short entry price;
- размер позиции в монетах;
- price alert threshold;
- funding alert threshold.

Приложение показывает:

- текущую цену buy-ноги;
- текущую цену sell-ноги;
- entry spread;
- текущий price spread;
- funding обеих ног;
- funding spread;
- live PnL;
- график spread за последние 30 минут.

Формула entry spread:

```text
((short_entry_price - long_entry_price) / long_entry_price) * 100
```

Entry spread может быть отрицательным. В UI:

- положительный spread отображается зелёным;
- отрицательный spread отображается красным.

Формула PnL:

```text
((current_buy - entry_buy) + (entry_sell - current_sell)) * position_size_coins
```

Комиссии, slippage и фактически начисленный funding пока не учитываются.

## Opportunities

Opportunities считаются по простой MVP-формуле:

```text
spread_percent = ((sell_price - buy_price) / buy_price) * 100
```

Где:

- `buy_price` — минимальный `last_price` среди бирж;
- `sell_price` — максимальный `last_price` среди бирж.

В таблице также отображается funding context:

- buy funding;
- sell funding;
- funding delta.

Funding нужен, чтобы лучше понимать, стоит ли рассматривать конкретный spread. Например, хороший price spread может быть съеден неблагоприятным funding.

## Миграции БД

Применить миграции:

```bash
docker compose exec backend alembic upgrade head
```

Проверить текущую ревизию:

```bash
docker compose exec backend alembic current
```

Создать новую миграцию после изменения моделей:

```bash
docker compose exec backend alembic revision --autogenerate -m "describe change"
```

## Тесты

Backend tests используют изолированную SQLite БД и не обращаются к реальным биржам.

Запуск:

```bash
docker compose exec backend pytest
```

Проверка компиляции backend:

```bash
docker compose exec backend python -m compileall app
```

Сборка frontend:

```bash
docker compose exec frontend npm run build
```

## Как добавить новую биржу

1. Создать adapter в `backend/app/exchanges/`.
2. Реализовать общий интерфейс `ExchangeAdapter`:

```python
async def get_ticker(self, symbol: str) -> Ticker: ...
async def get_markets(self) -> list[Market]: ...
async def get_funding_rate(self, symbol: str) -> FundingRate | None: ...
```

3. Нормализовать символы к виду `BASE/USDT`.
4. Для CEX по возможности использовать `ccxt` с `enableRateLimit`.
5. Для perp-DEX использовать официальный публичный API.
6. Зарегистрировать adapter в `backend/app/exchanges/registry.py`.
7. Добавить биржу в БД через Alembic migration.
8. Добавить тест.

## Как добавить новую стратегию

1. Создать класс в `backend/app/strategies/`.
2. Реализовать интерфейс `Strategy`.
3. Использовать нормализованные данные, а не raw payload биржи.
4. Возвращать `Opportunity`.
5. Подключить стратегию в service layer.
6. Добавить тесты бизнес-логики.

В будущем можно добавить:

- `FundingRateStrategy`;
- `SpotPerpSpreadStrategy`;
- `DexCexSpreadStrategy`;
- `TriangularArbitrageStrategy`.

## Deployment

Для VPS можно использовать `docker-compose.prod.yml`.

Пример:

```bash
cp .env.example .env
# Заполнить POSTGRES_PASSWORD, DATABASE_URL, CORS_ORIGINS, VITE_API_URL, Telegram values
docker compose -f docker-compose.prod.yml up -d --build
```

Рекомендуемая схема:

```text
VPS
  -> Docker Compose
  -> PostgreSQL volume
  -> backend FastAPI
  -> frontend Nginx
  -> reverse proxy Caddy или Nginx
  -> HTTPS
```

Пример routing:

```text
https://terminal.example.com      -> frontend
https://terminal.example.com/api  -> backend:8000/api
https://terminal.example.com/docs -> backend:8000/docs
```

Production checklist:

- не коммитить `.env`;
- закрыть PostgreSQL от публичного доступа;
- включить HTTPS;
- настроить backup volume;
- следить за размером snapshots;
- хранить Telegram token как secret;
- проверять логи scheduler.

## Сценарий демонстрации для защиты

1. Запустить проект:

```bash
docker compose up --build
```

2. Открыть Dashboard.
3. Показать количество активных бирж и пар.
4. Открыть Exchanges и показать статусы бирж.
5. Открыть Settings:
   - найти пару через поиск;
   - включить или выключить пару;
   - добавить новую пару, например `SEI`.
6. Открыть Opportunities:
   - показать buy/sell exchanges;
   - показать spread;
   - показать funding обеих ног.
7. Открыть Charts:
   - показать price chart;
   - показать spread chart.
8. Открыть My Trades:
   - создать наблюдаемую сделку;
   - показать entry spread;
   - показать live spread;
   - показать funding spread;
   - показать PnL;
   - показать график spread.
9. Открыть Settings и отправить Telegram test notification.
10. Открыть Swagger.

## Ограничения MVP

Это намеренные ограничения первого релиза:

- opportunities считаются по `last_price`, а не по `ask/bid`;
- комиссии не учитываются;
- slippage не учитывается;
- order book depth не учитывается;
- ликвидность не оценивается;
- funding отображается как context, но funding arbitrage strategy ещё не реализована;
- WebSocket streams ещё не используются;
- массовое включение сотен пар может замедлять scheduler;
- часть пар не поддерживается на всех биржах;
- Omni использует USDC-based публичные цены, которые нормализуются для сравнения с `USDT` рынками приблизительно.

Следующие логичные улучшения:

- считать executable spread по `buy ask` и `sell bid`;
- добавить комиссии;
- добавить order book depth;
- добавить slippage;
- добавить PnL по ногам;
- добавить закрытые сделки;
- добавить WebSocket или bulk-fetch оптимизацию.

## Статус проекта

Проект готов как MVP для курсовой работы:

- запускается через Docker Compose;
- backend работает на FastAPI;
- frontend работает на React + TypeScript;
- PostgreSQL подключён;
- Swagger доступен;
- реальные биржи подключены;
- perpetual markets мониторятся;
- opportunities считаются;
- Telegram test notification работает;
- My Trades реализован;
- графики реализованы;
- тесты добавлены;
- автотрейдинг отсутствует.
