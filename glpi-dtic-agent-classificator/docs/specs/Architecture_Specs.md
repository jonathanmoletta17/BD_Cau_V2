# Especificação de Arquitetura: Agente de Classificação GLPI

> **Origem:** Migrado do contexto do Trae (.trae) em Dez/2025.
> **Status:** Draft / Baseline

## Visão Geral
- Desenvolver um agente de classificação para tickets GLPI com NLP + GPU (CUDA), operando em dois modos: agendado e webhook.
- Alvo: precisão ≥90%, latência média <1.5s/ticket, logging detalhado, métricas em tempo real, rollback seguro.
- Integração com GLPI via API oficial, usando `USER TOKEN` e `APP TOKEN` fornecidos.

## Arquitetura
- Componentes:
  - `GLPI Client`: sessão (`initSession`), busca/atualização de tickets, consulta de `searchOptions` e campos (categoria).
  - `Taxonomia`: ingestão de `glpi.csv`, construção de árvore hierárquica de categorias e subcategorias, deduplicação, normalização.
  - `NLP Engine`: pré-processamento (limpeza, normalização PT-BR), embeddings semânticos em GPU, classificação zero-shot e supervisionada.
  - `Decision Engine`: pontuação, thresholds, regras de discrepância e fila de revisão.
  - `Logger & Metrics`: logs estruturados (JSON), métricas (latência, precisão, throughput), relatório diário.
  - `Scheduler & Webhook`: execução periódica (cron/Task Scheduler) e servidor HTTP para triggers.
  - `Rollback & Sandbox`: modo dry-run e reversão de alterações críticas.
- Fluxo:
  - Ingestão → Pré-processamento → Embeddings → Ranking de categorias → Decisão (auto, recategorização, revisão) → Atualização GLPI → Logging/Métricas.

## Dados & Taxonomia (agent/category_context.json)
- Ler `agent/category_context.json`.
- Interpretar hierarquia por separador `>`; remover duplicatas; padronizar nomes (casefold, espaços, acentos).
- Gerar embeddings estáticos das categorias e subcategorias (cache em GPU/CPU, warm-up on start).
- Opcional: enriquecer com sinônimos/termos relacionados (glossário interno) para melhorar recall sem afetar precisão.

