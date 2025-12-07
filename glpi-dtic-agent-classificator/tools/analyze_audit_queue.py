import json
import os
from collections import defaultdict
import statistics

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_PATH = os.path.join(PROJECT_ROOT, "data", "audit_queue.json")

def main():
    if not os.path.exists(QUEUE_PATH):
        print(f"File not found: {QUEUE_PATH}")
        return

    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        queue = json.load(f)

    print(f"Total Discrepancies: {len(queue)}")
    
    # Group by (Human -> AI)
    patterns = defaultdict(list)
    
    for item in queue:
        key = f"{item['human_label']} -> {item['ai_label']}"
        patterns[key].append(item['ai_confidence'])

    # Analyze
    results = []
    for key, confs in patterns.items():
        results.append({
            "pair": key,
            "count": len(confs),
            "avg_conf": statistics.mean(confs),
            "max_conf": max(confs)
        })

    # Sort by Count DESC
    results.sort(key=lambda x: x["count"], reverse=True)

    print("\n--- TOP 10 DISCREPANCY PATTERNS ---")
    print(f"{'COUNT':<6} | {'AVG CONF':<8} | {'PATTERN'}")
    print("-" * 60)
    
    for r in results[:10]:
        print(f"{r['count']:<6} | {r['avg_conf']:.1%}   | {r['pair']}")

    print("\n--- INSIGHTS ---")
    top_pattern = results[0]
    print(f"1. The most common disagreement is '{top_pattern['pair']}' with {top_pattern['count']} cases.")
    print(f"   The AI is {top_pattern['avg_conf']:.1%} confident on average here.")

if __name__ == "__main__":
    main()
