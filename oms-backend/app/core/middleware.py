import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging import request_id_var

logger = logging.getLogger("app.requests")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Per-request: generate/propagate `X-Request-ID`, time the request, log one INFO line."""

    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        token = request_id_var.set(rid)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "request_failed method=%s path=%s duration_ms=%.1f",
                request.method,
                request.url.path,
                duration_ms,
            )
            request_id_var.reset(token)
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "request method=%s path=%s status=%s duration_ms=%.1f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        response.headers["X-Request-ID"] = rid
        request_id_var.reset(token)
        return response
