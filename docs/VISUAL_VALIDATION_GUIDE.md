# 📊 Guia de Validação Visual - Dashboards SIS vs DTIC

**Data**: 2025-12-07 03:38
**Status**: Navegador aberto, aguardando validação visual do usuário

---

## 🎯 O Que Validar em Cada Dashboard

### 1. Dashboard SIS - http://localhost:3001

#### ✅ O Que Deve Aparecer

**Cards de Métricas** (primeira linha):
- **Novos**: Número > 0 (baseado em 5.146 tickets totais)
- **Em Progresso**: Número > 0
- **Pendentes**: Número > 0
- **Resolvidos**: Número grande (maioria dos 5.146 tickets)

**Rankings** (corpo da página):
- **Ranking de Entidades**: Lista com nomes de entidades e contagens
- **Ranking de Categorias**: Lista com categorias ITIL e contagens
- **Ranking de Técnicos**: Lista com nomes de técnicos e tickets atribuídos

#### ❌ Problemas Possíveis

Se você ver **todos os valores em 0**:
1. Pressione `Ctrl + Shift + Delete`
2. Limpe "Cached images and files"
3. Recarregue a página com `Ctrl + F5`
4. OU abra em **modo anônimo** (Ctrl + Shift + N)

Se você ver **erros 404 no Console** (F12):
1. Verifique se a mensagem é "GET http://localhost:8000/api/v1/sis/dashboard/... 404"
2. Isso indicaria que o backend não está respondendo
3. MAS os testes técnicos mostraram 200 OK, então pode ser cache

---

### 2. SIS Smart Search - http://localhost:3004

#### ✅ O Que Deve Aparecer

**Tela inicial**:
- Campo de busca vazio
- Contador mostrando total de tickets (ex: "11320 tickets" ou similar)

**Após digitar "impressora" e Enter**:
- Lista de resultados (NÃO vazia)
- Tickets relacionados a impressoras
- Cada resultado com:
  - ID do ticket
  - Título
  - Data
  - Solicitante

#### ❌ Problemas Possíveis

Se a lista ficar **vazia após buscar**:
1. Tente outro termo: "manutencao", "eletrica", "hidraulica"
2. Verifique se há dados no schema SIS (5.146 tickets confirmados)
3. Verifique console (F12) para erros de API

---

### 3. Dashboard DTIC - http://localhost:3000 (Referência)

#### ✅ O Que Deve Aparecer

Este dashboard **já estava funcionando**, então use como **referência**:

**Cards de Métricas**:
- Novos: 3
- Em Progresso: 90
- Pendentes: 16
- Resolvidos: 11.211

**Rankings**:
- Entidades preenchidas
- Categorias preenchidas
- Técnicos preenchidos (ex: Anderson da Silva com 2.819 tickets)

**Se o DTIC funcionar mas o SIS não**:
- Indica problema específico do SIS (não é problema geral de backend)
- Verifique se `.env` do SIS aponta para porta 8000

---

## 🔍 Checklist de Validação

### Dashboard SIS (3001)
- [ ] Cards mostram números reais (não zeros)
- [ ] Ranking de Entidades preenchido
- [ ] Ranking de Categorias preenchido
- [ ] Ranking de Técnicos preenchido
- [ ] Console sem erros 404
- [ ] Números fazem sentido (total ~5.146 tickets)

### SIS Search (3004)
- [ ] Interface de busca carrega
- [ ] Campo de busca visível
- [ ] Busca por "impressora" retorna resultados
- [ ] Resultados mostram detalhes dos tickets
- [ ] Console sem erros

### DTIC Dashboard (3000) [Referência]
- [ ] Cards com valores conhecidos (3, 90, 16, 11211)
- [ ] Rankings preenchidos
- [ ] Interface visual similar ao SIS

---

## 📸 O Que Documentar

Se possível, capture screenshots de:
1. Dashboard SIS com dados visíveis
2. SIS Search com resultados de "impressora"
3. Qualquer erro no console (F12)

Salve em: `BD_Cau_V2/screenshots/`

---

## 🛠️ Troubleshooting Rápido

### Problema: "Tudo zerado no SIS"
**Causa**: Cache do navegador
**Solução**: Modo anônimo (Ctrl+Shift+N)

### Problema: "404 Not Found"
**Causa provável**: Backend não atualizado
**Solução**: 
```bash
# Reiniciar backend
cd glpi-data-service-v3
uvicorn src.main:app --reload --port 8000
```

### Problema: "SIS Search não retorna nada"
**Causa 1**: Endpoint de busca não implementado
**Causa 2**: Dados não sincronizados
**Verificar**: Schema SIS tem 5.146 tickets (confirmado)

---

## ✅ Resultados Esperados (Baseado em Testes Técnicos)

### Endpoints Testados com Sucesso (200 OK)
```
✅ /api/v1/sis/dashboard/stats-gerais
✅ /api/v1/sis/dashboard/ranking-entidades
✅ /api/v1/sis/dashboard/ranking-categorias
✅ /api/v1/sis/dashboard/tickets-novos
✅ /api/v1/sis/dashboard/ranking-tecnicos
```

### Dados Disponíveis
- Schema SIS: **5.146 tickets**
- Schema DTIC: **11.320 tickets**
- Ambos conectados ao backend na porta 8000

### Frontends Online
```
SIS Dashboard (3001): HTTP 200 OK ✅
SIS Search (3004): HTTP 200 OK ✅
DTIC Dashboard (3000): HTTP 200 OK ✅
```

---

**Por favor, reporte os resultados**:
1. Dashboard SIS mostra dados reais? (Sim/Não)
2. Quais valores você vê nos cards?
3. SIS Search retorna resultados para "impressora"? (Sim/Não)
4. Há algum erro no console? (Se sim, qual?)
