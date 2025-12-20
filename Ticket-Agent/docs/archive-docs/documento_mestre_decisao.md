# Documento Mestre de Decisão (DMD) - VERSÃO FINAL (v2.1)

> [!IMPORTANT]
> **STATUS: FINAL - FONTE ÚNICA DE VERDADE**
> Este documento revoga e substitui todas as versões anteriores.
> Nenhuma linha de código deve ser escrita se violar as definições aqui contidas.

## 1. Missão e Fronteiras
O **Agente de Triagem Local** é um sistema de classificação e pré-atendimento determinístico. Sua função é coletar dados estruturados para abertura de chamados no GLPI.
- **NÃO FAZ:** Resolução técnica ou troubleshooting. Reset de senhas direto (apenas abre chamado). Criação de usuários no AD (apenas abre chamado).
- **FAZ:** Identificação de intenção, coleta de campos obrigatórios, formalização de ticket.

## 2. Mapa de Intenções Oficial (Lista Fechada)

O agente deve reconhecer **apenas** as 6 intenções abaixo. Qualquer outra solicitação é `UNKNOWN`.

| Intenção | Descrição | Escopo Estrito |
| :--- | :--- | :--- |
| **1. RESET_PASSWORD** | Problemas de login ou esquecimento de senha. | **Escopo:** Rede, AD, E-mails integrados. <br>**Nota:** Se o erro for específico de sistema (ex: erro no SAP), usar `CORPORATE_SYSTEMS`. |
| **2. CREATE_USER** | Solicitação de nova identidade digital. | Admissão, Contratação, Criação de Login. |
| **3. EQUIPMENT_REQUEST** | Problemas físicos ou necessidade de hardware. | **Subtipos:** <br>1. *Incident*: Quebra, fumaça, erro, não liga. <br>2. *Requisition*: Novo equipamento, troca por desgaste, "meu mouse está ruim". |
| **4. PRINTER_ISSUE** | Problemas de impressão. | Toner, Papel, Atolamento, Instalação de impressora. |
| **5. VPN_ACCESS** | Acesso remoto seguro. | **Escopo:** Concessão de permissão ou Instalação do Cliente VPN. <br>**Exclusão:** NÃO cria usuário VPN (usuário deve existir). |
| **6. CORPORATE_SYSTEMS** | Erros em software corporativo. | SAP, CRM, PROA, Sistemas Internos. |

> [!WARNING]
> **PROIBIÇÃO EXPLÍCITA:** A intenção `HARDWARE_ISSUE` deixa de existir. Foi absorvida integralmente por `EQUIPMENT_REQUEST` (ramo Incident). O código NÃO deve conter referências a `HARDWARE_ISSUE`.

## 3. Definições de Escopo Crítico

### 3.1 EQUIPMENT_REQUEST (Hardware Unificado)
Unifica toda a gestão de ativos físicos. O agente DEVE inferir silenciosamente o `request_type`:
- **Incident (Quebra):** Requer descrição do problema.
- **Requisition (Solicitação):** Requer item e quantidade (default=1).
- **Premissa:** Apenas equipamentos fornecidos pela empresa. Headsets e celulares pessoais são `UNKNOWN` (ou policy "não suportado").

### 3.2 VPN_ACCESS (Acesso, não Identidade)
A solicitação de VPN pressupõe que o colaborador já possui vínculo ativo.
- **O que faz:** Libera IP, instala GlobalProtect/FortiClient, adiciona em grupo de acesso.
- **O que NÃO faz:** "Criar usuário para VPN". Se o usuário não existe, a intenção correta é `CREATE_USER` (com observação de VPN).

### 3.3 CREATE_USER (Identidade Básica Estrita)
Foca nos dados essenciais para o RH/TI criar a identidade.

**Campos Obrigatórios Fixos:**
1. Nome Completo
2. Setor
3. Tipo de Usuário (Efetivo | Estagiário | Terceiro)

**Identificador Condicional (OBRIGATÓRIO conforme Tipo):**
- Se **Efetivo** → Exigir **CPF**.
- Se **Estagiário** → Exigir **RG**.
- Se **Terceiro** → Exigir **Matrícula** ou **Empresa**.

**Exclusões:**
- Não solicitar "Cargo" como obrigatório.
- Não solicitar "sistemas a acessar" ou "data de término" nesta etapa.

## 4. Princípios de Implementação (Invariantes)

1.  **Determinismo:** Se os campos obrigatórios estão presentes, o agente **NÃO** deve fazer perguntas adicionais ("chatting"). Deve abrir o ticket.
2.  **Anti-Amnésia:** O agente nunca deve perguntar o que já foi fornecido na mensagem inicial (`pinned_request`).
3.  **JSON Estrito:** A saída do extrator deve ser sempre JSON validável pelo Schema Pydantic correspondente.
4.  **Falha Segura:** Se a intenção é incerta ou o usuário está frustrado (`HANDOVER_TO_HUMAN`), encaminhar para humano imediatamente sem tentar classificar forçosamente.

## 5. Status de Validação
Este documento serve como **critério de aceite** para a auditoria de código.

- [ ] CREATE_USER valida Tipo + Identificador específico?
- [ ] RESET_PASSWORD evita conflito com CORPORATE_SYSTEMS?
- [ ] Missão estrita (sem dicas passo-a-passo)?
