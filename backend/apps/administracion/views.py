"""
Vistas de administración del sistema.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.usuarios.permissions import EsJefeDepartamento, EsCoordinadorOJefe
from .models import UnidadAcademica, ProgramaEducativo, PeriodoAcademico, ConfiguracionSistema
from .serializers import (
    UnidadAcademicaSerializer,
    ProgramaEducativoSerializer,
    PeriodoAcademicoSerializer,
    ConfiguracionSistemaSerializer
)


class UnidadAcademicaViewSet(viewsets.ModelViewSet):
    """ViewSet para unidades académicas."""
    
    queryset = UnidadAcademica.objects.all()
    serializer_class = UnidadAcademicaSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [EsJefeDepartamento()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = UnidadAcademica.objects.all()
        if not self.request.user.es_jefe:
            queryset = queryset.filter(activa=True)
        return queryset


class ProgramaEducativoViewSet(viewsets.ModelViewSet):
    """ViewSet para programas educativos."""
    
    queryset = ProgramaEducativo.objects.all()
    serializer_class = ProgramaEducativoSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [EsJefeDepartamento()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = ProgramaEducativo.objects.select_related('unidad')
        
        user = self.request.user
        if not user.es_jefe:
            queryset = queryset.filter(activo=True)
        
        # Filtrar por unidad
        unidad = self.request.query_params.get('unidad')
        if unidad:
            queryset = queryset.filter(unidad_id=unidad)
        
        return queryset


class PeriodoAcademicoViewSet(viewsets.ModelViewSet):
    """ViewSet para períodos académicos."""
    
    queryset = PeriodoAcademico.objects.all()
    serializer_class = PeriodoAcademicoSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'activar']:
            return [EsCoordinadorOJefe()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar un período académico."""
        periodo = self.get_object()
        periodo.activo = True
        periodo.save()
        return Response({'mensaje': f'Período {periodo.nombre} activado'})
    
    @action(detail=False, methods=['get'])
    def activo(self, request):
        """Obtener el período activo."""
        try:
            periodo = PeriodoAcademico.objects.get(activo=True)
            serializer = self.get_serializer(periodo)
            return Response(serializer.data)
        except PeriodoAcademico.DoesNotExist:
            return Response({'error': 'No hay período activo'}, status=404)


class ConfiguracionSistemaViewSet(viewsets.ModelViewSet):
    """ViewSet para configuración del sistema."""
    
    queryset = ConfiguracionSistema.objects.all()
    serializer_class = ConfiguracionSistemaSerializer
    permission_classes = [EsJefeDepartamento]
    lookup_field = 'clave'
