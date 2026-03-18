"""
Serializadores de administración.
"""

from rest_framework import serializers
from .models import UnidadAcademica, ProgramaEducativo, PeriodoAcademico, ConfiguracionSistema


class UnidadAcademicaSerializer(serializers.ModelSerializer):
    """Serializador de unidad académica."""
    
    programas_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UnidadAcademica
        fields = ['id', 'nombre', 'clave', 'direccion', 'telefono', 'activa', 'programas_count']
    
    def get_programas_count(self, obj):
        return obj.programas.filter(activo=True).count()


class ProgramaEducativoSerializer(serializers.ModelSerializer):
    """Serializador de programa educativo."""
    
    unidad_nombre = serializers.CharField(source='unidad.nombre', read_only=True)
    alumnos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProgramaEducativo
        fields = [
            'id', 'nombre', 'clave', 'unidad', 'unidad_nombre',
            'duracion_semestres', 'activo', 'alumnos_count'
        ]
    
    def get_alumnos_count(self, obj):
        return obj.alumnos.filter(activo=True).count()


class PeriodoAcademicoSerializer(serializers.ModelSerializer):
    """Serializador de período académico."""
    
    class Meta:
        model = PeriodoAcademico
        fields = ['id', 'nombre', 'clave', 'fecha_inicio', 'fecha_fin', 'activo']


class ConfiguracionSistemaSerializer(serializers.ModelSerializer):
    """Serializador de configuración del sistema."""
    
    class Meta:
        model = ConfiguracionSistema
        fields = ['id', 'clave', 'valor', 'descripcion']
