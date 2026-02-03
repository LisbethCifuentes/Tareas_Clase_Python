# 🏗️ ARQUITECTURA DEL SISTEMA

## Componentes Principales

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENTE / USUARIO (Browser)                   │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │          Interfaz Web (localhost:8000/)                 │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │  - Login con JWT                                  │  │    │
│  │  │  - Formulario de creación de mascotas           │  │    │
│  │  │  - Tarjetas interactivas                         │  │    │
│  │  │  - Modal con información enriquecida 🌟          │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────┘    │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ HTTP Requests
                        │ GET /             (Vista HTML)
                        │ POST /api/token/   (Login JWT)
                        │ POST /api/pets/    (Crear mascota)
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│              DJANGO REST API (Puerto 8000)                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  views.py                                                │   │
│  │  - pets_page()         ────► Renderiza vista HTML       │   │
│  │  - pets_api_list()     ────► Crea mascota en MongoDB    │   │
│  │                        └───► Envía tarea a Redis (RPUSH)│   │
│  │  - redis_stats()       ────► Consulta estado de cola    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  templates/pets/pets_list.html                                   │
│  ├─ Sistema de login (JavaScript + JWT)                         │
│  ├─ Formulario de creación                                      │
│  ├─ Grid de tarjetas con hover effects                          │
│  └─ Modal con información enriquecida                           │
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

## Flujo de Datos Completo

### 1. Usuario Accede a la Interfaz Web

```
Usuario ──GET http://localhost:8000/──► Django
                                         │
                                         └──► Renderiza pets_list.html
                                              ├─ Muestra login
                                              └─ Muestra tarjetas de mascotas
```

### 2. Login del Usuario

```
Usuario ──completa formulario──► JavaScript (Frontend)
                                      │
                                      │ POST /api/token/
                                      ▼
                                 Django API
                                      │
                                      └──► Genera JWT token
                                           │
                                           ▼
                                      Almacena en variable (authToken)
                                           │
                                           └──► Muestra formulario de creación
```

### 3. Creación de Mascota desde la Web

```
Usuario ──completa formulario──► JavaScript (Frontend)
                                      │
                                      │ POST /api/pets/
                                      │ Authorization: Bearer {token}
                                      ▼
                                 Django API
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
                                           │
                                           └──► Responde: {"task_queued": true}
                                                │
                                                ▼
                                           JavaScript recarga página
                                                │
                                                └──► Muestra nueva mascota en tarjeta
```

### 4. Interacción con el Modal

```
Usuario ──click en tarjeta──► JavaScript genera modal
                                      │
                                      ├──► Muestra información básica
                                      │    (de la tarjeta)
                                      │
                                      └──► Genera información enriquecida
                                           ├─ Datos curiosos (esperanza de vida)
                                           ├─ Fun facts por especie
                                           ├─ Recomendaciones de salud
                                           └─ Alertas (si no está vacunado)
```

### 5. Procesamiento por Workers

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
             /app/processed_data/123_Max_20250203_143022.json
```

## Interfaz Web - Desglose Técnico

### Frontend Stack
```
HTML5 + CSS3 + Vanilla JavaScript
├─ No frameworks (puro JavaScript)
├─ Fetch API para requests AJAX
├─ JWT almacenado en variable (authToken)
└─ Modal dinámico con datos enriquecidos
```

### Componentes de la Interfaz

#### 1. Sistema de Login
```javascript
// Flujo de autenticación
fetch('/api/token/', {
  method: 'POST',
  body: JSON.stringify({username, password})
})
.then(response => response.json())
.then(data => {
  authToken = data.access;  // Almacena JWT
  showCreateForm();         // Muestra formulario
});
```

#### 2. Creación de Mascotas
```javascript
// Envío con JWT
fetch('/api/pets/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(petData)
})
.then(() => window.location.reload());
```

#### 3. Modal Interactivo
```javascript
// Generación dinámica de contenido
function showPetDetails(petId, name, species, age, ...) {
  const modal = document.getElementById('petModal');
  modal.style.display = 'block';
  
  // Genera datos enriquecidos localmente
  generateEnrichedInfo(species, age, vaccinated);
}
```

### Datos Mostrados en el Modal

```
┌─────────────────────────────────────────┐
│         MODAL DE INFORMACIÓN            │
├─────────────────────────────────────────┤
│ 📋 Información Básica                   │
│    - ID, Nombre, Especie, Edad          │
│    - Dueño, Estado de vacunación        │
├─────────────────────────────────────────┤
│ 🎓 Datos Curiosos de la Especie         │
│    - Esperanza de vida: 10-13 años      │
│    - Grupo: Mamífero                    │
│    - Dieta: Omnívoro                    │
│    - 💡 Fun Fact: "Los perros..."       │
├─────────────────────────────────────────┤
│ 🏥 Recomendaciones de Salud             │
│    - ⚠️ URGENTE (si no vacunado)        │
│    - Tips por edad                      │
│    - Tips por especie                   │
├─────────────────────────────────────────┤
│ 📊 Estadísticas                         │
│    - Total recomendaciones: 3           │
│    - Estado: Necesita vacunación        │
│    - Categoría: Adulto                  │
└─────────────────────────────────────────┘
```

## Docker Compose - Orquestación

```yaml
services:
  redis         ──► Queue/Message Broker
  mongo         ──► Persistent Storage
  django-api    ──► Producer + Web Server + API
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

