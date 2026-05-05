from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class OrderItemLineIn(BaseModel):
    product_id: int = Field(ge=1)
    quantity: int = Field(ge=1, le=1000)


class OrderCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "shipping_address": "1 Main St, Springfield",
                "items": [
                    {"product_id": 1, "quantity": 2},
                    {"product_id": 2, "quantity": 1},
                ],
            }
        }
    )

    shipping_address: str = Field(min_length=1, max_length=500)
    items: list[OrderItemLineIn] = Field(min_length=1)


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: Decimal


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: str
    shipping_address: str
    items: list[OrderItemRead]


class OrderUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "shipping_address": "42 New Address Ave",
                "items": [{"product_id": 1, "quantity": 3}],
            }
        }
    )

    shipping_address: str | None = Field(default=None, max_length=500)
    items: list[OrderItemLineIn] | None = None

    @field_validator("shipping_address")
    @classmethod
    def address_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("shipping_address cannot be empty")
        return v

    @model_validator(mode="after")
    def at_least_one_field(self):
        if self.shipping_address is None and self.items is None:
            raise ValueError("Provide shipping_address and/or items")
        if self.items is not None and len(self.items) == 0:
            raise ValueError("items cannot be empty when provided")
        return self
