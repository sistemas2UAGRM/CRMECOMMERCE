from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from api.bitacora.receivers import set_action_log
from .serializer import CategoriaSerializer
from .models import Categoria

class CategoriaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CategoriaSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            serializer.save(tenant=request.tenant)
            set_action_log(sender=self.__class__, user=user, action='create category', request=request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user
        set_action_log(sender=self.__class__, user=user, action='read categories', request=request)
        categorias = Categoria.objects.all()
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        user = request.user
        try:
            categoria = Categoria.objects.get(pk=pk)
        except Categoria.DoesNotExist:
            return Response({"detail": "Category deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        
        categoria.delete()
        set_action_log(sender=self.__class__, user=user, action='delete category', request=request)
        return Response({"detail": "Category deleted successfully."}, status=status.HTTP_204_NO_CONTENT)