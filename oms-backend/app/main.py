from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.orders import router as orders_router
from app.api.products import router as products_router
from app.core.config import settings
from app.core.error_handlers import register_error_handlers
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware

configure_logging(settings.LOG_LEVEL)

API_DESCRIPTION = """
**Order Management System** — a small FastAPI service for managing products and orders.

- JWT-based authentication (`Authorization: Bearer <token>`)
- All errors share a single envelope: `{ "error": { "code", "message", "details" } }`
- Every response includes an `X-Request-ID` header that ties together the request log line and any error logs.
- See README for the auth flow and Postman collection.
""".strip()

TAGS_METADATA = [
    {"name": "health", "description": "Liveness check."},
    {"name": "auth", "description": "User registration and JWT login."},
    {"name": "products", "description": "Public product catalog."},
    {
        "name": "orders",
        "description": "Authenticated order lifecycle: create, list, view, update, cancel.",
    },
]

app = FastAPI(
    title="OMS Backend",
    description=API_DESCRIPTION,
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
)

app.add_middleware(RequestContextMiddleware)
register_error_handlers(app)

app.include_router(health_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(products_router, prefix="/products", tags=["products"])
app.include_router(orders_router, prefix="/orders", tags=["orders"])


@app.get("/", tags=["health"])
def root():
    return {"message": "OMS Backend running"}
