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

App: http://localhost:8000  
API docs: http://localhost:8000/docs

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

## Tests

Uses in-memory SQLite with foreign keys enabled (same SQLAlchemy models; no Docker required).

```bash
pytest
```

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | / | No | Root message |
| GET | /health | No | Health check |
| POST | /auth/register | No | Create user (bcrypt password hash) |
| POST | /auth/login | No | Returns JWT (`Bearer`) |
| GET | /products | No | List products (includes seeded catalog) |
| POST | /orders | Yes | Create order; validates product IDs and stock; snapshots `unit_price` per line |
| GET | /orders | Yes | List current user’s orders only |
| GET | /orders/{id} | Yes | Order detail; **403** if it belongs to another user; **404** if missing |
| PATCH | /orders/{id} | Yes | Update `shipping_address` and/or replace `items` (owner only) |
| POST | /orders/{id}/cancel | Yes | Set status to `cancelled`; restores stock; idempotent if already cancelled |

### Order rules

- New orders start as `pending`. Line items store `unit_price` at purchase time.
- Updates (PATCH) are allowed only while status is `pending` or `confirmed`.
- Cancelling restores product stock. Only `pending` or `confirmed` orders can be cancelled (already `cancelled` returns success without error).

## Project Structure

```
alembic/              # migration env + versions
app/
├── main.py           # entry point
├── core/             # config, database, security, constants
├── api/              # routes + auth dependency
├── models/           # ORM models
├── schemas/          # request/response DTOs
├── services/         # business logic
└── scripts/          # seed and one-off scripts
tests/                # pytest (in-memory SQLite)
```
