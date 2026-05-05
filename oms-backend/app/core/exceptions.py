from typing import Any


class DomainError(Exception):
    """Base class for business-rule errors that map to a 4xx HTTP response."""

    code: str = "domain_error"
    http_status: int = 400

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details: dict[str, Any] = details or {}


class UnknownProductError(DomainError):
    code = "unknown_product"

    def __init__(self, product_id: int) -> None:
        super().__init__(
            "One or more product IDs are invalid",
            details={"product_id": product_id},
        )


class InsufficientStockError(DomainError):
    code = "insufficient_stock"

    def __init__(self, product_id: int) -> None:
        super().__init__(
            "Insufficient stock for one or more products",
            details={"product_id": product_id},
        )


class OrderNotEditableError(DomainError):
    code = "order_not_editable"

    def __init__(self) -> None:
        super().__init__("Order cannot be updated in its current status")


class OrderNotCancellableError(DomainError):
    code = "order_not_cancellable"

    def __init__(self) -> None:
        super().__init__("Order cannot be cancelled in its current status")


class OrderNotFoundError(DomainError):
    code = "order_not_found"
    http_status = 404

    def __init__(self) -> None:
        super().__init__("Order not found")


class ForbiddenError(DomainError):
    code = "forbidden"
    http_status = 403

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message)


class AuthError(DomainError):
    code = "auth_failed"
    http_status = 401

    def __init__(self, message: str = "Not authenticated") -> None:
        super().__init__(message)


class EmailAlreadyRegisteredError(DomainError):
    code = "email_taken"

    def __init__(self) -> None:
        super().__init__("Email already registered")
