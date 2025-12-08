---
description: Sincronizar dados do GLPI para PostgreSQL local
---

# Sync GLPI → PostgreSQL

Sincronize dados da API GLPI para o banco PostgreSQL local.

---

## 1. Verificar Conectividade GLPI

```bash
curl -X GET "https://seu-glpi.com/apirest.php/" \
  -H "App-Token: seu-app-token" \
  -H "Session-Token: seu-session-token"
```

---

## 2. Rodar Sincronização

// turbo
```bash
cd glpi-data-service
python scripts/sync.py --context dtic --type all
```

**Opções:**
- `--context dtic`: Sincroniza DTIC
- `--context sis`: Sincroniza SIS
- `--context all`: Sincroniza ambos
- `--type metadata`: Apenas metadados (users, groups, entities, etc.)
- `--type tickets`: Apenas tickets
- `--type all`: Tudo (padrão)
- `--limit N`: Limitar quantidade para testes

---

## 3. Verificar Sincronização

```bash
# Conectar ao PostgreSQL
psql -U glpi_user -d glpi_data

# Verificar contagem de tickets DTIC
SELECT COUNT(*) FROM dtic.tickets;

# Verificar mais recente
SELECT glpi_id, titulo, criado_em 
FROM dtic.tickets 
ORDER BY criado_em DESC 
LIMIT 5;
```

---

## Troubleshooting
---
description: Sincronizar dados do GLPI para PostgreSQL local
---

# Sync GLPI → PostgreSQL

Sincronize dados da API GLPI para o banco PostgreSQL local.

---

## 1. Verificar Conectividade GLPI

```bash
curl -X GET "https://seu-glpi.com/apirest.php/" \
  -H "App-Token: seu-app-token" \
  -H "Session-Token: seu-session-token"
```

---

## 2. Rodar Sincronização

// turbo
```bash
cd glpi-data-service
python scripts/sync.py --context dtic --type all
```

**Opções:**
- `--context dtic`: Sincroniza DTIC
- `--context sis`: Sincroniza SIS
- `--context all`: Sincroniza ambos
- `--type metadata`: Apenas metadados (users, groups, entities, etc.)
- `--type tickets`: Apenas tickets
- `--type all`: Tudo (padrão)
- `--limit N`: Limitar quantidade para testes

---

## 3. Verificar Sincronização

```bash
# Conectar ao PostgreSQL
psql -U glpi_user -d glpi_data

# Verificar contagem de tickets DTIC
SELECT COUNT(*) FROM dtic.tickets;

# Verificar mais recente
SELECT glpi_id, titulo, criado_em 
FROM dtic.tickets 
ORDER BY criado_em DESC 
LIMIT 5;
```

---

## Troubleshooting

**Erro: "Connection refused"**
- Verificar se GLPI está acessível
- Confirmar tokens em `.env`

**Erro: "Table doesn't exist"**
- Rodar criação de tabelas: `python scripts/create_db.py`

**Dados desatualizados**
- Sincronizar: `python scripts/sync.py --context dtic`
- Validar integridade: `python scripts/validate_critical_tables.py`
