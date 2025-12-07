# Auditoria de Portas e Conexões (Localhost)

**Data da Auditoria**: 2025-12-07
**Status**: ✅ Resolvido e Limpo

## 📊 Visão Geral (Pós-Limpeza)

| Aplicação | Tipo | Porta Local | Target Backend (Proxy) | Status Configuração |
|-----------|------|-------------|------------------------|---------------------|
| **glpi-data-service-v3** | Backend | `8000` | N/A | ✅ Ativo (Porta Principal) |
| **glpi-dtic-dashboard** | Frontend | `3000` | `http://127.0.0.1:8000` | ✅ Ativo |
| **glpi-sis-dashboard** | Frontend | `3001` | `http://127.0.0.1:8000` | ✅ Ativo |
| **glpi-sis-carregadores** | Frontend | `3002` | `http://127.0.0.1:8000` | ✅ Ativo |
| **glpi-dtic-smart-search**| Frontend | `3003` | `http://127.0.0.1:8000` | ✅ Corrigido (Era 8003) |
| **glpi-sis-smart-search** | Frontend | `3004` | `http://127.0.0.1:8000` | ✅ Corrigido (Era 8004) |
| **local-ai-stack (WebUI)** | AI Tool | `3080` | N/A | ✅ Corrigido (Era 3000) |
| **local-ai-stack (Ollama)** | AI Tool | `11434` | N/A | ✅ Padrão |

---

## 🛠️ Ações Realizadas

1.  **Resolução de Conflito de Porta (3000)**:
    *   **Problema**: `glpi-dtic-dashboard` e `Open WebUI` disputavam a porta 3000.
    *   **Ação**: `Open WebUI` movido para a porta **3080** no `docker-compose.yml`.

2.  **Correção de Rotas Smart Search**:
    *   **Problema**: Frontends de busca apontavam para portas inexistentes (8003, 8004).
    *   **Ação**: Ambos reconfigurados para consumir o Backend V3 centralizado na porta **8000**.

3.  **Limpeza de Configuração Backend**:
    *   **Ação**: Removidas variáveis de ambiente redundantes/não utilizadas (`DATABASE_DTIC_*`, `DATABASE_SIS_*`) do `docker-compose.yml` do backend.

---

## 📝 Referência Técnica

- **Backend V3**: `http://localhost:8000/api/v1`
- **Dashboards**:
    - DTIC: `http://localhost:3000`
    - SIS: `http://localhost:3001`
- **IA Local**:
    - WebUI: `http://localhost:3080`
    - API Ollama: `http://localhost:11434`
