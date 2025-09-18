# api/v1/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .users.views import UserViewSet

#Crear un Router
router = DefaultRouter()

# Registrar nuestro UserViewSet con el router
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
   path('', include(router.urls)),
]