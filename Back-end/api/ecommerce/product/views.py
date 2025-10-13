from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from api.bitacora.receivers import set_action_log
from .serializer import ProductoSerializer
from .models import Producto

class ProductosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Producto.objects.filter(tenant=request.tenant).order_by('-created_at')
        user = request.user
        set_action_log(sender=self.__class__, user=user, action='read products', request=request)
        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProductoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

class ProductoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProductoSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            serializer.save(tenant=request.tenant)
            set_action_log(sender=self.__class__, user=user, action='create product', request=request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = Producto.objects.get(id=pk)
        serializer = ProductoSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            user = request.user
            serializer.save(tenant=request.tenant)
            set_action_log(sender=self.__class__, user=user, action=f'update product {pk}', request=request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        obj = Producto.objects.get(id=pk)
        serializer = ProductoSerializer(obj)
        return Response(serializer.data)

    def delete(self, request, pk):
        user = request.user
        try:
            producto = Producto.objects.get(pk=pk)
        except Producto.DoesNotExist:
            return Response({"detail": f"Error deleting product {pk}."}, status=status.HTTP_204_NO_CONTENT)
        
        producto.delete()
        set_action_log(sender=self.__class__, user=user, action='delete product', request=request)
        return Response({"detail": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)