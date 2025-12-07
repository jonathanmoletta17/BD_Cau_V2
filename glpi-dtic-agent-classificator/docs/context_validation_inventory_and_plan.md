# Inventário, Manutenção e Plano de Limpeza — Context Validation

## 1. Visão Geral
- Escopo: `tools/`, `reports/`, `docs/` dentro de `crawl4ai/context-validation/`.
- Objetivo: mapear propósito, dependências, uso e riscos; definir critérios objetivos de manutenção/limpeza e um plano validado em fases.

## 2. Inventário por Pasta

### 2.1 `tools/` (scripts utilitários)
- `audit_dataset.py`
  - Propósito: roda o `agent.simple_agent` sobre `data/datasets/validation_dataset.json` para detectar divergências humano vs IA e salvar em `data/audit_queue.json`.
  - Entradas: `agent/simple_agent.py`, `category_context.json`, dataset de validação, libs `torch`, `sentence_transformers`.
  - Saídas: `data/audit_queue.json` (ordenado por confiança desc).
  - Relações: alimenta `app_audit.py`, `auto_clean_dataset.py` e análises (`analyze_audit_queue.py`).
  - Risco/Impacto remoção: alto (quebra o fluxo de auditoria). Compatibilidade: requer GPU/CPU com `torch` e `sentence-transformers`.

- `app_audit.py`
  - Propósito: UI Streamlit para julgar conflitos na fila (`audit_queue.json`) e salvar decisões humanas em `audit_decisions.json`.
  - Entradas: `data/audit_queue.json`, `agent/manual_contexts.json`.
  - Saídas: `data/audit_decisions.json`.
  - Relações: precede `apply_audit.py` e `auto_clean_dataset.py`.
  - Risco/Impacto remoção: médio/alto (perde interface de revisão). Compatibilidade: `streamlit` instalado.

- `apply_audit.py`
  - Propósito: aplica decisões de auditoria no dataset, gerando `validation_dataset_CLEAN.json`.
  - Entradas: `validation_dataset.json`, `audit_decisions.json`.
  - Saídas: `validation_dataset_CLEAN.json`.
  - Relações: validação posterior via `evaluate_accuracy.py`.
  - Risco/Impacto remoção: médio (impede formalização do dataset limpo).

- `auto_clean_dataset.py`
  - Propósito: resolve automaticamente parte da fila usando regras e limiares (`CONFIDENCE_THRESHOLD`), atualiza dataset e reduz fila para revisão manual.
  - Entradas: `validation_dataset.json`, `audit_queue.json`, `audit_decisions.json`.
  - Saídas: `validation_dataset_CLEAN.json`, sobrescreve `audit_queue.json` (faz `.bak`).
  - Relações: acelera saneamento; referenciado em `docs/agent_control_map.md`.
  - Risco/Impacto remoção: médio (perde automação). Compatibilidade: regras internas específicas (ex.: `AJUDA E SUPORTE`).

- `evaluate_accuracy.py`
  - Propósito: mede a precisão do classificador; gera `reports/accuracy_report_*.json` e imprime relatório.
  - Entradas: `agent/category_context.json`, `validation_dataset.json` (ou CLEAN), `SentenceTransformer` E5-Large.
  - Saídas: JSON com detalhes, métricas e pares de confusão.
  - Relações: consumido por `show_report.py`, `analyze_errors.py`, `generate_diagnostic.py`, `force_clean_from_report.py`.
  - Risco/Impacto remoção: alto (perde medição objetiva).

- `fetch_validation_data.py`
  - Propósito: busca tickets categorizados no GLPI (ambiente de teste) e incrementa o dataset de validação.
  - Entradas: `glpi_agent.glpi_client`, `glpi_agent.preprocess.join_title_description`.
  - Saídas: atualiza `data/datasets/validation_dataset.json`.
  - Relações: alimenta avaliação e auditoria.
  - Risco/Impacto remoção: médio (perde ingestão incremental). Compatibilidade: credenciais GLPI e conectividade.

