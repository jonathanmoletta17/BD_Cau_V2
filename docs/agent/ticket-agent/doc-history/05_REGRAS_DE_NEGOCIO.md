
## 📁 05_REGRAS_DE_NEGOCIO.md

```markdown
# 05 — Regras de Negócio por Intenção

## RESET_PASSWORD
- Prioridade máxima.
- Se usuário diz “esqueci minha senha”, assume **Rede/Windows** por padrão.
- campos críticos:
  - usuario_rede
  - sistema_afetado

## CREATE_USER
- Identidade digital básica.
- Campos obrigatórios:
  - nome_completo
  - setor
  - tipo_usuario
  - identificador_condicional (CPF/RG/Matrícula/Empresa)

## EQUIPMENT_REQUEST
- Unifica incidentes e requisições.
- Incidente:
  - Falha súbita ou erro funcional.
- Requisição:
  - Novo item ou troca por desgaste.
- Quantidade livre (sem validação no chat).

## PRINTER_ISSUE
- Aceita apenas identificação informal.
- Proibido solicitar IP, caminho de fila ou patrimônio.
- Proibido pedir ações físicas (abrir, balançar toner).

## VPN_ACCESS
- Escopo: concessão de acesso e instalação do cliente.
- Não cria usuário.
- Se não tem usuário, direcionar para CREATE_USER.

## CORPORATE_SYSTEMS
- Erros em sistemas ERP/CRM.
- Coletar nome do sistema e mensagem de erro.

---

## Regras Gerais
- O agente **não deve** inventar dados.
- Regras estritas do DMD sempre prevalecem.
