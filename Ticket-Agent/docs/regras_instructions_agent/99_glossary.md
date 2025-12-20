# 99_glossary.md

> **ID:** DOC-099
> **Status:** Approved
> **Responsável:** Time de Produto
> **Última Atualização:** 2025-12-19

## Glossário de Termos do Domínio
Este documento define a linguagem ubiqua do projeto. O uso destes termos é obrigatório na documentação e no código.

---

### A
*   **AD (Active Directory):** Sistema de diretório da Microsoft. Principal fonte de autenticação. No contexto do LTA, "Senha" quase sempre se refere à senha do AD.
*   **Agent (Agente):** O sistema de IA conversacional. Não usar "Bot" em documentos técnicos.
*   **Alucinação:** Quando o agente inventa fatos ou procedimentos (ex: pedir para o usuário abrir a impressora).
*   **Amnésia de Contexto:** Falha onde o agente esquece dados informados na mensagem anterior. Resolvido pelo padrão `Silent Extraction`.

### C
*   **Chat-Driven:** (Depreciado) Arquitetura onde o fluxo depende do texto do chat. Substituído por `State-Driven`.

### G
*   **GLPI:** Sistema de gerenciamento de chamados (ITSM). O backend oficial.

### H
*   **Handover (Transbordo):** Processo de transferir o atendimento da IA para um humano. Ocorre após 3 falhas de entendimento ou por solicitação expressa.

### I
*   **Incidente:** Interrupção de um serviço que estava funcionando (ex: Mouse quebrou). Diferente de Requisição.
*   **Intent (Intenção):** O objetivo macro do usuário (ex: RESET_PASSWORD, PRINTER_ISSUE).

### R
*   **Requisição:** Pedido de algo novo ou alteração programada (ex: Quero um mouse novo).
*   **Role (Papel):** A permissão do usuário no sistema.

### S
*   **Silent Extraction (Extração Silenciosa):** Padrão arquitetural onde o agente extrai entidades do histórico sem fazer perguntas explícitas se a informação já existir.
*   **State-Driven:** Arquitetura obrigatória onde o estado (JSON) determina a próxima ação, não o texto do chat.

### U
*   **User (Usuário):** O servidor público que está pedindo ajuda. Assumido como "leigo tecnicamente".