- `deploy_to_test.py`
  - Propósito: aplica reclassificação em massa no GLPI de teste via `SimpleAgent` (pagina tickets e chama `process_ticket`).
  - Entradas: `agent.simple_agent`, cliente GLPI embutido.
  - Saídas: atualizações no GLPI (ambiente `test`), logs `deploy_log_*.txt`.
  - Relações: valida hipóteses em sandbox; não deve apontar para produção.
  - Risco/Impacto remoção: alto para fluxo de validação em ambiente; crítico se mal configurado (proteções já previstas).

- `analyze_audit_queue.py`
  - Propósito: sumariza padrões de discrepância `human_label -> ai_label`, com estatística de confiança.
  - Entradas: `data/audit_queue.json`.
  - Saídas: console; insights de top padrões.
  - Relações: suporte a priorização de limpeza.
  - Risco/Impacto remoção: baixo/médio (perde diagnóstico rápido).

- `analyze_errors.py`
  - Propósito: leitura do último `accuracy_report_*.json` e detalhamento de erros por categoria e pares de confusão.
  - Entradas: `reports/accuracy_report_*.json`.
  - Saídas: console.
  - Relações: suporte à análise estratégica (`docs/analysis_results.md`).
  - Risco/Impacto remoção: baixo (diagnóstico).

- `analyze_errors_deep.py`
  - Propósito: consolida erros com textos do dataset; agrupa por par (verdadeiro, predito) e mostra exemplos.
  - Entradas: `reports` (hardcoded), `data/datasets/validation_dataset.json` (hardcoded).
  - Saídas: console.
  - Relações: inspeção manual aprofundada.
  - Risco/Impacto remoção: baixo. Compatibilidade: caminhos absolutos — sugerir refatorar para relativos.

- `force_clean_from_report.py`
  - Propósito: corrige automaticamente casos onde humano usou categoria genérica (`AJUDA E SUPORTE`) e IA sugeriu específica, com confiança.
  - Entradas: `reports/accuracy_report_*.json`, dataset (CLEAN ou original).
  - Saídas: atualiza dataset alvo.
  - Relações: pós-avaliação para reduzir ruído.
  - Risco/Impacto remoção: médio.

- `inspect_errors.py`
  - Propósito: escreve amostra dos erros focando a categoria genérica alvo em `data/error_inspection.txt`.
  - Entradas: último relatório, dataset CLEAN.
  - Saídas: arquivo de inspeção textual.
  - Relações: suporte ao trabalho humano.
  - Risco/Impacto remoção: baixo.

- `generate_diagnostic.py`
  - Propósito: transforma o relatório de accuracy em `reports/baseline_diagnostico.md` (markdown legível).
  - Entradas: último `accuracy_report_*.json`.
  - Saídas: `baseline_diagnostico.md`.
  - Relações: documentação operacional.
  - Risco/Impacto remoção: baixo.

- `generate_rich_contexts.py`
  - Propósito: gera contextos descritivos por categoria com base nos tickets (termos, n-gramas), respeitando `manual_contexts.json`.
  - Entradas: `validation_dataset.json`, `agent/category_context.json`, `manual_contexts.json`.
  - Saídas: atualiza `agent/category_context.json` + `category_context_BACKUP.json`.
  - Relações: impacta diretamente a qualidade de classificação; usado antes de `evaluate_accuracy.py`.
  - Risco/Impacto remoção: alto (perde mecanismo de evolução dos contextos).

- `read_latest_report.py`
  - Propósito: gera `reports/summary_latest.txt` com métricas resumidas do último relatório.
  - Entradas: `reports/*.json`.
  - Saídas: `reports/summary_latest.txt`.
  - Relações: visões rápidas (consumido por humanos).
  - Risco/Impacto remoção: baixo.

- `show_report.py`
  - Propósito: imprime resumo amigável do último relatório (top erros e categorias problemáticas).
  - Entradas: `reports/accuracy_report_*.json`.
  - Saídas: console.
  - Relações: diagnóstico rápido.
  - Risco/Impacto remoção: baixo.

