#!/usr/bin/env python
"""
Consumer Worker - Procesa tareas de la cola de Redis
Tarea: Enriquecer datos de mascotas buscando información adicional y generando archivos JSON
"""

import os
import sys
import json
import time
import redis
import requests
from datetime import datetime
from typing import Dict, Any

# Configuración
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
CONSUMER_ID = os.environ.get('CONSUMER_ID', 'unknown')
QUEUE_NAME = 'pets:tasks'
PROCESSED_DIR = '/app/processed_data'

# Asegurar que existe el directorio
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Colores para logs
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def log(message: str, level: str = "INFO"):
    """Log con colores"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colors = {
        "INFO": Colors.OKBLUE,
        "SUCCESS": Colors.OKGREEN,
        "WARNING": Colors.WARNING,
        "ERROR": Colors.FAIL,
    }
    color = colors.get(level, Colors.OKBLUE)
    print(f"{color}[{timestamp}] [Consumer-{CONSUMER_ID}] [{level}] {message}{Colors.ENDC}")
    sys.stdout.flush()


def search_pet_info(species: str, name: str) -> Dict[str, Any]:
    """
    Busca información adicional sobre la especie usando una API pública
    Usa la API de Wikipedia para obtener datos interesantes
    """
    try:
        # Buscar en Wikipedia
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        search_term = species.lower()
        
        response = requests.get(f"{url}{search_term}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "wikipedia_extract": data.get("extract", "No description available"),
                "wikipedia_url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "thumbnail": data.get("thumbnail", {}).get("source", "") if data.get("thumbnail") else None,
            }
        else:
            return {
                "wikipedia_extract": f"No Wikipedia information found for {species}",
                "wikipedia_url": "",
                "thumbnail": None,
            }
    except Exception as e:
        log(f"Error fetching Wikipedia data: {str(e)}", "WARNING")
        return {
            "wikipedia_extract": f"Error fetching data for {species}",
            "wikipedia_url": "",
            "thumbnail": None,
        }


def get_fun_facts(species: str) -> Dict[str, Any]:
    """
    Genera datos interesantes basados en la especie
    """
    facts_db = {
        "dog": {
            "lifespan": "10-13 years",
            "group": "Mammal",
            "diet": "Omnivore",
            "fun_fact": "Dogs have been companions to humans for over 15,000 years!",
        },
        "cat": {
            "lifespan": "12-18 years",
            "group": "Mammal",
            "diet": "Carnivore",
            "fun_fact": "Cats spend 70% of their lives sleeping!",
        },
        "bird": {
            "lifespan": "5-30 years (varies by species)",
            "group": "Aves",
            "diet": "Varies (seeds, insects, nectar)",
            "fun_fact": "Some birds can see ultraviolet light!",
        },
        "fish": {
            "lifespan": "1-20 years (varies by species)",
            "group": "Pisces",
            "diet": "Varies",
            "fun_fact": "Fish were on Earth before dinosaurs!",
        },
        "rabbit": {
            "lifespan": "8-12 years",
            "group": "Mammal",
            "diet": "Herbivore",
            "fun_fact": "Rabbits can see nearly 360 degrees around them!",
        },
    }
    
    species_lower = species.lower()
    return facts_db.get(species_lower, {
        "lifespan": "Varies",
        "group": "Unknown",
        "diet": "Varies",
        "fun_fact": f"{species} is a wonderful pet!",
    })


def generate_health_tips(species: str, age: int, vaccinated: bool) -> list:
    """
    Genera tips de salud basados en los datos de la mascota
    """
    tips = []
    
    if not vaccinated:
        tips.append(f"⚠️ URGENT: This {species} needs vaccination! Please consult a veterinarian.")
    
    if age < 1:
        tips.append(f"🍼 This young {species} needs frequent check-ups and proper nutrition.")
    elif age > 10:
        tips.append(f"👴 Senior {species}! Consider more frequent vet visits and special diet.")
    else:
        tips.append(f"✅ Adult {species} in prime age. Maintain regular check-ups.")
    
    # Tips específicos por especie
    species_tips = {
        "dog": "🐕 Dogs need daily exercise and social interaction.",
        "cat": "🐱 Cats need scratching posts and regular grooming.",
        "bird": "🐦 Birds need large cages and mental stimulation.",
        "fish": "🐠 Fish need clean water and proper temperature control.",
        "rabbit": "🐰 Rabbits need space to hop and chew-safe toys.",
    }
    
    species_lower = species.lower()
    if species_lower in species_tips:
        tips.append(species_tips[species_lower])
    
    return tips


def process_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa una tarea: enriquece los datos de la mascota con información adicional
    """
    pet_id = task_data.get('pet_id', 'unknown')
    pet_name = task_data.get('name', 'Unknown')
    pet_species = task_data.get('species', 'Unknown')
    pet_age = task_data.get('age', 0)
    pet_owner = task_data.get('owner', 'Unknown')
    pet_vaccinated = task_data.get('vaccinated', False)
    
    log(f"Processing pet: {pet_name} ({pet_species}) - ID: {pet_id}", "INFO")
    
    # 1. Buscar información en Wikipedia
    log(f"Fetching Wikipedia data for {pet_species}...", "INFO")
    wiki_data = search_pet_info(pet_species, pet_name)
    time.sleep(1)  # Pequeña pausa para no saturar APIs
    
    # 2. Obtener datos curiosos
    log(f"Generating fun facts...", "INFO")
    fun_facts = get_fun_facts(pet_species)
    
    # 3. Generar tips de salud
    log(f"Generating health tips...", "INFO")
    health_tips = generate_health_tips(pet_species, pet_age, pet_vaccinated)
    
    # 4. Crear documento enriquecido
    enriched_data = {
        "metadata": {
            "processed_by": f"Consumer-{CONSUMER_ID}",
            "processed_at": datetime.now().isoformat(),
            "processing_duration_seconds": 2,  # Aproximado
        },
        "original_data": {
            "pet_id": pet_id,
            "name": pet_name,
            "species": pet_species,
            "age": pet_age,
            "owner": pet_owner,
            "vaccinated": pet_vaccinated,
        },
        "enriched_info": {
            "wikipedia": wiki_data,
            "species_facts": fun_facts,
            "health_tips": health_tips,
        },
        "statistics": {
            "total_tips": len(health_tips),
            "vaccination_status": "Up to date" if pet_vaccinated else "Needs vaccination",
            "age_category": "Puppy/Kitten" if pet_age < 1 else ("Senior" if pet_age > 10 else "Adult"),
        }
    }
    
    # 5. Guardar en archivo JSON
    filename = f"{pet_id}_{pet_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(PROCESSED_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(enriched_data, f, indent=2, ensure_ascii=False)
    
    log(f"✅ Enriched data saved to: {filename}", "SUCCESS")
    
    return enriched_data


