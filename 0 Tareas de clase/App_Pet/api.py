from flask import Flask, request, jsonify

app = Flask(__name__)

# "Database" in memory: list of dictionaries (burned data)
pets = [
    {
        "id": 1,
        "name": "Firu",
        "species": "dog",
        "age": 3,
        "owner": "Ana",
        "vaccinated": True
    },
    {
        "id": 2,
        "name": "Misu",
        "species": "cat",
        "age": 2,
        "owner": "Luis",
        "vaccinated": False
    },
    {
        "id": 3,
        "name": "Rocky",
        "species": "dog",
        "age": 5,
        "owner": "Carlos",
        "vaccinated": True
    },
    {
        "id": 4,
        "name": "Luna",
        "species": "rabbit",
        "age": 1,
        "owner": "Maria",
        "vaccinated": False
    },
    {
        "id": 5,
        "name": "Toby",
        "species": "dog",
        "age": 4,
        "owner": "Pedro",
        "vaccinated": True
    }
]

# next ID after the burned elements
next_id = 6


def generate_id():
    """Generate a new incremental ID."""
    global next_id
    new_id = next_id
    next_id += 1
    return new_id


def str_to_bool(value):
    """
    Convert a string query param to boolean.
    Accepted true values: 'true', '1', 'yes'
    Accepted false values: 'false', '0', 'no'
    Returns None if value is None or invalid.
    """
    if value is None:
        return None

    value = value.lower()

    if value in ["true", "1", "yes"]:
        return True
    if value in ["false", "0", "no"]:
        return False

    return None


@app.route("/")
def home():
    """Root endpoint to avoid Not Found on /."""
    return "Pets API is running. Go to /pets to see the data."


@app.route("/pets", methods=["GET"])
def get_all_pets():
    """
    Get all pets.

    Optional query filters:
    - species: /pets?species=dog
    - vaccinated: /pets?vaccinated=true

    You can combine filters, for example:
    - /pets?species=dog&vaccinated=true
    """
    species = request.args.get("species")
    vaccinated_param = request.args.get("vaccinated")
    vaccinated_bool = str_to_bool(vaccinated_param)

    filtered_pets = pets

    if species:
        filtered_pets = [
            p for p in filtered_pets
            if p["species"].lower() == species.lower()
        ]

    if vaccinated_bool is not None:
        filtered_pets = [
            p for p in filtered_pets
            if p["vaccinated"] == vaccinated_bool
        ]

    return jsonify(filtered_pets), 200


@app.route("/pets/<int:pet_id>", methods=["GET"])
def get_one_pet(pet_id):
    """
    Get one pet by ID.
    Example: /pets/1
    """
    for pet in pets:
        if pet["id"] == pet_id:
            return jsonify(pet), 200

    return jsonify({"error": "Pet not found"}), 404


@app.route("/pets", methods=["POST"])
def create_pet():
    """
    Create a new pet.

    Required fields in JSON body:
    - name
    - species

    Optional fields:
    - age
    - owner
    - vaccinated

    Example JSON:
    {
      "name": "Max",
      "species": "dog",
      "age": 2,
      "owner": "Laura",
      "vaccinated": true
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Required fields check
    if "name" not in data or "species" not in data:
        return jsonify(
            {"error": "Fields 'name' and 'species' are required"}
        ), 400

    new_pet = {
        "id": generate_id(),
        "name": data["name"],
        "species": data["species"],
        "age": data.get("age"),
        "owner": data.get("owner"),
        "vaccinated": data.get("vaccinated", False)
    }

    pets.append(new_pet)
    return jsonify(new_pet), 201


@app.route("/pets/<int:pet_id>", methods=["DELETE"])
def delete_pet(pet_id):
    """
    Delete a pet by ID.
    Example: DELETE /pets/3
    """
    for index, pet in enumerate(pets):
        if pet["id"] == pet_id:
            removed_pet = pets.pop(index)
            return jsonify({
                "message": "Pet deleted successfully",
                "deleted_pet": removed_pet
            }), 200

    return jsonify({"error": "Pet not found"}), 404


if __name__ == "__main__":
    # debug=True is useful for development
    app.run(debug=True)
