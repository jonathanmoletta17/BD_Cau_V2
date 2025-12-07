# Guia de Contribuição - BD_Cau_V2

## 🎯 Sobre Este Documento

Este guia estabelece as convenções e práticas para contribuir com o monorepo `BD_Cau_V2`.

---

## 📋 Conventional Commits (Obrigatório)

Todos os commits DEVEM seguir o padrão [Conventional Commits](https://www.conventionalcommits.org/).

### Formato
```
type(scope): message

[optional body]

[optional footer]
```

### Types Permitidos

| Type | Descrição | Exemplo |
|------|-----------|---------|
| `feat` | Nova funcionalidade | `feat(dashboard): add ticket filters` |
| `fix` | Correção de bug | `fix(api): resolve null pointer exception` |
| `chore` | Tarefas de manutenção | `chore(deps): update fastapi to 0.104.1` |
| `docs` | Documentação | `docs(readme): update installation steps` |
| `refactor` | Refatoração sem mudança de comportamento | `refactor(agent): extract category logic` |
| `test` | Adição ou correção de testes | `test(api): add tests for /metrics endpoint` |
| `perf` | Melhorias de performance | `perf(db): add index on tickets.date` |
| `style` | Formatação (sem mudança lógica) | `style(api): format with black` |
| `ci` | CI/CD e scripts | `ci: add github actions workflow` |

### Scopes Recomendados

- **Subprojetos**: `data-service`, `agent`, `dtic-dashboard`, `sis-dashboard`, `smart-search`
- **Componentes**: `api`, `db`, `frontend`, `auth`, `sync`
- **Geral**: `deps`, `config`, `docs`

### Exemplos Válidos
```bash
# Features
git commit -m "feat(agent): implement AI classification with Gemini API"
git commit -m "feat(dtic-dashboard): add real-time ticket updates"

# Fixes
git commit -m "fix(api): handle null values in ticket status"
git commit -m "fix(sis-dashboard): resolve chart rendering issue"

# Chores
git commit -m "chore(deps): bump react from 18.2.0 to 18.3.0"
git commit -m "chore(config): update GLPI API endpoints"

# Docs
git commit -m "docs(architecture): document database schemas"
```

---

## 🌳 Estrutura de Branches

### Branches Principais

```
main       → Produção (protegida)
  ↓
develop    → Integração (padrão para merge)
  ↓
feature/*  → Desenvolvimento
```

### Regras de Branches

1. **`main`**
   - ✅ Sempre deployável
   - ✅ Protegida (requer PR aprovado)
   - ✅ Deploys para produção

2. **`develop`**
   - ✅ Branch padrão para desenvolvimento
   - ✅ Integra features antes de produção
   - ✅ Deploys para homologação (quando implementado)

3. **`feature/*`**
   - ✅ Criadas a partir de `develop`
   - ✅ Um feature branch por funcionalidade
   - ✅ Deletadas após merge

### Nomenclatura de Feature Branches

```bash
# Padrão
feature/<ticket-id>-<description>

# Exemplos
feature/GLPI-123-add-ticket-filters
feature/DTIC-456-fix-chart-rendering
feature/SIS-789-implement-search
```

---

## 🔄 Workflow de Desenvolvimento

### 1. Criar Feature Branch
```bash
git checkout develop
git pull origin develop
git checkout -b feature/GLPI-123-add-filters
```

### 2. Desenvolver e Commitar
```bash
# Fazer alterações...
git add .
git commit -m "feat(dashboard): add ticket status filters"
```

### 3. Manter Atualizado com Develop
```bash
git checkout develop
git pull origin develop
git checkout feature/GLPI-123-add-filters
git rebase develop  # ou: git merge develop
```

### 4. Push e Pull Request
```bash
git push origin feature/GLPI-123-add-filters
# Criar PR no GitHub/GitLab para develop
```

### 5. Após Aprovação e Merge
```bash
git checkout develop
git pull origin develop
git branch -d feature/GLPI-123-add-filters
```

---

## ✅ Checklist de PR (Pull Request)

Antes de abrir um PR, certifique-se:

- [ ] Código segue convenções do projeto (PEP 8 para Python, ESLint para JS/TS)
- [ ] Commits seguem Conventional Commits
- [ ] Testes executados e passando (quando aplicável)
- [ ] Documentação atualizada (README, docstrings, comentários)
- [ ] `.env.example` atualizado se novas variáveis adicionadas
- [ ] Sem credenciais ou segredos commitados
- [ ] Branch atualizado com `develop` (sem conflitos)

---

## 🧪 Testes

### Backend (Python)
```bash
cd glpi-data-service-v3
pytest                    # Rodar todos os testes
pytest tests/test_api.py  # Rodar teste específico
pytest -v                 # Verbose
```

### Frontend (React/Vite)
```bash
cd glpi-dtic-dashboard/frontend
npm test                  # Rodar testes Jest
npm run test:watch        # Watch mode
```

---

## 📝 Documentação

### Código Python
- Usar **docstrings** em funções e classes (PEP 257)
- Comentários para lógica complexa

```python
def classify_ticket(ticket_id: int) -> str:
    """
    Classifica um ticket GLPI usando IA.
    
    Args:
        ticket_id: ID do ticket no GLPI
        
    Returns:
        Categoria sugerida para o ticket
        
    Raises:
        GeminiAPIError: Se API Gemini falhar
    """
    # Implementação...
```

### Código TypeScript
- Usar **JSDoc** para funções complexas
- Tipos TypeScript descritivos

```typescript
/**
 * Fetch ticket metrics from API
 * @param filters - Optional filters for tickets
 * @returns Promise with metrics data
 */
async function fetchMetrics(filters?: TicketFilters): Promise<Metrics> {
    // Implementação...
}
```

### Documentação Arquitetural
- Decisões importantes em `docs/architecture/`
- Diagramas usando Mermaid quando útil

---

## 🚫 Proibições

### NÃO Commitar:
- ❌ Arquivos `.env` (usar `.env.example`)
- ❌ `node_modules/` ou `venv/`
- ❌ Arquivos `.pyc`, `__pycache__/`
- ❌ Logs (`.log`)
- ❌ Contextos de IA (`.trae/`, `.gemini/`, `.cursor/`)
- ❌ Credenciais, tokens, senhas

### NÃO Fazer:
- ❌ Commits diretamente em `main`
- ❌ Push com `--force` em branches compartilhadas
- ❌ Commits com mensagens vagas ("fix", "update", "wip")

---

## 🛠️ Ferramentas Recomendadas

### Python
- **Black**: Formatação automática
- **Flake8**: Linting
- **pytest**: Testes

### JavaScript/TypeScript
- **ESLint**: Linting
- **Prettier**: Formatação
- **Vitest**: Testes (para projetos Vite)

---

## 🔐 Segurança

### Variáveis de Ambiente
```bash
# ✅ CORRETO: .env.example
GLPI_API_URL=https://glpi.example.com
GLPI_API_TOKEN=your-token-here
DATABASE_URL=postgresql://user:password@localhost/dbname

# ❌ ERRADO: Valores reais em .env.example
GLPI_API_TOKEN=abc123real456token
```

### Verificação de Segredos
```bash
# Antes de commitar, verificar:
git diff --cached | grep -E "(password|token|secret|key)"
```

---

## 📞 Dúvidas?

- Consulte `README.md` para setup inicial
- Veja `MIGRATION_HISTORY.md` para contexto histórico
- Documentação técnica em `docs/`

---

**Última Atualização**: 2025-12-06  
**Versão**: 1.0 (Clean Slate Baseline)
