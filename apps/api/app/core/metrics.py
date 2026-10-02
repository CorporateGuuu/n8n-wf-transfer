from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest

REGISTRY = CollectorRegistry()

HTTP_REQUESTS = Counter(
    "ops_http_requests_total",
    "Total HTTP requests handled by the API.",
    ["method", "route", "status"],
    registry=REGISTRY,
)

HTTP_REQUEST_DURATION = Histogram(
    "ops_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
    registry=REGISTRY,
)


def observe_request(*, method: str, route: str, status: int, duration_seconds: float) -> None:
    HTTP_REQUESTS.labels(method=method, route=route, status=str(status)).inc()
    HTTP_REQUEST_DURATION.labels(method=method, route=route).observe(duration_seconds)


def metrics_payload() -> bytes:
    return generate_latest(REGISTRY)