### 2.2 `reports/` (resultados e diagnósticos)
- `accuracy_report_YYYYMMDD_HHMMSS.json`: relatórios gerados por `evaluate_accuracy.py` (diversos arquivos no dia 2025-12-06).
- `baseline_diagnostico.md`: gerado por `generate_diagnostic.py`; análise de pares de confusão e categorias.
- `automation_validation_report.md`: relatório textual manual/automatizado de validação.
- `summary_latest.txt`: resumo do último relatório. Atual: `Accuracy Total/Valid: 84.89%`; top categorias com erros incluem `AJUDA E SUPORTE` e `IMPRESSORA`.

### 2.3 `docs/` (documentação técnica)
- Conteúdos principais e relações:
  - `project_architecture.md`: mapa dos componentes (`glpi_client`, `simple_agent`, scripts de análise).
  - `conceptual_architecture.md`: pipeline ideal (normalização, recuperação híbrida, thresholds dinâmicos).
  - `agent_classification_rules.md`: regras operacionais, thresholds e critérios de ação do agente.
  - `agent_control_map.md`: pontos de controle; referencia `tools/auto_clean_dataset.py`.
  - `data_audit_design.md`: design do fluxo de auditoria e UI; referencia `app_audit.py`.
  - `analysis_results.md`: sínteses e próximos passos; referencia `evaluate_accuracy.py`, `app_audit.py`, `apply_audit.py`.
  - `INC_2025_001_Technical_Inconsistencies.md`: relatório formal de inconsistências; referencia execução de `evaluate_accuracy.py` com V1/V2 de contextos.
  - `category_guide.md`, `context_json_proposal.md`, `validation_guide.md`: guias de categorias, estrutura de contexto e validação/calibração.
  - `audit_report_2025.md`: auditoria das fontes de inconsistência e roadmap.

## 3. Dependências e Compatibilidade
- Internas:
  - `agent/simple_agent.py`, `agent/category_context.json`, `agent/manual_contexts.json`.
  - `glpi_agent/glpi_client.py`, `glpi_agent/preprocess.py`.
  - `data/datasets/*.json`, `data/audit_queue.json`, `data/audit_decisions.json`.
- Externas (pip): `torch`, `sentence-transformers`, `streamlit`.
- Ambiente: acesso ao GLPI (ambiente `test`), `.env` com credenciais; filesystem com permissões de escrita em `data/` e `reports/`.
- Observação de compatibilidade: `analyze_errors_deep.py` usa caminhos absolutos Windows — refatorar para relativos baseados em `PROJECT_ROOT`.

## 4. Uso e Frequência (última modificação)
- `tools/`: todos atualizados em 2025-12-06 (ativos). Tamanhos variam de ~1.3KB a ~12KB.
- `reports/`: múltiplos `accuracy_report_*` gerados em 2025-12-06; `summary_latest.txt` atualizado.
- `docs/`: vários documentos atualizados recentemente (inclui `INC_2025_001_*` em 2025-12-06).
- Referências cruzadas (código): docs mencionam diretamente `evaluate_accuracy.py`, `auto_clean_dataset.py`, `app_audit.py`, `apply_audit.py`. Outros módulos (`glpi-agent-classificator/docs`) mencionam scripts ausentes (`extract_prod_categories.py`) — sinalizam obsolescência externa.

## 5. Critérios Objetivos para Limpeza/Manutenção
- Remoção/arquivamento:
  - Não referenciado em código ou docs por ≥ 60 dias.
  - Sem execução recente e sem saída consumível (`reports`/`data`).
  - Duplicidade funcional com outro script/documento mais atualizado.
  - Caminhos hardcoded e side-effects perigosos sem proteção (ex.: apontar produção).
- Manter/refatorar:
  - Parte do pipeline core (`audit_dataset.py`, `evaluate_accuracy.py`, `generate_rich_contexts.py`).
  - UI de auditoria (`app_audit.py`) e aplicação (`apply_audit.py`).
  - Scripts de ingestão (`fetch_validation_data.py`) e deploy de teste (`deploy_to_test.py`).
