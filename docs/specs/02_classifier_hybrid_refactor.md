# Spec: Refatoração Híbrida do Classificador (Hybrid Taxonomy)

## 1. Objetivo
Melhorar a precisão do Agente Classificador combinando a **atualidade** das categorias do GLPI (IDs e estrutura) com a **riqueza semântica** da taxonomia local (`taxonomy.yaml`).
Atualmente, o GLPI fornece IDs corretos mas descrições pobres. O YAML fornece descrições ricas mas IDs fictícios. A união dos dois cria o "Super Classificador".

## 2. Contratos de Dados

### Estrutura da Categoria Híbrida (Internal)
Objeto que será vetorizado no RAG.

| Campo | Tipo | Origem | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `str` | **GLPI** | ID Real do ticket para abertura. |
| `name` | `str` | **GLPI** | Nome oficial (ex: `Root > Hardware`). |
| `rich_text` | `str` | **YAML** | Texto otimizado para RAG (Keywords + Descrição). |
| `fallback` | `bool` | `System` | True se usou apenas dados do GLPI (sem match no YAML). |

## 3. Algoritmo de Fusão (Matching Strategy)

O algoritmo deve ser executado na inicialização do Agente (`__init__` ou `daemon` start).

1.  **Fetch GLPI:** Baixar todas as categorias ativas via API.
    *   Chave de Junção: `completename` (ex: `1. Hardware e Impressão > Computadores`).
2.  **Load YAML:** Carregar `taxonomy.yaml` local.
    *   Chave de Junção: `name` (Normalizar string para garantir match).
3.  **Merge:**
    *   Iterar sobre categorias do GLPI.
    *   Se `glpi.completename` == `yaml.name`:
        *   Usar `yaml.description` + `yaml.keywords` como fonte do Embedding.
    *   Se não houver match:
        *   Usar `glpi.comment` como fallback.
        *   Logar warning: "Categoria sem metadados ricos: {name}".

## 4. Definição da Classe (Pydantic Refactor)

```python
from pydantic import BaseModel, Field

class Taxon(BaseModel):
    id: str
    name: str
    description: str
    embedding_source: str
    score: float = 0.0
```

## 5. Regras de Negócio
1.  **Prioridade Semântica:** O texto do YAML **sempre** tem precedência sobre o comentário do GLPI para geração de embeddings.
2.  **Verdade do ID:** O ID do GLPI **sempre** é a fonte da verdade para a ação final de classificação/abertura.
3.  **Fail-safe:** Se o GLPI estiver offline, o agente deve falhar na inicialização (pois não pode classificar para IDs inexistentes), a menos que implementemos um cache de IDs. *Decisão: Falhar e alertar.*

## 6. Plano de Testes
- [ ] **Unitário:** Mockar retorno do GLPI e garantir que o Merge ocorre corretamente.
- [ ] **Integração:** Rodar script que lista quais categorias do GLPI "casaram" com o YAML e quais ficaram órfãs.
