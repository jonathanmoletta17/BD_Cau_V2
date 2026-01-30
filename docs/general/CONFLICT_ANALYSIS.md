ria # Análise de Conflitos e Estratégia de Isolamento de Ambiente
**Contexto**: Execução simultânea de dois projetos idênticos (`BD_Cau_V2` e `projects-glpi`).

Para garantir que a cópia do projeto (`projects-glpi`) rode simultaneamente com o original (`BD_Cau_V2`) sem conflitos, precisamos isolar três camadas principais: **Rede (Portas)**, **Containers (Nomes)** e **Dados (Volumes)**.

---

## 1. Mapeamento de Recursos Atuais (O que conflita?)

### A. Portas (Hosts)
Se você subir os dois projetos, o Docker falhará ao tentar alocar estas portas na sua máquina (Host):

| Serviço | Porta Atual (Host) | Arquivo de Definição |
| :--- | :--- | :--- |
| **PostgreSQL** | `5432` | `docker-compose.yml`, `.env` |
| **Data Service (API)** | `8000` | `docker-compose.yml`, `frontend/vite.config.ts` (proxies) |
| **SIS Dashboard** | `3001` | `glpi-sis-dashboard/.../vite.config.ts` |
| **DTIC Smart Search** | `3002` | `glpi-dtic-smart-search/.../vite.config.ts` |
| **SIS Carregadores** | `3004` | `glpi-sis-carregadores/.../vite.config.ts` |
| **SIS Smart Search** | `3005` | `glpi-sis-smart-search/.../vite.config.ts` |
| **DTIC Dashboard** | `3006` | `glpi-dtic-dashboard/.../vite.config.ts` |
| **Agent Web (Chat)** | `8001` | `docker-compose.yml` |
| **Analysis Web** | `8002` | `docker-compose.yml` |

### B. Nomes de Container
O `docker-compose.yml` define nomes fixos (`container_name`). O Docker **não permite** dois containers com o mesmo nome na mesma máquina.
- `bd_cau_postgres`
- `glpi-data-service`
- `dtic-dashboard`, `sis-dashboard`, etc...

### C. Volumes de Dados
O volume `postgres_data` é definido como local. Se ambos os projetos usarem o mesmo nome de volume, eles **compartilharão o mesmo banco de dados**, o que destruirá o isolamento.

---

## 2. Plano de Ação: Migração para "Projects GLPI"

Para o novo projeto (`projects-glpi`), aplicaremos um **Offset de +10** em todas as portas e usaremos sufixos para containers.

### Passo 1: Limpeza de Nomes Fixos (`docker-compose.yml`)
**Ação**: Remover ou Alterar a propriedade `container_name`.
O ideal é deixar o Docker gerar nomes baseados na pasta (ex: `projectsglpi_postgres_1`), OU renomear explicitamente.
*Recomendação*: Renomear adicionando sufixo `_v2` ou `_new`.
- `bd_cau_postgres` -> `pg_glpi_new`
- `glpi-data-service` -> `data_glpi_new`
- (Repetir para todos)

### Passo 2: Isolamento de Volume (`docker-compose.yml`)
**Ação**: Alterar o nome do volume no `docker-compose.yml`.
```yaml
volumes:
  postgres_data_new:  # Renomear de 'postgres_data'
    driver: local
```
E atualizar o serviço postgres para usar `postgres_data_new`.

### Passo 3: Remapeamento de Portas (Tabela de De-Para)

Você precisará alterar os arquivos listados abaixo na pasta do **NOVO PROJETO**:

| Serviço | Porta Antiga | **Nova Porta** | Onde Alterar? |
| :--- | :--- | :--- | :--- |
| Postgres | 5432 | **5442** | `docker-compose.yml` (ports), `.env` (POSTGRES_PORT) |
| Data Service | 8000 | **8010** | `docker-compose.yml` (ports), `.env` |
| Agent Web | 8001 | **8011** | `docker-compose.yml` (ports: "8011:8000") |
| Analysis Web | 8002 | **8012** | `docker-compose.yml` (ports: "8012:8001") |
| SIS Dash | 3001 | **3011** | `glpi-sis-dashboard/.../vite.config.ts` |
| DTIC Search | 3002 | **3012** | `glpi-dtic-smart-search/.../vite.config.ts` |
| Carregadores | 3004 | **3014** | `glpi-sis-carregadores/.../vite.config.ts` |
| SIS Search | 3005 | **3015** | `glpi-sis-smart-search/.../vite.config.ts` |
| DTIC Dash | 3006 | **3016** | `glpi-dtic-dashboard/.../vite.config.ts` |

### Passo 4: Atualização de Proxies (Frontends)
Os frontends (Vite) usam um proxy para falar com o backend (`localhost:8000`). Como o backend mudará para `8010`, você deve atualizar todos os `vite.config.ts`:

*De:*
```ts
target: process.env.VITE_API_URL || 'http://127.0.0.1:8000'
```
*Para:*
```ts
target: process.env.VITE_API_URL || 'http://127.0.0.1:8010'
```
*(Ou melhor: configurar a variável VITE_API_URL no ambiente de execução/Docker)*

---

## 3. Checklist de Execução (Para o futuro)

Quando for subir o novo ambiente:

1.  [ ] **Editar .env**: Configurar `POSTGRES_PORT=5442` e ajustar credenciais se desejar.
2.  [ ] **Editar docker-compose.yml**:
    *   Renomear `container_name`s (ou remover).
    *   Renomear volume `postgres_data`.
    *   Atualizar mapeamento `ports` (Lado esquerdo: HOST).
3.  [ ] **Editar Frontends**:
    *   Abrir cada `vite.config.ts` e atualizar `port: XXXX` e proxy target.
4.  [ ] **Build Limpo**: Rodar `docker-compose up --build -d`.

Esta estrutura garante que `BD_Cau_V2` (Legado/Estável) e `projects-glpi` (Dev/Novo) coexistam na mesma máquina sem cruzar dados ou derrubar serviços um do outro.
