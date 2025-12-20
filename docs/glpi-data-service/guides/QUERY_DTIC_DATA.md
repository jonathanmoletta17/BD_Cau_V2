# Guia de Consultas DTIC - PostgreSQL

## 🚀 Opção 1: Script Python (Recomendado)

```bash
# Instalar tabulate (se necessário)
pip install tabulate psycopg2-binary

# Rodar script
python scripts/query_dtic_data.py
```

**O script mostra:**
- ✅ Todas as tabelas do schema DTIC
- ✅ Resumo de tickets (total, novos, em atendimento, etc.)
- ✅ Últimos 5 tickets
- ✅ Histórico de sync
- ✅ Top 10 categorias
- ✅ Top 10 técnicos

---

## 🗄️ Opção 2: psql Direto

### Conectar ao banco:
```bash
psql -h localhost -p 5433 -U glpi_user -d glpi_data
# Senha: (do .env)
```

### Consultas úteis:

#### 1. Listar tabelas DTIC:
```sql
\dt dtic.*
```

#### 2. Count de tickets:
```sql
SELECT COUNT(*) FROM dtic.tickets WHERE is_deleted = false;
```

#### 3. Últimos 10 tickets:
```sql
SELECT glpi_id, titulo, status, prioridade, criado_em 
FROM dtic.tickets 
WHERE is_deleted = false 
ORDER BY criado_em DESC 
LIMIT 10;
```

#### 4. Tickets por status:
```sql
SELECT status, COUNT(*) as total
FROM dtic.tickets
WHERE is_deleted = false
GROUP BY status
ORDER BY total DESC;
```

#### 5. Ver estrutura da tabela:
```sql
\d dtic.tickets
```

#### 6. Top categorias:
```sql
SELECT categoria, COUNT(*) as total
FROM dtic.tickets
WHERE is_deleted = false AND categoria IS NOT NULL
GROUP BY categoria
ORDER BY total DESC
LIMIT 10;
```

#### 7. Histórico de sincronização:
```sql
SELECT * FROM dtic.sync_history 
ORDER BY iniciado_em DESC 
LIMIT 5;
```

---

## 📊 Opção 3: SQL Direto (PowerShell)

```powershell
# Variáveis do .env
$env:PGPASSWORD = "sua_senha_aqui"

# Query simples
psql -h localhost -p 5433 -U glpi_user -d glpi_data -c "SELECT COUNT(*) FROM dtic.tickets;"

# Query com resultado formatado
psql -h localhost -p 5433 -U glpi_user -d glpi_data -c "SELECT glpi_id, titulo, status FROM dtic.tickets LIMIT 5;"
```

---

## 🔍 Queries Prontas

### Ver todas as tabelas e counts:
```sql
SELECT 
    schemaname,
    tablename,
    n_live_tup as rows
FROM pg_stat_user_tables
WHERE schemaname = 'dtic'
ORDER BY n_live_tup DESC;
```

### Tickets criados hoje:
```sql
SELECT COUNT(*) 
FROM dtic.tickets 
WHERE criado_em::date = CURRENT_DATE;
```

### Tickets por técnico:
```sql
SELECT 
    tecnico,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'NOVO') as novos
FROM dtic.tickets
WHERE is_deleted = false AND tecnico IS NOT NULL
GROUP BY tecnico
ORDER BY total DESC;
```

---

## 💡 Dica Rápida

Para ver TUDO de uma vez:
```bash
python scripts/query_dtic_data.py
```

É a forma mais fácil e visual! 📊
