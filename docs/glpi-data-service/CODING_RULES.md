# Regras de Codificação - Projeto GLPI Data Service V3

## ❌ PROIBIÇÕES ABSOLUTAS

### 1. NUNCA usar EMOJIS em código Python

**Motivo:** Causa `UnicodeEncodeError` no PowerShell do Windows

**Proibido:**
```python
print("🚀 Starting...")  # ❌ NUNCA
logger.info("✅ Success")  # ❌ NUNCA
```

**Permitido:**
```python
print("[START] Starting...")  # ✅ OK
logger.info("[OK] Success")   # ✅ OK
```

**Símbolos permitidos para output:**
- `[OK]`, `[DONE]`, `[SUCCESS]` - Sucesso
- `[ERROR]`, `[FAIL]` - Erro
- `[WARN]`, `[WARNING]` - Aviso
- `[INFO]`, `[START]` - Informação
- `[LOAD]`, `[SYNC]` - Processamento
- `-`, `=`, `*` - Separadores visuais

---

### 2. NUNCA usar caracteres especiais em logs/prints

**Proibido:**
- Emojis: 🚀✅❌📊🔧⚠️
- Símbolos Unicode: →←↑↓✓✗
- Caracteres acentuados em variáveis: `função`, `validação`

**Permitido:**
- ASCII básico (a-z, A-Z, 0-9, símbolos básicos)
- Português em comentários e docstrings (OK)
- Texto de usuário final (OK se necessário)

---

### 3. SEMPRE testar em PowerShell Windows

Scripts devem funcionar em:
- PowerShell 5.1+ (Windows nativo)
- CMD
- Bash/WSL (opcional)

**Teste obrigatório antes de commit:**
```powershell
python script.py 2>&1
# Não deve gerar UnicodeEncodeError
```

---

## ✅ Boas Práticas de Logging

### Formato Padrão

```python
# Níveis de log
logger.info("[START] Syncing DTIC context")
logger.info("[OK] Synced 1,234 tickets")
logger.warning("[WARN] Missing field: category_id")
logger.error("[ERROR] API connection failed")

# Output para usuário
print("=" * 60)
print("[START] GLPI Data Service - Sync Tool")
print("=" * 60)
print(f"[OK] Completed in {duration:.1f}s")
```

### Evitar

```python
# ❌ Emojis
print("🚀 Starting...")

# ❌ Unicode fancy
print("✓ Done")
print("→ Processing...")

# ❌ Mistura de idiomas em código
def sincronizar_entidades():  # ❌ Nome em português
    pass

# ✅ Correto
def sync_entities():  # ✅ Nome em inglês
    """Sincroniza entidades do GLPI."""  # ✅ Doc em português OK
    pass
```

---

## 🔧 Enforcement

1. **Code Review:** Rejeitar PRs com emojis
2. **Pre-commit Hook:** Adicionar verificação automática
3. **Lint Rule:** Adicionar regra no flake8/pylint

```python
# .flake8 ou setup.cfg
[flake8]
exclude = *.md,*.txt
# Adicionar custom checker para emojis
```

---

## 📋 Checklist Pré-Commit

Antes de fazer commit de qualquer script Python:

- [ ] Sem emojis no código
- [ ] Sem símbolos Unicode fancy
- [ ] Testado em PowerShell Windows
- [ ] Logs usam `[TAG]` ao invés de emojis
- [ ] Encoding explícito se necessário: `# -*- coding: utf-8 -*-`

---

## 🎯 Referência Rápida

**Substituições:**

| Emoji | Substituir por |
|-------|----------------|
| 🚀    | `[START]`      |
| ✅    | `[OK]`         |
| ❌    | `[ERROR]`      |
| ⚠️     | `[WARN]`       |
| 📊    | `[DATA]`       |
| 🔧    | `[FIX]`        |
| 📥    | `[LOAD]`       |
| 🏁    | `[DONE]`       |

---

**ÚLTIMA ATUALIZAÇÃO:** 2025-12-07  
**MOTIVO:** Erro Unicode em PowerShell Windows causou falha silenciosa na sincronização DTIC
