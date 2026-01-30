# Análise de Scripts - Essenciais vs Descartáveis

## CRITÉRIO DE ESSENCIALIDADE

**ESSENCIAL para DTICução:**
- Scripts que criam/migram schema do banco
- Scripts que sincronizam dados da API GLPI  
- Scripts de deploy/setup inicial

**DESCARTÁVEL:**
- Scripts de teste/debug/validação
- Scripts de análise/auditoria one-time
- Scripts duplicados ou obsoletos
- Scripts de desenvolvimento local

---

## ANÁLISE COMPLETA (21 scripts)

### ✅ ESSENCIAIS PARA DTICUÇÃO (4)

| Script | Função | Motivo |
|--------|--------|--------|
| **sync.py** | Sincroniza dados GLPI→DB | Core - usado em DTICução |
| **create_db.py** | Cria schema e tabelas | Setup inicial obrigatório |
| **deploy.sh** | Deploy Linux/Docker | DTICução Linux |
| **deploy.ps1** | Deploy Windows | DTICução Windows |

---

### ❌ DELETAR - Scripts de Teste/Debug (11)

| Script | Tipo | Motivo para Deletar |
|--------|------|---------------------|
| truncate_dtic.py | Debug | One-time use, não recorrente |
| validate_corrections.py | Teste | Validação one-time das funções |
| validate_entities.py | Teste | Validação one-time da hierarquia |
| validate_entities.sql | Teste | SQL de validação, não usado |
| quick_check.py | Debug | Diagnóstico rápido, não essencial |
| validate_sync_results.py | Teste | Validação pós-sync, one-time |
| audit_data_quality.py | Análise | Auditoria one-time |
| audit_db.py | Análise | Auditoria one-time |
| diagnose_categories.py | Debug | Diagnóstico específico |
| probe_glpi_types.py | Debug | Exploração da API |
| seed_validation_data.py | Teste | Seed de dados de teste |

---

### ❌ DELETAR - Scripts Duplicados/Obsoletos (4)

| Script | Motivo |
|--------|--------|
| rebuild_database.py | Substituído por create_db.py |
| drop_tables.py | Operação perigosa, não deve estar em DTICução |
| setup-postgres-docker.ps1 | Setup local dev, não DTICução |
| run_dev.ps1 | Alias dev, não DTICução |

---

### ⚠️ MANTER COMO DOCUMENTAÇÃO (2)

| Script | Status | Motivo |
|--------|--------|--------|
| README.md | Docs | Documentação útil |
| setup_helpers.py | Helpers | Funções auxiliares (verificar se usado) |

**Ação:** Verificar se `setup_helpers.py` é importado por scripts essenciais. Se não, deletar.

---

## DECISÃO FINAL

### ✅ MANTER (4-5 scripts)

1. **sync.py** - Sincronização CORE
2. **create_db.py** - Setup DB CORE
3. **deploy.sh** - Deploy Linux
4. **deploy.ps1** - Deploy Windows
5. **README.md** - Documentação (opcional)

### ❌ DELETAR (15-16 scripts)

**Categoria Teste/Debug (11):**
- truncate_dtic.py
- validate_corrections.py
- validate_entities.py
- validate_entities.sql
- quick_check.py
- validate_sync_results.py
- audit_data_quality.py
- audit_db.py
- diagnose_categories.py
- probe_glpi_types.py
- seed_validation_data.py

**Categoria Duplicado/Obsoleto (4):**
- rebuild_database.py
- drop_tables.py
- setup-postgres-docker.ps1
- run_dev.ps1

**Verificar antes de deletar:**
- setup_helpers.py (se não for importado, deletar)

---

## 📂 ESTRUTURA FINAL PROPOSTA

```
scripts/
├── sync.py              # Sincroniza dados GLPI → PostgreSQL
├── create_db.py         # Cria schema e tabelas
├── deploy.sh            # Deploy em Linux/Docker
├── deploy.ps1           # Deploy em Windows
└── README.md            # Documentação (opcional)
```

**Total:** 4-5 scripts essenciais (redução de 76% - 21→5)

---

## 🔧 PASTA src/core - NÃO MEXER

Todos os módulos em `src/core` são ESSENCIAIS:

```
src/core/
├── __init__.py          ✅ MANTER
├── config.py            ✅ MANTER - Configurações
├── database.py          ✅ MANTER - Conexão DB
├── data_cleaning.py     ✅ MANTER - Funções de limpeza
├── glpi_client.py       ✅ MANTER - Client API GLPI
└── api_helpers.py       ✅ MANTER - Helpers API
```

**Status:** ✅ MANTER TODOS - São módulos core do sistema

---

## AÇÕES PROPOSTAS

1. ✅ Criar backup dos scripts antes de deletar
2. ✅ Deletar 15-16 scripts não essenciais
3. ✅ Manter apenas 4-5 scripts de DTICução
4. ✅ Atualizar README se necessário

**Resultado:** Pasta limpa e organizada, apenas essencial para DTICução
