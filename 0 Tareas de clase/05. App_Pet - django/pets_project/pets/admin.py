from django.contrib import admin
from .models import Pet   # 👈 importamos el modelo

admin.site.register(Pet)  # 👈 lo registramos en el admin
