from django.contrib import admin
from django.urls import path, include  # ← IMPORTANTE

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pets/', include('pets.urls')),  # ← REDIRECCIONA A LA APP
]
