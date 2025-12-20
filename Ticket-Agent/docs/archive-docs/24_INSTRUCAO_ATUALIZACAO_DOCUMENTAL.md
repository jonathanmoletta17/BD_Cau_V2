# 24 — Instrução Formal: EQUIPMENT_REQUEST

**Escopo:** Atualização de Governança para `EQUIPMENT_REQUEST`.
**Papel:** Documentador.

---

## 1. Contexto Operacional (Verdades)
- **Impressoras:** Apenas departamentais (Simpress/HP). Sem uso pessoal.
- **Periféricos:** Teclado/Mouse (patrimoniais), Fones simples (suportados), Headset (não suportado).
- **Ativos:** Apenas patrimoniados. Pessoais sem suporte.
- **Automação:** Serial/Patrimônio cruzados pelo backend. Agente pede apenas se o ativo for *outro*.
- **Perfil:** Usuário tem 1 PC (Desktop ou Notebook). Exceções são raras.

---

## 2. Distinção Obrigatória (Incidente vs Requisição)

### A) Incidente
- **Sintoma:** "Não liga", "Quebrou", "Parou", "Falha súbita".
- **Regras:** Exigir descrição breve. Não pedir diagnóstico.

### B) Requisição
- **Sintoma:** "Novo item", "Troca por desgaste", "Para terceiro".
- **Regras:** "Desgaste" = Requisição (não incidente).
- **Quantidade:** Campo livre, sem validação, sem limite no chat.
- **Aprovação:** Fora do chat.

---

## 3. Comportamento do Agente
- Não pergunta "é incidente ou requisição?". Classifica silenciosamente.
- Não cria controles burocráticos inexistentes.
- Não bloqueia por dados não críticos.

---

## 4. Atualizações Esperadas
1. **DMD:** Formalizar os dois ramos de `EQUIPMENT_REQUEST`.
2. **Políticas:** Definir classificação silenciosa e proibir suporte a pessoal.
3. **Congelamento:** Marcar `EQUIPMENT_REQUEST` como encerrada/congelada.
