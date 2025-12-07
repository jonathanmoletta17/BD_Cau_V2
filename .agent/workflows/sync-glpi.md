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
cd glpi-data-service-v3
python scripts/sync_glpi.py --full
```

**Opções**:
- `--full`: Sincronização completa (primeira vez)
- `--incremental`: Apenas dados novos/modificados
- `--tickets-only`: Apenas tickets
- `--users-only`: Apenas usuários

---

## 3. Verificar Sincronização

```bash
# Conectar ao PostgreSQL
psql -U seu_usuario -d glpi_db

# Verificar contagem de tickets
SELECT COUNT(*) FROM glpi.tickets;

# Verificar mais recente
SELECT id, date, title 
FROM glpi.tickets 
ORDER BY date DESC 
LIMIT 5;
```

---

## Troubleshooting

**Erro: "Connection refused"**
- Verificar se GLPI está acessível
- Confirmar tokens em `.env`

**Erro: "Table doesn't exist"**
- Rodar migrations: `alembic upgrade head`

**Dados muito antigos**
- Executar `--full` para reset completo
