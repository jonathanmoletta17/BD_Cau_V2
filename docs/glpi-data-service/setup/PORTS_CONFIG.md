# Configuração V1 vs V2 - Portas e Containers

## Portas Usadas

### V1 (Produção - glpi-data-service)
- Backend: **8000**
- PostgreSQL: **5432**
- pgAdmin: **5050**
- Containers: `glpi-postgres`, `glpi-pgadmin`,  `glpi-service`
- Network: `glpi-network`

### V2 (Novo - glpi-data-service-v2)
- Backend: **8001** ← Não conflita com V1
- PostgreSQL: **5433** ← Não conflita com V1
- pgAdmin: **5051** ← Não conflita com V1
- Containers: `glpi-postgres-v2`, `glpi-pgadmin-v2`, `glpi-service-v2`
- Network: `glpi-network-v2`

## Comandos

### V1 (NÃO MEXER)
```bash
cd glpi-data-service
docker-compose up -d     # Subir
docker-compose down      # Parar
docker logs glpi-service  # Ver logs
```

### V2 (Desenvolvimento)
```bash
cd glpi-data-service-v2
docker-compose up -d           # Subir V2
docker-compose down            # Parar V2
docker logs glpi-service-v2    # Ver logs V2
```

## Testar V2
```bash
cd glpi-data-service-v2

# Subir containers
docker-compose up -d

# Aguardar iniciar (30s)
sleep 30

# Executar validação
python validate_backend_v2.py
```

## Verificar Conflitos
```bash
# Ver todos os containers rodando
docker ps

# Ver portas em uso
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

**IMPORTANTE:** V1 e V2 podem rodar **juntos** sem conflitos!
