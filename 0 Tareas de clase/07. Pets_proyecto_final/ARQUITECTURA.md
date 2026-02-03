# 🏗️ ARQUITECTURA DEL SISTEMA

## Componentes Principales

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTE / USUARIO                        │
│                    (curl, Postman, Browser)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Requests
                             │ POST /api/pets/
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO REST API (Puerto 8000)                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  views.py                                                │   │
│  │  - pets_api_list() ────► Crea mascota en MongoDB        │   │
│  │                    └───► Envía tarea a Redis (RPUSH)    │   │
│  │  - redis_stats()   ────► Consulta estado de cola        │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────┬─────────────────────────────────┬────────────────┘
               │                                 │
               │ mongoengine                     │ redis-py
               │ (ORM)                           │ (client)
               ▼                                 ▼
  ┌─────────────────────┐           ┌──────────────────────────┐
  │   MONGODB:27017     │           │    REDIS:6379            │
  │  ┌───────────────┐  │           │  ┌────────────────────┐ │
  │  │   Database    │  │           │  │  Lista (Queue):    │ │
  │  │  pets_database│  │           │  │   "pets:tasks"     │ │
  │  │               │  │           │  │                    │ │
  │  │  Collection:  │  │           │  │  [task1, task2,...]│ │
  │  │    - pet      │  │           │  │                    │ │
  │  └───────────────┘  │           │  │  FIFO: RPUSH/BLPOP │ │
  └─────────────────────┘           │  └────────────────────┘ │
                                    └──────────┬───────────────┘
                                               │
                      ┌────────────────────────┼────────────────────────┐
                      │                        │                        │
                      │ BLPOP                  │ BLPOP                  │ BLPOP
                      │ (blocking)             │ (blocking)             │ (blocking)
                      ▼                        ▼                        ▼
         ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
         │   CONSUMER 1         │ │   CONSUMER 2         │ │   CONSUMER 3         │
         │  ┌────────────────┐  │ │  ┌────────────────┐  │ │  ┌────────────────┐  │
         │  │ consumer.py    │  │ │  │ consumer.py    │  │ │  │ consumer.py    │  │
         │  │                │  │ │  │                │  │ │  │                │  │
         │  │ 1. Recibe tarea│  │ │  │ 1. Recibe tarea│  │ │  │ 1. Recibe tarea│  │
         │  │ 2. Busca info  │  │ │  │ 2. Busca info  │  │ │  │ 2. Busca info  │  │
         │  │    Wikipedia   │  │ │  │    Wikipedia   │  │ │  │    Wikipedia   │  │
         │  │ 3. Genera tips │  │ │  │ 3. Genera tips │  │ │  │ 3. Genera tips │  │
         │  │ 4. Crea JSON   │  │ │  │ 4. Crea JSON   │  │ │  │ 4. Crea JSON   │  │
         │  └────────┬───────┘  │ │  └────────┬───────┘  │ │  └────────┬───────┘  │
         └───────────┼──────────┘ └───────────┼──────────┘ └───────────┼──────────┘
                     │                        │                        │
                     └────────────────────────┴────────────────────────┘
                                              │
                                              ▼
                                  ┌─────────────────────────┐
                                  │  /app/processed_data/   │
                                  │  (Shared Volume)        │
                                  │                         │
                                  │  ├─ pet1_Max.json       │
                                  │  ├─ pet2_Luna.json      │
                                  │  └─ pet3_Rocky.json     │
                                  └─────────────────────────┘
```

## Flujo de Datos

### 1. Creación de Mascota

```
Usuario ──POST /api/pets/──► Django API
                               │
                               ├──► MongoDB: Guarda mascota
                               │
                               └──► Redis: RPUSH pets:tasks
                                           {
                                             "pet_id": "123",
                                             "name": "Max",
                                             "species": "Dog",
                                             ...
                                           }
