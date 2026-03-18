"""
Serializadores para dashboard de coordinación.
"""

from rest_framework import serializers


class EstadisticasGeneralesSerializer(serializers.Serializer):
    """Estadísticas generales del dashboard."""
    
    total_alumnos = serializers.IntegerField()
    total_tutores = serializers.IntegerField()
    alumnos_con_tutor = serializers.IntegerField()
    alumnos_sin_tutor = serializers.IntegerField()
    alumnos_requieren_individual = serializers.IntegerField()
    total_reportes = serializers.IntegerField()
    reportes_pendientes = serializers.IntegerField()
    reportes_procesados = serializers.IntegerField()
    reportes_error = serializers.IntegerField()


class EstadisticasTutorSerializer(serializers.Serializer):
    """Estadísticas por tutor."""
    
    tutor_id = serializers.IntegerField()
    tutor_nombre = serializers.CharField()
    alumnos_asignados = serializers.IntegerField()
    reportes_subidos = serializers.IntegerField()
    reportes_pendientes = serializers.IntegerField()


class AlumnoRiesgoSerializer(serializers.Serializer):
    """Alumno en riesgo para seguimiento."""
    
    id = serializers.IntegerField()
    matricula = serializers.CharField()
    nombre_completo = serializers.CharField()
    programa = serializers.CharField()
    semestre = serializers.IntegerField()
    tutor_nombre = serializers.CharField(allow_null=True)
    motivo = serializers.CharField()
