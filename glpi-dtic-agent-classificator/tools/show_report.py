"""Exibe o resumo do relatório de accuracy mais recente."""
import os
import json
import glob

reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
pattern = os.path.join(reports_dir, "accuracy_report_*.json")
files = sorted(glob.glob(pattern))

if not files:
    print("Nenhum relatório encontrado.")
    exit(1)

latest = files[-1]
print(f"Arquivo: {os.path.basename(latest)}\n")

with open(latest, "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 55)
print("  BASELINE DE ACCURACY")
print("=" * 55)
print(f"  Total tickets:  {data['total_tickets']}")
print(f"  Acertos:        {data['correct']}")
print(f"  Erros:          {data['incorrect']}")
print(f"  ACCURACY:       {data['accuracy']}%")
print()

if data.get("confusion_pairs"):
    print("--- Top 5 Erros Mais Frequentes ---")
    pairs = sorted(data["confusion_pairs"].items(), key=lambda x: x[1], reverse=True)[:5]
    for pair, count in pairs:
        print(f"  {count}x: {pair}")

if data.get("errors_by_category"):
    print("\n--- Categorias com Mais Erros ---")
    cats = sorted(data["errors_by_category"].items(), key=lambda x: len(x[1]), reverse=True)[:5]
    for cat, errors in cats:
        print(f"  {len(errors)} erros: {cat}")

print("\n" + "=" * 55)
