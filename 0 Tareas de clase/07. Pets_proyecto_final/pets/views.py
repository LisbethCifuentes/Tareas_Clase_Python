from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Pet
import json
import redis
import os

# Configuración de Redis
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
QUEUE_NAME = 'pets:tasks'

# Conexión a Redis (se inicializa al importar)
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_timeout=5,
    )
    redis_client.ping()
    print(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except redis.ConnectionError:
    print(f"⚠️  Warning: Could not connect to Redis at {REDIS_HOST}:{REDIS_PORT}")
    redis_client = None


def serialize_pet(pet):
    """Serializa un objeto Pet a diccionario"""
    return {
        "id": str(pet.id),
        "name": pet.name,
        "species": pet.species,
        "age": pet.age,
        "owner": pet.owner,
        "vaccinated": pet.vaccinated,
    }


def enqueue_pet_task(pet_data):
    """
    Envía una tarea a la cola de Redis para procesamiento asíncrono
    """
    if redis_client is None:
        print("⚠️  Redis not available, skipping task queue")
        return False
    
    try:
        task = {
            "pet_id": str(pet_data['id']),
            "name": pet_data['name'],
            "species": pet_data['species'],
            "age": pet_data['age'],
            "owner": pet_data['owner'],
            "vaccinated": pet_data['vaccinated'],
        }
        
        # RPUSH: añade al final de la cola (FIFO)
        redis_client.rpush(QUEUE_NAME, json.dumps(task))
        print(f"✅ Task enqueued for pet: {pet_data['name']} (ID: {pet_data['id']})")
        return True
    except Exception as e:
        print(f"❌ Error enqueueing task: {str(e)}")
        return False


# ==================== VISTA RENDERIZADA (SIN AUTH) ====================
def pets_page(request):
    """Vista HTML renderizada - NO requiere autenticación"""
    pets = Pet.objects.all()
    return render(request, 'pets/pets_list.html', {'pets': pets})


# ==================== API CRUD (CON JWT) ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def pets_api_list(request):
    """
    GET: Lista todas las mascotas (con filtros opcionales)
    POST: Crea una nueva mascota y envía tarea a Redis
    """
    if request.method == 'GET':
        pets = Pet.objects.all()
        
        # Filtros opcionales
        species = request.GET.get('species')
        vaccinated = request.GET.get('vaccinated')
        
        if species:
            pets = pets.filter(species=species)
        
        if vaccinated is not None:
            pets = pets.filter(vaccinated=(vaccinated.lower() == 'true'))
        
        serialized_pets = [serialize_pet(pet) for pet in pets]
        return Response(serialized_pets, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        data = request.data
        
        # Validación básica
        required_fields = ['name', 'species', 'age', 'owner']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Field "{field}" is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            # Crear mascota en MongoDB
            pet = Pet.objects.create(
                name=data['name'],
                species=data['species'],
                age=int(data['age']),
                owner=data['owner'],
                vaccinated=data.get('vaccinated', False)
            )
            
            pet_data = serialize_pet(pet)
            
            # 🎯 ENVIAR TAREA A REDIS
            task_enqueued = enqueue_pet_task(pet_data)
            
            response_data = {
                'message': 'Pet created successfully',
                'pet': pet_data,
                'task_queued': task_enqueued,
            }
            
            if task_enqueued:
                response_data['info'] = 'Task sent to workers for processing. Enriched data will be generated.'
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def pets_api_detail(request, pet_id):
    """
    GET: Obtiene una mascota específica
    PUT: Actualiza una mascota
    DELETE: Elimina una mascota
    """
    try:
        pet = Pet.objects.get(id=pet_id)
    except Pet.DoesNotExist:
        return Response(
            {'error': 'Pet not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        return Response(serialize_pet(pet), status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        data = request.data
        
        # Actualizar campos
        if 'name' in data:
            pet.name = data['name']
        if 'species' in data:
            pet.species = data['species']
        if 'age' in data:
            pet.age = int(data['age'])
        if 'owner' in data:
            pet.owner = data['owner']
        if 'vaccinated' in data:
            pet.vaccinated = data['vaccinated']
        
        pet.save()
        
        return Response(
            {
                'message': 'Pet updated successfully',
                'pet': serialize_pet(pet)
            },
            status=status.HTTP_200_OK
        )
    
    elif request.method == 'DELETE':
        pet.delete()
        return Response(
            {'message': 'Pet deleted successfully'},
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def redis_stats(request):
    """
    Endpoint para ver estadísticas de la cola de Redis
    """
    if redis_client is None:
        return Response(
            {'error': 'Redis not available'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        queue_length = redis_client.llen(QUEUE_NAME)
        redis_info = redis_client.info()
        
        stats = {
            'queue_name': QUEUE_NAME,
            'pending_tasks': queue_length,
            'redis_host': REDIS_HOST,
            'redis_port': REDIS_PORT,
            'connected_clients': redis_info.get('connected_clients', 0),
            'total_commands_processed': redis_info.get('total_commands_processed', 0),
        }
        
        return Response(stats, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
