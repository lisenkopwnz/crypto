# test-crypto

Тестовое задание на junior backend.

Клиент для биржи [Deribit](https://docs.deribit.com/) раз в минуту забирает index price `btc_usd` и `eth_usd` и сохраняет в PostgreSQL тикер, цену и время в UNIX timestamp. Сохранённые данные отдаются через API на FastAPI.

Стек: Python 3.12, FastAPI, SQLAlchemy 2 (async + asyncpg), Alembic, Celery (worker + beat), aiohttp, PostgreSQL, pytest, Docker Compose, uv.

## Запуск

Нужен Docker с Compose v2.

```bash
git clone <repo-url> test-crypto
cd test-crypto
cp .env.example .env
docker compose up -d --build
```

Файл `.env` можно не создавать, тогда возьмутся значения по умолчанию из `docker-compose.yml`.

Поднимаются два контейнера:

- `db` - PostgreSQL 17, данные лежат в volume `postgres_data`;
- `app` - приложение. При старте применяет миграции (`alembic upgrade head`), потом supervisord запускает три процесса: API (uvicorn), Celery worker и Celery beat.

После запуска:

- Swagger: http://localhost:8000/docs
- логи: `docker compose logs -f app`, там видно каждую сохранённую цену, например `Task collect_price[...] succeeded in 0.21s: 'btc_usd 83370.31 1791963985'`
- первая цена появляется примерно через минуту после старта:

```bash
curl "http://localhost:8000/api/v1/prices/latest?ticker=btc_usd"
```

Если порт 8000 или 5432 уже занят, поменяйте `APP_PORT` / `DB_PORT` в `.env`.

Остановить: `docker compose down`, вместе с данными: `docker compose down -v`.

## API

Все методы GET, у каждого обязательный query-параметр `ticker` (`btc_usd` или `eth_usd`). Если тикер не передан или неизвестен, вернётся 422.

| Запрос | Что возвращает |
|---|---|
| `GET /api/v1/prices?ticker=btc_usd` | все сохранённые данные по валюте, сначала новые |
| `GET /api/v1/prices/latest?ticker=btc_usd` | последнюю цену; 404, если цен ещё нет |
| `GET /api/v1/prices/by-date?ticker=btc_usd&date=2026-10-14` | цены за указанный день (сутки по UTC) |

Формат записи:

```json
{"ticker": "btc_usd", "price": 83370.31, "timestamp": 1791963985}
```

`timestamp` - UNIX-время в секундах, когда цена была получена с биржи.

## Настройки

Читаются из переменных окружения или `.env` (см. `.env.example`).

| Переменная | По умолчанию | |
|---|---|---|
| `POSTGRES_HOST` | `localhost` | в docker compose всегда `db` |
| `POSTGRES_PORT` | `5432` | |
| `POSTGRES_USER` | `crypto` | |
| `POSTGRES_PASSWORD` | - | обязательная |
| `POSTGRES_DB` | `crypto` | |
| `DERIBIT_BASE_URL` | `https://www.deribit.com/api/v2` | |
| `DERIBIT_TIMEOUT` | `10` | таймаут запроса к бирже, сек |
| `COLLECT_INTERVAL` | `60` | как часто забирать цены, сек |
| `APP_PORT` | `8000` | порт API на хосте (только compose) |
| `DB_PORT` | `5432` | порт базы на хосте (только compose) |

## Локальный запуск без Docker

```bash
uv sync
docker compose up -d db
uv run alembic upgrade head

uv run uvicorn app.main:create_app --factory --reload
uv run celery -A app.worker.main:celery_app worker --loglevel=INFO
uv run celery -A app.worker.main:celery_app beat --loglevel=INFO
```

На Windows воркер нужно запускать с `--pool=solo`.

## Тесты

```bash
uv run pytest
```

- `tests/unit` - API, сервисы, клиент Deribit (поднимается локальный aiohttp-сервер вместо биржи), задача Celery и расписание beat. Ничего внешнего не нужно.
- `tests/integration` - репозиторий и API на настоящем PostgreSQL. Запускаются, только если задана `TEST_DATABASE_URL`, иначе пропускаются. Каждый тест выполняется в транзакции, которая потом откатывается, так что в базе ничего не остаётся.

Запуск вместе с интеграционными:

```bash
docker compose up -d db
docker compose exec db createdb -U crypto crypto_test
TEST_DATABASE_URL=postgresql+asyncpg://crypto:crypto@localhost:5432/crypto_test uv run pytest
```

В `.gitlab-ci.yml` то же самое плюс `ruff check` и `alembic check` (что миграции совпадают с моделями).

## Структура

```
app/
  config.py           настройки (pydantic-settings)
  main.py             create_app() - сборка FastAPI
  domain/             Ticker, IndexPrice, интерфейсы PriceRepository и ExchangeClient
  services/           PriceService - чтение для API, PriceCollector - получить цену и сохранить
  db/                 Database (engine + сессии), ORM-модель, репозиторий
  clients/deribit.py  клиент Deribit на aiohttp
  api/                зависимости, схема ответа, роуты /api/v1/prices
  worker/             Celery: create_celery_app(), задача, расписание beat
migrations/           Alembic
docker/               конфиг supervisord
tests/
```

## Design decisions

**Слои.** `domain` не зависит ни от FastAPI, ни от SQLAlchemy, ни от aiohttp. Сервисы работают через интерфейсы `PriceRepository` и `ExchangeClient`, а конкретные реализации (`db`, `clients`) подставляются в точках входа (`api`, `worker`). Поэтому сервисы и API тестируются на моках без базы и сети, а поменять хранилище или биржу можно, не трогая логику.

**Без глобальных переменных.** Настройки, engine и сессии не создаются при импорте модулей. FastAPI собирается фабрикой `create_app()` (uvicorn запускается с `--factory`), объект `Database` хранится в `app.state` и закрывается в lifespan. Celery тоже собирается фабрикой `create_celery_app(settings)`. Единственный объект на уровне модуля - `celery_app` в `app/worker/main.py`: CLI Celery не умеет вызывать фабрики, ему нужен готовый экземпляр. Этот модуль импортирует только CLI.

**Асинхронность.** Эндпоинты асинхронные, поэтому и работа с базой асинхронная (SQLAlchemy + asyncpg): синхронный запрос внутри `async def` блокировал бы event loop. Клиент Deribit на aiohttp, как и просили в ТЗ. Задачи Celery синхронные, поэтому задача запускает корутину через `asyncio.run`. У каждого запуска свой event loop, а соединения asyncpg к нему привязаны, поэтому в воркере engine создаётся на задачу с `NullPool`.

**Сбор цен.** Beat раз в 60 секунд ставит отдельную задачу на каждый тикер, поэтому ошибка по одному тикеру не мешает сохранить второй. Если биржа не ответила или ответила ошибкой, задача повторяется до 3 раз с растущей задержкой (до 5, 10 и 20 секунд), то есть ещё в пределах той же минуты. У задач `expires` = 60 секунд: если воркер какое-то время лежал, после старта он не будет разгребать очередь устаревших задач. Результаты задач не нужны, поэтому result backend не настроен.

**Брокер Celery - тот же PostgreSQL.** По ТЗ контейнеров два: приложение и база. Без брокера Celery не работает, а поднимать ради него третий контейнер с Redis не хотелось, поэтому используется SQLAlchemy-транспорт kombu поверх той же базы (таблицы `kombu_queue` и `kombu_message` он создаёт сам). Для двух сообщений в минуту этого более чем достаточно. Минусы: в документации Celery этот транспорт помечен как экспериментальный, а обработанные сообщения остаются в `kombu_message` (около 3 тыс. строк в сутки). В нагруженном проекте брокер лучше вынести в Redis или RabbitMQ: меняется `broker_url` в `config.py` и добавляется сервис в compose.

**Несколько процессов в контейнере `app`.** API, worker и beat запускает supervisord: логи всех трёх идут в stdout контейнера, упавший процесс перезапускается. Миграции применяются до запуска supervisord, так что процессы стартуют уже с актуальной схемой.

**Хранение.** Время - UNIX timestamp в секундах, момент получения цены. Тип `BIGINT`, обычный `INTEGER` переполнится в 2038 году. Цена хранится как `NUMERIC(20, 8)`, в коде `Decimal`, чтобы не было ошибок округления float. В ответе API цена отдаётся числом. Индекс `(ticker, timestamp)` покрывает все три запроса: фильтр по тикеру плюс сортировка или диапазон по времени.

**Фильтр по дате.** Параметр `date` в формате `YYYY-MM-DD`, отдаются цены за эти сутки по UTC. Дата переводится в полуинтервал `[00:00 этого дня; 00:00 следующего)` в timestamp, выборка идёт по индексу.

**Все данные без пагинации.** В ТЗ сказано «получение всех сохранённых данных», поэтому `/prices` отдаёт всё. За сутки набегает 1440 записей на тикер, если данных станет много, стоит добавить `limit`/`offset`.

**Тикер - Enum.** FastAPI сам проверяет параметр: на пустой или неизвестный тикер вернётся 422, а в Swagger будет выпадающий список. Что во всех методах `ticker` обязательный и все они GET, проверяет отдельный тест по OpenAPI-схеме.

**Alembic вместо `create_all`.** Схема версионируется, изменения можно накатывать на базу с данными.

**Deribit.** Используется публичный метод `public/get_index_price` основного API, авторизация не нужна. Адрес вынесен в `DERIBIT_BASE_URL`, при желании можно переключить на `https://test.deribit.com/api/v2`.

**Конфигурация** только через переменные окружения. `.env` в репозиторий не попадает, вместо него есть `.env.example`.
