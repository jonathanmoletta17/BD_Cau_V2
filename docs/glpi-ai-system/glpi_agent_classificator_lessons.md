# Lições Aproveitadas do GLPI Agent Classificator

## Prompt Engineering e Preparação de Texto
- Estrutura de prompts: contexto, persona, tarefa, formatos de entrada/saída, regras, exemplos, edge cases.
- Pré-processamento (aplicável ao `glpi_agent/preprocess.py`):
  - Lowercase, expansão de abreviações comuns (pq→porque, vc→você, ñ→não), remover ruído, normalizar espaços.
  - Combinar título+descrição com peso maior ao título (2:1) para embeddings.
  - Remover dados pessoais e manter jargão técnico.
- Detecção de qualidade de texto: tickets curtos/somente números devem ir para triagem manual.

## Descrições Ricas de Categorias
- Template para contexto: definição formal, escopo, tipos de problema, palavras-chave (técnicos/usuário/sinônimos), exemplos e contra-exemplos, regras objetivas e casos limítrofes.
- Aplicação: reforça `tools/generate_rich_contexts.py` e `agent/manual_contexts.json` com diferenciadores e exemplos negativos.

## Embeddings vs Fine-Tuning
- Embeddings + similaridade: alta flexibilidade e baixo custo; ideal para nossa taxonomia dinâmica.
- Fine-tuning: considerar somente com dataset balanceado e grande; custo/complexidade altos.
- Calibração de thresholds e margem entre Top-1 e Top-2 para reduzir ambiguidade (já contemplado em `agent_classification_rules.md`).

## Governança dos Dados
- Evitar ciclo vicioso de rótulos ruins; usar auditoria (fila de discrepâncias) e limpeza assistida (já implementado em `auto_clean_dataset.py`).
- Manter “Gold Set” validado e medir periodicamente (`evaluate_accuracy.py`).

## Replicação e Sandbox
- Replicação (prod→teste) com mapeamento de IDs: já suportada por `glpi_agent/migration.py`.
- Proteções: operações de escrita apenas em teste; produção read-only.

## Próximas Integrações
- Expandir `preprocess.py` com normalização adicional baseada nas regras acima.
- Enriquecer `manual_contexts.json` com exemplos negativos e critérios formais por categoria.
- Adicionar verificação de ambiguidade Top-1 vs Top-2 no agente (`simple_agent`), derivado das recomendações.
