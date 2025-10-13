from django.urls import path, include
from .views import *

urlpatterns = [
    path('bitacora/', BitacoraView.as_view()),
]
