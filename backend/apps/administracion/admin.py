from django.contrib import admin
from .models import UnidadAcademica, ProgramaEducativo, PeriodoAcademico, ConfiguracionSistema


@admin.register(UnidadAcademica)
class UnidadAcademicaAdmin(admin.ModelAdmin):
    list_display = ['clave', 'nombre', 'activa']
    list_filter = ['activa']
    search_fields = ['nombre', 'clave']


@admin.register(ProgramaEducativo)
class ProgramaEducativoAdmin(admin.ModelAdmin):
    list_display = ['clave', 'nombre', 'unidad', 'duracion_semestres', 'activo']
    list_filter = ['unidad', 'activo']
    search_fields = ['nombre', 'clave']


@admin.register(PeriodoAcademico)
class PeriodoAcademicoAdmin(admin.ModelAdmin):
    list_display = ['clave', 'nombre', 'fecha_inicio', 'fecha_fin', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'clave']


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ['clave', 'valor']
    search_fields = ['clave', 'descripcion']
