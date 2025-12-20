# Quick Start: Backend V2

## ✅ Configurado para NÃO Conflitar com V1

**V1 (Produção):** Porta 8000, containers `glpi-*`  
**V2 (Novo):** Porta 8001, containers `glpi-*-v2`

## 🚀 Como Subir V2

```bash
# 1. Ir para diretório V2
cd glpi-data-service-v2

# 2. Subir containers
docker-compose up -d

# 3. Aguardar inicialização (30 segundos)
timeout /t 30

# 4. Verificar se subiu
docker ps | findstr v2

# 5. Testar backend
python validate_backend_v2.py
```

## 🔍 Troubleshooting

### Containers não sobem
```bash
# Ver erros
docker-compose logs

# Tentar rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Porta 8001 em uso
```bash
# Ver o que está usando
netstat -ano | findstr :8001

# Parar V2 e tentar novamente
docker-compose down
docker-compose up -d
```

### Backend não responde
```bash
# Ver logs do serviço
docker logs glpi-service-v2 -f

# Verificar se DB iniciou
docker logs glpi-postgres-v2
```

## ✅ Critério de Sucesso

Após executar `python validate_backend_v2.py`:
- Taxa de sucesso ≥ 75%
- Endpoints retornam dados
- Sem erros de conexão

## 📊 Verificar V1 e V2 Juntos

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
```

Deve mostrar ambos rodando:
- `glpi-service` → 8000
- `glpi-service-v2` → 8001
