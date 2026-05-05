# OMS Backend

FastAPI-based Order Management System backend. Modular structure: routes → services → models.

## Architecture decisions

- **Database: PostgreSQL** — ACID transactions, constraints, and relational modeling fit orders, inventory, and user data. Matches production-style backends and the Docker Compose setup.
- **ORM: SQLAlchemy** — Python-native data layer for FastAPI; schema changes are versioned with **Alembic** (like Git for your database shape). The ORM maps tables to classes; it does not replace PostgreSQL as the source of truth for persisted data.

## Setup

```bash
docker-compose up --build
```

The container entrypoint runs `alembic upgrade head` and the product seed script before starting Uvicorn.

- App: http://localhost:8000
- Interactive API docs (Swagger UI): http://localhost:8000/docs
- Alternate API docs (ReDoc): http://localhost:8000/redoc

## Local Run (without Docker)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run PostgreSQL and set `.env` with `DB_HOST=localhost` (and matching `DB_*` credentials).
3. Apply migrations and seed products:
   ```bash
   alembic upgrade head
   python -m app.scripts.seed_products
   ```
4. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Database migrations

```bash
# Create DB schema from latest revision
alembic upgrade head

# Optional: tear down all tables (destructive)
alembic downgrade base
```

## Seed data

Idempotent: inserts sample products only if the `products` table is empty.

```bash
python -m app.scripts.seed_products
```

## Configuration

Settings come from `.env` (see [`app/core/config.py`](app/core/config.py)).

| Variable | Default | Purpose |
|----------|---------|---------|
| `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` | — | PostgreSQL connection |
| `SECRET_KEY` | — | JWT signing secret (required) |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token lifetime |
| `LOG_LEVEL` | `INFO` | Root log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

## Tests

Uses in-memory SQLite with foreign keys enabled (same SQLAlchemy models; no Docker required).

```bash
pytest                    # all tests
pytest tests/unit         # fast unit tests only
pytest tests/integration  # HTTP/end-to-end tests
```

Test layout:

- `tests/unit/` — pure-function tests (security, services).
- `tests/integration/` — HTTP-level tests using FastAPI's `TestClient`, including a full
  register → login → create → patch → cancel end-to-end flow in `test_e2e_flow.py`.

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | / | No | Root message |
| GET | /health | No | Health check |
| POST | /auth/register | No | Create user (bcrypt password hash) |
| POST | /auth/login | No | Returns JWT (`Bearer`) |
| GET | /products | No | List products (includes seeded catalog) |
| POST | /orders | Yes | Create order; validates product IDs and stock; snapshots `unit_price` per line |
| GET | /orders | Yes | List current user's orders only |
| GET | /orders/{id} | Yes | Order detail; **403** if it belongs to another user; **404** if missing |
| PATCH | /orders/{id} | Yes | Update `shipping_address` and/or replace `items` (owner only) |
| POST | /orders/{id}/cancel | Yes | Set status to `cancelled`; restores stock; idempotent if already cancelled |

### Order rules

- New orders start as `pending`. Line items store `unit_price` at purchase time.
- Updates (PATCH) are allowed only while status is `pending` or `confirmed`.
- Cancelling restores product stock. Only `pending` or `confirmed` orders can be cancelled (already `cancelled` returns success without error).

## Authentication walkthrough

```bash
# 1. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"supersecret1"}'

# 2. Login -> capture the JWT
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"supersecret1"}' | jq -r .access_token)

# 3. Use the token on protected routes
curl http://localhost:8000/orders -H "Authorization: Bearer $TOKEN"

# 4. Create an order
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"shipping_address":"1 Main St","items":[{"product_id":1,"quantity":2}]}'
```

## Error envelope

All non-2xx responses share one shape:

```json
{
  "error": {
    "code": "insufficient_stock",
    "message": "Insufficient stock for one or more products",
    "details": { "product_id": 7 }
  }
}
```

| Code | HTTP | Meaning |
|------|------|---------|
| `validation_error` | 422 | Request body failed Pydantic schema validation; `details.errors` lists each failure |
| `unknown_product` | 400 | Order line references a non-existent `product_id` |
| `insufficient_stock` | 400 | Order line quantity exceeds available stock |
| `order_not_editable` | 400 | PATCH attempted on an order whose status is not `pending`/`confirmed` |
| `order_not_cancellable` | 400 | Cancel attempted on an order whose status is not `pending`/`confirmed` |
| `email_taken` | 400 | Registration attempted with an already-registered email |
| `auth_failed` | 401 | Missing, invalid, or expired bearer token (or wrong login credentials) |
| `forbidden` | 403 | Authenticated user does not own the requested resource |
| `order_not_found` | 404 | No order with the given id |
| `http_error` | * | Catch-all for raw `HTTPException`s raised outside the domain layer |
| `internal_error` | 500 | Unhandled exception. The server logs the stack trace; the client gets only a generic message |

## Logging

- One log line per request via `RequestContextMiddleware`:
  ```
  2026-05-05 13:00:01 INFO [app.requests] [req=8c1f...] request method=POST path=/orders status=201 duration_ms=12.3
  ```
- Every request gets an `X-Request-ID` (echoed back as a response header). Pass an existing `X-Request-ID` header to trace a request across services.
- `domain_error_handler` logs at `WARNING`; `unhandled_error_handler` logs at `ERROR` with the full stack trace.
- Adjust verbosity via the `LOG_LEVEL` env var.

## Postman collection

A ready-to-import collection lives at [`docs/postman_collection.json`](docs/postman_collection.json).

1. Import it into Postman or Insomnia.
2. Set the `baseUrl` collection variable (defaults to `http://localhost:8000`).
3. Run **Auth → Register**, then **Auth → Login**. The Login request has a Tests script that automatically saves `access_token` into the `{{token}}` variable, so subsequent authenticated requests work without any copy-paste.
4. The **Orders → Create order** request similarly stashes the new id into `{{orderId}}` for the follow-up requests.

## Project Structure

```
alembic/              # migration env + versions
app/
├── main.py           # entry point: configures logging, middleware, error handlers, routers
├── core/             # config, database, security, constants, exceptions, error_handlers, logging, middleware
├── api/              # routes + auth dependency + reusable OpenAPI response snippets
├── models/           # ORM models
├── schemas/          # request/response DTOs (incl. shared ErrorEnvelope)
├── services/         # business logic (raises typed DomainError subclasses)
└── scripts/          # seed and one-off scripts
docs/
└── postman_collection.json
tests/
├── unit/             # pure-function tests
└── integration/      # HTTP/TestClient tests + end-to-end flow
```
