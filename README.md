# BD_Cau_V2 - Ecossistema GLPI/DTIC

Monorepo contendo serviços de análise, classificação e visualização de dados do GLPI para os departamentos DTIC e SIS.

## 📂 Estrutura do Projeto

### Backend & Serviços
- **`glpi-data-service/`**: API Principal (FastAPI + PostgreSQL)
  - Backend unificado para DTIC e SIS (porta 8000)
  - Sincronização de dados GLPI com banco local
  - Schemas: `dtic`, `sis`

- **`glpi-dtic-agent-classificator/`**: Agente de Classificação de Tickets
  - Classificação automática usando IA/NLP
  - Integração com API GLPI
  - Validação e contexto de categorias
  - Classificação automática usando IA/NLP
  - Integração com API GLPI

- **`glpi-analysis-cli/`**: Ferramenta de Análise CLI
  - Análise de dados e relatórios
  - Assistente IA baseado em PandasAI
  - Suporte a múltiplos backends LLM

### Dashboards (Frontend React/Vite)
- **`glpi-dtic-dashboard/`**: Painel Principal DTIC
  - Métricas gerais, status de tickets, atividades recentes
  - Visualizações gráficas com Recharts

- **`glpi-sis-dashboard/`**: Painel SIS
  - Monitoramento específico do departamento SIS
  - Dashboards customizados

- **`glpi-sis-carregadores-dashboard/`**: Monitoramento de Carregadores
  - Dashboard especializado para gestão de carregadores

### Busca Inteligente
- **`glpi-dtic-smart-search/`**: Busca Inteligente DTIC
- **`glpi-sis-smart-search/`**: Busca Inteligente SIS

### Documentação
- **`docs/`**: Documentação técnica e arquitetura
  - Comparações de versões (V1 vs V2)
  - Guias de modelo de dados

## 🚀 Como Rodar

### Backend (glpi-data-service)
```bash
cd glpi-data-service
pip install -r requirements.txt
cp .env.example .env  # Configure suas variáveis
uvicorn src.main:app --reload
```

### Agente de Classificação
```bash
cd glpi-dtic-agent-classificator
pip install -r requirements.txt
cp .env.example .env  # Configure API GLPI e outros serviços
python agent_classificator/main.py
```

### Dashboards (Exemplo: DTIC)
```bash
cd glpi-dtic-dashboard/frontend
npm install
npm run dev
```

## 🛠️ Tecnologias

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React, Vite, TypeScript, Recharts
- **IA/NLP**: Gemini API, Python
- **DevOps**: Docker, Docker Compose

## 📋 Governança

Este repositório utiliza **Clean Slate Versioning** a partir de Dezembro/2025.

- **Monorepo**: Todos os componentes GLPI em um único repositório
- **Commits**: Seguir [Conventional Commits](https://www.conventionalcommits.org/)
- **Branches**: GitFlow simplificado (`main`, `develop`, `feature/*`)
- **Documentação**: Decisões arquiteturais em `docs/architecture/`

## 📝 Versionamento

### Histórico
- **Dezembro 2025**: Consolidação Clean Slate (este commit)
  - Projeto reestruturado após múltiplas migrações
  - Histórico anterior não recuperável
  - Ver `MIGRATION_HISTORY.md` para detalhes

### Estrutura de Branches
```
main       → produção (protegido)
  ↓
develop    → integração
  ↓
feature/*  → desenvolvimento
```

## 🤝 Contribuindo

Consulte `CONTRIBUTING.md` para:
- Regras de commit e PR
- Convenções de código
- Processo de review

## 📖 Documentação Adicional

- [Comparação V1 vs V2](docs/general/V1_VS_V2_ORGANIZATION.md)
- [Modelo de Dados GLPI](docs/glpi-data-service/)
- [Histórico de Migração](docs/general/MIGRATION_HISTORY.md)

## 🔧 Mapeamento de Portas

| Serviço | Porta |
|---------|-------|
| PostgreSQL | 5432 |
| Backend API | 8000 |
| SIS Dashboard | 3001 |
| DTIC Smart Search | 3002 |
| SIS Carregadores | 3004 |
| SIS Smart Search | 3005 |
| DTIC Dashboard | 3006 |

## 📞 Contato

Projeto interno - Departamentos DTIC e SIS