### 4. MVC + SPA Híbrido
- **Model**: MongoDB + MongoEngine
- **View**: Django Templates + JavaScript
- **Controller**: Django Views + JavaScript handlers
- **SPA Elements**: Modal dinámico, AJAX requests

## Escalabilidad

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

### Vertical (Recursos)
```bash
# Aumentar recursos a un servicio
docker update --cpus="2.0" --memory="2g" pets-django-api
```

## Tecnologías por Capa

| Capa | Tecnología | Puerto | Propósito |
|------|-----------|--------|-----------|
| Frontend | HTML5 + CSS3 + JavaScript | - | Interfaz interactiva |
| API | Django 4.2.7 + DRF | 8000 | REST API + Web Server |
| Queue | Redis 7 Alpine | 6379 | Message broker |
| Database | MongoDB 7.0 | 27017 | Persistencia NoSQL |
| Workers | Python 3.11 | - | Procesamiento asíncrono |
| Orchestration | Docker Compose | - | Orquestación de servicios |

## Comunicación entre Servicios

```
Usuario (Browser) ←─────────────────→ Django API (HTTP/AJAX)
                                         │
                                         ├─────────────→ MongoDB (mongoengine)
                                         │
                                         └─────────────→ Redis (redis-py)
                                                          │
                                                          │
                                        Consumers ←───────┘
                                             │
                                             └─────────→ External APIs (requests)
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
curl http://localhost:8000/api/redis/stats/ \
  -H "Authorization: Bearer {token}"
# {
#   "pending_tasks": 5,
#   "connected_clients": 4,
#   ...
# }
```

### Interfaz Web
- Acceso directo: `http://localhost:8000/`
- Vista en tiempo real de mascotas
- Modal interactivo para inspección detallada

## Seguridad

### Autenticación JWT
```
1. Usuario envía credenciales
2. Django genera JWT token (access + refresh)
3. Frontend almacena token en variable
4. Todas las requests llevan: Authorization: Bearer {token}
5. Django valida token en cada request
```

### Tokens
- **Access Token**: Válido por 1 hora
- **Refresh Token**: Válido por 1 día
- Almacenamiento: Variable JavaScript (no localStorage por seguridad)

## Experiencia de Usuario

### Flujo Completo
```
1. Usuario accede → http://localhost:8000/
2. Ve login + lista de mascotas existentes
3. Inicia sesión (admin/admin123)
4. Aparece formulario de creación
5. Crea mascota → API responde inmediato
6. Página se recarga → Nueva mascota visible
7. Click en tarjeta → Modal con info enriquecida
   ├─ Datos curiosos
   ├─ Fun facts
   ├─ Recomendaciones
   └─ Alertas (si aplica)
8. Worker procesa en background (logs visibles)
9. JSON enriquecido guardado en volumen
```

### Características UX
- ✅ Respuesta inmediata (no bloquea)
- ✅ Feedback visual (mensajes de éxito/error)
- ✅ Modal elegante con animaciones
- ✅ Hover effects en tarjetas
- ✅ Atajos de teclado (ESC para cerrar)
- ✅ Responsive (adapta a móviles)

## Ventajas de la Arquitectura

1. **Desacoplamiento**: Frontend, API y workers independientes
2. **Escalabilidad**: Fácil agregar más workers
3. **Resiliencia**: Si un worker falla, otros continúan
4. **Performance**: API responde inmediato, procesamiento asíncrono
5. **UX Superior**: Interfaz moderna sin recargas innecesarias
6. **Monitoreable**: Logs separados por servicio
7. **Mantenible**: Cada componente es independiente

## Mejoras Futuras

- [ ] WebSocket para actualización en tiempo real sin reload
- [ ] Redis Pub/Sub para notificaciones push
- [ ] Sistema de caché con Redis
- [ ] Rate limiting por usuario
- [ ] Paginación en la interfaz web
- [ ] Búsqueda y filtros dinámicos
- [ ] Dashboard de monitoreo con métricas
- [ ] Autenticación OAuth2
