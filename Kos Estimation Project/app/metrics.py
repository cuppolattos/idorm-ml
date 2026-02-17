import numpy as np
import threading

class MetricsTracker:
    def __init__(self):
        self.lock = threading.Lock()
        self.total_requests = 0
        self.latencies = []

    def record(self, latency_ms: float):
        with self.lock:
            self.total_requests += 1
            self.latencies.append(latency_ms)

    def summary(self):
        with self.lock:
            if not self.latencies:
                return {
                    "total_requests": 0,
                    "mean_latency_ms": 0,
                    "p50_latency_ms": 0,
                    "p90_latency_ms": 0,
                    "p95_latency_ms": 0,
                }

            arr = np.array(self.latencies)

            return {
                "total_requests": self.total_requests,
                "mean_latency_ms": round(float(arr.mean()), 3),
                "p50_latency_ms": round(float(np.percentile(arr, 50)), 3),
                "p90_latency_ms": round(float(np.percentile(arr, 90)), 3),
                "p95_latency_ms": round(float(np.percentile(arr, 95)), 3),
            }


metrics_tracker = MetricsTracker()
