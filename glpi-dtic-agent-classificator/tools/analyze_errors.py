"""Analisa erros do relatório de accuracy de forma detalhada."""
import os
import json
import glob

reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
pattern = os.path.join(reports_dir, "accuracy_report_*.json")
files = sorted(glob.glob(pattern))

if not files:
    print("Nenhum relatorio encontrado.")
    exit(1)

with open(files[-1], "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 60)
print("ANALISE DE ERROS DO CLASSIFICADOR")
print("=" * 60)
print(f"Accuracy: {data['accuracy']}%")
print(f"Acertos: {data['correct']} / Erros: {data['incorrect']}")
print()

# Pares de confusao
print("-" * 60)
print("TOP 10 PARES DE CONFUSAO (Verdadeiro -> Predito)")
print("-" * 60)
pairs = sorted(data["confusion_pairs"].items(), key=lambda x: x[1], reverse=True)[:10]
for pair, count in pairs:
    # Substitui a seta unicode por texto simples
    clean_pair = pair.replace("\u2192", "->")
    print(f"  {count}x: {clean_pair}")

# Categorias com mais erros
print()
print("-" * 60)
print("CATEGORIAS VERDADEIRAS COM MAIS ERROS")
print("-" * 60)
errors_by_cat = data.get("errors_by_category", {})
sorted_cats = sorted(errors_by_cat.items(), key=lambda x: len(x[1]), reverse=True)
for cat, errors in sorted_cats[:10]:
    print(f"\n  [{len(errors)} erros] {cat}")
    for err in errors[:3]:
        pred = err["predicted"]
        conf = err["confidence"]
        print(f"      Predito: {pred} (conf: {conf})")

print()
print("=" * 60)
