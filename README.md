# 📊 BDCau Data Platform — Ecossistema GLPI

**Versão**: v2.1  
**Última Atualização**: 22/01/2026  
**Ecossistema**: [GLPI Ecosystem](../glpi-ecosystem/README.md)

---

## 📍 O que é?

**BDCau Data Platform** é a camada de dados e analytics do ecossistema GLPI, sincronizando dados de múltiplas instâncias GLPI (DTIC + SIS) para um PostgreSQL centralizado e fornecendo dashboards analíticos especializados.

**Propósito**: Transformar dados operacionais GLPI em insights analíticos através de agregações, métricas e visualizações.

---

## 🌐 Como Acessar

| Serviço | URL | Tipo |
|:---|:---|:---|
| **Core API** | http://core-api.localhost | Backend (FastAPI) |
| **Dashboard DTIC** | http://view.localhost | Frontend (React) |

**Nota**: Acesso via Traefik proxy reverso. Portas locais (8000, 3001) liberadas.

---

## 🏗️ Arquitetura

### 4 Serviços no Stack

| Serviço | Container | Função | Status |
|:---|:---|:---|:---:|
| **Core Database** | `glpi-core-db` | PostgreSQL (schemas: dtic, sis) | ✅ Ativo |
| **Core API** | `glpi-core-api` | FastAPI (porta 8000) | ✅ Ativo |
| **Sync Daemon** | `glpi-core-sync` | Worker de sincronização GLPI→DB | ✅ Ativo |
| **Dashboard DTIC** | `glpi-view-dtic` | React Dashboard (porta 80) | ✅ Ativo |

### Fluxo de Dados

```
GLPI APIs (DTIC + SIS) 
    ↓ (sincronização bulk)
Sync Daemon (daemon_sync.py)
    ↓ (ETL)
PostgreSQL (schemas separados)
    ↓ (queries agregadas)
Core API (FastAPI)
    ↓ (REST API)
Dashboards React
```

---

## 🚀 Como Rodar

### Pré-requisitos
```bash
# Verificar Traefik
docker ps | grep dev-proxy

# Verificar rede web_proxy
docker network inspect web_proxy
```

### Primeira Vez (Build)
```bash
cd /home/workbench/projects/BDCauV2-1
docker-compose up --build -d
```

### Reiniciar Serviços
```bash
docker-compose restart
```

### Parar Tudo
```bash
docker-compose down
```

### Logs
```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f core-api
docker-compose logs -f glpi-sync
docker-compose logs -f view-dtic
```

---

## 🗄️ Database PostgreSQL

### Acesso Direto
```bash
docker exec -it glpi-core-db psql -U glpi_user -d glpi_data
```

### Schemas
- **`dtic`**: Dados GLPI DTIC
- **`sis`**: Dados GLPI SIS

### Porta Externa
- **5433** (mapeada para evitar conflito com outros projetos)

```bash
# Conectar de fora do Docker
psql -h localhost -p 5433 -U glpi_user -d glpi_data
```

---

## 📂 Estrutura do Projeto

```
BDCauV2-1/
├── docker-compose.yml          → Stack completo (DB + API + Sync + Dashboard)
├── .env                        → Configuração (tokens GLPI, credenciais DB)
│
├── glpi-data-service/          → Backend + Sync
│   ├── src/
│   │   ├── main.py             → FastAPI app
│   │   ├── database.py         → Conexão PostgreSQL
│   │   └── api/                → Endpoints REST
│   ├── scripts/
│   │   └── daemon_sync.py      → Daemon de sincronização
│   ├── logs/                   → Logs de execução
│   ├── requirements.txt
│   └── Dockerfile
│
├── glpi-dtic-dashboard/        → Dashboard DTIC (Implementado)
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/         → Componentes React
│   │   └── api/                → Cliente API
│   ├── package.json
│   └── Dockerfile
│
├── glpi-sis-dashboard/         → Dashboard SIS (Planejado)
├── [+4 dashboards planejados]  → Dashboards especializados
│
└── docs/
    ├── TRAEFIK_INTEGRATION.md  → Documentação Traefik
    └── [outras docs]
```

---

## 🔧 Componentes

### 1. Core API (Backend)
**Arquivo principal**: `glpi-data-service/src/main.py`

**Funcionalidades**:
- Endpoints REST para dados agregados
- Consultas otimizadas ao PostgreSQL
- Health check: `/health`
- API Docs: `http://core-api.localhost/docs`

**Tecnologias**: FastAPI, SQLAlchemy, PostgreSQL

### 2. Sync Daemon (Worker)
**Arquivo principal**: `glpi-data-service/scripts/daemon_sync.py`

**Funcionalidades**:
- Sincronização periódica GLPI → PostgreSQL
- Suporta múltiplas instâncias GLPI (DTIC + SIS)
- ETL com transformações de dados
- Logs estruturados

**Execução**: Roda como daemon em container separado

### 3. Dashboard DTIC (Frontend)
**Status**: ✅ Implementado

**Funcionalidades**:
- Visualização de métricas DTIC
- Gráficos com Recharts
- Ranking de técnicos
- Lista de tickets recentes
- Filtros de data

**Tecnologias**: React, Vite, TypeScript, Recharts

### 4. Database PostgreSQL
**Imagem**: postgres:15-alpine

