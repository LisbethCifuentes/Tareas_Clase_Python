# 🐾 Pet App - Django + MongoDB + Redis + Workers

Sistema distribuido para gestionar mascotas con API REST, colas de Redis y procesamiento asíncrono con múltiples workers.

## 🎯 Características Principales

✅ **API CRUD** completa de mascotas con Django REST Framework  
✅ **Autenticación JWT** para endpoints protegidos  
✅ **MongoDB** como base de datos NoSQL  
✅ **Redis** como sistema de colas (message broker)  
✅ **3 Consumidores** (workers) para procesamiento distribuido  
✅ **Docker Compose** orquestando todos los servicios  
✅ **Procesamiento asíncrono**: enriquecimiento inteligente de datos de mascotas  

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │ POST /api/pets/
       ▼
┌─────────────────┐
│  Django API     │ ──► Guarda en MongoDB
│  (Productor)    │ ──► Envía tarea a Redis Queue
└────────┬────────┘
         │
         ▼
   ┌──────────┐
   │  Redis   │ (Cola: pets:tasks)
   └─────┬────┘
         │
    ┌────┴────┬─────────┬─────────┐
    ▼         ▼         ▼         
┌──────┐  ┌──────┐  ┌──────┐
│Worker│  │Worker│  │Worker│  Consumen tareas
│  1   │  │  2   │  │  3   │  y procesan datos
└──┬───┘  └──┬───┘  └──┬───┘
   │         │         │
   └─────────┴─────────┘
           │
           ▼
    📁 processed_data/
    (Archivos JSON enriquecidos)
```

---

## 🛠️ Tecnologías

| Componente | Tecnología | Versión |
|-----------|------------|---------|
| **Backend** | Django + DRF | 4.2.7 |
| **Base de Datos** | MongoDB | 7.0 |
| **Message Queue** | Redis | 7 Alpine |
| **ORM** | MongoEngine | 0.27.0 |
| **Autenticación** | JWT | Simple JWT 5.3.0 |
| **Contenedores** | Docker Compose | - |

---

## 📋 Requisitos Previos

- **Docker Desktop** instalado y ejecutándose
- **Git** (opcional)
- Puertos disponibles: `8000` (Django), `6379` (Redis), `27017` (MongoDB)

---

## 🚀 Instalación y Ejecución

### 1. Levantar todos los servicios

```bash
docker-compose up --build
```

Esto iniciará automáticamente:
- ✅ Redis (puerto 6379)
- ✅ MongoDB (puerto 27017)  
- ✅ Django API (puerto 8000)
- ✅ 3 Workers/Consumidores

**Espera a ver estos mensajes:**
```
pets-redis        | Ready to accept connections
pets-mongodb      | Waiting for connections
pets-django-api   | Starting development server at http://0.0.0.0:8000/
pets-consumer-1   | [Consumer-1] 👂 Waiting for tasks...
pets-consumer-2   | [Consumer-2] 👂 Waiting for tasks...
pets-consumer-3   | [Consumer-3] 👂 Waiting for tasks...
```

---

### 2. Migrar la base de datos (nueva terminal)

```bash
docker exec -it pets-django-api python manage.py migrate
```

---

### 3. Crear superusuario

```bash
docker exec -it pets-django-api python manage.py createsuperuser
```

Credenciales sugeridas:
- **Username**: `admin`
- **Password**: `admin123`

---

## 🌐 Endpoints Disponibles

### 📄 Vista Pública (Sin autenticación)

| URL | Método | Descripción |
|-----|--------|-------------|
| `http://localhost:8000/` | GET | Vista HTML de todas las mascotas |

---

### 🔑 Autenticación JWT

| URL | Método | Body | Descripción |
|-----|--------|------|-------------|
| `/api/token/` | POST | `{"username": "admin", "password": "admin123"}` | Obtener tokens |
| `/api/token/refresh/` | POST | `{"refresh": "REFRESH_TOKEN"}` | Renovar access token |

---

### 🐾 API de Mascotas (Requiere JWT)

| URL | Método | Descripción |
|-----|--------|-------------|
| `/api/pets/` | GET | Listar mascotas |
| `/api/pets/` | POST | ⭐ Crear mascota + enviar a cola Redis |
| `/api/pets/<id>/` | GET | Obtener mascota |
| `/api/pets/<id>/` | PUT | Actualizar mascota |
| `/api/pets/<id>/` | DELETE | Eliminar mascota |
| `/api/redis/stats/` | GET | Ver estadísticas de Redis |

---

## 📝 Flujo Completo de Uso

### Paso 1: Obtener Token JWT

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Respuesta:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Guarda el `access` token.

---

### Paso 2: Crear una Mascota (¡Aquí pasa la magia!)

