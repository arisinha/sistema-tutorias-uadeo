"""
Serializadores de alumnos.
"""

from rest_framework import serializers
from .models import Alumno


class AlumnoSerializer(serializers.ModelSerializer):
    """Serializador completo de alumno."""
    
    nombre_completo = serializers.ReadOnlyField()
    tutor_nombre = serializers.CharField(
        source='tutor.get_full_name',
        read_only=True
    )
    programa_nombre = serializers.CharField(
        source='programa_educativo.nombre',
        read_only=True
    )
    
    class Meta:
        model = Alumno
        fields = [
            'id', 'matricula', 'nombre', 'apellido_paterno',
            'apellido_materno', 'nombre_completo', 'email', 'telefono',
            'programa_educativo', 'programa_nombre', 'semestre',
            'tutor', 'tutor_nombre', 'requiere_tutoria_individual',
            'motivo_tutoria_individual', 'activo', 'fecha_registro'
        ]
        read_only_fields = ['id', 'fecha_registro']


class AlumnoListSerializer(serializers.ModelSerializer):
    """Serializador ligero para listados."""
    
    nombre_completo = serializers.ReadOnlyField()
    tutor_nombre = serializers.CharField(
        source='tutor.get_full_name',
        read_only=True,
        default=None
    )
    programa_nombre = serializers.CharField(
        source='programa_educativo.nombre',
        read_only=True
    )
    
    class Meta:
        model = Alumno
        fields = [
            'id', 'matricula', 'nombre_completo', 'programa_educativo',
            'programa_nombre', 'semestre', 'tutor', 'tutor_nombre',
            'requiere_tutoria_individual', 'activo'
        ]


class AsignacionTutorSerializer(serializers.Serializer):
    """Serializador para asignar tutor a alumnos."""
    
    alumno_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    tutor_id = serializers.IntegerField()


class ImportacionExcelSerializer(serializers.Serializer):
    """Serializador para importar alumnos desde Excel."""
    
    archivo = serializers.FileField()
    programa_educativo = serializers.IntegerField()
