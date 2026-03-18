"""
Vistas de autenticación y usuarios.
"""

from django.contrib.auth import authenticate, login, logout
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Usuario
from .serializers import (
    UsuarioSerializer,
    UsuarioLoginSerializer,
    UsuarioCreateSerializer
)
from .permissions import EsCoordinadorOJefe


class LoginView(APIView):
    """Vista para inicio de sesión."""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UsuarioLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if user is not None:
            login(request, user)
            return Response({
                'message': 'Inicio de sesión exitoso',
                'user': UsuarioSerializer(user).data
            })
        
        return Response(
            {'error': 'Credenciales inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """Vista para cerrar sesión."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': 'Sesión cerrada exitosamente'})


class PerfilView(APIView):
    """Vista para obtener el perfil del usuario actual."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)
    
    def patch(self, request):
        serializer = UsuarioSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de usuarios (solo coordinadores/jefes)."""
    
    queryset = Usuario.objects.all()
    permission_classes = [EsCoordinadorOJefe]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer
    
    def get_queryset(self):
        queryset = Usuario.objects.all()
        
        # Filtrar por rol
        rol = self.request.query_params.get('rol')
        if rol:
            queryset = queryset.filter(rol=rol)
        
        # Filtrar por programa educativo
        programa = self.request.query_params.get('programa')
        if programa:
            queryset = queryset.filter(programa_educativo_id=programa)
        
        # Filtrar por unidad
        unidad = self.request.query_params.get('unidad')
        if unidad:
            queryset = queryset.filter(unidad_id=unidad)
        
        return queryset.select_related('unidad', 'programa_educativo')
    
    @action(detail=False, methods=['get'])
    def tutores(self, request):
        """Obtener lista de tutores."""
        tutores = self.get_queryset().filter(rol='tutor', is_active=True)
        serializer = self.get_serializer(tutores, many=True)
        return Response(serializer.data)
