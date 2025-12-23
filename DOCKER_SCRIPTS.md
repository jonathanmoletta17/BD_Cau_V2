# Scripts de Teste Docker

Este diretório contém scripts para testar a containerização.

## Build Individual

### Backend
```bash
cd /home/workbench/projects/BD_Cau_V2/glpi-ticket-agent
docker build -t glpi-backend:latest .
```

### Frontend
```bash
cd /home/workbench/projects/BD_Cau_V2/glpi-webChat-agent
docker build --build-arg VITE_API_URL=http://localhost:4000 -t glpi-frontend:latest .
```

## Build com Docker Compose

### Apenas Backend + Frontend
```bash
docker-compose build backend frontend
```

### Stack Completa
```bash
docker-compose build
```

## Executar

### Desenvolvimento (com Redis)
```bash
docker-compose up redis backend frontend
```

### Verificar Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Testar

### Backend Health
```bash
curl http://localhost:4000/health
```

### Frontend
```bash
curl http://localhost:3000/health
```

### Chat Integration
```bash
curl -X POST http://localhost:4000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Preciso resetar minha senha"}'
```

## Limpar

### Parar containers
```bash
docker-compose down
```

### Remover imagens
```bash
docker rmi glpi-backend:latest glpi-frontend:latest
```

### Limpar tudo
```bash
docker-compose down -v
docker system prune -f
```
