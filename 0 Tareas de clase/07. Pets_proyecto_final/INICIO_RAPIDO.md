# 🚀 INICIO RÁPIDO - PETS + REDIS PROJECT

## ⚡ Puesta en Marcha en 5 Pasos

### 1️⃣ LEVANTAR LOS SERVICIOS

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
pets-django-api   | Watching for file changes with StatReloader
pets-consumer-1   | [Consumer-1] 👂 Waiting for tasks...
pets-consumer-2   | [Consumer-2] 👂 Waiting for tasks...
pets-consumer-3   | [Consumer-3] 👂 Waiting for tasks...
```

---

### 2️⃣ MIGRAR LA BASE DE DATOS (en otra terminal)

```bash
docker exec -it pets-django-api python manage.py migrate
```

**Resultado esperado:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  No migrations to apply.
```

---

### 3️⃣ CREAR SUPERUSUARIO

```bash
docker exec -it pets-django-api python manage.py createsuperuser
```

Usa estas credenciales:
- **Username**: `admin`
- **Email**: (presiona Enter)
- **Password**: `admin123`
- **Confirmar password**: `admin123`

**Nota:** Si te advierte que la contraseña es común, escribe `y` para confirmar.

---

### 4️⃣ OBTENER TOKEN JWT

#### Opción A - PowerShell (Windows):
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/token/" -Method Post -ContentType "application/json" -Body '{"username": "admin", "password": "admin123"}'
$token = $response.access
Write-Host "Token obtenido: $token"
```

#### Opción B - Bash (Linux/Mac):
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Guarda el `access` token** que recibes en la respuesta.

---

### 5️⃣ CREAR UNA MASCOTA (y ver la magia)

#### PowerShell:
```powershell
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$body = '{"name": "Max", "species": "Dog", "age": 5, "owner": "Juan Perez", "vaccinated": true}'

Invoke-RestMethod -Uri "http://localhost:8000/api/pets/" -Method Post -Headers $headers -Body $body
```

#### Bash:
```bash
curl -X POST http://localhost:8000/api/pets/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -d '{
    "name": "Max",
    "species": "Dog",
    "age": 5,
    "owner": "Juan Perez",
    "vaccinated": true
  }'
```

---

## 🎉 ¡Listo! ¿Qué Pasó?

1. ✅ La mascota se guardó en **MongoDB**
2. ✅ Se envió una tarea a la cola de **Redis**
3. ✅ Uno de los 3 **workers** la procesó automáticamente
4. ✅ Se generó un **archivo JSON enriquecido** con:
   - Información de Wikipedia sobre la especie
   - Datos curiosos (esperanza de vida, dieta, etc.)
   - Recomendaciones de salud personalizadas
   - Alertas (si la mascota no está vacunada)

---

## 👀 Ver los Resultados

### Ver logs de un worker procesando:
```bash
docker logs -f pets-consumer-1
```

**Deberías ver:**
```
[2026-02-03 13:49:41] [Consumer-1] [INFO] 📨 Received new task from queue
[2026-02-03 13:49:41] [Consumer-1] [INFO] Processing pet: Max (Dog) - ID: 67698abc
[2026-02-03 13:49:41] [Consumer-1] [INFO] Fetching Wikipedia data for Dog...
[2026-02-03 13:49:42] [Consumer-1] [INFO] Generating fun facts...
[2026-02-03 13:49:42] [Consumer-1] [INFO] Generating health tips...
[2026-02-03 13:49:43] [Consumer-1] [SUCCESS] ✅ Enriched data saved to: 67698abc_Max_20260203_134943.json
[2026-02-03 13:49:43] [Consumer-1] [SUCCESS] ⏱️  Task processed in 2.15s
[2026-02-03 13:49:43] [Consumer-1] [INFO] 📊 Generated 2 health tips
```

### Ver archivo JSON generado:
```bash
docker exec -it pets-consumer-1 ls -lh /app/processed_data
docker exec -it pets-consumer-1 cat /app/processed_data/NOMBRE_ARCHIVO.json
```

### Ver estadísticas de Redis:

#### PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/redis/stats/" -Method Get -Headers @{"Authorization" = "Bearer $token"}
```

