# Organização V1 vs V2 - GLPI Backend

## 📁 Estrutura de Diretórios

### `glpi-data-service` (V1 - PRODUÇÃO - NÃO MEXER)
**Status:** Backend legado em produção  
**Responsabilidade:** Manter funcionando até migração completa

**Conteúdo:**
- `src/` - Código legado (FastAPI fat controllers)
- `src/glpi_client/` - Cliente API GLPI (compartilhado)
- `src/utils/` - Utilitários (compartilhado)
- `docker-compose.yml` - Infraestrutura atual
- `.env` - Configurações de produção

**NÃO criar arquivos novos aqui!**

---

### `glpi-data-service-v2` (V2 - NOVO - TRABALHAR AQUI)
**Status:** Backend refatorado com Clean Architecture  
**Responsabilidade:** Todo desenvolvimento novo

**Conteúdo:**
```
glpi-data-service-v2/
├── src/
│   ├── domain/          # Modelos de domínio
│   ├── repositories/    # Data layer
│   │   ├── base.py
│   │   └── ticket_repository.py
│   ├── services/        # Business logic
│   │   └── dashboard_service.py
│   └── api/            # Controllers
│       └── routes/
│           └── dashboard.py
├── scripts/            # Scripts auxiliares
│   ├── populate_test_env.py         ✅ Movido de v1
│   └── analyze_ticket_topics.py     ✅ Movido de v1
├── docs/
│   ├── POPULATE_TEST_ENV_GUIDE.md   ✅ Movido de v1
│   └── ANALYSIS_STATUS.md           ✅ Movido de v1
├── data/
│   └── test_env_mapping.json        ✅ Movido de v1
└── README.md
```

---

## 🔄 Arquivos Movidos (2025-11-30)

| Arquivo | Origem (v1) | Destino (v2) | Status |
|---------|-------------|--------------|--------|
| `populate_test_env.py` | glpi-data-service/ | glpi-data-service-v2/ | ✅ Movido |
| `analyze_ticket_topics.py` | glpi-data-service/ | glpi-data-service-v2/ | ✅ Movido |
| `POPULATE_TEST_ENV_GUIDE.md` | glpi-data-service/ | glpi-data-service-v2/ | ✅ Movido |
| `ANALYSIS_STATUS.md` | glpi-data-service/ | glpi-data-service-v2/ | ✅ Movido |
| `test_env_mapping.json` | glpi-data-service/ | glpi-data-service-v2/ | ✅ Movido |

---

## 📜 Regras de Trabalho

### ✅ FAZER (V2)
- Criar novos endpoints
- Refatorar código legado
- Adicionar testes
- Implementar Clean Architecture
- Scripts de análise/população
- Documentação nova

### ❌ NÃO FAZER (V1)
- Adicionar código novo
- Refatorar (pode quebrar produção)
- Deletar arquivos (pode afetar prod)
- Criar scripts novos

### 🔄 COMPARTILHADO (entre V1 e V2)
- `src/glpi_client/` - Cliente API GLPI
- `src/utils/` - Utilitários (logger, etc)
- `.env` config (ambos usam)
- PostgreSQL database (mesmo schema)

---

## 🚀 Workflow de Desenvolvimento

1. **Desenvolvimento:** Trabalhar em `glpi-data-service-v2/`
2. **Testes:** Executar contra ambiente de teste
3. **Validação:** Garantir compatibilidade
4. **Deploy:** Blue-Green deployment (v1 e v2 em paralelo)
5. **Migração:** Switch gradual de prod para v2
6. **Cleanup:** Após 100% migrado, arquivar v1

---

## 📊 Status Atual

| Componente | V1 (Prod) | V2 (Novo) | Progresso |
|-----------|-----------|-----------|-----------|
| Dashboard routes | ✅ Funcionando | ✅ Refatorado | 100% |
| Sync Worker | ✅ Funcionando | ⏳ Pendente | 0% |
| Stats endpoints | ✅ Funcionando | ⏳ Pendente | 0% |
| Repositories | ❌ N/A | ✅ Criados | 40% |
| Services | ❌ N/A | ✅ Criados | 40% |
| Testes | ❌ N/A | ⏳ Pendente | 0% |

---

## 🎯 Próximos Passos (V2)

1. ⏳ Refatorar `sync_worker.py`
2. ⏳ Refatorar `stats.py` endpoints
3. ⏳ Criar Pydantic schemas
4. ⏳ Suite de testes (unit + integration)
5. ⏳ CI/CD pipeline

---

**Importante:** SEMPRE criar arquivos novos em `glpi-data-service-v2`, nunca em `glpi-data-service` (produção).
