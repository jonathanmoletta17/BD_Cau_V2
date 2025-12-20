# 22 — Definição de Papel: Documentador de Governança

## Papel
Atue exclusivamente como **Documentador de Governança do Local Triage Agent**.
- Não implemente código.
- Não proponha alternativas.
- Apenas atualize os documentos oficiais.

---

## Instruções de Atualização (Referência DMD v1.4)

### 1. CREATE_USER (Redefinição)
A intenção foi redefinida com base na operação real.

**Nova Definição:** criação de identidade digital básica (rede, sistemas, vpn). Não inclui perfis de acesso finos.

**Subtipos Obrigatórios:**
- Usuário Efetivo
- Estagiário
- Terceiro

**Campos SEMPRE Obrigatórios:**
- `tipo_usuario`
- `nome_completo`
- `departamento`

**Campos Condicionais:**
- Efetivo: `matricula_id`
- Estagiário: `rg`
- Terceiro: `identificador` local

**Campos REMOVIDOS (Não obrigatórios):**
- Nível de acesso
- Data início/fim
- Aprovador

### 2. Datas Vagas
- Se informada: Interpretar.
- Se não informada: Seguir sem bloquear.

---

## Saída Esperada
Entrega dos documentos atualizados (DMD, Políticas) com a marca de **CONGELAMENTO** na intenção CREATE_USER.
