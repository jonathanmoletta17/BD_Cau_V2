# Plano de Separação: Sync Service Modular

## Problema Atual

`sync_service.py` é um **monolito de 626 linhas** que centraliza sincronização de DTIC e SIS. Isso gera:

- ❌ Difícil manutenção
- ❌ Risco de regressões (mudança em SIS afeta DTIC)
- ❌ Difícil testar isoladamente
- ❌ Inconsistências acumuladas

## Proposta: Separação Mínima e Limpa

### Estrutura Nova

```
src/services/
├── sync/
│   ├── __init__.py
│   ├── base.py              # Funções compartilhadas (clean_*, parse_date, etc)
│   ├── dtic_sync.py         # Sincronização DTIC específica
│   └── sis_sync.py          # Sincronização SIS específica
└── sync_service.py          # MANTER para compatibilidade (facade)
```

### Responsabilidades

#### `base.py` - Utilitários Compartilhados
```python
# Funções genéricas usadas por ambos
def parse_date(date_str) -> datetime: ...
def calc_hash(ticket_data) -> str: ...
def get_int(val) -> Optional[int]: ...

# Funções de limpeza (já existem em data_cleaning)
from src.core.data_cleaning import clean_html, clean_usuario_nome, get_campo_name
```

#### `dtic_sync.py` - Lógica DTIC
```python
class DTICSync:
    @staticmethod
    def sync_tickets(client, session, limit=None):
        # Lógica específica DTIC
        # - Campos: versao, ultimo_atualizador_id
        # - Tabelas: dtic.tickets, dtic.ticket_changes
        pass
    
    @staticmethod
    def sync_ticket_changes(client, session, limit=None):
        # DTIC tem: usuario_nome, campo_id
        pass
```

#### `sis_sync.py` - Lógica SIS
```python
class SISSync:
    @staticmethod  
    def sync_tickets(client, session, limit=None):
        # SIS não tem: versao, ultimo_atualizador_id
        pass
    
    @staticmethod
    def sync_carregadores(client, session):
        # Específico SIS
        pass
```

#### `sync_service.py` - Facade (Compatibilidade)
```python
# Mantém API existente para não quebrar scripts
class SyncService:
    @staticmethod
    def sync_tickets(client, session, TicketModel, valid_ids, context='dtic', limit=None):
        if context == 'dtic':
            from src.services.sync.dtic_sync import DTICSync
            return DTICSync.sync_tickets(client, session, limit)
        else:
            from src.services.sync.sis_sync import SISSync
            return SISSync.sync_tickets(client, session, limit)
```

---

## Benefícios

✅ **Separação de responsabilidades**: DTIC e SIS isolados
✅ **Testável**: Cada módulo testável independentemente  
✅ **Rastreável**: Mudanças versionadas por contexto
✅ **Compatível**: Facade mantém API existente
✅ **Limpo**: 3 arquivos de ~200 linhas vs 1 de 626

---

## Implementação (FASE 4 - Futura)

**NÃO fazer agora!** Focar em corrigir dados primeiro.

**Depois:** Refatorar gradualmente
1. Criar `base.py` com funções compartilhadas
2. Extrair `DTICSync` do monolito
3. Extrair `SISSync` do monolito
4. Deprecar `SyncService` gradualmente

**Risco:** Médio (requer testes extensivos)
**Prioridade:** P2 (após correção de dados)
