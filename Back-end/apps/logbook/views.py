# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from .models import Bitacora
from .serializer import BitacoraSerializer
from datetime import datetime, time, date

class BitacoraView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Bitacora.objects.filter(tenant=request.tenant).order_by('-timestamp')

        # Filtering parameters
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        usuario_id = request.query_params.get('usuario_id')
        accion = request.query_params.get('accion_contiene')
        ip = request.query_params.get('ip')

        if fecha_inicio:
            try:
                fecha_inicio_date = date.fromisoformat(fecha_inicio)
                fecha_inicio_dt = datetime.combine(fecha_inicio_date, time.min)
                queryset = queryset.filter(timestamp__gte=fecha_inicio_dt)
            except ValueError:
                pass

        if fecha_fin:
            try:
                fecha_fin_date = date.fromisoformat(fecha_fin)
                fecha_fin_dt = datetime.combine(fecha_fin_date, time.max)
                queryset = queryset.filter(timestamp__lte=fecha_fin_dt)
            except ValueError:
                pass

        if usuario_id:
            queryset = queryset.filter(user_id=usuario_id)

        if accion:
            queryset = queryset.filter(action__icontains=accion)

        if ip:
            queryset = queryset.filter(ip_address=ip)

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(queryset, request)
        serializer = BitacoraSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)
