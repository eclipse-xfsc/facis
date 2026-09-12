"""Optional OpenTelemetry tracing for the local Phoenix UI."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from typing import Any, Iterator


_tracer: Any = None
_initialized = False
_initialization_error: str | None = None


def _enabled() -> bool:
    return os.getenv("PHOENIX_ENABLED", "0").lower() in {"1", "true", "yes"}


def _get_tracer() -> Any:
    global _tracer, _initialized, _initialization_error
    if _initialized:
        return _tracer
    _initialized = True
    if not _enabled():
        return None

    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        endpoint = os.getenv(
            "PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006/v1/traces"
        )
        provider = TracerProvider(
            resource=Resource.create(
                {
                    "service.name": os.getenv(
                        "PHOENIX_PROJECT_NAME", "facis-thin-slice-mvp"
                    ),
                    "openinference.project.name": os.getenv(
                        "PHOENIX_PROJECT_NAME", "facis-thin-slice-mvp"
                    ),
                }
            )
        )
        exporter = OTLPSpanExporter(endpoint=endpoint, timeout=1)
        provider.add_span_processor(
            BatchSpanProcessor(
                exporter,
                schedule_delay_millis=200,
                export_timeout_millis=1000,
            )
        )
        _tracer = provider.get_tracer("facis.thin_slice_mvp")
    except (ImportError, ValueError) as exc:
        _initialization_error = f"{type(exc).__name__}: {exc}"
        _tracer = None
    return _tracer


def tracing_status() -> dict[str, Any]:
    """Return a small status object suitable for startup logs and tests."""
    tracer = _get_tracer()
    return {
        "enabled": _enabled(),
        "active": tracer is not None,
        "endpoint": os.getenv(
            "PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006/v1/traces"
        ),
        "error": _initialization_error,
    }


def _json(value: Any) -> str:
    return json.dumps(value, default=str, ensure_ascii=False)


def set_span_output(span: Any, value: Any) -> None:
    if span is None:
        return
    span.set_attribute("output.value", _json(value))
    span.set_attribute("output.mime_type", "application/json")


def set_span_attribute(span: Any, key: str, value: Any) -> None:
    if span is None or value is None:
        return
    if isinstance(value, (dict, list, tuple)):
        value = _json(value)
    span.set_attribute(key, value)


def trace_id(span: Any) -> str | None:
    if span is None or not hasattr(span, "get_span_context"):
        return None
    context = span.get_span_context()
    if not getattr(context, "is_valid", False):
        return None
    return format(context.trace_id, "032x")


def trace_reference(span: Any) -> dict[str, str] | None:
    current_trace_id = trace_id(span)
    if current_trace_id is None:
        return None
    return {
        "trace_id": current_trace_id,
        "project": os.getenv("PHOENIX_PROJECT_NAME", "facis-thin-slice-mvp"),
        "ui": os.getenv("PHOENIX_UI_URL", "http://localhost:6006"),
    }


@contextmanager
def observed_span(
    name: str,
    kind: str,
    *,
    input_value: Any = None,
    attributes: dict[str, Any] | None = None,
) -> Iterator[Any]:
    """Create an OpenInference-compatible span, or a no-op when disabled."""
    tracer = _get_tracer()
    if tracer is None:
        yield None
        return

    with tracer.start_as_current_span(name) as span:
        span.set_attribute("openinference.span.kind", kind)
        if input_value is not None:
            span.set_attribute("input.value", _json(input_value))
            span.set_attribute("input.mime_type", "application/json")
        for key, value in (attributes or {}).items():
            set_span_attribute(span, key, value)
        yield span