- Compatibilidade a documentar:
  - Dependência de `torch`/GPU (performance) e `sentence-transformers`.
  - `streamlit` para UI.
  - Conexões GLPI (ambiente `test`).

## 6. Checklist de Avaliação (por tipo)
- Scripts (`tools/`):
  - Ver docstring/cabeçalho e side-effects (escritas, GLPI).
  - Ver referências (`grep` no repo) e uso em docs.
  - Ver última modificação e tamanho (proxy de atividade).
  - Ver caminhos (relativos vs absolutos) e variáveis de ambiente.
  - Validar dependências internas/externas e executar em sandbox.
- Relatórios (`reports/`):
  - Mantém últimos N dias (ex.: 7); arquiva anteriores.
  - Ver consistência de métricas e integridade do JSON.
  - Validar `summary_latest.txt` após geração.
- Documentos (`docs/`):
  - Ver referências atualizadas (links para scripts/pastas).
  - Evitar redundância; consolidar guias correlatos.
  - Atualizar histórico/versão.

## 7. Decisões por Item (estado inicial)
- Manter (core): `audit_dataset.py`, `app_audit.py`, `apply_audit.py`, `auto_clean_dataset.py`, `evaluate_accuracy.py`, `generate_rich_contexts.py`.
- Manter (diagnóstico): `analyze_audit_queue.py`, `analyze_errors.py`, `show_report.py`, `generate_diagnostic.py`, `inspect_errors.py`, `read_latest_report.py`.
- Manter com refatoração: `analyze_errors_deep.py` (remover caminhos absolutos; usar `PROJECT_ROOT`).
- Manter com atenção: `deploy_to_test.py` (validar ambiente `test`; proteger contra produção).
- `reports/`: limpar arquivos de mais de 7 dias via tarefa de housekeeping; manter `baseline_diagnostico.md` e último `summary_latest.txt`.
- `docs/`: manter; consolidar conteúdos correlatos em releases futuros (evitar duplicação entre `conceptual_architecture.md` e `project_architecture.md`).

## 8. Plano de Limpeza (fases controladas)
- Fase 1 (Baixo risco):
  - Arquivar `reports/accuracy_report_*` com mais de 7 dias (mover para `reports/archive/`).
  - Refatorar `analyze_errors_deep.py` para caminhos relativos.
- Fase 2 (Médio risco):
  - Padronizar geração/uso de `validation_dataset_CLEAN.json` nos scripts consumidores.
  - Revisar regras em `auto_clean_dataset.py` (parametrizar categorias genéricas via config).
- Fase 3 (Alto impacto):
  - Revisar `deploy_to_test.py` com feature flag explícita e checagem de ambiente.
  - Consolidar documentação (`docs/`) e publicar versãoada.

## 9. Validação
- Após cada remoção/refatoração significativa:
  - Rodar `python tools/evaluate_accuracy.py` e verificar geração do último `accuracy_report_*.json`.
  - Rodar `python tools/read_latest_report.py` e validar `summary_latest.txt`.
  - Abrir `app_audit.py` em modo streamlit e validar leitura/escrita (`audit_queue.json`, `audit_decisions.json`).
  - Executar `generate_rich_contexts.py` e inspecionar `category_context.json` + backup.

## 10. Registro e Rollback
- Manter changelog técnico em `docs/maintenance_log.md` (data, ação, arquivos afetados, motivo, responsável).
- Usar controle de versão (git) e tags para marcos (antes/depois da limpeza).
- Sempre criar backups (`*.bak`) ao sobrescrever dados (`audit_queue.json`, `category_context.json`).

## 11. Observações adicionais
- Cross-projeto: `glpi-agent-classificator/docs` referencia `context-validation/tools` com scripts inexistentes (`extract_prod_categories.py`, `extract_prod_entities.py`). Decisão: revisar e alinhar documentação externa; marcar como desatualizada até ajuste.
- Métrica atual: `summary_latest.txt` indica `Accuracy ~84.89%` pós-limpeza — manter como baseline e comparar após próximas fases.
