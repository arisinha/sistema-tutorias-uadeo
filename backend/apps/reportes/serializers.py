"""
Serializadores de reportes.
"""

from rest_framework import serializers
from .models import Reporte, DatoReporteIndividual, DatoReporteGrupal


class DatoReporteIndividualSerializer(serializers.ModelSerializer):
    """Serializador de datos de reporte individual."""
    
    alumno_matricula = serializers.CharField(
        source='alumno.matricula', read_only=True
    )
    alumno_nombre = serializers.CharField(
        source='alumno.nombre_completo', read_only=True
    )
    
    class Meta:
        model = DatoReporteIndividual
        fields = [
            'id', 'alumno', 'alumno_matricula', 'alumno_nombre',
            'asistencia', 'rendimiento', 'materias_riesgo',
            'observaciones', 'requiere_seguimiento', 'fecha_sesion'
        ]


class DatoReporteGrupalSerializer(serializers.ModelSerializer):
    """Serializador de datos de reporte grupal."""
    
    porcentaje_asistencia = serializers.ReadOnlyField()
    
    class Meta:
        model = DatoReporteGrupal
        fields = [
            'id', 'num_alumnos_atendidos', 'num_alumnos_grupo',
            'porcentaje_asistencia', 'temas_tratados',
            'problematicas_detectadas', 'alumnos_riesgo_ids',
            'observaciones', 'fecha_sesion'
        ]


class ReporteSerializer(serializers.ModelSerializer):
    """Serializador completo de reporte."""
    
    tutor_nombre = serializers.CharField(
        source='tutor.get_full_name', read_only=True
    )
    tipo_reporte_display = serializers.CharField(
        source='get_tipo_reporte_display', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    periodo_nombre = serializers.CharField(
        source='periodo.nombre', read_only=True
    )
    nombre_archivo = serializers.ReadOnlyField()
    datos_individuales = DatoReporteIndividualSerializer(many=True, read_only=True)
    datos_grupales = DatoReporteGrupalSerializer(read_only=True)
    
    class Meta:
        model = Reporte
        fields = [
            'id', 'tutor', 'tutor_nombre', 'tipo_reporte',
            'tipo_reporte_display', 'periodo', 'periodo_nombre',
            'archivo_original', 'nombre_archivo', 'estado',
            'estado_display', 'mensaje_error', 'fecha_subida',
            'fecha_procesado', 'datos_individuales', 'datos_grupales'
        ]
        read_only_fields = ['id', 'tutor', 'estado', 'fecha_subida', 'fecha_procesado']


class ReporteListSerializer(serializers.ModelSerializer):
    """Serializador ligero para listados."""
    
    tutor_nombre = serializers.CharField(
        source='tutor.get_full_name', read_only=True
    )
    tipo_reporte_display = serializers.CharField(
        source='get_tipo_reporte_display', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    
    class Meta:
        model = Reporte
        fields = [
            'id', 'tutor_nombre', 'tipo_reporte', 'tipo_reporte_display',
            'estado', 'estado_display', 'fecha_subida'
        ]


class ReporteUploadSerializer(serializers.Serializer):
    """Serializador para subir reportes."""
    
    tipo_reporte = serializers.ChoiceField(choices=Reporte.TipoReporte.choices)
    periodo = serializers.IntegerField()
    archivo = serializers.FileField()
