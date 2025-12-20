# 17 — Detalhamento: CREATE_USER

Este documento redefine a intenção `CREATE_USER` alinhada à realidade operacional.

---

## 1. Fronteira da Intenção
**CREATE_USER** = Abertura de identidade digital básica.
- **Inclui:** Usuário de rede, Usuário de sistemas internos, Credencial VPN inicial.
- **Exclui:** Alteração de acesso, Reativação, Perfil fino/permissões específicas.
- **Solicitante Típico:** RH (para usuários de rede) ou Chefia Imediata. Raramente o próprio usuário final (self-service).

---

## 2. Tipos de Criação e Campos
A intenção possui sub-tipos lógicos que definem os campos obrigatórios.

### 2.1. Subtipos
1. **Usuário Efetivo (Regular/Nomeado)**
2. **Estagiário**

### 2.2. Campos Obrigatórios (Hard Requirement)
Estes campos são **gate lógico** e indispensáveis.

| Campo | Obrigatoriedade | Nota |
| :--- | :--- | :--- |
| `tipo_usuario` | **SEMPRE** | (Efetivo / Estagiário) |
| `nome_completo` | **SEMPRE** | Base da identidade |
| `setor` | **SEMPRE** | "TI", "RH", "Contabilidade" (aceitar informal) |

### 2.3. Identificadores Condicionais
Dependem do `tipo_usuario`.

- **Para Efetivo:** Exige `cpf` **E** `matricula` (ID Funcional).
- **Para Estagiário:** Exige `rg`. (CPF não é o identificador primário aqui).

---

## 3. Campos Excluídos / Opcionais
O agente **NÃO** deve bloquear o fluxo por falta destes dados:
- ❌ **Nível de Acesso:** Resolvido posteriormente.
- ❌ **Data de Início:** Frequentemente "imediato" ou irrelevante para a abertura técnica.
- ❌ **Data Fim:** Exceção.
- ❌ **Aprovador:** Implícito pelo solicitante (Chefia/RH).

### Sobre Datas Vagas
- Se efornecida ("semana que vem"), o agente interpreta.
- Se não fornecida, o ticket segue sem bloqueio.

---

## 4. Contexto Operacional
- Este fluxo não é autoatendimento.
- O foco é criar a *identidade*. Permissões granulares são tratadas em chamados de "Acesso" ou posteriormente pelo N2.
