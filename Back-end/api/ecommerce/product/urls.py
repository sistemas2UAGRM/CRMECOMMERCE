from django.urls import path
from .views import *

urlpatterns = [
    path('product/', ProductoView.as_view()),
    path('product/<int:pk>/', ProductoView.as_view()),
]