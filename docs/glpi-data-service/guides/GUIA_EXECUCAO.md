# GUIA DE EXECUÇÃO - V3 Scripts

## ORDEM CORRETA DE EXECUÇÃO

### Opção 1: Rebuild Completo (RECOMENDADO)
```bash
# De qualquer diretório
python scripts/rebuild_database.py

# OU se estiver em scripts/
python rebuild_database.py
```
**O que faz:**
1. DROP todas as tabelas
2. CREATE todas as tabelas
3. SYNC metadados (8 entidades)
4. SYNC tickets

**Tempo:** ~40 segundos
**Resultado:** Banco 100% limpo e populado

---

### Opção 2: Sync Completo (mantém estrutura)
```bash
python scripts/sync_all.py
```
**O que faz:**
1. SYNC metadados (Users, Groups, Entities, Categories, Locations, Profiles + relacionamentos)
2. SYNC tickets

**Tempo:** ~40 segundos
**Resultado:** Atualiza dados existentes

---

### Opção 3: Syncs Individuais (passo a passo)
```bash
# 1. Metadata (obrigatório primeiro)
python scripts/sync_metadata.py

# 2. Tickets (depende de metadata)
python scripts/sync_tickets_simple.py
```

---

## VALIDAÇÃO

Após qualquer sync, valide:
```bash
python validate_database.py
```

**Deve mostrar:**
- Users: ~1209
- Groups: ~85
- Entities: ~87
- **Tickets: ~11000+**
- Ticket-Users: (dependendo do sync)
- Ticket-Groups: (dependendo do sync)

---

## SCRIPTS DE MANUTENÇÃO

### Limpar Dados (mantém tabelas)
```bash
python scripts/clean_database.py
# Digite: DELETE ALL
```

### Destruir Tabelas
```bash
python scripts/drop_tables.py
# Digite: DROP TABLES
```

### Criar Tabelas
```bash
python scripts/create_tables.py
```

---

## TROUBLESHOOTING

### Problema: "No module named 'src'"
**Solução:** Execute da raiz do projeto, não de dentro de src/

### Problema: Erro de encoding/emoji
**Solução:** Use:
```bash
$env:PYTHONIOENCODING="utf-8"; python scripts/sync_all.py
```

### Problema: Tickets não populados
**Causa:** sync_all.py pode ter parado no metadata
**Solução:** 
```bash
# Rode o sync de tickets manualmente
python scripts/sync_tickets_simple.py
```

---

## RESUMO RÁPIDO

**Para uso normal:**
```bash
python scripts/sync_all.py
```

**Para reset total:**
```bash
python scripts/rebuild_database.py
```

**Para validar:**
```bash
python validate_database.py
```
