# Documento de Transição: Governança -> Planejamento Técnico 🛠️

**Origem:** Governança Local Triage Agent (DMD v1.6)
**Destino:** Code Mode (Implementation Phase)
**Status:** PRONTO PARA EXECUÇÃO

Este documento formaliza o encerramento da fase de Governança e entrega o pacote de especificações para a fase de Implementação Técnica.

---

## 1. Revisão Final de Intents (The "Gold Standard")

A implementação do `Router` deve reconhecer estritamente e apenas estas chaves. Qualquer outra chave existente no código legado deve ser removida.

1.  `RESET_PASSWORD`
2.  `CREATE_USER`
3.  `PRINTER_ISSUE`
4.  `EQUIPMENT_REQUEST` (Engloba Hardware Failure e New Requests)
5.  `VPN_ACCESS`
6.  `CORPORATE_SYSTEMS`

*   **REMOVER do Código:** `HARDWARE_ISSUE`, `WIFI_ACCESS` (se existir), `EMAIL_ISSUE` (se existir - cai em Corporate ou Password dependendo do caso, ou deve ser explicitado se for intenção real, mas por hora focar no core).

---

## 2. Revisão de Schemas Esperados (Pydantic)

Os `State Models` devem ser refatorados para espelhar estas estruturas de dados.

### 2.1. `CreateUserSchema`
*   `full_name` (str, required)
*   `user_type` (enum: [EFETIVO, ESTAGIARIO, TERCEIRO], required)
*   `department` (str, required)
*   `identifier` (str, conditional based on user_type)
    *   *Nota:* Implementar validator customizado que exige CPF se Efetivo, RG se Estagiário.
*   `start_date` (date, optional) - *Não bloquear se nulo.*

### 2.2. `EquipmentRequestSchema`
*   `request_type` (enum: [INCIDENT, REQUISITION], inferred)
*   `item_description` (str, required) - *Ex: "Monitor", "Meu teclado"*
*   `issue_description` (str, required if INCIDENT) - *Ex: "Não liga"*
*   `quantity` (int, default=1)
*   `asset_id` (str, optional) - *Só pedir se for INCIDENT em equipamento específico.*

### 2.3. `PrinterIssueSchema`
*   `location_description` (str, required) - *Aceitar informal.*
*   `issue_summary` (str, required)
*   *Remover:* `ip_address`, `queue_name`.

### 2.4. `VpnAccessSchema`
*   `request_type` (enum: [ACCESS_GRANT, INSTALL], required)
*   `justification` (str, required)
*   *Remover:* `user_creation_details`.

---

## 3. Checklist de Limpeza de Código (Pre-Flight)

Antes de iniciar novas features, a base de código deve ser limpa das dívidas de governança antigas.

- [ ] **Router Prompt:** Atualizar prompt do `orchestrator` para remover referência a `HARDWARE_ISSUE`.
- [ ] **Router Definitions:** Remover classe/enum `HardwareIssue` do arquivo de definições.
- [ ] **State Graph:** Verificar se há nós órfãos apontando para falhas de hardware antigas. Redirecionar para o nó de `EquipmentRequest`.
- [ ] **Legacy Prompts:** Buscar e destruir prompts que peçam "IP da impressora" ou "Senha de VPN".

---

## 4. Pontos de Validação (Quality Gates)

O sucesso da implementação será medido por estes cenários de teste (`simulation_suite`):

1.  **Cenário "A Impressora do RH":** O agente deve aceitar a string "A do RH" no campo de localização e abrir o ticket.
2.  **Cenário "Mouse Ruim":** O agente deve classificar como `EQUIPMENT_REQUEST (REQUISITION)` e não Incidente.
3.  **Cenário "VPN para o João":** O agente deve perguntar a justificativa do acesso, e *não* perguntar CPF/RG para criar o usuário João (assumindo que João já existe).
4.  **Cenário "Semana que vem":** O agente deve inferir a data correta para `CREATE_USER` e logar o aviso, sem travar.

---

**Aprovação:**
Documento gerado automaticamente para sinalizar o fim do ciclo de definição de regras.
👉 **Próximo Passo:** Executar `Refactoring Blueprint` baseando-se nestas specs.
