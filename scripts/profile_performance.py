
import os
import requests
import time
import statistics

API_URL = "http://localhost:8000/api/v1/dtic"

def benchmark(name, url, params={}, runs=5):
    times = []
    print(f"--- Benchmarking: {name} ---")
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    for i in range(runs):
        start = time.time()
        try:
            resp = requests.get(url, params=params)
            duration = (time.time() - start) * 1000 # ms
            if resp.status_code == 200:
                times.append(duration)
                print(f"Run {i+1}: {duration:.2f} ms")
            else:
                print(f"Run {i+1}: Failed ({resp.status_code})")
        except Exception as e:
             print(f"Run {i+1}: Exception {e}")
    
    if times:
        avg = statistics.mean(times)
        p95 = statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times)
        print(f"Creates Result: Avg={avg:.2f}ms | Max={max(times):.2f}ms")
        return avg
    return 0

def main():
    print("🚀 Starting API Performance Profiling...")
    
    # 1. Baseline (All Time)
    benchmark("General Stats (No Filter)", f"{API_URL}/metrics-gerais")
    
    # 2. Filtered (Last 30 Days) -> This is what user does
    params_30d = {
        "inicio": "2025-12-22T00:00:00",
        "fim": "2026-01-21T23:59:59"
    }
    
    print("\n--- Filtered Benchmarks ---")
    benchmark("General Stats (30d)", f"{API_URL}/metrics-gerais", params_30d)
    benchmark("Ranking Entidades (30d)", f"{API_URL}/ranking-entidades", params_30d)
    benchmark("Ranking Categorias (30d)", f"{API_URL}/ranking-categorias", params_30d)
    benchmark("Ranking Tecnicos (30d)", f"{API_URL}/ranking-tecnicos", params_30d)
    benchmark("Status Niveis (30d)", f"{API_URL}/status-niveis", params_30d)
    
    # 3. New Tickets (Subquery logic)
    benchmark("Tickets Novos (Limit 5)", f"{API_URL}/tickets-novos", {"limit": 5})

if __name__ == "__main__":
    main()
