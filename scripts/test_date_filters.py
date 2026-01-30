
import os
import sys
import requests
import json
from datetime import datetime, timedelta

# API URL
API_URL = "http://localhost:8000/api/v1/dtic"

def test_endpoint(name, endpoint, params={}):
    print(f"\n--- Testing {name} ---")
    print(f"URL: {API_URL}/{endpoint}")
    print(f"Params: {params}")
    
    try:
        resp = requests.get(f"{API_URL}/{endpoint}", params=params)
        if resp.status_code == 200:
            data = resp.json()
            print("✅ Status 200 OK")
            # Print summary of data to see differences
            if isinstance(data, list):
                print(f"Count: {len(data)}")
                if len(data) > 0:
                    print(f"First Item: {data[0]}")
            elif isinstance(data, dict):
                print(f"Data Keys: {list(data.keys())}")
                print(f"Sample: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Error {resp.status_code}: {resp.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    print("🔍 Starting Date Filter Backend Validation...")
    
    # 1. Baseline (No Filter)
    print("\n[1] Baseline (All Time)")
    stats_all = test_endpoint("General Stats", "metrics-gerais")
    
    # 2. Filter: Last 30 Days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    params_30d = {
        "inicio": start_date.isoformat(),
        "fim": end_date.isoformat()
    }
    
    print("\n[2] Filter: Last 30 Days")
    stats_30d = test_endpoint("General Stats (30d)", "metrics-gerais", params_30d)
    
    # Analysis
    if stats_all and stats_30d:
        print("\n📊 Comparison (General Stats):")
        print(f"Novos (All): {stats_all.get('novos')} vs (30d): {stats_30d.get('novos')}")
        print(f"Resolvidos (All): {stats_all.get('resolvidos')} vs (30d): {stats_30d.get('resolvidos')}")
        
        if stats_all['novos'] == stats_30d['novos']:
            print("⚠️ 'Novos' count did NOT change (Expected behavior per service.py analysis)")
        else:
            print("✅ 'Novos' count changed (Unexpected)")
            
        if stats_all['resolvidos'] != stats_30d['resolvidos']:
            print("✅ 'Resolvidos' count changed (Filter working)")
        else:
            print("⚠️ 'Resolvidos' count identical (Might be no data > 30d or filter broken)")

    # 3. Ranking Filter Test
    print("\n[3] Ranking Filter Test")
    rank_all = test_endpoint("Technician Ranking (All)", "ranking-tecnicos")
    rank_30d = test_endpoint("Technician Ranking (30d)", "ranking-tecnicos", params_30d)
    
    if rank_all and rank_30d:
         print(f"Technicians (All): {len(rank_all)} vs (30d): {len(rank_30d)}")


if __name__ == "__main__":
    main()
