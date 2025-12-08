import os
import pandas as pd
import unicodedata
import matplotlib.pyplot as plt
import json

# 1. Carregar o novo CSV
fname = "glpi-tickets-fechados.csv"
path = os.path.join("/app", fname)

if not os.path.exists(path):
    # Fallback for local testing
    if os.path.exists(fname):
            path = fname
    elif os.path.exists(os.path.join("..", fname)):
            path = os.path.join("..", fname)
    else:
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

print(f"Loading {path}...")
# Note: The file uses ";" as separator and has quoted fields based on inspection
df = pd.read_csv(path, sep=";", encoding="utf-8-sig", quotechar='"', low_memory=False)

# 2. Inspeção preliminar
print("Total de linhas:", len(df))
print("Colunas:", df.columns.tolist())

# 3. Normalização de texto
def normalize(text):
    if not isinstance(text, str):
        return ""
    t = text.lower()
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode('ascii')
    return t.strip()

# Normalize Title and Description (if available)
# Based on inspection: "Título", "Descrição"
col_titulo = next((c for c in df.columns if normalize(c) == "titulo"), "Título")
col_desc = next((c for c in df.columns if normalize(c) == "descricao"), "Descrição")

print(f"Usando colunas: Título='{col_titulo}', Descrição='{col_desc}'")

df['titulo_norm'] = df[col_titulo].apply(normalize)
if col_desc in df.columns:
    df['desc_norm'] = df[col_desc].apply(normalize)
else:
    print("AVISO: Coluna de descrição não encontrada, buscando apenas no título.")
    df['desc_norm'] = ""

# 4. Definir lista de termos esperados para busca
busca = "hp elite mini 800 g9"
busca_norm = normalize(busca)

# 5. Filtrar os tickets que deveriam corresponder (Busca em Título OU Descrição)
# Ajustando a busca para ser mais flexível (termos isolados ou regex)
# Vamos buscar por tickets que tenham "hp" E "elite" E "mini" na mesma linha (titulo ou desc)
def contains_all_terms(text, terms):
    if not isinstance(text, str): return False
    return all(term in text for term in terms)

termos_busca = ["hp", "elite", "mini"] # "800" e "g9" podem ser muito especificos e faltar
mask = df.apply(lambda row: contains_all_terms(row['titulo_norm'], termos_busca) or 
                            contains_all_terms(row['desc_norm'], termos_busca), axis=1)

hp_tickets = df[mask].copy()

print("Número de tickets que correspondem à busca (HP + Elite + Mini):", len(hp_tickets))

# Busca ampla para diagnóstico
print("\n--- Diagnóstico de Termos ---")
termos_teste = ["hp", "elite", "mini", "800", "g9"]
for termo in termos_teste:
    count_title = df['titulo_norm'].str.contains(termo, na=False).sum()
    count_desc = df['desc_norm'].str.contains(termo, na=False).sum()
    print(f"Tickets contendo '{termo}': Título={count_title}, Descrição={count_desc}")
    
    # Show examples if few matches
    if count_title > 0 and count_title < 5:
        print(f"Exemplos Título '{termo}':", df.loc[df['titulo_norm'].str.contains(termo, na=False), col_titulo].tolist())
    if count_desc > 0 and count_desc < 5:
        # Truncate description for readability
        examples = df.loc[df['desc_norm'].str.contains(termo, na=False), col_desc].apply(lambda x: str(x)[:100]).tolist()
        print(f"Exemplos Descrição '{termo}':", examples)


# 6. Se não encontrar resultados — gerar relatório de diagnóstico e sair
output_dir = "/app/output"
if not os.path.exists("/app"):
    output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

if hp_tickets.empty:
    debug_path = os.path.join(output_dir, "debug_tickets_checagem.csv")
    df.to_csv(debug_path, index=False, sep=";")
    print("###### DEBUG REPORT ######")
    print("Nenhum ticket com título/descrição contendo:", busca_norm)
    print("Foram salvos todos os tickets no arquivo:", debug_path)
    
    result = {"status": "no_match_found", "matched_count": 0}
else:
    # 7. Se encontrar — continuar análise
    print("\n--- Análise dos Resultados Encontrados ---")
    
    # Status Distribution
    if 'Status' in df.columns:
        status_col = 'Status'
    else:
        status_col = next((c for c in df.columns if normalize(c) == "status"), None)

    if status_col:
        plt.figure(figsize=(8,5))
        hp_tickets[status_col].value_counts().plot(kind='bar')
        plt.title(f"Status - {busca}")
        plt.xlabel("Status")
        plt.ylabel("Contagem")
        plt.tight_layout()
        plot_path = os.path.join(output_dir, "hp_tickets_status_dist.png")
        plt.savefig(plot_path)
        print("Gráfico gerado:", plot_path)
        status_dist = hp_tickets[status_col].value_counts().to_dict()
    else:
        status_dist = {}
        print("Coluna de Status não identificada para gráfico.")

    # Top Entities
    if 'Entidade' in df.columns:
        summary = hp_tickets['Entidade'].value_counts().head(5).reset_index()
        summary.columns = ['Entidade', 'Count']
        print("Top entidades:", summary)
        top_entities = summary.to_dict(orient="records")
    else:
        top_entities = []

    result = {
        "status": "match_found",
        "matched_count": len(hp_tickets),
        "status_distribution": status_dist,
        "top_entities": top_entities
    }

# 8. Retornar result
out_path = os.path.join(output_dir, "diagnosis_result.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print("Resultado da análise gravado em:", out_path)