```bash
curl -X POST http://localhost:8000/api/pets/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_ACCESS_TOKEN" \
  -d '{
    "name": "Luna",
    "species": "Cat",
    "age": 3,
    "owner": "María García",
    "vaccinated": true
  }'
```

**Respuesta:**
```json
{
  "message": "Pet created successfully",
  "pet": {
    "id": "67698abc123def456789",
    "name": "Luna",
    "species": "Cat",
    "age": 3,
    "owner": "María García",
    "vaccinated": true
  },
  "task_queued": true,
  "info": "Task sent to workers for processing. Enriched data will be generated."
}
```

✨ **¡Automáticamente!**:
1. La mascota se guarda en MongoDB
2. Se envía una tarea a Redis
3. Uno de los 3 workers la procesa
4. Se genera un archivo JSON enriquecido

---

### Paso 3: Ver Estadísticas de Redis

```bash
curl http://localhost:8000/api/redis/stats/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN"
```

**Respuesta:**
```json
{
  "queue_name": "pets:tasks",
  "pending_tasks": 0,
  "redis_host": "redis",
  "redis_port": 6379,
  "connected_clients": 4,
  "total_commands_processed": 3365
}
```

---

## 🔄 ¿Qué Hacen los Workers?

Cuando creas una mascota, los workers procesan la tarea y:

1. **Buscan información en Wikipedia** sobre la especie
2. **Generan datos curiosos** (esperanza de vida, dieta, curiosidades)
3. **Crean recomendaciones de salud personalizadas** basadas en:
   - Edad de la mascota
   - Estado de vacunación
   - Especie
4. **Detectan alertas** (ej: mascotas sin vacunar)
5. **Guardan todo en un archivo JSON** enriquecido

### Ejemplo de Archivo Generado

Ubicación: `/processed_data/6981fcf3dd7c1b67498baf89_Mishi_20260203_134940.json`

```json
{
  "metadata": {
    "processed_by": "Consumer-3",
    "processed_at": "2026-02-03T13:49:40.520041",
    "processing_duration_seconds": 2
  },
  "original_data": {
    "pet_id": "6981fcf3dd7c1b67498baf89",
    "name": "Mishi",
    "species": "Cat",
    "age": 2,
    "owner": "Ana Garcia",
    "vaccinated": false
  },
  "enriched_info": {
    "wikipedia": {
      "wikipedia_extract": "The cat is a domestic species...",
      "wikipedia_url": "https://en.wikipedia.org/wiki/Cat",
      "thumbnail": "https://upload.wikimedia.org/..."
    },
    "species_facts": {
      "lifespan": "12-18 years",
      "group": "Mammal",
      "diet": "Carnivore",
      "fun_fact": "Cats spend 70% of their lives sleeping!"
    },
    "health_tips": [
      "⚠️ URGENT: This Cat needs vaccination! Please consult a veterinarian.",
      "🐱 Adult Cat in prime age. Maintain regular check-ups.",
      "🐱 Cats need scratching posts and regular grooming."
    ]
  },
  "statistics": {
    "total_tips": 3,
    "vaccination_status": "Needs vaccination",
    "age_category": "Adult"
  }
}
```

---

## 🐋 Comandos Docker Útiles

### Ver logs de todos los servicios
```bash
docker-compose logs -f
```

### Ver logs de un servicio específico
```bash
docker logs -f pets-consumer-1
docker logs -f pets-consumer-2
docker logs -f pets-consumer-3
docker logs -f pets-django-api
docker logs -f pets-redis
```

### Detener servicios
```bash
docker-compose down
```

### Limpiar todo (incluye volúmenes)
```bash
docker-compose down -v
```

### Reconstruir imágenes
```bash
docker-compose up --build
```

### Ver contenedores activos
```bash
docker ps
```

---

## 🔍 Verificar que Todo Funciona

### 1. ✅ Verificar Redis está corriendo
```bash
docker exec -it pets-redis redis-cli ping
# Debe responder: PONG
```

### 2. ✅ Ver cola de Redis
```bash
docker exec -it pets-redis redis-cli LLEN pets:tasks
# Debe responder: (integer) 0 si no hay tareas pendientes
```

### 3. ✅ Verificar workers procesando
```bash
docker logs pets-consumer-1 --tail 50
```

Deberías ver logs como:
```
[2026-02-03 13:49:40] [Consumer-1] [INFO] 👂 Waiting for tasks...
[2026-02-03 13:49:41] [Consumer-1] [INFO] 📨 Received new task from queue
[2026-02-03 13:49:41] [Consumer-1] [INFO] Processing pet: Luna (Cat) - ID: 67698abc
[2026-02-03 13:49:43] [Consumer-1] [SUCCESS] ✅ Enriched data saved to: 67698abc_Luna_20260203_134943.json
[2026-02-03 13:49:43] [Consumer-1] [SUCCESS] ⏱️  Task processed in 2.15s
```