**Schemas**:
- `dtic`: Tabelas GLPI DTIC
- `sis`: Tabelas GLPI SIS

**Configuração**:
- Healthcheck automático
- Volume persistente
- Porta customizada (5433)

---

## 🔐 Configuração (.env)

```env
# PostgreSQL
POSTGRES_DB=glpi_data
POSTGRES_USER=glpi_user
POSTGRES_PASSWORD=<senha_segura>

# GLPI DTIC
GLPI_DTIC_URL=https://glpi-dtic.example.com
GLPI_DTIC_APP_TOKEN=<app_token>
GLPI_DTIC_USER_TOKEN=<user_token>

# GLPI SIS (Opcional)
GLPI_SIS_URL=https://glpi-sis.example.com
GLPI_SIS_APP_TOKEN=<app_token>
GLPI_SIS_USER_TOKEN=<user_token>

# Timezone
TZ=America/Sao_Paulo

# Logging
LOG_LEVEL=INFO
```

---

## 📊 Dashboards

### Implementados
| Dashboard | URL | Status | Descrição |
|:---|:---|:---:|:---|
| **DTIC Dashboard** | http://view.localhost | ✅ Ativo | Métricas gerais DTIC |

### Planejados (Roadmap)
| Dashboard | Porta Original | Status | Descrição |
|:---|:---:|:---:|:---|
| **SIS Dashboard** | 3006 | 🔴 Não implementado | Visão geral SIS |
| **DTIC Smart Search** | 3002 | 🔴 Não implementado | Busca inteligente DTIC |
| **SIS Smart Search** | 3005 | 🔴 Não implementado | Busca inteligente SIS |
| **SIS Carregadores** | 3004 | 🔴 Não implementado | Monitoramento carregadores |

> **Nota**: Novas implementações serão integradas via Traefik com domínios `.localhost`.

---

## 🧩 Integrações

| Sistema | Tipo | Uso |
|:---|:---|:---|
| **GLPI DTIC API** | REST | Sincronização de dados (leitura) |
| **GLPI SIS API** | REST | Sincronização de dados (leitura) |
| **PostgreSQL** | Database | Armazenamento centralizado |
| **Traefik** | Proxy | Reverse proxy |

---

## 🛠️ Tecnologias

### Backend
- **Python 3.11+**
- **FastAPI** — API REST
- **SQLAlchemy** — ORM
- **PostgreSQL 15** — Database

### Frontend
- **React 18** — UI Framework
- **Vite** — Build tool
- **TypeScript** — Type safety
- **Recharts** — Visualizações gráficas

### DevOps
- **Docker + Docker Compose** — Containerização
- **Traefik** — Proxy reverso

---

## 📋 Governança e Versionamento

### Clean Slate Versioning
Projeto reestruturado em Dezembro/2025 após migrações

### Commits
Seguir [Conventional Commits](https://www.conventionalcommits.org/)

### Branches
```
main       → Produção (protegido)
  ↓
develop    → Integração
  ↓
feature/*  → Desenvolvimento
```

---

## 🎯 Status e Roadmap

### ✅ Completo
- Core API + PostgreSQL
- Sync Daemon (DTIC + SIS)
- Dashboard DTIC
- Integração Traefik

### 🔄 Em Andamento
- Expansão de métricas e agregações
- Otimização de queries

### 📋 Planejado
- Dashboard SIS
- 4+ dashboards especializados
- Smart Search (DTIC + SIS)
- Monitoramento de carregadores

---

## 🛠️ Troubleshooting

### Erro: Database não conecta
```bash
# Verificar healthcheck
docker-compose ps

# Inspecionar logs
docker-compose logs core-db

# Testar conexão
docker exec -it glpi-core-db pg_isready -U glpi_user
```

### Erro: Sync falha
```bash
# Verificar logs do daemon
docker-compose logs glpi-sync

# Verificar tokens GLPI no .env
cat .env | grep GLPI
```

### Erro: "502 Bad Gateway" no frontend
```bash
# Verificar Core API
curl http://core-api.localhost/health

# Verificar rede Traefik
docker network inspect web_proxy
```

### Erro: Porta 5433 ocupada
```bash
# Verificar quem está usando
sudo lsof -i :5433

# Alterar porta no docker-compose.yml se necessário
```

---

## 📚 Documentação Adicional

- **[TRAEFIK_INTEGRATION.md](docs/TRAEFIK_INTEGRATION.md)** — Configuração Traefik completa
- **[Ecossistema GLPI](../glpi-ecosystem/README.md)** — Visão geral de todos os projetos
- **[PROJECT_ORGANIZATION_ANALYSIS.md](../docs/PROJECT_ORGANIZATION_ANALYSIS.md)** — Análise arquitetural

---

## 📞 Contato

**Projeto Interno**: Departamentos DTIC e SIS  
**Documentação Técnica**: Ver `docs/`  
**Bugs/Features**: Criar issue no repositório

---

## 🏆 Características Técnicas

- ✅ Sincronização automática multi-GLPI
- ✅ Schemas PostgreSQL separados (DTIC/SIS)
- ✅ API REST documentada (FastAPI Swagger)
- ✅ Dashboards responsivos (React + Recharts)
- ✅ Healthchecks e monitoramento
- ✅ Proxy reverso centralizado (Traefik)
- ✅ Logs estruturados

**Estado**: Sistema em produção ativa com dashboard DTIC operacional.
