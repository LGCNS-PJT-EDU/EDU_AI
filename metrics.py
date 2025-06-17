# metrics.py
from prometheus_client import Histogram
from typing import Callable
from starlette.requests import Request

def latency_histogram() -> Callable:
    histogram = Histogram(
        "http_request_duration_seconds",
        "Histogram of request duration in seconds",
        ["method", "path"]
    )

    def instrumentation(info) -> None:
        request: Request = info.request
        histogram.labels(request.method, request.url.path).observe(info.duration)

    return instrumentation

