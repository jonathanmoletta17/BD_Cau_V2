# Arquitetura DDD/Hexagonal

## Decisões de Design

### Context Isolation
Cada contexto (DTIC, SIS) é completamente isolado:
- Database schema próprio
- Domain models
- Services
- API routes

### Dependency Injection
```python
# Header obrigatório
X-Context: dtic  # ou sis

# FastAPI Dependencies
get_context()      → ContextEnum
get_db_session()   → SQLAlchemy Session (schema correto)
```

### Repository Pattern (Ports & Adapters)
```
Domain Layer:
  TicketRepository (Protocol) → Interface

Infrastructure Layer:
  PostgresTicketRepository → Implementation
```

### Multi-Schema Strategy
```python
SessionFactory.create(schema="dtic")
# Queries automaticamente redirecionadas para schema correto
```

---

## Layers

### 1. Domain
- **Entities:** Objetos de negócio puros
- **Ports:** Interfaces de repositórios (Protocols)
- **Sem dependências** de frameworks

### 2. Infrastructure
- **Adapters:** Implementações PostgreSQL
- **Dependências:** SQLAlchemy, drivers

### 3. Application
- **Services:** Lógica de negócio
- **Use Cases:** Orquestração
- **Usa:** Domain ports

### 4. Interface
- **API Routes:** FastAPI endpoints
- **Schemas:** Pydantic models
- **Dependências:** Services

---

## Fluxo de Request

```
1. Client → GET /api/v1/dtic/tickets
            Header: X-Context: dtic

2. Dependencies → get_context() → dtic
                  get_db_session() → Session(schema="dtic")

3. Route Handler → Injeta dependências

4. Service → TicketService(repository)

5. Repository → PostgresTicketRepository
                Query no schema "dtic"

6. Response → JSON
```

---

## Benefícios

✅ **Testabilidade:** Mocks fáceis via Protocols  
✅ **Manutenibilidade:** Camadas bem definidas  
✅ **Escalabilidade:** Adicionar contextos sem duplicação  
✅ **Flexibilidade:** Trocar implementações (ex: MongoDB)  
✅ **Clareza:** Código organizado e intuitivo
