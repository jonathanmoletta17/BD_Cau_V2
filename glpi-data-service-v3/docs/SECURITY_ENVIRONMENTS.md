# Ambientes e Segurança

## 🚨 Regra de Ouro
**JAMAIS executar operações de escrita (POST, PUT, DELETE) no ambiente de PRODUÇÃO.**

## Ambientes Configuradas

### 1. Produção (DTIC)
- **URL**: `http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php`
- **Permissão**: 🔒 **APENAS LEITURA (GET)**
- **Uso**: Sincronização de dados para o banco local.

### 2. Teste
- **URL**: `http://10.72.16.202/atual/apirest.php`
- **Permissão**: ✅ **TOTAL (GET, POST, PUT, DELETE)**
- **Uso**: Testes de scripts, validação de fluxos de escrita, sandbox.

## Scripts Seguros

Os seguintes scripts operam **apenas no banco de dados local PostgreSQL** e são seguros para rodar conectados à produção (pois apenas leem de lá):

- `scripts/sync_tickets.py` (Lê do GLPI Prod -> Escreve no Postgres Local)
- `scripts/fix_ticket_changes.py` (Lê do Postgres Local -> Escreve no Postgres Local)

## Scripts de Escrita (CUIDADO)

Qualquer script que use `GLPIClient` com métodos `post`, `put` ou `delete` deve verificar explicitamente se está conectado ao ambiente de TESTE antes de executar.
