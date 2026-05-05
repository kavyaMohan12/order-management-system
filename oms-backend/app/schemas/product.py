from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Widget",
                "description": "A useful widget",
                "price": "9.99",
                "stock": 100,
            }
        },
    )

    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
