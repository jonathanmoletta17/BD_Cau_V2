# Estudo de Modelos — Classificação, LLMs e Aplicações no BD_Cau_V2

## 1. Taxonomia de Modelos

- **Descritivo**
  - Objetivo: descrever padrões e tendências; sumarização e exploração.
  - Exemplos no projeto: métricas e dashboards (`glpi-dtic-dashboard`, `glpi-sis-dashboard`).
- **Inferencial**
  - Objetivo: responder hipóteses com decisão estatística (p-valor, IC).
  - Exemplo no projeto: não há testes formais; usamos validação com F1/precision/recall.
- **Preditivo (Discriminativo)**
  - Objetivo: prever/atribuir rótulos para novos dados (classificação/regressão).
  - Exemplo no projeto: agente de classificação de tickets por categoria.
- **Mecanicista vs Empírico**
  - Mecanicista: baseado em leis/teoria explícita.
  - Empírico: derivado de dados/algoritmos (ML). Nosso agente é empírico.
- **Determinista vs Não Determinista**
  - Determinista: mesmas entradas ⇒ mesma saída. Embeddings + similaridade são deterministas.
  - Não determinista: envolve aleatoriedade (amostragem em LLMs). LLM via Ollama é não determinista por padrão.
- **Discreto vs Contínuo**
  - Discreto: escolhe entre classes finitas. Classificação de tickets é discreta.
  - Contínuo: estima valores reais (ex.: tempo de resolução previsto).
- **Matemático vs Algorítmico/Computacional**
  - Matemático: formulações fechadas/analíticas.
  - Algorítmico: implementação em código/heurísticas/ML. Nossos agentes de NLP são algorítmicos.

## 2. O Que Usamos Hoje (por app/contexto)

- **Agente Classificador de Tickets (DTIC)**
  - Tipo: empírico, determinista, discreto, preditivo (classificação semântica).
  - Modelo: `intfloat/multilingual-e5-large` (embeddings Transformer encoder-only).
  - Referência: `glpi-dtic-agent-classificator/docs/ai_concepts_embeddings_finetuning.md:16`.
  - Funcionamento: texto → vetor; decisão por `cosine_similarity` com contextos de categoria.
  - Artefatos: `agent/category_context.json` mantém descrições canônicas (`glpi-dtic-agent-classificator/agent/category_context.json:29`).
  - Validação: F1/precision/recall; guia em `glpi-dtic-agent-classificator/docs/validation_guide.md`.

- **Stack de LLM Local (Ollama + Llama 3)**
  - Tipo: empírico, não determinista (sampling), gerativo.
  - Uso: redação, explicação, boilerplate, automações assistidas; secundário no fluxo de classificação.
  - Referência: instruções de uso e configuração em `TRAE_ONBOARDING.md:163`.
  - Modelos sugeridos: `llama3:13b` (também existem variantes menores como ~3B). Métricas de latência em `local-ai-stack/models.md:144`.

- **Smart Search (DTIC/SIS)**
  - Tipo: algorítmico determinista (ranking por pesos e regras), descritivo/preditivo leve.
  - Referência: lógica de pesos em `docs/glpi_analysis/03_metricas_regras_negocio.md:52`.

- **Data Service V3**
  - Tipo: serviço de dados (não é modelo); fornece integridade, métricas e APIs.
  - Referência: `glpi-data-service-v3/src/main.py:45` (saúde) e módulos de entidades/categorias.

## 3. Comparação — Ollama 3B vs Classificador de Tickets

- **Objetivo**
  - Ollama 3B (LLM): gerar texto, responder, planejar; pode classificar via prompt, porém com variância e latência.
  - Classificador (E5-Large): atribuir categoria com consistência e baixa latência.
- **Determinismo**
  - Ollama: não determinista (temperature/top‑p); pode fixar com `temperature=0`, ainda sujeito a engenharia de prompt.
  - E5: determinista (mesma entrada ⇒ mesma saída/score).
- **Performance**
  - Ollama 3B: menor VRAM que 13B, mas ainda segundos de latência; throughput limitado.
  - E5: milissegundos por amostra; adequado para lote/tempo real.
- **Custo/Manutenção**
  - Ollama: manutenção de runtime/container e VRAM; melhor para tarefas gerativas.
  - E5: simples de operar; ideal para classificação massiva.
- **Precisão esperada**
  - Ollama: sensível a prompt/contexto; sem fine‑tune, pode oscilar.
  - E5: alta precisão com contextos curados e limiares de confiança.

## 4. Quando Usar Cada Um

- **Embeddings (E5-Large)**
  - Classificação de tickets, deduplicação, busca semântica, clustering.
  - Garante estabilidade, baixa latência e interpretabilidade de decisão (scores).
- **LLM (Ollama 3B/13B)**
  - Geração de respostas, sumarização assistida, criação de playbooks, explicação ao usuário.
  - Útil como fallback: se diferença de scores entre 1º e 2º lugar < margem, pedir julgamento do LLM.

## 5. Boas Práticas e Riscos

- **Curadoria de Contextos**
  - Manter descrições canônicas e exemplos negativos no `category_context.json`.
- **Higiene de Dados**
  - Remover HTML/boilerplates antes de gerar embeddings.
- **Margens de Decisão**
  - Implementar “zona cinzenta” para casos ambíguos; acionar revisão humana/LLM.
- **Observabilidade**
  - Registrar relatórios diários do agente (`glpi-dtic-agent-classificator/agent/simple_agent.py:104`).

## 6. Mapeamento por Casos de Uso (Projeto)

- **Classificar Tickets GLPI** → Embeddings deterministas (E5-Large).
- **Explicar decisão ao operador** → LLM (Ollama) para texto natural.
- **Busca Inteligente (DTIC/SIS)** → Algorítmico determinista com pesos.
- **Dashboards** → Descritivo (agregações) em Data Service.

## 7. Recomendação Executiva

- **Produção**: manter o classificador baseado em embeddings como motor principal para categorias.
- **Híbrido**: integrar LLM como apoio em ambiguidade e geração de comunicação com usuários.
- **Governança**: curadoria contínua de contextos e validação com F1, revisão mensal.

