"""
Vistas de gestión de reportes.
"""

from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.usuarios.permissions import EsCoordinadorOJefe, EsTutorOCoordinador
from apps.usuarios.audit import registrar_accion
from apps.administracion.models import PeriodoAcademico
from .models import Reporte
from .serializers import (
    ReporteSerializer,
    ReporteListSerializer,
    ReporteUploadSerializer
)
from .processors import generar_plantilla_reporte
from .tasks import procesar_reporte_async



class ReporteViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de reportes."""
    
    queryset = Reporte.objects.all()
    
    def get_permissions(self):
        if self.action in ['destroy']:
            return [EsCoordinadorOJefe()]
        return [EsTutorOCoordinador()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReporteListSerializer
        return ReporteSerializer
    
    def get_queryset(self):
        queryset = Reporte.objects.select_related(
            'tutor', 'periodo'
        ).prefetch_related(
            'datos_individuales', 'datos_individuales__alumno'
        )
        
        user = self.request.user
        
        # Filtrar según rol
        if user.es_tutor:
            queryset = queryset.filter(tutor=user)
        elif user.es_coordinador:
            queryset = queryset.filter(
                tutor__programa_educativo=user.programa_educativo
            )
        
        # Filtros adicionales
        tipo = self.request.query_params.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo_reporte=tipo)
        
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        periodo = self.request.query_params.get('periodo')
        if periodo:
            queryset = queryset.filter(periodo_id=periodo)
        
        tutor = self.request.query_params.get('tutor')
        if tutor and not user.es_tutor:
            queryset = queryset.filter(tutor_id=tutor)
        
        return queryset

    def perform_destroy(self, instance):
        registrar_accion(
            self.request,
            'ELIMINAR_REPORTE',
            f'Se eliminó el reporte {instance.id} de {instance.tutor.username} ({instance.tipo_reporte})'
        )
        instance.delete()
    
    @action(detail=False, methods=['post'])
    def subir(self, request):
        """Subir un nuevo reporte."""
        serializer = ReporteUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        archivo = serializer.validated_data['archivo']
        
        # Validar tipo de archivo
        if not archivo.name.endswith(('.xlsx', '.xls')):
            return Response(
                {'error': 'El archivo debe ser Excel (.xlsx o .xls)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar tamaño (10 MB máximo)
        if archivo.size > 10 * 1024 * 1024:
            return Response(
                {'error': 'El archivo excede el tamaño máximo de 10 MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Validar periodo
        if not PeriodoAcademico.objects.filter(id=serializer.validated_data['periodo']).exists():
            return Response(
                {'error': 'El período especificado no existe'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear reporte
        reporte = Reporte.objects.create(
            tutor=request.user,
            tipo_reporte=serializer.validated_data['tipo_reporte'],
            periodo_id=serializer.validated_data['periodo'],
            archivo_original=archivo,
            estado=Reporte.Estado.PENDIENTE
        )
        
        # Iniciar procesamiento asíncrono
        procesar_reporte_async.delay(reporte.id)
        
        registrar_accion(
            request,
            'SUBIR_REPORTE',
            f'Se subió el reporte {reporte.id} ({reporte.tipo_reporte})'
        )
        
        return Response({
            'mensaje': 'Reporte subido exitosamente. El procesamiento ha iniciado.',
            'reporte': ReporteSerializer(reporte).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def plantilla(self, request):
        """Descargar plantilla Excel para un tipo de reporte."""
        tipo = request.query_params.get('tipo')
        
        if not tipo:
            return Response(
                {'error': 'Debe especificar el tipo de reporte'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if tipo not in dict(Reporte.TipoReporte.choices):
            return Response(
                {'error': 'Tipo de reporte inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        output = generar_plantilla_reporte(tipo)
        
        nombre_archivo = f'plantilla_{tipo}.xlsx'
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={nombre_archivo}'
        return response
    
    @action(detail=True, methods=['post'])
    def reprocesar(self, request, pk=None):
        """Reprocesar un reporte con error."""
        reporte = self.get_object()
        
        if reporte.estado != Reporte.Estado.ERROR:
            return Response(
                {'error': 'Solo se pueden reprocesar reportes con error'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reporte.estado = Reporte.Estado.PENDIENTE
        reporte.mensaje_error = ''
        reporte.save(update_fields=['estado', 'mensaje_error'])
        
        procesar_reporte_async.delay(reporte.id)
        
        return Response({
            'mensaje': 'Reprocesamiento iniciado'
        })
    
    @action(detail=True, methods=['get'])
    def descargar(self, request, pk=None):
        """Descargar archivo original del reporte."""
        reporte = self.get_object()
        
        response = HttpResponse(
            reporte.archivo_original.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={reporte.nombre_archivo}'
        return response
