# 20 — Prompt: Pesquisa e Investigação (Modo Estudo)

*Este é um artefato histórico usado para orientar a fase de pesquisa do agente.*

---

## Papel do Agente
Você está atuando exclusivamente como **pesquisador, analista técnico e validador conceitual**.
Você **NÃO** deve alterar código de produção.

## Objetivo
Estudar profundamente as inconsistências identificadas nos testes de simulação (Efeito Goldfish, Perfeccionismo, Loops).

## Linhas de Pesquisa

### 1. Memória em Agentes Conversacionais
- Diferença entre Context Window, Sliding Window, Short/Long-term memory.
- Por que confiar apenas no histórico (chat log) falha.

### 2. State-Driven vs Chat-Driven
- Comparar arquiteturas puramente conversacionais vs guiadas por máquina de estados (State-Driven).
- Investigar Slot Filling e abordagens híbridas.

### 3. Extração Explícita (NER / Slot Filling)
- Pipelines dedicados de extração vs extração durante a conversa.
- Persistência de entidades.

### 4. Validação Semântica Relaxada
- Como interpretar termos vagos ("quebrou", "não funciona") sem loops de validação rígida.

### 5. Estratégias de Pinning
- Fixação da intenção inicial para evitar deriva de contexto (Context Drift).

## Resultado Esperado
Conhecimento sólido documentado para evoluir a arquitetura de "Conversa Pura" para "State-Driven", sem implementação imediata.
