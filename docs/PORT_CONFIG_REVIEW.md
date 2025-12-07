# Levantamento de Portas Configuradas (Estado Atual)

**Data**: 2025-12-07 02:46
**Objetivo**: Documentar configurações ANTES de alterações

## 📋 Portas Configuradas nos Arquivos vite.config.ts

| Projeto | Porta Configurada | Arquivo |
|---------|-------------------|---------|
| **glpi-dtic-dashboard** | 3000 | `glpi-dtic-dashboard/frontend/vite.config.ts:58` |
| **glpi-sis-dashboard** | 3001 | `glpi-sis-dashboard/frontend/vite.config.ts:10` |
| **glpi-sis-carregadores-dashboard** | 3002 | `glpi-sis-carregadores-dashboard/frontend/vite.config.ts:19` |
| **glpi-dtic-smart-search** | 3003 | `glpi-dtic-smart-search/frontend/vite.config.ts:22` |
| **glpi-sis-smart-search** | 3004 | `glpi-sis-smart-search/frontend/vite.config.ts:22` |

## 🔍 Informação do Usuário

**Relatado**: Dashboard de Carregadores antigamente rodava na porta **3005**.

## ⚙️ Configurações de Proxy (Target Backend)

Todas as aplicações devem apontar para `http://127.0.0.1:8000` (Backend V3).

### Estado Atual dos Proxies:

1. **glpi-dtic-dashboard**: 
   - Proxy: `process.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'` ✅

2. **glpi-sis-dashboard**: 
   - Proxy: `process.env.VITE_API_URL || "http://127.0.0.1:8000"` ✅

3. **glpi-sis-carregadores-dashboard**: 
   - Proxy: `process.env.VITE_API_URL || 'http://127.0.0.1:8000'` ✅

4. **glpi-dtic-smart-search**: 
   - Proxy: `process.env.VITE_API_URL || 'http://127.0.0.1:8000'` ✅ (Corrigido de 8003)

5. **glpi-sis-smart-search**: 
   - Proxy: `process.env.VITE_API_URL || 'http://127.0.0.1:8000'` ✅ (Corrigido de 8004)

## 🎯 Ação Recomendada

Se o Dashboard de Carregadores deve rodar na porta **3005** (configuração original):

1. Alterar `glpi-sis-carregadores-dashboard/frontend/vite.config.ts`
2. Linha 19: `port: 3002` → `port: 3005`
3. Reiniciar o serviço `npm run dev`

## 📝 Notas

- Porta 3002 está atualmente configurada mas **não está sendo usada** (WebUI foi movido para 3002 mas está offline)
- Alterar para 3005 não causará conflitos
- Todas as outras portas (3000, 3001, 3003, 3004) estão funcionais

---
**Próximo passo**: Aguardar confirmação do usuário para alterar porta 3002 → 3005
