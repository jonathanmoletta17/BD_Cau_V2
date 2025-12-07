GLPI Ticket Viewer (Teste)

- Backend: Flask
- Importa `glpi_agent.glpi_client` da pasta `context-validation` para listar tickets e categorias do ambiente de teste.
- Endpoints:
  - `GET /api/tickets` — paginação, filtros e ordenação
  - `GET /api/categories` — lista de categorias (deduplicadas)
  - `GET /api/stats` — estatísticas por categoria/status
  - `DELETE /api/tickets/<id>` — exclusão (proteção via `X-Admin-Token`)

Executar:
```
python crawl4ai/context-validation/tools/ticket_viewer/app.py
```

Requisitos:
- Variáveis `.env` configuradas em `context-validation/.env` (GLPI TEST)
- `Flask` instalado

Notas:
- Carrega categorias do GLPI; opcionalmente usa `context-validation/data/id_mappings.json` se existir.
