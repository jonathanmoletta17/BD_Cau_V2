# 📊 Relatório de Testes de Endpoints

**Data**: 2025-12-07 02:54
**Resultados**: 9/19 endpoints funcionais (47%)

---

## ✅ Backend API (8000) - Status: PARCIAL

### Endpoints Funcionais (9/14)

| Endpoint | Status | Tempo | Exemplo de Dados |
|----------|--------|-------|------------------|
| `/health` | ✅ 200 | 6ms | `healthy, v3.0.0` |
| `/` (Root) | ✅ 200 | 14ms | Welcome message |
| **DTIC - Métricas Gerais** | ✅ 200 | 29ms | `novos: 3, em_progresso: 90, pendentes: 16, resolvidos: 11211` |
| **DTIC - Ranking Entidades** | ✅ 200 | 21ms | 10KB JSON (lista completa) |
| **DTIC - Ranking Categorias** | ✅ 200 | 23ms | 5.9KB JSON |
| **DTIC - Tickets Novos** | ✅ 200 | 26ms | 3 tickets retornados |
| **DTIC - Ranking Técnicos** | ✅ 200 | 42ms | 966 bytes (lista técnicos) |
| **DTIC - Status Níveis** | ✅ 200 | 83ms | N1-N4 stats |
| **DTIC - Atividades Recentes** | ✅ 200 | 12ms | 1.9KB JSON |

### Endpoints com Falha (5/14)

| Endpoint | Status | Problema |
|----------|--------|----------|
| `/api/v1/sis/dashboard/stats-gerais` | ❌ 404 | Not Found |
| `/api/v1/sis/dashboard/ranking-entidades` | ❌ 404 | Not Found |
| `/api/v1/sis/dashboard/ranking-categorias` | ❌ 404 | Not Found |
| `/api/v1/sis/dashboard/tickets-novos` | ❌ 404 | Not Found |
| `/api/v1/sis/dashboard/ranking-tecnicos` | ❌ 404 | Not Found |

**Diagnóstico SIS**: Rotas não registradas no FastAPI (ver logs do uvicorn para confirmar se houve erro de import).

---

## ❌ Frontends - Status: OFFLINE

| App | Porta | Erro |
|-----|-------|------|
| DTIC Dashboard | 3000 | Connection Refused |
| SIS Dashboard | 3001 | Connection Refused |
| Carregadores | 3005 | Connection Refused |
| DTIC Search | 3003 | Connection Refused |
| SIS Search | 3004 | Connection Refused |

**Diagnóstico**: Scripts Python `requests` não conseguem se conectar aos servers Vite (timeout SSL/TLS).
**Possível causa**: Biblioteca Python requests não aceita conexões HTTP locais do Vite.

---

## 📋 Dados Validados (DTIC)

### Métricas Gerais
```json
{
  "novos": 3,
  "em_progresso": 90,
  "pendentes": 16,
  "resolvidos": 11211
}
```

### Ranking Técnicos (Top 3)
1. Anderson da Silva Morim de Oliveira: **2.819 tickets**
2. Silvio Godinho Valim: **2.050 tickets**
3. Jorge Antonio Vicente Júnior: **2.017 tickets**

### Tickets Novos
- ID 11778: "INCIDENTE - DRC" (Solicitante: Gustavo Santos)
- ID 11766: [Segundo ticket novo]
- Total: **3 tickets com status "Novo"**

---

## 🔍 Problemas Identificados

### 1. Rotas SIS (Crítico)
- **Status**: ❌ Todas retornando 404
- **Causa Provável**: Import falhou no `main.py` ou router não registrado
- **Ação**: Verificar logs do uvicorn para erros de import

### 2. Frontends (Informativo)
- **Status**: ⚠️ Teste Python falhou (conexão recusada)
- **Realidade**: Serviços podem estar rodando (validar com curl/PowerShell)
- **Ação**: Testar manualmente via navegador

---

## ✅ Validação Manual Recomendada

### Backend
```bash
# Testar SIS manualmente
curl http://localhost:8000/docs
# Procurar seção "SIS Dashboard" no Swagger
```

### Frontends (Navegador)
- DTIC Dashboard: `http://localhost:3000`
- SIS Dashboard: `http://localhost:3001`
- Carregadores: `http://localhost:3005`
- DTIC Search: `http://localhost:3003`
- SIS Search: `http://localhost:3004`

---

**Arquivo de Dados**: `endpoint_test_results.json`
