from django.urls import path
from . import views   # ← Importa las funciones creadas en views.py

urlpatterns = [
    path('', views.get_pets),  # 127.0.0.1:8000/pets/
]