def connect_redis():
    """Conecta a Redis con reintentos"""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            r = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            r.ping()
            log(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}", "SUCCESS")
            return r
        except redis.ConnectionError as e:
            if attempt < max_retries - 1:
                log(f"Failed to connect to Redis (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay}s...", "WARNING")
                time.sleep(retry_delay)
            else:
                log(f"❌ Could not connect to Redis after {max_retries} attempts", "ERROR")
                raise


def main():
    """Loop principal del consumidor"""
    log(f"🚀 Starting Consumer Worker {CONSUMER_ID}", "INFO")
    log(f"📍 Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}", "INFO")
    log(f"📋 Listening on queue: {QUEUE_NAME}", "INFO")
    
    # Conectar a Redis
    r = connect_redis()
    
    log(f"👂 Waiting for tasks... (Press CTRL+C to stop)", "INFO")
    
    while True:
        try:
            # BLPOP: espera bloqueante (eficiente) por un elemento en la cola
            # Timeout de 1 segundo para permitir señales de interrupción
            result = r.blpop(QUEUE_NAME, timeout=1)
            
            if result:
                queue_name, task_json = result
                log(f"📨 Received new task from queue", "INFO")
                
                try:
                    # Parsear tarea
                    task_data = json.loads(task_json)
                    
                    # Procesar tarea
                    start_time = time.time()
                    enriched = process_task(task_data)
                    duration = time.time() - start_time
                    
                    log(f"⏱️  Task processed in {duration:.2f}s", "SUCCESS")
                    log(f"📊 Generated {len(enriched['enriched_info']['health_tips'])} health tips", "INFO")
                    
                except json.JSONDecodeError as e:
                    log(f"❌ Invalid JSON in task: {str(e)}", "ERROR")
                except Exception as e:
                    log(f"❌ Error processing task: {str(e)}", "ERROR")
            
        except KeyboardInterrupt:
            log(f"🛑 Shutting down Consumer-{CONSUMER_ID}", "WARNING")
            break
        except redis.ConnectionError:
            log(f"❌ Lost connection to Redis. Attempting to reconnect...", "ERROR")
            try:
                r = connect_redis()
            except Exception as e:
                log(f"❌ Failed to reconnect: {str(e)}", "ERROR")
                break
        except Exception as e:
            log(f"❌ Unexpected error: {str(e)}", "ERROR")
            time.sleep(5)


if __name__ == "__main__":
    main()
