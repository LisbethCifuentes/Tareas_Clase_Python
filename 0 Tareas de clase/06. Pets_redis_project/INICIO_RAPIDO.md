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

### 4️⃣ ABRIR LA INTERFAZ WEB

```
http://localhost:8000/
```

Verás una interfaz elegante con tarjetas de mascotas y un formulario de login.

---

### 5️⃣ USAR LA APLICACIÓN

#### A. Iniciar Sesión
1. En la página principal, verás el formulario de login
2. Ingresa:
   - **Usuario**: `admin`
   - **Contraseña**: `admin123`
3. Click en **"Iniciar Sesión"**

#### B. Crear una Mascota
Después del login, aparecerá el formulario de creación:
1. **Nombre**: `Max`
2. **Especie**: `Dog` (Perro)
3. **Edad**: `5`
4. **Dueño**: `Juan Pérez`
5. **Vacunación**: `Vacunado`
6. Click en **"Crear Mascota"**

#### C. Ver Información Enriquecida 🌟
1. La página se recargará mostrando la nueva mascota en una tarjeta
2. **Haz click en la tarjeta de Max**
3. Se abrirá un modal con información enriquecida:
   - 📋 Información básica
   - 🎓 Datos curiosos de la especie (esperanza de vida, dieta, fun fact)
   - 🏥 Recomendaciones de salud personalizadas
   - 📊 Estadísticas

#### D. Observar el Procesamiento en Tiempo Real
En otra terminal, ejecuta:
```bash
docker logs -f pets-consumer-1
```

Verás cómo el worker procesó la tarea:
```
[Consumer-1] [INFO] 📨 Received new task from queue
[Consumer-1] [INFO] Processing pet: Max (Dog) - ID: ...
[Consumer-1] [INFO] Fetching Wikipedia data for Dog...
[Consumer-1] [SUCCESS] ✅ Enriched data saved to: ...Max_....json
```

---

## 🎉 ¡Listo! ¿Qué Acabas de Lograr?

1. ✅ Sistema distribuido con 6 contenedores corriendo
2. ✅ Interfaz web interactiva con login JWT
3. ✅ Creaste una mascota desde el navegador
4. ✅ Viste el procesamiento asíncrono en los logs
5. ✅ Exploraste información enriquecida en el modal
6. ✅ Worker generó un archivo JSON con datos curiosos y recomendaciones

---

## 🎮 Experimenta Más

### Crear Diferentes Especies

Prueba creando mascotas de diferentes especies para ver información única:

**Gato sin vacunar** (verás alerta URGENTE en el modal):
- Nombre: `Mishi`
- Especie: `Cat`
- Edad: `2`
- Dueño: `Ana García`
- Vacunación: `Sin Vacunar` ❌

**Pájaro**:
- Nombre: `Piolín`
- Especie: `Bird`
- Edad: `1`
- Dueño: `Luis Rodríguez`
- Vacunación: `Vacunado` ✅

**Conejo**:
- Nombre: `Tambor`
- Especie: `Rabbit`
- Edad: `3`
- Dueño: `Sofía Martínez`
- Vacunación: `Vacunado` ✅

**Pez**:
- Nombre: `Nemo`
- Especie: `Fish`
- Edad: `1`
- Dueño: `Carlos López`
- Vacunación: `Sin Vacunar`

Cada especie mostrará:
- 💡 Fun fact diferente
- 🏥 Recomendaciones específicas
- 📊 Datos de esperanza de vida única

---

## 👀 Ver los Resultados

### 1. Interfaz Web
- Abre `http://localhost:8000/`
- Verás todas las mascotas en tarjetas elegantes
- **Click en cualquier tarjeta** para ver el modal con información enriquecida

### 2. Archivos JSON Generados
```bash
docker exec -it pets-consumer-1 ls -lh /app/processed_data
```

Verás archivos como:
```
69814cb73dc3439156b7d55_Max_20260203_133457.json
6981fa92791827497cb2290f_Mishi_20260203_133932.json
```

### 3. Ver Contenido de un Archivo
```bash
docker exec -it pets-consumer-1 cat /app/processed_data/NOMBRE_ARCHIVO.json
```

### 4. Estadísticas de Redis
Si estás logueado en la interfaz web, puedes obtener el token de la consola del navegador (F12) y ejecutar:

