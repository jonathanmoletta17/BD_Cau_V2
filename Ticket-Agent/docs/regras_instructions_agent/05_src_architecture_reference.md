# Referência de Arquitetura Técnica (`src/`)

## 1. Visão Geral e Princípios Arquitetônicos

O código fonte do Ticket Agent segue uma arquitetura **Config-Driven Development (CDD)** e **State-Driven Design**. O objetivo central é desacoplar completamente a lógica de processamento ("Cérebro") das regras de negócio e comportamento ("Personalidade/Regras").

### Princípios Fundamentais

1.  **Separação Lógica vs. Configuração**:
    *   **Lógica (`src/agent/*.ts`)**: Código TypeScript imutável que sabe *como* processar regras, mas não *quais* são as regras. Não contém `if (intent === 'RESET_PASSWORD')` hardcoded (salvo exceções de fallback muito específicas).
    *   **Configuração (`src/agent/config/*.json`)**: Arquivos JSON que definem *o que* o agente faz. Novas intenções, campos e fluxos são criados aqui, sem recompilar o código.

2.  **Máquina de Estados (Triage Graph)**:
    *   O processo de atendimento é modelado como um grafo de estados.
    *   Cada interação do usuário transforma o estado atual (`AgentState`) em um novo estado, acumulando informações até atingir a completude.

3.  **Abordagem Híbrida e Determinística**:
    *   Prioriza-se métodos determinísticos (Keywords, Regex, Regras de Inferência) para velocidade e previsibilidade.
    *   LLMs (Large Language Models) são usados apenas como *fallback* (último recurso) ou para tarefas complexas de interpretação que falharam nas regras estáticas.

---

## 2. Estrutura de Diretórios e Arquivos

```text
src/
├── agent/
│   ├── config/                 # A "Alma" do agente (Regras de Negócio)
│   │   ├── intents.json        # Definição de intenções e palavras-chave
│   │   ├── inference_rules.json# Regras de extração (Regex, Keywords contextuais)
│   │   ├── schemas.json        # Estrutura de dados esperada (Zod schemas)
│   │   ├── policies.json       # Configurações globais (mensagens, retries)
│   │   └── inquiry_templates.json # Templates de perguntas para o usuário
│   │   
│   ├── config_loader.ts        # Gerenciador de carregamento das configs (Singleton)
│   ├── router.ts               # Classificador de Intenções (Keyword -> LLM)
│   ├── extractor.ts            # Extrator de Entidades (Inference -> Regex -> Fallback)
│   ├── validator.ts            # Validador de Schema (Zod Dinâmico)
│   ├── graph.ts                # Orquestrador do Fluxo (Triage Graph)
│   └── schema.ts               # Definições de Tipos TypeScript e Zod
│
├── index.ts                    # Ponto de entrada (CLI / API)
└── benchmark_golden.ts         # Script de validação contra Golden Dataset
```

---

## 3. Componentes Core

### 3.1. ConfigManager (`config_loader.ts`)
Responsável por carregar, validar e fornecer acesso tipado às configurações JSON. Atua como a "Single Source of Truth" para as regras de negócio.

### 3.2. RouterConfigDriven (`router.ts`)
Realiza a classificação da intenção do usuário em duas etapas:
1.  **Fast Path (Determinístico)**: Verifica correspondência exata de palavras-chave definidas em `intents.json`. Alta performance e custo zero.
2.  **Slow Path (AI Fallback)**: Se nenhuma palavra-chave for encontrada, envia o prompt para um LLM (ex: Nemotron/OpenAI) via API compatível.

### 3.3. ExtractorConfigDriven (`extractor.ts`)
O componente mais complexo, responsável por preencher o payload do ticket.
*   **Estratégia de Inferência**: Utiliza `inference_rules.json` para mapear palavras-chave em valores de campos (ex: "lento" -> `incident_type: "Performance"`).
*   **Extração Contextual**: Se o agente perguntou especificamente por um campo, a resposta do usuário é tratada com prioridade para esse campo.
*   **Regex Especializado**: Possui lógicas avançadas para extração de padrões como CPF, E-mail e Nomes Próprios.

### 3.4. ValidatorConfigDriven (`validator.ts`)
Verifica se o payload atual satisfaz o schema da intenção.
*   Suporta campos obrigatórios simples.
*   Suporta **validação condicional** (ex: Se `tipo` for "Hardware", então `patrimonio` é obrigatório).

### 3.5. TriageGraphConfigDriven (`graph.ts`)
O orquestrador. Executa o loop principal:
1.  Recebe mensagem.
2.  Chama Router (se intenção desconhecida).
3.  Chama Extractor.
4.  Chama Validator.
5.  Decide o próximo passo:
    *   Se incompleto: Gera pergunta (Inquiry) para o próximo campo faltante.
    *   Se completo: Finaliza e gera o JSON do ticket.

---

## 4. Referência de Configuração

### `intents.json`
Define os tipos de solicitação que o agente entende.
```json
{
  "id": "CREATE_USER",
  "keywords": ["novo usuario", "admissão"], // Gatilhos determinísticos
  "priority": 9,                          // Ordem de verificação
  "schema": "create_user"                 // Link para o schema de dados
}
```

### `inference_rules.json`
Mapeia texto livre para valores estruturados.
```json
{
  "user_type": { // Nome do campo no payload
    "keywords": {
      "Estagiário": ["estagiário", "estágio"], // Valor Final: [Lista de gatilhos]
      "Efetivo": ["clt", "efetivo"]
    }
  }
}
```

---

## 5. Fluxo de Dados (State Flow)

O objeto `AgentState` é passado e mutado através do grafo:

```typescript
interface AgentState {
  intent: IntentType;       // Ex: "RESET_PASSWORD"
  ticket_payload: any;      // Ex: { username: "joao", system: "SAP" }
  missing_fields: string[]; // Ex: ["confirm_password"]
  is_complete: boolean;     // false
  messages: Message[];      // Histórico da conversa
}
```

**Fluxo de Processamento:**
1.  **Input**: Usuário envia "Esqueci a senha do SAP".
2.  **Router**: Detecta "senha" + "SAP" -> Define Intent `RESET_PASSWORD`.
3.  **Extractor**:
    *   Detecta "SAP" -> Infere `target_system: "SAP"`.
    *   Procura `username` -> Não encontra.
4.  **Validator**: Verifica schema `reset_password`.
    *   `target_system`: OK.
    *   `username`: Faltando.
5.  **Graph**: Identifica `username` como `missing_field`.
6.  **Output**: Gera pergunta: "Qual é o seu usuário de rede?"

---

## 6. Guia de Extensão (Como adicionar nova funcionalidade)

Para adicionar um novo tipo de solicitação (ex: "Solicitar Licença de Software"), **nenhum código TypeScript precisa ser alterado**.

1.  **Defina o Schema (`schemas.json`)**:
    Crie a estrutura de dados para a licença (nome do software, versão, justificativa).
2.  **Crie a Intenção (`intents.json`)**:
    Adicione `SOFTWARE_LICENSE` com keywords ("licença", "adobe", "instalar software").
3.  **Configure a Extração (`inference_rules.json`)**:
    Mapeie softwares comuns ("photoshop" -> "Adobe Creative Cloud").
4.  **Defina Perguntas (`inquiry_templates.json`)**:
    Crie templates para perguntar a versão ou justificativa.

O sistema automaticamente reconhecerá a nova intenção e seguirá o fluxo de triagem.
