📘 API de Mascotas – Proyecto Flask

Este proyecto es una API REST construida en Flask, creada como parte de la tarea asignada.
El tema seleccionado es 🐶 Mascotas, e incluye un conjunto de datos “quemados” (hardcoded) y los endpoints solicitados.

El proyecto demuestra:

Creación de una app Flask

Diccionario/lista con 5 elementos iniciales

Endpoint GET (uno y todos)

Filtros por query params

Endpoint POST para agregar elementos

Endpoint DELETE para eliminar elementos

Carpeta /img con las evidencias solicitadas

📁 Estructura del Proyecto
your-repo/
│── app.py
│── README.md
│── requirements.txt
│── .gitignore
└── img/
    ├── get_all.png
    ├── get_filtered_species.png
    ├── get_filtered_vaccinated.png
    ├── get_one.png
    ├── post_create.png
    └── delete_pet.png

🛠️ Requisitos

Asegúrate de tener Python 3 instalado.

Instala las dependencias del proyecto desde requirements.txt:

pip install -r requirements.txt


Opcional: usar un entorno virtual (recomendado)

python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt

▶️ Cómo ejecutar la aplicación
python app.py


El servidor iniciará en:

http://127.0.0.1:5000

🐾 Endpoints de la API

A continuación, se describen los endpoints creados según los requisitos de la tarea.

1️⃣ Obtener todas las mascotas

URL: /pets
Método: GET
Descripción: Devuelve la lista completa de mascotas.

Filtros disponibles (Query Params)
Filtro	Ejemplo	Descripción
species	/pets?species=dog	Filtra por especie
vaccinated	/pets?vaccinated=true	Filtra por vacunación (true/false)
También se pueden combinar:
/pets?species=dog&vaccinated=true

2️⃣ Obtener una sola mascota

URL: /pets/<id>
Método: GET
Descripción: Devuelve la mascota correspondiente al ID solicitado.

Ejemplo:

/pets/2

3️⃣ Agregar una nueva mascota

URL: /pets
Método: POST
Body: JSON

Ejemplo de cuerpo JSON:

{
  "name": "Max",
  "species": "dog",
  "age": 2,
  "owner": "Laura",
  "vaccinated": true
}


Descripción: Crea una nueva mascota en la lista con un ID generado automáticamente.

4️⃣ Eliminar una mascota

URL: /pets/<id>
Método: DELETE

Ejemplo:

DELETE /pets/4


Ejemplo de respuesta:

{
  "message": "Pet deleted successfully",
  "deleted_pet": {
    "id": 4,
    "name": "Luna",
    "species": "rabbit",
    "age": 1,
    "owner": "Maria",
    "vaccinated": false
  }
}

🖼️ Evidencias (Screenshots)

Todas las capturas solicitadas están ubicadas dentro de la carpeta /img/, incluyendo:

✔ GET todas las mascotas

✔ GET filtrado por especie

✔ GET filtrado por vacunación

✔ GET por ID

✔ POST creando nueva mascota

✔ DELETE eliminando mascota

📝 Contenido del .gitignore
__pycache__/
venv/
*.pyc
.env

🎓 Autor

Proyecto desarrollado como parte de la tarea asignada, mostrando conocimientos básicos de APIs con Python y Flask.