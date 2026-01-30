import time
import requests
import statistics

BASE_URL = "http://localhost:3001/api/v1"

def benchmark_endpoint(name, path, count=20):
    url = f"{BASE_URL}{path}"
    latencies = []
    errors = 0
    
    print(f"Benchmarking {name} ({count} reqs)...")
    for _ in range(count):
        try:
            start = time.time()
            res = requests.get(url, timeout=5)
            # Ensure we get JSON, otherwise it's an Nginx error page (invalid)
            if "application/json" not in res.headers.get("Content-Type", ""):
                 errors += 1
                 continue
                 
            if res.status_code == 200:
                latencies.append((time.time() - start) * 1000)
            else:
                errors += 1
        except Exception as e:
            errors += 1
            
    if not latencies:
        print(f"  FAILED: All requests to {name} failed.")
        return
        
    avg = statistics.mean(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
    
    print(f"  {name}: Avg={avg:.2f}ms, P95={p95:.2f}ms, Errors={errors}/{count}")

def run_suite():
    print("Starting API Stability & Latency Benchmark...")
    endpoints = [
        ("Health", "/health"),
        ("Metrics", "/dtic/metrics-gerais?inicio=2025-01-01&fim=2025-12-31"),
        ("Ranking", "/dtic/ranking-tecnicos?inicio=2025-01-01&fim=2025-12-31"),
        ("Tickets", "/dtic/tickets-novos?limit=5")
    ]
    
    for name, path in endpoints:
        benchmark_endpoint(name, path)

if __name__ == "__main__":
    run_suite()
