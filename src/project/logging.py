import logging
from collections.abc import Sequence
from contextvars import ContextVar
from dataclasses import dataclass

from starlette.datastructures import URL
from starlette.types import ASGIApp, Receive, Scope, Send

ctx_request_url = ContextVar("request_url")


@dataclass
class RequestUrlMiddleware:
    """Extract the request URL to append it to all relevant logs."""

    app: ASGIApp

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Extract the URL pathname + query string and store it in context."""
        if scope["type"] == "http":
            url = URL(scope=scope).remove_query_params("token")
            ctx_request_url.set(url.path + "?" + url.query)
        await self.app(scope, receive, send)


class AccessLogFilter(logging.Filter):
    """Perform some transformations on the default uvicorn access logs."""

    def __init__(self, skip_prefix: Sequence[str]) -> None:
        """Create a new Filter instance."""
        self.skip_prefix = (skip_prefix,) if isinstance(skip_prefix, str) else tuple(skip_prefix)

    def filter(self, record: logging.LogRecord) -> bool:
        """Skip access logs by matching URLs to specified patterns."""
        if record.name == "uvicorn.access":
            full_path = ""
            if isinstance(record.args, Sequence):
                full_path = str(record.args[2])
            return not full_path.startswith(self.skip_prefix)

        # Attach request URL to all other log types
        record.request_url = ctx_request_url.get("-")
        return True
