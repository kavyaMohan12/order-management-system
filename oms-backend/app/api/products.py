from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Product
from app.schemas.product import ProductRead

router = APIRouter()


@router.get(
    "",
    response_model=list[ProductRead],
    summary="List products",
    description="Public catalog of available products.",
)
def list_products(db: Session = Depends(get_db)):
    stmt = select(Product).order_by(Product.id)
    products = db.scalars(stmt).all()
    return list(products)
