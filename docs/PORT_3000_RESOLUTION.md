# Resolução do Conflito de Porta 3000

**Data**: 2025-12-07
**Problema Diagnosticado**: Cache de navegador

## Situação

1.  **Open WebUI** foi configurado para porta `3002` no `docker-compose.yml`.
2.  Container do WebUI foi parado com sucesso (`docker ps` confirmou ausência).
3.  **DTIC Dashboard** (Vite) está rodando e respondendo na porta `3000`:
    ```
    curl http://localhost:3000
    StatusCode: 200
    Content-Type: text/html
    ```

## Problema

O navegador continuava exibindo a página do WebUI (em `/error`) devido a **cache agressivo** e múltiplas abas antigas abertas.

## Solução

Para visualizar o DTIC Dashboard corretamente:

1.  **Fechar TODAS as abas** de `localhost:3000` no navegador.
2.  Abrir uma **janela anônima** (Ctrl+Shift+N no Chrome ou Edge).
3.  Acessar `http://localhost:3000`.

Ou alternativamente:

1.  Limpar cache do navegador (Ctrl+Shift+Delete).
2.  Reabrir `http://localhost:3000` em nova aba.

## Status Atual (Correto)

| Serviço | Porta | Status |
|---|---|---|
| Backend V3 | 8000 | ✅ Online |
| DTIC Dashboard | 3000 | ✅ Online (Vite) |
| SIS Dashboard | 3001 | ✅ Online |
| DTIC Search | 3003 | ✅ Online |
| Open WebUI | 3002 | ⏹️ Parado (Conflito resolvido) |

---
**Próximo Passo**: Validar visualmente via janela anônima.
