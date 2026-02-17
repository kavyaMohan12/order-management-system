# OMS Backend

FastAPI-based Order Management System backend. Modular structure: routes → services → models.

## Setup

```bash
docker-compose up --build
```

App: http://localhost:8000  
API docs: http://localhost:8000/docs

## Local Run (without Docker)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run PostgreSQL locally (or use Docker for db only) and set `.env` with `DB_HOST=localhost`.
3. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Endpoints

| Method | Path     | Description   |
|--------|----------|---------------|
| GET    | /        | Root message  |
| GET    | /health  | Health check  |

## Project Structure

```
app/
├── main.py           # entry point
├── core/             # config, database
├── api/              # routes (health, auth, products, orders)
├── models/           # ORM models
├── schemas/          # request/response DTOs
├── services/         # business logic
└── tests/
```
