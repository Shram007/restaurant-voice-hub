"""
Structured observability for restaurant-voice-hub.
Emits JSON log lines for every tool invocation, error, and pipeline event.
"""
import json
import time
import uuid
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable


def _emit(level: str, event: str, **fields: Any) -> None:
    """Emit a structured JSON log line."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "event": event,
        **fields,
    }
    print(json.dumps(record), flush=True)


def log_info(event: str, **fields: Any) -> None:
    _emit("INFO", event, **fields)


def log_error(event: str, **fields: Any) -> None:
    _emit("ERROR", event, **fields)


def log_warn(event: str, **fields: Any) -> None:
    _emit("WARN", event, **fields)


def trace_tool(tool_name: str) -> Callable:
    """
    Decorator that wraps a tool endpoint function with structured logging.
    Logs: tool name, request payload, response, latency_ms, and any errors.
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            trace_id = str(uuid.uuid4())[:8]
            start = time.perf_counter()
            log_info(
                "tool_invoked",
                tool=tool_name,
                trace_id=trace_id,
            )
            try:
                result = fn(*args, **kwargs)
                latency_ms = round((time.perf_counter() - start) * 1000, 2)
                log_info(
                    "tool_success",
                    tool=tool_name,
                    trace_id=trace_id,
                    latency_ms=latency_ms,
                )
                return result
            except Exception as exc:
                latency_ms = round((time.perf_counter() - start) * 1000, 2)
                log_error(
                    "tool_error",
                    tool=tool_name,
                    trace_id=trace_id,
                    latency_ms=latency_ms,
                    error=str(exc),
                    error_type=type(exc).__name__,
                )
                raise
        return wrapper
    return decorator
