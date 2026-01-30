# Traefik Integration - Antigravity (BDCauV2-1)

**Data**: 22/01/2026  
**Projeto**: BDCauV2-1 (Antigravity)  
**Proxy**: Traefik (dev-proxy)

---

## ✅ Configuração Completa

### Inventário Completo de Serviços (4 Total)

| Serviço | Container Name | Tipo | Traefik? | Acesso |
|:---|:---|:---|:---:|:---|
| **Core Database** | `glpi-core-db` | PostgreSQL | ❌ Não | Porta 5433 (local) |
| **Core API** | `glpi-core-api` | FastAPI Backend | ✅ Sim | `core-api.localhost` |
| **Core Sync Daemon** | `glpi-core-sync` | Worker (daemon) | ❌ Não | Interno (sem portas) |
| **DTIC Dashboard** | `glpi-view-dtic` | React Frontend | ✅ Sim | `view.localhost` |

**Resumo**: 
- **4 serviços totais**
- **2 serviços com Traefik** (core-api e view-dtic)
- **2 serviços internos** (core-db e core-sync)

### Serviços com Proxy Reverso Configurado

| Serviço | Container Name | Domínio | Porta Interna | Router Name |
|:---|:---|:---|:---:|:---|
| **Core API** | `glpi-core-api` | `core-api.localhost` | 8000 | antigravity-core-api |
| **DTIC Dashboard** | `glpi-view-dtic` | `view.localhost` | 80 | antigravity-view-dtic |

### Acesso aos Serviços
- **Core API**: http://core-api.localhost
- **DTIC Dashboard**: http://view.localhost

**Nota**: As portas 8000 e 3001 do localhost foram **liberadas**. Os serviços agora são acessíveis apenas via Traefik.

---

## 📋 Labels Traefik Aplicadas

### core-api (Backend)
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.docker.network=web_proxy"
  - "traefik.http.routers.antigravity-core-api.rule=Host(`core-api.localhost`)"
  - "traefik.http.services.antigravity-core-api.loadbalancer.server.port=8000"
```

### view-dtic (Frontend)
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.docker.network=web_proxy"
  - "traefik.http.routers.antigravity-view-dtic.rule=Host(`view.localhost`)"
  - "traefik.http.services.antigravity-view-dtic.loadbalancer.server.port=80"
```

---

## 🔧 Fallback: Configuração Manual (dynamic.yml)

**Ambiente**: WSL com possível instabilidade na descoberta automática via Docker socket

Se a descoberta automática via labels não funcionar, adicione ao arquivo `dynamic.yml` do Traefik (`/home/workbench/projects/dev-proxy/config/dynamic.yml`):

```yaml
http:
  routers:
    # Antigravity Core API
    antigravity-core-api:
      rule: "Host(`core-api.localhost`)"
      service: antigravity-core-api
      entryPoints:
        - web
    
    # Antigravity View DTIC
    antigravity-view-dtic:
      rule: "Host(`view.localhost`)"
      service: antigravity-view-dtic
      entryPoints:
        - web

  services:
    # Antigravity Core API Service
    antigravity-core-api:
      loadBalancer:
        servers:
          - url: "http://glpi-core-api:8000"
    
    # Antigravity View DTIC Service
    antigravity-view-dtic:
      loadBalancer:
        servers:
          - url: "http://glpi-view-dtic:80"
```

### Aplicação do Fallback

1. Edite o arquivo dynamic.yml:
   ```bash
   nano /home/workbench/projects/dev-proxy/config/dynamic.yml
   ```

2. Adicione a configuração acima

3. **Não é necessário reiniciar** o Traefik - ele detecta mudanças automaticamente

4. Verifique logs do Traefik:
   ```bash
   docker logs dev-proxy
   ```

---

## 🔍 Verificação de Status

### 1. Verificar Redes Docker
```bash
docker network inspect web_proxy
```

Deve mostrar os containers `glpi-core-api` e `glpi-view-dtic` conectados.

### 2. Verificar Labels dos Containers
```bash
docker inspect glpi-core-api | grep -A 10 "Labels"
docker inspect glpi-view-dtic | grep -A 10 "Labels"
```

### 3. Testar Acesso
```bash
curl -I http://core-api.localhost/health
curl -I http://view.localhost
```

### 4. Verificar Dashboard do Traefik
Se o dashboard estiver habilitado, acesse:
```
http://localhost:8080  # ou porta configurada
```

Procure pelos routers `antigravity-core-api` e `antigravity-view-dtic`.

---

## 🚀 Como Subir os Serviços

### Primeira Vez (Build Necessário)
```bash
cd /home/workbench/projects/BDCauV2-1
docker-compose up --build -d
```

### Reiniciar Sem Rebuild
```bash
docker-compose restart
```

### Logs
```bash
docker-compose logs -f core-api
docker-compose logs -f view-dtic
```

---

## ⚠️ Troubleshooting

### Problema: Serviço não responde
**Causa**: Container não está na rede `web_proxy`

**Solução**:
```bash
docker network connect web_proxy glpi-core-api
docker network connect web_proxy glpi-view-dtic
```

### Problema: "502 Bad Gateway"
**Causa**: Porta interna incorreta ou serviço não respondendo

**Verificação**:
```bash
docker exec glpi-core-api curl -I http://localhost:8000/health
docker exec glpi-view-dtic curl -I http://localhost:80
```

### Problema: "404 Not Found"
**Causa**: Traefik não reconheceu as labels ou rota não foi registrada

**Solução**: Use o fallback manual no `dynamic.yml` (vide acima)

---

## 📦 Informações do Projeto

**Network Externa**: `web_proxy` (criada pelo `dev-proxy`)  
**Network Interna**: `app_network` (bridge local do BDCauV2-1)  
**Database**: `core-db` (porta 5433 mapeada, não usa Traefik)  
**Sync Service**: `glpi-sync` (daemon interno, não usa Traefik)

---

## 🔄 Comparação: Antes vs Depois

| Aspecto | Antes | Depois |
|:---|:---|:---|
| **Core API** | `localhost:8000` | `http://core-api.localhost` |
| **DTIC View** | `localhost:3001` | `http://view.localhost` |
| **Conflito de Portas** | ❌ Sim (8000, 3001 ocupadas) | ✅ Não (portas liberadas) |
| **Acesso Interno Docker** | ✅ Sim | ✅ Sim (mantido) |
| **Proxy Reverso** | ❌ Não | ✅ Traefik |

---

**Status**: ✅ INTEGRAÇÃO COMPLETA  
**Próximos Passos**: Reiniciar containers e testar acesso via domínios `.localhost`
