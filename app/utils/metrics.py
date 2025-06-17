# app/utils/metrics.py 또는 app/metrics.py

from prometheus_client import Histogram

latency_histogram = Histogram(
    "response_latency_seconds",
    "Request latency by method and path",
    ["method", "path"]
)

def observe_latency(info):
    latency_histogram.labels(
        method=info.method,
        path=info.path  #  'modified_path' → 'path'
    ).observe(info.duration)
