"""
Vistas de gestión de alumnos.
"""

from django.db.models import Q
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.usuarios.models import Usuario
from apps.usuarios.permissions import EsCoordinadorOJefe
from rest_framework.permissions import IsAuthenticated
from .models import Alumno
from .serializers import (
    AlumnoSerializer,
    AlumnoListSerializer,
    AsignacionTutorSerializer,
    ImportacionExcelSerializer
)
from .utils import procesar_excel_alumnos, generar_plantilla_alumnos


class AlumnoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de alumnos."""
    
    queryset = Alumno.objects.all()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 
                           'importar_excel', 'asignar_tutor']:
            return [EsCoordinadorOJefe()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AlumnoListSerializer
        return AlumnoSerializer
    
    def get_queryset(self):
        queryset = Alumno.objects.select_related(
            'programa_educativo', 'tutor'
        )
        
        user = self.request.user
        
        # Filtrar según rol
        if user.es_tutor:
            queryset = queryset.filter(tutor=user)
        elif user.es_coordinador:
            queryset = queryset.filter(
                programa_educativo=user.programa_educativo
            )
        
        # Filtros adicionales
        programa = self.request.query_params.get('programa')
        if programa:
            queryset = queryset.filter(programa_educativo_id=programa)
        
        semestre = self.request.query_params.get('semestre')
        if semestre:
            queryset = queryset.filter(semestre=semestre)
        
        tutor = self.request.query_params.get('tutor')
        if tutor:
            queryset = queryset.filter(tutor_id=tutor)
        
        sin_tutor = self.request.query_params.get('sin_tutor')
        if sin_tutor == 'true':
            queryset = queryset.filter(tutor__isnull=True)
        
        requiere_individual = self.request.query_params.get('requiere_individual')
        if requiere_individual == 'true':
            queryset = queryset.filter(requiere_tutoria_individual=True)
        
        buscar = self.request.query_params.get('buscar')
        if buscar:
            queryset = queryset.filter(
                Q(matricula__icontains=buscar) |
                Q(nombre__icontains=buscar) |
                Q(apellido_paterno__icontains=buscar) |
                Q(apellido_materno__icontains=buscar)
            )
        
        return queryset
    
    @action(detail=False, methods=['post'], permission_classes=[EsCoordinadorOJefe])
    def importar_excel(self, request):
        """Importar alumnos desde archivo Excel."""
        serializer = ImportacionExcelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        archivo = serializer.validated_data['archivo']
        programa_id = serializer.validated_data['programa_educativo']
        
        # Validar tipo de archivo
        if not archivo.name.endswith(('.xlsx', '.xls')):
            return Response(
                {'error': 'El archivo debe ser Excel (.xlsx o .xls)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Procesar archivo
        alumnos_data, errores = procesar_excel_alumnos(archivo, programa_id)
        
        if errores and not alumnos_data:
            return Response(
                {'errores': errores},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear/actualizar alumnos
        creados = 0
        actualizados = 0
        
        for datos in alumnos_data:
            alumno, created = Alumno.objects.update_or_create(
                matricula=datos['matricula'],
                defaults=datos
            )
            if created:
                creados += 1
            else:
                actualizados += 1
        
        return Response({
            'mensaje': f'Importación completada: {creados} creados, {actualizados} actualizados',
            'creados': creados,
            'actualizados': actualizados,
            'errores': errores
        })
    
    @action(detail=False, methods=['get'])
    def plantilla(self, request):
        """Descargar plantilla Excel para importar alumnos."""
        output = generar_plantilla_alumnos()
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=plantilla_alumnos.xlsx'
        return response
    
    @action(detail=False, methods=['post'], permission_classes=[EsCoordinadorOJefe])
    def asignar_tutor(self, request):
        """Asignar tutor a múltiples alumnos."""
        serializer = AsignacionTutorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        alumno_ids = serializer.validated_data['alumno_ids']
        tutor_id = serializer.validated_data['tutor_id']
        
        # Verificar que el tutor existe y es tutor
        try:
            tutor = Usuario.objects.get(id=tutor_id, rol='tutor')
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Tutor no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Actualizar alumnos
        updated = Alumno.objects.filter(id__in=alumno_ids).update(tutor=tutor)
        
        return Response({
            'mensaje': f'{updated} alumnos asignados a {tutor.get_full_name()}'
        })
    
    @action(detail=False, methods=['get'])
    def sugerencias_tutoria(self, request):
        """Obtener alumnos sugeridos para tutoría individual."""
        # Esta lógica se puede expandir con criterios más complejos
        alumnos = self.get_queryset().filter(
            requiere_tutoria_individual=True,
            activo=True
        )
        serializer = AlumnoListSerializer(alumnos, many=True)
        return Response(serializer.data)
