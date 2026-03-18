"""
Vistas del dashboard de coordinación.
"""

from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.usuarios.models import Usuario
from apps.usuarios.permissions import EsCoordinadorOJefe
from apps.alumnos.models import Alumno
from apps.reportes.models import Reporte
from .serializers import (
    EstadisticasGeneralesSerializer,
    EstadisticasTutorSerializer,
    AlumnoRiesgoSerializer
)


class DashboardView(APIView):
    """Vista principal del dashboard."""
    
    permission_classes = [EsCoordinadorOJefe]
    
    def get(self, request):
        user = request.user
        
        # Filtros base según rol
        if user.es_coordinador and user.programa_educativo:
            alumnos = Alumno.objects.filter(
                programa_educativo=user.programa_educativo
            )
            tutores = Usuario.objects.filter(
                programa_educativo=user.programa_educativo,
                rol='tutor',
                is_active=True
            )
            reportes = Reporte.objects.filter(
                tutor__programa_educativo=user.programa_educativo
            )
        elif user.es_jefe and user.unidad:
            # Jefe de departamento ve toda su unidad
            alumnos = Alumno.objects.filter(
                programa_educativo__unidad=user.unidad
            )
            tutores = Usuario.objects.filter(
                unidad=user.unidad,
                rol='tutor',
                is_active=True
            )
            reportes = Reporte.objects.filter(
                tutor__unidad=user.unidad
            )
        else:
            # Sin filtros - muestra todo (para admin sin unidad asignada)
            alumnos = Alumno.objects.all()
            tutores = Usuario.objects.filter(rol='tutor', is_active=True)
            reportes = Reporte.objects.all()
        
        # Estadísticas generales
        stats = {
            'total_alumnos': alumnos.filter(activo=True).count(),
            'total_tutores': tutores.count(),
            'alumnos_con_tutor': alumnos.filter(tutor__isnull=False, activo=True).count(),
            'alumnos_sin_tutor': alumnos.filter(tutor__isnull=True, activo=True).count(),
            'alumnos_requieren_individual': alumnos.filter(
                requiere_tutoria_individual=True, activo=True
            ).count(),
            'total_reportes': reportes.count(),
            'reportes_pendientes': reportes.filter(
                estado__in=['pendiente', 'procesando']
            ).count(),
            'reportes_procesados': reportes.filter(estado='procesado').count(),
            'reportes_error': reportes.filter(estado='error').count(),
        }
        
        serializer = EstadisticasGeneralesSerializer(stats)
        return Response(serializer.data)


class EstadisticasTutoresView(APIView):
    """Estadísticas por tutor."""
    
    permission_classes = [EsCoordinadorOJefe]
    
    def get(self, request):
        user = request.user
        
        if user.es_coordinador and user.programa_educativo:
            tutores = Usuario.objects.filter(
                programa_educativo=user.programa_educativo,
                rol='tutor',
                is_active=True
            )
        elif user.es_jefe and user.unidad:
            tutores = Usuario.objects.filter(
                unidad=user.unidad,
                rol='tutor',
                is_active=True
            )
        else:
            tutores = Usuario.objects.filter(rol='tutor', is_active=True)
        
        # Anotar con conteos
        tutores = tutores.annotate(
            alumnos_count=Count('alumnos_asignados', filter=Q(alumnos_asignados__activo=True)),
            reportes_count=Count('reportes'),
            reportes_pend_count=Count(
                'reportes',
                filter=Q(reportes__estado__in=['pendiente', 'procesando'])
            )
        )
        
        data = []
        for tutor in tutores:
            data.append({
                'tutor_id': tutor.id,
                'tutor_nombre': tutor.get_full_name(),
                'alumnos_asignados': tutor.alumnos_count,
                'reportes_subidos': tutor.reportes_count,
                'reportes_pendientes': tutor.reportes_pend_count,
            })
        
        serializer = EstadisticasTutorSerializer(data, many=True)
        return Response(serializer.data)


class AlumnosRiesgoView(APIView):
    """Alumnos que requieren tutoría individual."""
    
    permission_classes = [EsCoordinadorOJefe]
    
    def get(self, request):
        user = request.user
        
        if user.es_coordinador and user.programa_educativo:
            alumnos = Alumno.objects.filter(
                programa_educativo=user.programa_educativo,
                requiere_tutoria_individual=True,
                activo=True
            )
        elif user.es_jefe and user.unidad:
            alumnos = Alumno.objects.filter(
                programa_educativo__unidad=user.unidad,
                requiere_tutoria_individual=True,
                activo=True
            )
        else:
            alumnos = Alumno.objects.filter(
                requiere_tutoria_individual=True,
                activo=True
            )
        
        alumnos = alumnos.select_related('programa_educativo', 'tutor')
        
        data = []
        for alumno in alumnos:
            data.append({
                'id': alumno.id,
                'matricula': alumno.matricula,
                'nombre_completo': alumno.nombre_completo,
                'programa': alumno.programa_educativo.nombre,
                'semestre': alumno.semestre,
                'tutor_nombre': alumno.tutor.get_full_name() if alumno.tutor else None,
                'motivo': alumno.motivo_tutoria_individual or 'Bajo rendimiento detectado',
            })
        
        serializer = AlumnoRiesgoSerializer(data, many=True)
        return Response(serializer.data)


class ResumenReportesView(APIView):
    """Resumen de reportes por tipo y estado."""
    
    permission_classes = [EsCoordinadorOJefe]
    
    def get(self, request):
        user = request.user
        
        if user.es_coordinador and user.programa_educativo:
            reportes = Reporte.objects.filter(
                tutor__programa_educativo=user.programa_educativo
            )
        elif user.es_jefe and user.unidad:
            reportes = Reporte.objects.filter(
                tutor__unidad=user.unidad
            )
        else:
            reportes = Reporte.objects.all()
        
        # Agrupar por tipo
        por_tipo = reportes.values('tipo_reporte').annotate(
            total=Count('id'),
            procesados=Count('id', filter=Q(estado='procesado')),
            pendientes=Count('id', filter=Q(estado__in=['pendiente', 'procesando'])),
            errores=Count('id', filter=Q(estado='error'))
        )
        
        return Response({
            'por_tipo': list(por_tipo)
        })
