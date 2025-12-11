# Autenticação GLPI – Interface Web

Interface mínima e real de autenticação contra GLPI em produção.

## Configuração

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure o `.env` na raiz do projeto:
   ```env
   GLPI_PROD_URL=http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php
   GLPI_PROD_APP_TOKEN=2UVQ8P4gL2Z1xyo31liYpeSH2xaHjUQHJNABfuWO
   # Opcional: GLPI_DTIC_URL / GLPI_DTIC_APP_TOKEN
   ```

## Uso

Interface Web de Login (Flask):
```bash
python web/app.py
```
- Campos: usuário (auto-preenchido quando possível), senha com toggle, botão de login.
- Validações: tempo real, senha mínima (8), campos obrigatórios, sanitização.
- Segurança: CSRF (token + cookie), sem logar credenciais.
- Integração: `GET /initSession` (Authorization: Basic) com fallback para `POST /initSession`.

## Testes
- Unitários e integração do web app: `python -m pytest -q`
