# AI-Native Engineering Framework
> *A Foundation for Deterministic AI Development*

**Versão:** 1.0.0  
**Autor:** Trae AI (Post-Bet Loss Edition)  
**Destino:** Antigravity & Parceiros

---

## 🎯 Objetivo
Transformar o desenvolvimento assistido por IA de uma atividade probabilística ("espero que funcione") para uma engenharia determinística ("sei que funciona").

## 📜 Os 3 Pilares da Governança de IA

### 1. Spec-Driven Development (SDD)
**Regra de Ouro:** Nenhuma linha de código é gerada sem antes existir um documento de especificação (Markdown) validado por um humano.
*   A IA não deve "inventar" regras de negócio.
*   A IA deve "implementar" contratos definidos.
*   *Referência:* O sucesso do desenvolvimento aumenta drasticamente quando a IA atua como "implementadora de specs" e não "criadora de produtos".

### 2. Validação de Realidade (The "No-Mock" Rule)
**Regra de Ouro:** Funcionalidades que interagem com infraestrutura (DB, API, File System) **JAMAIS** devem ser validadas exclusivamente por mocks.
*   Todo projeto deve ter um script de `pre_flight_check.py` que valida credenciais e conexões reais.
*   Testes de Integração > Testes Unitários para código gerado por IA.

### 3. Prompts como Código (PaC)
**Regra de Ouro:** Prompts não são strings mágicas soltas no código. São artefatos versionados, tipados e testáveis.
*   Separação total entre Lógica (Python/JS) e Instrução (Prompts).
*   Uso de variáveis estruturadas (YAML/JSON) para inputs.

---

## 📊 Métricas de Desempenho (MCPs)

Para medir se a IA está ajudando ou atrapalhando:

| Métrica | Definição | Meta |
| :--- | :--- | :--- |
| **Hallucination Rate** | % de chamadas de tool/função com parâmetros inválidos (chaves inexistentes, tipos errados). | < 5% |
| **Integration Success** | % de código gerado que roda no ambiente real na 1ª tentativa (sem ajustes manuais). | > 80% |
| **Spec-to-Code Ratio** | Tempo gasto escrevendo Specs vs. Tempo gasto debugando código. | 2:1 (Gastar o dobro do tempo planejando) |
| **Self-Correction** | Capacidade do Agente de ler o erro e corrigir sem intervenção humana. | > 90% |

---

## 🛠️ Stack Tecnológico Recomendado

*   **IDE:** VS Code / Cursor / Trae (com acesso a terminal e contexto de arquivo).
*   **Linguagem de Scripting:** Python (pela facilidade de tipagem com Pydantic e integração com LLMs).
*   **Banco de Dados:** Dockerized PostgreSQL (Padrão ouro para consistência dev/prod).
*   **Validação de Dados:** Pydantic (Python) / Zod (JS) - **Obrigatório** para validar saídas de LLM.
*   **Testes:** Pytest (com markers de integração) / Jest.

---

## 🔄 Ciclo de Trabalho (Workflow)

1.  **Humano:** Cria `docs/specs/FEATURE_X.md`. Define entradas, saídas e regras.
2.  **Humano:** Executa `scripts/pre_flight_check.py` para garantir que o ambiente está saudável.
3.  **IA:** Lê a Spec e gera o código + Teste de Integração.
4.  **IA/Humano:** Roda o teste de integração.
5.  **Falha?** A IA lê o erro (stack trace real) e corrige. **NÃO SE USA MOCK AQUI.**
6.  **Sucesso?** Commit.

---

## 📂 Estrutura de Pastas Padrão

```
/
├── .ai/                  # Configurações de IA
│   ├── prompts/          # Templates de Prompt (YAML)
│   └── context/          # Contexto manual para o Agente
├── docs/
│   └── specs/            # Especificações de Funcionalidades
├── scripts/
│   └── pre_flight.py     # Validador de Ambiente Real
├── src/                  # Código Fonte
├── tests/
│   ├── unit/             # Testes de Lógica Pura
│   └── integration/      # Testes com DB/API Real (Obrigatório para IA)
└── Makefile              # Comandos padronizados
```
