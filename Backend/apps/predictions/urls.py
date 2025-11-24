from django.urls import path
from . import views

urlpatterns = [
    path('predecir/', views.PredictionView.as_view(), name='prediction'),
]