#### PowerShell:
```powershell
$token = "TU_TOKEN_ACCESS"
Invoke-RestMethod -Uri "http://localhost:8000/api/redis/stats/" -Method Get -Headers @{"Authorization" = "Bearer $token"}
```

**Respuesta esperada:**
```
queue_name               : pets:tasks
pending_tasks            : 0
redis_host               : redis
redis_port               : 6379
connected_clients        : 4
total_commands_processed : 3500+
```

---

## 📊 Verificar que TODO Funciona

### 1. Ver Contenedores Activos
```bash
docker ps
```
**Debes ver 6 contenedores:** 
- pets-django-api
- pets-redis (Healthy)
- pets-mongodb (Healthy)
- pets-consumer-1
- pets-consumer-2
- pets-consumer-3

### 2. Verificar Redis
```bash
docker exec -it pets-redis redis-cli ping
```
**Debe responder:** `PONG`

### 3. Ver Tareas en Cola
```bash
docker exec -it pets-redis redis-cli LLEN pets:tasks
```
**Debe responder:** `(integer) 0` (si no hay tareas pendientes)

### 4. Ver Logs de un Worker
```bash
docker logs pets-consumer-1 --tail 20
```

Deberías ver mensajes como:
```
[Consumer-1] [INFO] 👂 Waiting for tasks...
[Consumer-1] [INFO] 📨 Received new task from queue
[Consumer-1] [SUCCESS] ✅ Enriched data saved to: ...
```

### 5. Probar la Interfaz Web
1. ✅ Login funciona
2. ✅ Puedes crear mascotas
3. ✅ Las tarjetas se muestran correctamente
4. ✅ El modal se abre al hacer click
5. ✅ La información enriquecida aparece

---

## 🔥 Ver Procesamiento en Tiempo Real

### Setup de Dos Terminales

**Terminal 1 - Logs del Worker:**
```bash
docker logs -f pets-consumer-1
```

**Terminal 2 - Crear Mascota desde la Web:**
1. Ve a `http://localhost:8000/`
2. Inicia sesión
3. Crea una mascota

**En Terminal 1 verás INMEDIATAMENTE:**
```
[2026-02-03 20:15:42] [Consumer-1] [INFO] 📨 Received new task from queue
[2026-02-03 20:15:42] [Consumer-1] [INFO] Processing pet: Rocky (Dog) - ID: 6981...
[2026-02-03 20:15:42] [Consumer-1] [INFO] Fetching Wikipedia data for Dog...
[2026-02-03 20:15:43] [Consumer-1] [INFO] Generating fun facts...
[2026-02-03 20:15:43] [Consumer-1] [INFO] Generating health tips...
[2026-02-03 20:15:44] [Consumer-1] [SUCCESS] ✅ Enriched data saved to: 6981..._Rocky_20260203_201544.json
[2026-02-03 20:15:44] [Consumer-1] [SUCCESS] ⏱️  Task processed in 2.1s
[2026-02-03 20:15:44] [Consumer-1] [INFO] 📊 Generated 2 health tips
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

### Modal no se muestra al hacer click
1. **Limpia caché del navegador**: Ctrl + Shift + R
2. **Verifica consola**: F12 → Console (busca errores)
3. **Asegúrate de usar**: `pets_list_FINAL.html`

### La página no carga / Error 404
```bash
# Verifica que Django esté corriendo
docker logs pets-django-api --tail 30

