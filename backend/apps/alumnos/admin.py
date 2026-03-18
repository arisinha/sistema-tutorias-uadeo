from django.contrib import admin
from .models import Alumno


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = [
        'matricula', 'nombre_completo', 'programa_educativo',
        'semestre', 'tutor', 'requiere_tutoria_individual', 'activo'
    ]
    list_filter = ['programa_educativo', 'semestre', 'activo', 'requiere_tutoria_individual']
    search_fields = ['matricula', 'nombre', 'apellido_paterno', 'apellido_materno', 'email']
    raw_id_fields = ['tutor']
    
    fieldsets = (
        ('Datos Personales', {
            'fields': ('matricula', 'nombre', 'apellido_paterno', 'apellido_materno', 'email', 'telefono')
        }),
        ('Información Académica', {
            'fields': ('programa_educativo', 'semestre', 'activo')
        }),
        ('Tutoría', {
            'fields': ('tutor', 'requiere_tutoria_individual', 'motivo_tutoria_individual')
        }),
    )
