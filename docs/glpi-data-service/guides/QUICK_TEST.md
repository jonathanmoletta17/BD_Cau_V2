# Guia Rápido - Testar API DDD

## 🚀 Servidor RODANDO

```powershell
# Já está rodando em: http://0.0.0.0:8000
# INFO: Application startup complete.
```

---

## ✅ Testar Endpoints

### 1. Health Check
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET
```

**Resposta esperada:**
```json
{"status":"healthy","version":"2.0.0"}
```

---

### 2. Listar Tickets (DTIC)
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/dtic/tickets?page=1&limit=10" `
  -Method GET `
  -Headers @{"X-Context"="dtic"}
```

**Resposta esperada:**
```json
{
  "context": "dtic",
  "total": <N>,
  "page": 1,
  "limit": 10,
  "total_pages": <N>,
  "tickets": [...]
}
```

---

### 3. Detalhe de Ticket
```powershell
# Substitua 12345 pelo GLPI ID real
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/dtic/tickets/12345" `
  -Method GET `
  -Headers @{"X-Context"="dtic"}
```

---

### 4. Meus Chamados (Mobile)
```powershell
# Substitua 'usuario' pelo username real
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/dtic/meus-chamados/usuario" `
  -Method GET `
  -Headers @{"X-Context"="dtic"}
```

---

## 🌐 Documentação Interativa

Acesse no navegador:
```
http://localhost:8000/docs
```

**Swagger UI automático!**

---

## 🛑 Parar Servidor

```powershell
# No terminal onde está rodando, pressione:
Ctrl + C
```

---

## 📝 Logs

O servidor mostra logs em tempo real:
- `INFO` - Requisições recebidas
- `ERROR` - Erros
- Queries SQL (se LOG_LEVEL=DEBUG)

---

## 🎯 Próximos Passos

1. Testar `/health` ✅
2. Testar `/api/v1/dtic/tickets` com dados reais
3. Implementar SIS context (mesma estrutura)
4. Adicionar dashboard, search, audit routes
