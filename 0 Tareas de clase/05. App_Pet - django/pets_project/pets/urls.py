from django.urls import path
from .views import pets_view

urlpatterns = [
    path("", pets_view),
]
