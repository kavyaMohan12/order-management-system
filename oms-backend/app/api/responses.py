"""Reusable OpenAPI `responses=` snippets so error envelope is documented in Swagger."""

from app.schemas.errors import ErrorEnvelope

ERROR_400 = {400: {"model": ErrorEnvelope, "description": "Bad request / domain error"}}
ERROR_401 = {401: {"model": ErrorEnvelope, "description": "Not authenticated"}}
ERROR_403 = {403: {"model": ErrorEnvelope, "description": "Forbidden"}}
ERROR_404 = {404: {"model": ErrorEnvelope, "description": "Not found"}}
ERROR_422 = {422: {"model": ErrorEnvelope, "description": "Request validation failed"}}

AUTH_ERRORS = {**ERROR_401, **ERROR_422}
ORDER_RW_ERRORS = {**ERROR_400, **ERROR_401, **ERROR_403, **ERROR_404, **ERROR_422}
ORDER_RO_ERRORS = {**ERROR_401, **ERROR_403, **ERROR_404}
