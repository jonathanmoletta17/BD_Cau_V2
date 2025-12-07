---
description: Deploy ambiente de desenvolvimento completo
---

# Deploy Dev - Todos os Serviços GLPI

Este workflow sobe todos os serviços necessários para desenvolvimento.

## Pré-requisitos
- Python 3.11+ instalado
- Node.js 18+ instalado
- PostgreSQL rodando
- `.env` configurado em cada subprojeto

---

## 1. Backend (glpi-data-service-v3)

// turbo
```bash
cd glpi-data-service-v3
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

**Health Check**:
```bash
curl http://localhost:8000/health
```

---

## 2. Dashboard DTIC

// turbo
```bash
cd glpi-dtic-dashboard/frontend
npm install
npm run dev
```

**Acesso**: http://localhost:5173

---

## 3. Dashboard SIS (Opcional)

```bash
cd glpi-sis-dashboard/frontend
npm install
npm run dev
```

**Acesso**: http://localhost:5174

---

## 4. Agente Classificador (Opcional - Para Testes)

```bash
cd glpi-dtic-agent-classificator
pip install -r requirements.txt
python agent_classificator/main.py
```

---

## Verificação Final

**Backend**:
- [ ] API respondendo em http://localhost:8000
- [ ] `/health` retorna 200 OK

**Frontend**:
- [ ] Dashboard carregando
- [ ] Conectando com backend

**Banco de Dados**:
- [ ] PostgreSQL acessível
- [ ] Schemas `glpi`, `sis`, `dtic` existem
