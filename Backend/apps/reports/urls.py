from django.urls import path
from . import views

urlpatterns = [
    path('generar-reporte-ia/', views.ReportView.as_view(), name='generate_report'),
]