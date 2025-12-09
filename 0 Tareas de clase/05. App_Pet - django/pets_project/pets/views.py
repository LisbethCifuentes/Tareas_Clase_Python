from django.http import JsonResponse
from .models import Pet

def get_pets(request):
    # Trae todas las mascotas de la BD como diccionarios
    pets_qs = Pet.objects.all().values() #trae todos los campos como diccionarios
    pets_list = list(pets_qs)# convertimos el QuerySet a lista
    return JsonResponse(pets_list, safe=False)# safe=False permite devolver listas
