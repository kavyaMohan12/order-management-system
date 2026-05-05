from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.orders import router as orders_router
from app.api.products import router as products_router

app = FastAPI(title="OMS Backend")

app.include_router(health_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(products_router, prefix="/products", tags=["products"])
app.include_router(orders_router, prefix="/orders", tags=["orders"])


@app.get("/")
def root():
    return {"message": "OMS Backend running"}
