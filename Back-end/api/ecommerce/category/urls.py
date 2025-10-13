from django.urls import path
from .views import *

urlpatterns = [
    path('categories/', CategoriasView.as_view()),
    path('category/', CategoriaView.as_view()),
    path('category/<int:pk>/', CategoriaView.as_view()),
]