```

### 2. Procesamiento por Workers

```
Consumer (Worker) ──BLPOP pets:tasks──► Redis
      │                                  (Espera bloqueante)
      │
      ├── Recibe: {"pet_id": "123", "name": "Max", ...}
      │
      ├── 1. Busca en Wikipedia API
      │      GET https://en.wikipedia.org/api/rest_v1/page/summary/dog
      │
      ├── 2. Genera fun facts
      │      {lifespan, diet, fun_fact}
      │
      ├── 3. Genera health tips
      │      ["Tip 1", "Tip 2", ...]
      │
      └── 4. Guarda JSON enriquecido
             /app/processed_data/123_Max_20250124_143022.json
```

## Docker Compose - Orquestación

```yaml
services:
  redis         ──► Queue/Message Broker
  mongo         ──► Persistent Storage
  django-api    ──► Producer (Genera tareas)
  consumer-1    ──┐
  consumer-2    ──┼──► Consumers (Procesan tareas)
  consumer-3    ──┘

networks:
  pets-network  ──► Comunicación entre contenedores

volumes:
  mongo_data        ──► Persistencia de MongoDB
  processed_data    ──► Archivos JSON compartidos
```

## Patrones Implementados

### 1. Producer-Consumer Pattern
- **Producer**: Django API genera tareas
- **Queue**: Redis lista FIFO
- **Consumers**: Workers procesan tareas

### 2. Microservicios
- Cada servicio en su contenedor
- Comunicación vía Redis
- Escalable horizontalmente

### 3. Async Processing
- API responde inmediatamente
- Procesamiento en background
- Sin bloqueo del usuario

## Escalabilidad

### Vertical (Recursos)
```bash
# Aumentar recursos a un servicio
docker-compose up -d --scale consumer=5
```

### Horizontal (Instancias)
```yaml
# Agregar más consumers en docker-compose.yml
consumer-4:
  build:
    context: .
    dockerfile: Dockerfile.consumer
  environment:
    - CONSUMER_ID=4
```

## Tecnologías por Capa

| Capa | Tecnología | Puerto |
|------|-----------|--------|
| API | Django 4.2.7 + DRF | 8000 |
| Queue | Redis 7 Alpine | 6379 |
| Database | MongoDB 7.0 | 27017 |
| Workers | Python 3.11 | - |
| Orchestration | Docker Compose | - |

## Comunicación entre Servicios

```
Django API ←─────────────────→ MongoDB (mongoengine)
     │
     ├─────────────────────────→ Redis (redis-py)
     │                               │
     │                               │
Consumer ←────────────────────────────┘
     │
     └─────────────────────────→ External APIs (requests)
                                  - Wikipedia API
```

## Volúmenes y Persistencia

```
┌─────────────────────────┐
│  mongo_data (volume)    │  ──► Datos de MongoDB
│  /data/db               │      (Persiste entre reinicios)
└─────────────────────────┘

┌─────────────────────────┐
│  processed_data (volume)│  ──► Archivos JSON generados
│  /app/processed_data    │      (Compartido entre workers)
└─────────────────────────┘

┌─────────────────────────┐
│  . (bind mount)         │  ──► Código fuente de Django
│  /app                   │      (Hot reload en desarrollo)
└─────────────────────────┘
```

## Health Checks

```yaml
redis:
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    # Espera PONG antes de iniciar dependientes

mongo:
  healthcheck:
    test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
    # Verifica conexión a MongoDB

django-api:
  depends_on:
    redis: condition: service_healthy
    mongo: condition: service_healthy
    # No inicia hasta que estén listos
```

## APIs Externas Usadas

1. **Wikipedia REST API**
   - Endpoint: `https://en.wikipedia.org/api/rest_v1/page/summary/{term}`
   - Uso: Enriquecer información sobre especies
   - Rate Limit: No especificado (uso razonable)

## Monitoreo

### Logs
```bash
docker logs -f pets-consumer-1    # Ver procesamiento
docker logs -f pets-django-api    # Ver requests
docker logs -f pets-redis         # Ver comandos Redis
```

### Métricas Redis
```bash
docker exec pets-redis redis-cli INFO
# connected_clients, total_commands_processed, etc.
```

### Estado de Cola
```bash
curl http://localhost:8000/api/redis/stats/
# {
#   "pending_tasks": 5,
#   "connected_clients": 4,
#   ...
# }
```
