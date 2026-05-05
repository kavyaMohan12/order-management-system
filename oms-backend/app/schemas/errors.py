from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ErrorBody(BaseModel):
    code: str = Field(description="Stable machine-readable error code")
    message: str = Field(description="Human-readable error message")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional structured context about the error",
    )


class ErrorEnvelope(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "insufficient_stock",
                    "message": "Insufficient stock for one or more products",
                    "details": {"product_id": 7},
                }
            }
        }
    )

    error: ErrorBody