## Modelos & NLP (GPU)
- Pré-processamento PT-BR: normalização, remoção de ruído, lematização opcional, detecção de linguagem.
- Embeddings multilíngues otimizados para português:
  - Preferência: `intfloat/multilingual-e5-large` ou `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (PyTorch + CUDA).
- Classificação:
  - Estágio 1 (Zero-shot): similaridade coseno ticket ↔ categorias; rápido e robusto.
  - Estágio 2 (Supervisionado): pequena cabeça neural (PyTorch) treinada em histórico de tickets GLPI com categorias validadas; melhora a precisão para ≥90%.
- Performance:
  - Pré-carregar modelo em `cuda:0`, usar `fp16` com autocast, batch quando aplicável, cache de embeddings de categorias.

## Decisão & Regras
- Pontuação base: `score = softmax(similaridades)` ou normalização de cosenos.
- Não categorizados:
  - Auto-confirmação se `score_top ≥ 95%`.
  - Fila de revisão se `95% > score_top ≥ 80%` e `Δ < 15%`.
  - Propor recategorização se `score_top ≥ 85%` e `Δ ≥ 15%`.
- Já categorizados:
  - Manter se `score_categoria_atual > 90%`.
  - Ignorar casos marginais se `Δ < 5%`.
  - Propor recategorização se existir outra categoria com `score` maior e `Δ ≥ 15%`.
- Subcategorias:
  - Após escolher categoria pai, explorar filhos; selecionar subcategoria se `score_sub ≥ score_pai + 5%` e `score_sub ≥ 85%`.

## Integração GLPI
- Autenticação: `initSession` com `Authorization: user_token ...` e `App-Token: ...`; usar `Session-Token` nas chamadas seguintes.
- Tickets:
  - Buscar não categorizados: campo categoria vazio (`itilcategories_id` == null) via `searchOptions` + `search`.
  - Buscar já categorizados: coletar título/descrição/categoria atual.
  - Atualizar categoria/subcategoria: `Update item(s)` para `Ticket` com rollback metadata.
- Justificativas:
  - Adicionar `followup` privado com rationale técnico, `score`, `Δ`, categoria sugerida.
- Fila de revisão:
  - Marcar com etiqueta interna (comentário/flag), e manter lista no agente para triagem manual.

## Logging & Métricas
- Logging estruturado: `timestamp`, `ticket_id`, `ação`, `categoria_atual`, `categoria_sugerida`, `score_top`, `Δ`, `modo` (cron/webhook), `latência_ms`, `erro`.
- Métricas:
  - Latência média, p95, throughput, taxa de auto-confirmação, taxa de recategorização, acurácia (em dataset validado).
  - Expor endpoint `/metrics` (Prometheus) no modo servidor.
- Relatórios diários:
  - `tickets processados`, `categorizações alteradas`, `precisão`, `tempos (média/p95)`, `fila revisão`.

## Performance & Qualidade
- Alvos:
  - Precisão ≥90%: treinar com histórico de tickets; validação estratificada; métricas macro/micro F1.
  - <1.5s/ticket: cache de modelos, GPU warm-up, inferência em `fp16`, minimização de I/O.
- Benchmarks:
  - Comparar zero-shot vs supervisionado; medir latência por etapa; otimizar batch e pipeline.

## Robustez & Segurança
- Exceções: timeouts GLPI, indisponibilidade GPU, erros de rede, inconsistências CSV.
- Retentativas exponenciais e circuit breaker para GLPI.
- SSL:
  - Preferir `https://10.72.16.202/...` com `verify=True`; suportar CA custom se necessário.
- Segredos:
  - Tokens via variáveis de ambiente; nunca logar credenciais; mascarar em erros.
- Rollback:
  - Registrar estado anterior; função de reversão por `ticket_id` ou lote diário.
- Sandbox:
  - Modo dry-run: não aplicar atualizações, apenas registrar sugestões e métricas.

## Modos de Operação
- Agendado:
  - Windows Task Scheduler ou serviço em WSL; verifica tickets novos/pendentes em intervalos.
- Webhook:
  - Servidor leve (FastAPI/Flask) recebe eventos; processa ticket em tempo real; endpoint protegido e com SSL.

## Implementação (Módulos)
- `config`: URL, tokens, thresholds, SSL, device.
- `glpi_client`: sessão, busca, atualização, followups.
- `taxonomy`: parser CSV, árvore, embeddings das categorias.
- `preprocess`: pipeline PT-BR.
- `embeddings`: carregamento de modelos, caching e inferência GPU.
- `classifier`: zero-shot + cabeça supervisionada PyTorch.
- `decision`: regras, thresholds, seleção de subcategoria.
- `queue`: fila interna para revisão manual.
- `logger_metrics`: logging JSON, métricas/endpoint.
- `scheduler_webhook`: cron e servidor webhook.
- `rollback_sandbox`: trilha de auditoria e reversões.

## Validação
- Construir dataset com tickets históricos (título+descrição+categoria), dividir treino/validação/teste.
- Medir acurácia, F1, confusão; ajuste de thresholds para metas.
- Testes de carga para latência; avaliar p95/p99.

## Entregáveis
- Agente executável (serviço) com documentação de uso.
- Configuração segura (env vars), scripts de agendamento, servidor webhook.
- Relatórios diários e endpoint de métricas.
- Plano de rollback e sandbox habilitado.

## Próximos Passos
- Confirmar uso de `https` no endpoint GLPI e disponibilidade de certificado.
- Escolher modelo de embeddings multilíngue primário para PT-BR.
- Autorizar acesso de leitura a tickets históricos para treino.
- Validar campos exatos de categoria via `searchOptions` no GLPI.
