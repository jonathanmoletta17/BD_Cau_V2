# 16 — Detalhamento: VPN e Equipamentos

Este documento consolida as decisões de governança sobre `VPN_ACCESS` e `EQUIPMENT_REQUEST`.

---

## 1. VPN_ACCESS

**Conclusão de Governança:**
- **Não cria identidade:** O agente não cria usuários nem identidades.
- **Apenas concede acesso:** O fluxo é para liberar acesso remoto a um usuário *já existente*.
- **Credenciais:** Geradas fora do domínio L1/L2 (via Procergs), mas o chamado serve para iniciar o processo.
- **Papel do Agente:** Abrir o chamado corretamente com as informações necessárias.

**Definição:**
> "Solicitação de habilitação de acesso remoto para usuário já existente."

**Campos Mínimos:**
- Identificação do usuário (já criado).
- Justificativa básica (trabalho remoto, plantão, etc).

**Fronteira:**
- Se o usuário disser "não tenho usuário de rede", orientar `CREATE_USER` primeiro.

---

## 2. EQUIPMENT_REQUEST

Esta intenção é a fonte de maior risco operacional e foi dividida em dois fluxos lógicos distintos.

### 2.1. Escopo de Itens
- Notebook, Desktop, Monitor
- Teclado, Mouse, Webcam
- Celular corporativo (se aplicável)
- TV, Projetor
- **Exclusões:**
    - Impressoras pessoais (não existem).
    - Headsets pessoais (não suportados, usar fones simples).
    - VOIP (já vem com handset).

### 2.2. A Grande Fratura: Incidente vs. Requisição

#### 🅰️ Incidente (Quebrou / Parou / Defeito)
- **Definição:** Algo existia e deixou de funcionar. Falha súbita.
- **Impacto:** Afeta SLA de incidente.
- **Exemplos:** "Meu notebook não liga", "O monitor queimou", "Teclado parou".
- **Dados:**
    - Pode haver patrimônio (coletado automaticamente se for o ativo em uso).
    - Pode haver urgência.

#### 🅱️ Requisição (Quero / Novo / Troca)
- **Definição:** Algo não existia, ou não atende mais (desgaste), ou é um pedido de item adicional.
- **Impacto:** Envolve estoque, SLA de requisição.
- **Exemplos:** "Preciso de um segundo monitor", "Quero trocar meu mouse velho", "Preciso de um headset".
- **Regra de Quantidade:** Aceitar sem validação.

### 2.3. O que o Agente DEVE e NÃO DEVE decidir

**DEVE:**
- Identificar se é Incidente ou Requisição (pelo contexto).
- Coletar o mínimo necessário.
- Não discutir política de estoque.

**NÃO DEVE:**
- Decidir se o usuário "tem direito".
- Decidir modelo, marca ou configuração.
- Discutir disponibilidade.
- Pedir patrimônio para periféricos simples.

### 2.4. Dados Operacionais (Realidade)
- **Impressoras:** Apenas departamentais (Simpress/HP). Não há uso pessoal.
- **Headsets:** Fones simples apenas.
- **Quantidade de Ativos:** Regra geral é 1 PC por usuário (Desktop OU Notebook). Exceções são raras (Autoridades).
- **Patrimônio:**
    - Coletado automaticamente via serial (script `get_system_info.py`).
    - Só pedir se a solicitação for para *outro* equipamento.
    - Só existe para equipamentos de valor (PC, Monitor, Impressora). Periféricos (mouse, teclado) não são patrimoniados para fins de chat.

---

### Resumo para o Agente
O agente deve atuar como um **facilitador**, organizando o pedido em "Incidente" ou "Requisição" e coletando o item e o problema/quantidade, sem burocratizar com perguntas técnicas que o usuário não sabe responder.
