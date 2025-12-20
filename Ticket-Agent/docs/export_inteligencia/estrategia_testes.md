# Estratégia de Testes

## 1. Casos de Teste Comparativos (Baseline vs Novo)

Crie um dataset de validação (`golden_dataset.json`) contendo inputs e resultados esperados.

### Exemplo de Dataset:
```json
[
  {
    "id": "T01",
    "input": "Meu mouse parou de funcionar",
    "expected_root": "Hardware",
    "expected_keywords": ["mouse", "periférico"]
  },
  {
    "id": "T02",
    "input": "Preciso liberar acesso para o estagiário novo na pasta de Rede",
    "expected_root": "Acesso",
    "expected_keywords": ["pasta", "rede", "permissão"]
  },
  {
    "id": "T03",
    "input": "O sistema SAP está dando erro 500",
    "expected_root": "Software",
    "expected_keywords": ["erro", "sistema", "sap"]
  }
]
```

## 2. Script de Verificação de Consistência
Desenvolver um script Python (`validate_migration.py`) que:
1.  Instancia o `ClassifierService` novo.
2.  Itera sobre o dataset.
3.  Compara o resultado obtido com o esperado.
4.  Gera relatório de "Pass/Fail".

## 3. Testes de Integração
- **Teste de Conectividade LLM**: Verificar se o novo agente consegue alcançar o Ollama (ping/health check).
- **Teste de Leitura de Arquivo**: Verificar se o `categories_list.json` é carregado corretamente (contagem de itens em memória deve ser > 0).

## 4. Testes de Regressão de Performance
- Medir o tempo de resposta médio para 50 requisições sequenciais.
- Se o tempo aumentar > 20% em relação ao original, investigar overhead de rede ou serialização no novo projeto.
