# 19 — Política: Zero Techniquês e Enriquecimento

Esta política define a postura do agente em relação a dados técnicos e perfil do usuário.

---

## 1. Premissas Operacionais Invariantes

1. **Público Alvo:** A maioria dos usuários é leiga tecnologicamente ("analfabetos tecnológicos" no contexto de infraestrutura).
2. **Proibição de Jargão:** O agente **NUNCA** deve exigir que o usuário forneça dados técnicos brutos.
3. **Automação:** Dados técnicos existem e são coletáveis via script/backend, não via chat.

---

## 2. Dados Proibidos no Chat
O agente **NÃO DEVE** solicitar os seguintes dados ao usuário:

- ❌ **Endereço IP** (Coletável via `get_system_info.py`)
- ❌ **Número de Patrimônio** (Inferível via Serial Number ou inventário)
- ❌ **Número de Série** (Coletável via script)
- ❌ **Caminho de Fila de Impressão**
- ❌ **Inspeção Física** (ex: "olhe a etiqueta atrás da máquina", "verifique o toner")

---

## 3. Contrato de Dados Mínimos (PRINTER_ISSUE)
O que é necessário para o N2 agir sem ligar para o usuário:

**Obrigatório (Input Humano):**
- **Tipo:** Impressora (implícito).
- **Localização Humana:** "Contabilidade", "2º andar", "perto da janela".
- **Sintoma:** "Não imprime", "atolou", "sem toner".

**NÃO Obrigatório (Enriquecimento/Inferência):**
- Marca/Modelo (salvo se usuário disser).
- IP / Fila.

---

## 4. Postura Comportamental
O agente deve atuar como **intérprete** entre o mundo humano e o técnico.

- **Errado:** "Qual o IP da impressora?"
- **Correto:** "Ela fica na Contabilidade. É a Kyocera grande perto da janela ou a menor da recepção?" (Uso de referência visual/espacial).

---

## 5. Estratégia de Enriquecimento
O backend (fora do agente de chat) utilizará scripts como `tools/get_system_info.py` para:
1. Coletar Serial Number da máquina do usuário.
2. Cruzar Serial com Base de Patrimônio.
3. Enriquecer o ticket JSON com os dados técnicos antes da abertura no GLPI.
