# ✅ Guia de Validação Final - Ambiente BD_Cau_V2

**Data**: 2025-12-07 02:42
**Status**: Ambiente configurado e pronto para validação visual

## 🎯 Checklist de Validação

### 1. Backend (Porta 8000)

- [x] Serviço rodando (uvicorn)
- [x] Rotas DTIC registradas
- [x] Rotas SIS registradas
- [x] Banco de dados acessível (5433 → PostgreSQL)

**Como validar**:
```bash
# Testar health
curl http://localhost:8000/health

# Testar DTIC
curl http://localhost:8000/api/v1/dtic/metrics-gerais

# Testar SIS
curl http://localhost:8000/api/v1/sis/dashboard/stats-gerais
```

### 2. Dashboards

#### DTIC Dashboard (Porta 3000) ✅
- **Como validar**:
  1. Feche todas as abas de `localhost:3000`
  2. Abra **modo anônimo** (Ctrl+Shift+N)
  3. Acesse: `http://localhost:3000`
  4. **Esperado**: Cards com métricas, gráficos, ranking

#### SIS Dashboard (Porta 3001) ⚠️
- **Status**: Interface OK, mas dados zerados (cache)
- **Como validar**:
  1. Feche todas as abas de `localhost:3001`
  2. Abra **modo anônimo** (Ctrl+Shift+N)
  3. Acesse: `http://localhost:3001`
  4. **Esperado**: Cards com métricas de 5.146 tickets

#### Dashboard Carregadores (Porta 3002) ✅
- **Como validar**:
  1. Abra **modo anônimo** (Ctrl+Shift+N)
  2. Acesse: `http://localhost:3002`
  3. **Esperado**: Interface de gestão de carregadores

### 3. Smart Search

#### DTIC Search (Porta 3003) ✅
- **Como validar**:
  1. Acesse: `http://localhost:3003`
  2. Digite "impressora" e pressione Enter
  3. **Esperado**: ~843 resultados

#### SIS Search (Porta 3004) ⚠️
- **Status**: Lista vazia (cache ou endpoint não implementado)
- **Como validar**:
  1. Feche todas as abas de `localhost:3004`
  2. Abra **modo anônimo**
  3. Acesse: `http://localhost:3004`
  4. Teste uma busca

---

## 🔧 Resolução de Problemas

### Problema: Apps SIS exibem zeros/vazio

**Causa**: Cache do navegador mostrando dados antigos

**Solução** (escolha uma):

#### Opção 1: Modo Anônimo (Rápido)
1. Pressione `Ctrl + Shift + N` (Chrome) ou `Ctrl + Shift + P` (Firefox)
2. Acesse a URL do app
3. Valide se os dados aparecem

#### Opção 2: Limpar Cache
1. Pressione `Ctrl + Shift + Delete`
2. Selecione "Imagens e arquivos em cache"
3. Clique em "Limpar dados"
4. Recarregue a página (`F5`)

#### Opção 3: Hard Refresh
1. Na página do app, pressione `Ctrl + F5`
2. Aguarde recarregamento completo

### Problema: Porta já em uso

**Sintoma**: `EADDRINUSE` ou "porta já está sendo usada"

**Solução**:
```powershell
# Verificar o que está usando a porta (ex: 3000)
netstat -ano | findstr :3000

# Matar o processo (substitua PID)
taskkill /PID <PID> /F
```

### Problema: Backend não inicia

**Sintoma**: Erro de import ou conexão com banco

**Solução**:
1. Verificar se PostgreSQL está rodando (porta 5433)
2. Verificar `.env` do backend
3. Reiniciar uvicorn:
   ```bash
   cd glpi-data-service-v3
   uvicorn src.main:app --reload --port 8000
   ```

---

## 📝 Comandos Úteis

### Iniciar Ambiente Completo

```bash
# Backend
cd glpi-data-service-v3
uvicorn src.main:app --reload --port 8000

# DTIC Dashboard
cd glpi-dtic-dashboard/frontend
npm run dev

# SIS Dashboard
cd glpi-sis-dashboard/frontend
npm run dev

# Carregadores
cd glpi-sis-carregadores-dashboard/frontend
npm run dev

# DTIC Search
cd glpi-dtic-smart-search/frontend
npm run dev

# SIS Search
cd glpi-sis-smart-search/frontend
npm run dev
```

### Parar Todos os Serviços

```powershell
# Matar todos os processos node e uvicorn
taskkill /IM node.exe /F
taskkill /IM python.exe /F
```

---

## ✅ Próximos Passos

1. **Validar visualmente cada app** usando modo anônimo
2. **Reportar quaisquer problemas** encontrados
3. **Confirmar que dados SIS aparecem** após limpar cache
4. **Testar funcionalidades principais** de cada dashboard

---

**Documentação Complementar**:
- `docs/AUDIT_PORTS_AND_CONNECTIONS.md` - Mapeamento de portas
- `docs/VALIDATION_REPORT.md` - Relatório de validação técnica
- `docs/SIS_APPS_DIAGNOSIS.md` - Diagnóstico específico SIS
- `docs/FINAL_PORTS_MAP.md` - Status atual de todos os serviços