# Reinicia Django
docker-compose restart django-api
```

---

## 🎯 Características del Modal

Cuando hagas click en una tarjeta, verás:

### 📋 Información Básica
- ID único de la mascota
- Nombre, especie, edad, dueño
- Estado de vacunación

### 🎓 Datos Curiosos de la Especie
- **Esperanza de vida**: Años promedio que vive
- **Grupo**: Mamífero, Aves, Peces
- **Dieta**: Carnívoro, Omnívoro, Herbívoro
- **💡 Fun Fact**: Dato curioso único por especie

Ejemplos de Fun Facts:
- 🐕 Dog: "¡Los perros han sido compañeros de los humanos por más de 15,000 años!"
- 🐱 Cat: "¡Los gatos pasan el 70% de sus vidas durmiendo!"
- 🐦 Bird: "¡Algunos pájaros pueden ver luz ultravioleta!"
- 🐰 Rabbit: "¡Los conejos pueden ver casi 360 grados a su alrededor!"
- 🐠 Fish: "¡Los peces existían en la Tierra antes que los dinosaurios!"

### 🏥 Recomendaciones de Salud Personalizadas

**Si no está vacunado:**
```
⚠️ URGENTE: ¡Esta Cat necesita vacunación! Consulte a un veterinario.
```
(Aparece con fondo rojo)

**Por edad:**
- 🍼 Cachorro/Cría (< 1 año): "Necesita chequeos frecuentes"
- ✅ Adulto (1-10 años): "En edad óptima. Mantener chequeos regulares"
- 👴 Senior (> 10 años): "Considere visitas más frecuentes y dieta especial"

**Por especie:**
- 🐕 Perros: "Necesitan ejercicio diario e interacción social"
- 🐱 Gatos: "Necesitan rascadores y aseo regular"
- 🐦 Pájaros: "Necesitan jaulas grandes y estimulación mental"
- 🐰 Conejos: "Necesitan espacio para saltar"
- 🐠 Peces: "Necesitan agua limpia y control de temperatura"

### 📊 Estadísticas
- Total de recomendaciones generadas
- Estado actual de vacunación
- Categoría de edad

---

## 🎨 Atajos del Modal

- **ESC**: Cerrar modal
- **Click fuera**: Cerrar modal
- **X (esquina superior derecha)**: Cerrar modal

---

## 🚀 Próximos Pasos

1. ✅ Crea mascotas de todas las especies disponibles
2. ✅ Observa las diferentes alertas y recomendaciones
3. ✅ Explora los archivos JSON generados
4. ✅ Ve los logs de los 3 workers procesando en paralelo
5. ✅ Experimenta cerrando sesión y volviendo a entrar

---

## 📚 Más Información

- **README.md** - Documentación completa del proyecto
- **ARQUITECTURA.md** - Diagramas y explicación técnica detallada
- **COMANDOS.txt** - Todos los comandos útiles
- **RESUMEN_EJECUTIVO.md** - Overview ejecutivo del proyecto

---

## 🏆 Lo que Acabas de Implementar

✅ **Sistema Distribuido Completo**
- 3 workers procesando tareas en paralelo
- Redis como message broker
- MongoDB como base de datos NoSQL

✅ **Interfaz Web Moderna**
- Login con JWT
- Creación de mascotas desde el navegador
- Tarjetas elegantes con efecto hover
- Modal interactivo con información enriquecida

✅ **Procesamiento Inteligente**
- Enriquecimiento con datos de Wikipedia
- Generación de datos curiosos por especie
- Alertas personalizadas según vacunación
- Recomendaciones por edad y especie
- Archivos JSON estructurados

✅ **Arquitectura Profesional**
- Microservicios con Docker
- Procesamiento asíncrono
- Escalabilidad horizontal
- Logs detallados y monitoreo

---

## ⭐ Comandos Esenciales - Resumen

```bash
# 1. Iniciar todo
docker-compose up --build

# 2. Migrar DB
docker exec -it pets-django-api python manage.py migrate

# 3. Crear usuario
docker exec -it pets-django-api python manage.py createsuperuser

# 4. Abrir navegador
# http://localhost:8000/

# 5. Ver logs de worker
docker logs -f pets-consumer-1

# 6. Ver archivos generados
docker exec -it pets-consumer-1 ls -lh /app/processed_data

# 7. Detener todo
docker-compose down

# 8. Limpiar todo
docker-compose down -v
```

---

## 🎯 Tips Finales

### Para la Mejor Experiencia:

1. **Usa Chrome o Edge** para mejor compatibilidad
2. **Mantén los logs abiertos** para ver el procesamiento en tiempo real
3. **Prueba todas las especies** para ver diferentes fun facts
4. **Crea mascotas sin vacunar** para ver las alertas URGENTES
5. **Experimenta con diferentes edades** (cachorros, adultos, seniors)

### Para Demostración:

1. Abre 3 terminales:
   - Terminal 1: `docker logs -f pets-consumer-1`
   - Terminal 2: `docker logs -f pets-consumer-2`
   - Terminal 3: Navegador en `http://localhost:8000/`

2. Crea 3 mascotas rápidamente desde el navegador

3. Observa cómo los **diferentes workers** procesan las tareas en paralelo

4. Haz click en las tarjetas para mostrar el modal con información enriquecida

---

**🎉 ¡Disfruta tu sistema distribuido con interfaz web interactiva completamente funcional!**
