"""Gera relatorio de diagnostico detalhado em formato legivel."""
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

# Gera relatorio em markdown
output_path = os.path.join(reports_dir, "baseline_diagnostico.md")

with open(output_path, "w", encoding="utf-8") as out:
    out.write("# Diagnóstico de Baseline - Classificador de Tickets\n\n")
    out.write(f"**Data:** {data['timestamp'][:10]}\n\n")
    
    out.write("## Resumo\n\n")
    out.write("| Métrica | Valor |\n")
    out.write("|---------|-------|\n")
    out.write(f"| Total de tickets | {data['total_tickets']} |\n")
    out.write(f"| Acertos | {data['correct']} |\n")
    out.write(f"| Erros | {data['incorrect']} |\n")
    out.write(f"| **Accuracy** | **{data['accuracy']}%** |\n\n")
    
    out.write("## Top 10 Pares de Confusão\n\n")
    out.write("Onde o classificador está errando:\n\n")
    out.write("| Qtd | Categoria Verdadeira | Categoria Predita |\n")
    out.write("|-----|---------------------|-------------------|\n")
    pairs = sorted(data["confusion_pairs"].items(), key=lambda x: x[1], reverse=True)[:10]
    for pair, count in pairs:
        parts = pair.split(" → ")
        if len(parts) == 2:
            out.write(f"| {count} | {parts[0]} | {parts[1]} |\n")
    
    out.write("\n## Categorias com Mais Erros\n\n")
    errors_by_cat = data.get("errors_by_category", {})
    sorted_cats = sorted(errors_by_cat.items(), key=lambda x: len(x[1]), reverse=True)
    
    for cat, errors in sorted_cats[:10]:
        out.write(f"\n### {cat} ({len(errors)} erros)\n\n")
        out.write("| Predito Como | Confiança |\n")
        out.write("|-------------|----------|\n")
        for err in errors[:5]:
            out.write(f"| {err['predicted']} | {err['confidence']} |\n")
    
    out.write("\n## Análise dos Padrões de Erro\n\n")
    out.write("### Observações:\n\n")
    out.write("1. **Muitos erros para subcategorias**: O classificador confunde categorias pai/filho\n")
    out.write("2. **AJUDA E SUPORTE** é frequentemente predita incorretamente\n")
    out.write("3. **IMPRESSORA** e **OFFICE 365** têm alta confusão com subcategorias\n\n")
    out.write("### Causas Prováveis:\n\n")
    out.write("1. Contextos **genéricos demais** - não diferenciam subcategorias\n")
    out.write("2. Falta de **termos específicos** nos contextos\n")
    out.write("3. Hierarquia de categorias **muito granular**\n")

print(f"Relatorio salvo em: {output_path}")
