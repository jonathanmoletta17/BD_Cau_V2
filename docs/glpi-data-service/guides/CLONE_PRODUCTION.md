# Clone de DTICução para Teste - Guia

## 🎯 Objetivo

Clonar dados **completos** do GLPI DTICução para ambiente de teste.

---

## ⚙️ Configuração

### 1. Adicionar ao `.env`:
```env
# GLPI DTICução
GLPI_DTIC_URL=http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php
GLPI_DTIC_APP_TOKEN=<seu_token_app_DTICucao>
GLPI_DTIC_USER_TOKEN=<seu_token_user_DTICucao>
```

### 2. Instalar dependências:
```bash
pip install tqdm psycopg2-binary requests python-dotenv
```

---

## 🚀 Uso

### Dry-Run (Testar sem inserir):
```bash
python scripts/clone_DTICuction_to_test.py --dry-run --limit 10
```

### Clone Parcial (100 tickets):
```bash
python scripts/clone_DTICuction_to_test.py --limit 100
```

### Clone Completo:
```bash
python scripts/clone_DTICuction_to_test.py --full
```

---

## 📊 O que faz:

1. **Autentica** no GLPI DTICução
2. **Busca** todos os tickets (paginado)
3. **Valida** se já existe no teste (por glpi_id)
4. **Insere** apenas novos
5. **Reporta** estatísticas

**Campos clonados:**
- ✅ Título, descrição
- ✅ Status, prioridade
- ✅ Categoria, entidade
- ✅ Técnico, grupo, requerente
- ✅ Todas as datas
- ✅ Hash MD5

---

## ✅ Resultado Esperado

```
📊 ESTATÍSTICAS
  Buscados:  15000
  Ignorados: 11204 (já existiam)
  Inseridos: 3796
  Erros:     0
```

**Total no teste:** ~22K tickets (dados atuais + DTICução)

---

## ⚠️ Importante

- **Não apaga** dados existentes
- **Skip duplicados** automaticamente
- **Logs detalhados** para debug
- **Backup recomendado** antes do clone

---

## 🔄 Próximos Passos

Após clone básico, implementar:
- [ ] Clone de históricos (ticket_changes)
- [ ] Clone de followups
- [ ] Clone de documents (metadados)
- [ ] Sincronização incremental