#### Bash:
```bash
curl http://localhost:8000/api/redis/stats/ \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

**Respuesta esperada:**
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

## 🐱 Crear Más Mascotas (Ejemplos)

### Gato sin vacunar (verás alertas):
```powershell
$body = '{"name": "Mishi", "species": "Cat", "age": 2, "owner": "Ana Garcia", "vaccinated": false}'
Invoke-RestMethod -Uri "http://localhost:8000/api/pets/" -Method Post -Headers $headers -Body $body
```

### Pájaro vacunado:
```powershell
$body = '{"name": "Piolin", "species": "Bird", "age": 1, "owner": "Luis Rodriguez", "vaccinated": true}'
Invoke-RestMethod -Uri "http://localhost:8000/api/pets/" -Method Post -Headers $headers -Body $body
```

### Conejo:
```powershell
$body = '{"name": "Tambor", "species": "Rabbit", "age": 3, "owner": "Sofia Martinez", "vaccinated": true}'
Invoke-RestMethod -Uri "http://localhost:8000/api/pets/" -Method Post -Headers $headers -Body $body
```

### Pez:
```powershell
$body = '{"name": "Nemo", "species": "Fish", "age": 1, "owner": "Carlos Lopez", "vaccinated": false}'
Invoke-RestMethod -Uri "http://localhost:8000/api/pets/" -Method Post -Headers $headers -Body $body
```

**Cada especie genera datos curiosos diferentes y recomendaciones personalizadas.**

---

## 🔥 Ver el Procesamiento en Tiempo Real

Abre **DOS terminales**:

**Terminal 1 - Ver logs:**
```bash
docker logs -f pets-consumer-1
```

**Terminal 2 - Crear mascotas:**
```powershell
# Crea varias mascotas y observa Terminal 1
$body = '{"name": "Rocky", "species": "Dog", "age": 7, "owner": "Pedro", "vaccinated": true}'
Invoke-RestMethod -Uri "http://localhost:8000/api/pets/" -Method Post -Headers $headers -Body $body
```

Verás el procesamiento **en tiempo real** en Terminal 1.

---

## 📊 Verificar que TODO Funciona

### 1. Ver contenedores activos:
```bash
docker ps
```
**Debes ver 6 contenedores:** django-api, redis, mongodb, consumer-1, consumer-2, consumer-3

### 2. Verificar Redis:
```bash
docker exec -it pets-redis redis-cli ping
```
**Debe responder:** `PONG`

### 3. Ver tareas pendientes:
```bash
docker exec -it pets-redis redis-cli LLEN pets:tasks
```
**Debe responder:** `(integer) 0` (si no hay tareas pendientes)

### 4. Ver archivos generados:
```bash
docker exec -it pets-consumer-1 ls -lh /app/processed_data
```

### 5. Listar todas las mascotas creadas:

#### PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/pets/" -Method Get -Headers @{"Authorization" = "Bearer $token"}
```

#### Bash:
```bash
curl http://localhost:8000/api/pets/ \
  -H "Authorization: Bearer TU_TOKEN"
```

---

## 🛑 Detener Todo

```bash
docker-compose down
```

Para limpiar TODO (incluyendo datos):
```bash
docker-compose down -v
```

---

## ❓ Problemas Comunes

### "Port 8000 already in use"
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### "Redis connection refused"
```bash
docker-compose restart redis
docker logs pets-redis
```

### Workers no procesan
```bash
docker-compose restart consumer-1 consumer-2 consumer-3
docker logs --tail 50 pets-consumer-1
```

### Token expirado (después de 1 hora)
```powershell
# Obtener nuevo token
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/token/" -Method Post -ContentType "application/json" -Body '{"username": "admin", "password": "admin123"}'
$token = $response.access
```

---


## 📚 Más Información

- **README.md** - Documentación completa
- **ARQUITECTURA.md** - Diagramas y explicación técnica
- **COMANDOS.txt** - Todos los comandos disponibles
- **RESUMEN_EJECUTIVO.md** - Overview del proyecto

---

## 🏆 Características del Sistema

✅ **Procesamiento distribuido** - 3 workers en paralelo  
✅ **Detección inteligente** - Alertas para mascotas sin vacunar  
✅ **Enriquecimiento de datos** - Wikipedia + datos curiosos  
✅ **Recomendaciones personalizadas** - Por especie, edad y vacunación  
✅ **Escalable** - Fácil agregar más workers  
✅ **Monitoreable** - Logs detallados y estadísticas  

---
