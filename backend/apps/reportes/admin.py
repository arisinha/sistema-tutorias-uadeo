from django.contrib import admin
from .models import Reporte, DatoReporteIndividual, DatoReporteGrupal


class DatoReporteIndividualInline(admin.TabularInline):
    model = DatoReporteIndividual
    extra = 0
    readonly_fields = ['alumno', 'asistencia', 'rendimiento', 'requiere_seguimiento']


class DatoReporteGrupalInline(admin.StackedInline):
    model = DatoReporteGrupal
    extra = 0


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'tutor', 'tipo_reporte', 'periodo',
        'estado', 'fecha_subida', 'fecha_procesado'
    ]
    list_filter = ['tipo_reporte', 'estado', 'periodo']
    search_fields = ['tutor__username', 'tutor__first_name', 'tutor__last_name']
    readonly_fields = ['fecha_subida', 'fecha_procesado']
    raw_id_fields = ['tutor']
    
    inlines = [DatoReporteIndividualInline, DatoReporteGrupalInline]


@admin.register(DatoReporteIndividual)
class DatoReporteIndividualAdmin(admin.ModelAdmin):
    list_display = ['reporte', 'alumno', 'asistencia', 'rendimiento', 'requiere_seguimiento']
    list_filter = ['asistencia', 'rendimiento', 'requiere_seguimiento']
    raw_id_fields = ['reporte', 'alumno']


@admin.register(DatoReporteGrupal)
class DatoReporteGrupalAdmin(admin.ModelAdmin):
    list_display = ['reporte', 'num_alumnos_atendidos', 'num_alumnos_grupo', 'fecha_sesion']
    raw_id_fields = ['reporte']
