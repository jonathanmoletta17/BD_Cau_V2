# Mapeamento Completo de Portas e Status - Ambiente Local

**Data**: 2025-12-07 02:40
**Ambiente**: Desenvolvimento (Windows + Vite + uvicorn)

## 🗺️ Tabela de Serviços Ativos

| App | Tipo | Porta | URL | Status | PID/Comando |
|-----|------|-------|-----|--------|-------------|
| **Backend V3** | API | 8000 | http://localhost:8000 | ✅ Online | uvicorn (8m+) |
| **DTIC Dashboard** | Frontend | 3000 | http://localhost:3000 | ✅ Online | npm dev (11m+) |
| **SIS Dashboard** | Frontend | 3001 | http://localhost:3001 | ⚠️ Sem dados | npm dev (8m+) |
| **SIS Carregadores** | Frontend | 3002 | http://localhost:3002 | ✅ Online | npm dev (iniciado) |
| **DTIC Smart Search** | Frontend | 3003 | http://localhost:3003 | ✅ Online | - |
| **SIS Smart Search** | Frontend | 3004 | http://localhost:3004 | ⚠️ Vazio | npm dev (9m+) |
| **PostgreSQL** | Database | 5433 | localhost:5433 | ✅ Online | Docker |
| **Open WebUI** | IA | 3002→OFF | - | ⏹️ Parado | - |

## 📋 Configuração de Portas por App

### Backend
- **glpi-data-service-v3**: Porta 8000
- Schemas: `dtic` (11.320 tickets), `sis` (5.146 tickets)

### Dashboards
- **DTIC**: Porta 3000 → Backend 8000 ✅
- **SIS**: Porta 3001 → Backend 8000 (`.env` corrigido) ⚠️
- **Carregadores**: Porta 3002 → Backend 8000 ✅

### Smart Search
- **DTIC**: Porta 3003 → Backend 8000 ✅
- **SIS**: Porta 3004 → Backend 8000 (corrigido) ⚠️

## ⚠️ Problemas Conhecidos

1. **SIS Dashboard e Search**: Exibem zeros/vazios apesar de dados no banco
   - Causa: Provável cache de navegador
   - Solução: Modo anônimo (Ctrl+Shift+N)

2. **Conflito porta 3002**: Resolvido (WebUI movido, agora parado)

## ✅ Validações Pendentes

- [ ] Testar Dashboard Carregadores visualmente
- [ ] Confirmar dados do SIS via modo anônimo
- [ ] Validar busca no SIS Search

---
**Última atualização**: Todos os serviços principais estão online.
