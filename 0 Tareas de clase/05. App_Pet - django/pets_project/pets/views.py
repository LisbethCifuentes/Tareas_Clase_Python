from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Pet
import json


def serialize_pet(pet):
    return {
        "id": str(pet.id),
        "name": pet.name,
        "species": pet.species,
        "age": pet.age,
        "owner": pet.owner,
        "vaccinated": pet.vaccinated,
    }


@csrf_exempt
def pets_view(request):
    try:
        if request.method == "GET":
            pets = Pet.objects.all()

            species = request.GET.get("species")
            vaccinated = request.GET.get("vaccinated")

            if species:
                pets = pets.filter(species=species)

            if vaccinated is not None:
                pets = pets.filter(
                    vaccinated=(vaccinated.lower() == "true")
                )

            return JsonResponse(
                [serialize_pet(pet) for pet in pets],
                safe=False
            )

        if request.method == "POST":
            data = json.loads(request.body)

            pet = Pet.objects.create(
                name=data["name"],
                species=data["species"],
                age=data["age"],
                owner=data["owner"],
                vaccinated=data.get("vaccinated", False)
            )

            return JsonResponse(
                {"message": "Pet created", "id": str(pet.id)},
                status=201
            )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )
