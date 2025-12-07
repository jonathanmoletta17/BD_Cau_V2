import json
import os
import sys
from collections import defaultdict

# Resolve project-relative paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(PROJECT_ROOT, "reports")
DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "datasets", "validation_dataset.json")

# Find latest report file
files = [os.path.join(REPORT_DIR, f) for f in os.listdir(REPORT_DIR) if f.startswith("accuracy_report_")]
latest_file = max(files, key=os.path.getctime)

print(f"Analyzing: {latest_file}")

with open(latest_file, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    dataset = json.load(f)
    
# Map ID -> Text
id_to_text = {item["id"]: item["text"] for item in dataset}

details = data["details"]

# Group by (True, Predicted) pair
errors = defaultdict(list)
for item in details:
    if not item["correct"]:
        pair = (item["true_category"], item["predicted_category"])
        # Add text to item
        item["text"] = id_to_text.get(item["id"], "TEXT NOT FOUND")
        errors[pair].append(item)

# Sort by frequency
sorted_errors = sorted(errors.items(), key=lambda x: len(x[1]), reverse=True)

print("\n=== DEEP DIVE INTO INCONSISTENCIES ===\n")

for (true_cat, pred_cat), items in sorted_errors[:10]:
    print(f"🔴 MISTAKE: True: '{true_cat}'  -->  Pred: '{pred_cat}' ({len(items)} cases)")
    print("-" * 80)
    for i, item in enumerate(items[:3]): # Show top 3 examples
        print(f"   Ticket #{item['id']}: {item['text'][:150]}...")
        print(f"   Confidence: {item['confidence']:.4f}")
        print("")
    print("=" * 80)
