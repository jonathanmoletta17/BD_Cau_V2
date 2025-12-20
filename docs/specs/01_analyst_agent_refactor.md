# Spec: Refatoração do GLPI Analyst Agent

## 1. Objetivo
Tornar o `GLPIAnalystAgent` robusto contra erros de tipagem e falhas de conexão, utilizando Pydantic para validação de dados e SQLAlchemy para execução segura.

## 2. Contratos de Dados (Schemas)

### Timeline Event
Estrutura obrigatória para retorno da timeline.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `timestamp` | `datetime` | Data da mudança |
| `actor` | `str` | Nome do usuário |
| `action` | `str` | Descrição legível da ação |
| `details` | `str` | Detalhes técnicos (ex: de -> para) |

### Health Check
Estrutura para saúde do ticket.

| Campo | Tipo | Regra |
| :--- | :--- | :--- |
| `ticket_id` | `int` | ID do GLPI |
| `reopens` | `int` | Contagem de reaberturas |
| `ping_pong` | `int` | Contagem de trocas de técnico |
| `status` | `str` | "Healthy" | "Warning" | "Critical" |

## 3. Regras de Implementação
1.  **NÃO usar Pandas `merge` cegamente:** O banco pode retornar tipos incompatíveis. Fazer joins via SQL (SQLAlchemy) e retornar objetos tipados.
2.  **Tratamento de Erros:** Se o banco cair, retornar um objeto de erro limpo, não um stack trace gigante.
3.  **Validação:** Usar Pydantic para garantir que o que sai do banco cabe no modelo.