### 4. ✅ Ver archivos generados
```bash
docker exec -it pets-consumer-1 ls -lh /app/processed_data
```

### 5. ✅ Ver contenido de un archivo
```bash
docker exec -it pets-consumer-1 cat /app/processed_data/NOMBRE_ARCHIVO.json
```

---

## 🎨 Características Avanzadas

### Filtros en la API

```bash
# Filtrar por especie
curl "http://localhost:8000/api/pets/?species=Dog" \
  -H "Authorization: Bearer TOKEN"

# Filtrar por vacunación
curl "http://localhost:8000/api/pets/?vaccinated=true" \
  -H "Authorization: Bearer TOKEN"

# Filtros combinados
curl "http://localhost:8000/api/pets/?species=Cat&vaccinated=false" \
  -H "Authorization: Bearer TOKEN"
```

---

## 📊 Escalabilidad

### Agregar más workers

Edita `docker-compose.yml` y añade:

```yaml
consumer-4:
  build:
    context: .
    dockerfile: Dockerfile.consumer
  container_name: pets-consumer-4
  restart: unless-stopped
  environment:
    - REDIS_HOST=redis
    - REDIS_PORT=6379
    - CONSUMER_ID=4
  depends_on:
    redis:
      condition: service_healthy
  networks:
    - pets-network
  volumes:
    - processed_data:/app/processed_data
```

Luego ejecuta:
```bash
docker-compose up -d consumer-4
```

---

## 🚨 Solución de Problemas

### Problema: "Connection refused" en Redis

**Solución**: Asegúrate de que Redis esté corriendo
```bash
docker-compose ps
docker-compose restart redis
```

### Problema: Workers no procesan tareas

**Verificar**:
1. ¿Hay tareas en la cola?
   ```bash
   docker exec -it pets-redis redis-cli LLEN pets:tasks
   ```

2. ¿Están los workers corriendo?
   ```bash
   docker ps | grep consumer
   ```

3. Ver logs de workers:
   ```bash
   docker logs pets-consumer-1 --tail 100
   ```

### Problema: Puerto 8000 ocupado

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

---

## 📁 Estructura del Proyecto

```
pets-redis-project/
├── docker-compose.yml          # Orquestación de servicios
├── Dockerfile                  # Imagen de Django API
├── Dockerfile.consumer         # Imagen de Workers
├── requirements.txt            # Dependencias Python
├── manage.py                   # Django management
├── consumer.py                 # Script del worker
│
├── pets_project/               # Proyecto Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── pets/                       # App de mascotas
│   ├── models.py               # Modelo Pet (MongoEngine)
│   ├── views.py                # API + Redis producer
│   ├── urls.py
│   └── admin.py
│
└── templates/                  # Templates HTML
    └── pets/
        └── pets_list.html
```

---

## 🎓 Conceptos Clave Implementados

### 1. **Productor-Consumidor**
- Django API = Productor (envía tareas)
- Workers = Consumidores (procesan tareas)

### 2. **FIFO Queue (First In, First Out)**
```python
# Productor añade al final
redis_client.rpush('pets:tasks', task)

# Consumidor saca del principio
redis_client.blpop('pets:tasks', timeout=1)
```

### 3. **Procesamiento Asíncrono**
- La API responde inmediatamente
- El procesamiento ocurre en background
- Escalable horizontalmente (más workers = más throughput)

### 4. **Microservicios**
- Cada servicio en su propio contenedor
- Comunicación vía Redis
- Desacoplamiento total

---

## 📈 Mejoras Futuras

- [ ] Agregar Redis Pub/Sub para notificaciones en tiempo real
- [ ] Implementar reintentos con exponential backoff
- [ ] Agregar dead-letter queue para tareas fallidas
- [ ] Métricas con Prometheus/Grafana
- [ ] Sistema de prioridades en las tareas
- [ ] WebSocket para actualizaciones en vivo
- [ ] Panel de administración para monitorear workers

---

## 👨‍💻 Autor

Proyecto desarrollado como ejemplo de arquitectura distribuida con colas de mensajes.

---

## 📄 Licencia

MIT License - Uso libre

---

## 🔗 Referencias

- [Redis Documentation](https://redis.io/docs/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Docker Compose](https://docs.docker.com/compose/)
- [MongoEngine](http://mongoengine.org/)

---

## ⭐ Resumen de Comandos Esenciales

```bash
# Iniciar todo
docker-compose up --build

# Migrar DB
docker exec -it pets-django-api python manage.py migrate

# Crear usuario
docker exec -it pets-django-api python manage.py createsuperuser

# Ver logs
docker logs -f pets-consumer-1

# Ver archivos generados
docker exec -it pets-consumer-1 ls -lh /app/processed_data

# Detener todo
docker-compose down

# Limpiar todo
docker-compose down -v
```

---

