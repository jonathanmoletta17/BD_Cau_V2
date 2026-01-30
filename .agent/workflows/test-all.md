---
description: Rodar todos os testes do projeto
---

# Test Suite Completa

Execute todos os testes automatizados do projeto.

---

## 1. Backend Tests (glpi-data-service-v3)

// turbo
```bash
cd glpi-data-service-v3
pytest -v --cov=src --cov-report=term-missing
```

**Esperado**: Coverage >= 70%

---

## 2. Agente Tests (glpi-dtic-agent-classificator)

// turbo
```bash
cd glpi-dtic-agent-classificator
pytest tests/ -v
```

---

## 3. Frontend Tests (glpi-dtic-dashboard)

```bash
cd glpi-dtic-dashboard/frontend
npm test
```

---

## 4. Linting & Formatting

### Python
// turbo
```bash
black . --check
flake8 .
```

### TypeScript
```bash
cd glpi-dtic-dashboard/frontend
npm run lint
```

---

## Checklist de Validação

- [ ] Backend tests: PASS
- [ ] Agente tests: PASS
- [ ] Frontend tests: PASS
- [ ] Linting: PASS
- [ ] Coverage >= 70%
