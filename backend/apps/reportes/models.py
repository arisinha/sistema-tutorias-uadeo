"""
Modelos de reportes de tutoría.
"""

import os
from django.db import models
from django.conf import settings


def reporte_upload_path(instance, filename):
    """Genera ruta de almacenamiento para reportes."""
    from datetime import datetime
    now = datetime.now()
    return f'reportes/{now.year}/{now.month:02d}/{filename}'


class Reporte(models.Model):
    """Modelo principal de reporte de tutoría."""
    
    class TipoReporte(models.TextChoices):
        INDIVIDUAL_INICIAL = 'ind_inicial', 'Tutoría Individual - Inicial'
        INDIVIDUAL_MEDIO = 'ind_medio', 'Tutoría Individual - Medio Semestre'
        INDIVIDUAL_FINAL = 'ind_final', 'Tutoría Individual - Final'
        GRUPAL_INICIAL = 'grup_inicial', 'Tutoría Grupal - Inicial'
        GRUPAL_MEDIO = 'grup_medio', 'Tutoría Grupal - Medio Semestre'
        GRUPAL_FINAL = 'grup_final', 'Tutoría Grupal - Final'
    
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        PROCESANDO = 'procesando', 'Procesando'
        PROCESADO = 'procesado', 'Procesado'
        ERROR = 'error', 'Error'
    
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reportes',
        verbose_name='Tutor'
    )
    tipo_reporte = models.CharField(
        max_length=20,
        choices=TipoReporte.choices,
        verbose_name='Tipo de Reporte'
    )
    periodo = models.ForeignKey(
        'administracion.PeriodoAcademico',
        on_delete=models.PROTECT,
        related_name='reportes',
        verbose_name='Período Académico'
    )
    archivo_original = models.FileField(
        upload_to=reporte_upload_path,
        verbose_name='Archivo Original'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name='Estado'
    )
    mensaje_error = models.TextField(
        blank=True,
        verbose_name='Mensaje de Error'
    )
    fecha_subida = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Subida'
    )
    fecha_procesado = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Procesado'
    )
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-fecha_subida']
        indexes = [
            models.Index(fields=['tutor', 'tipo_reporte']),
            models.Index(fields=['periodo', 'estado']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_reporte_display()} - {self.tutor.get_full_name()}"
    
    @property
    def es_individual(self):
        return self.tipo_reporte.startswith('ind_')
    
    @property
    def es_grupal(self):
        return self.tipo_reporte.startswith('grup_')
    
    @property
    def nombre_archivo(self):
        return os.path.basename(self.archivo_original.name)


class DatoReporteIndividual(models.Model):
    """Datos extraídos de reportes de tutoría individual."""
    
    class NivelAsistencia(models.TextChoices):
        EXCELENTE = 'excelente', 'Excelente'
        BUENA = 'buena', 'Buena'
        REGULAR = 'regular', 'Regular'
        DEFICIENTE = 'deficiente', 'Deficiente'
    
    class NivelRendimiento(models.TextChoices):
        ALTO = 'alto', 'Alto'
        MEDIO = 'medio', 'Medio'
        BAJO = 'bajo', 'Bajo'
        MUY_BAJO = 'muy_bajo', 'Muy Bajo'
    
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        related_name='datos_individuales',
        verbose_name='Reporte'
    )
    alumno = models.ForeignKey(
        'alumnos.Alumno',
        on_delete=models.CASCADE,
        related_name='datos_reportes',
        verbose_name='Alumno'
    )
    asistencia = models.CharField(
        max_length=20,
        choices=NivelAsistencia.choices,
        blank=True,
        verbose_name='Nivel de Asistencia'
    )
    rendimiento = models.CharField(
        max_length=20,
        choices=NivelRendimiento.choices,
        blank=True,
        verbose_name='Nivel de Rendimiento'
    )
    materias_riesgo = models.TextField(
        blank=True,
        verbose_name='Materias en Riesgo'
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    requiere_seguimiento = models.BooleanField(
        default=False,
        verbose_name='Requiere Seguimiento'
    )
    fecha_sesion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Sesión'
    )
    
    class Meta:
        verbose_name = 'Dato Reporte Individual'
        verbose_name_plural = 'Datos Reportes Individuales'
        unique_together = ['reporte', 'alumno']
    
    def __str__(self):
        return f"{self.reporte} - {self.alumno.matricula}"


class DatoReporteGrupal(models.Model):
    """Datos extraídos de reportes de tutoría grupal."""
    
    reporte = models.OneToOneField(
        Reporte,
        on_delete=models.CASCADE,
        related_name='datos_grupales',
        verbose_name='Reporte'
    )
    num_alumnos_atendidos = models.PositiveIntegerField(
        default=0,
        verbose_name='Número de Alumnos Atendidos'
    )
    num_alumnos_grupo = models.PositiveIntegerField(
        default=0,
        verbose_name='Número de Alumnos en Grupo'
    )
    temas_tratados = models.TextField(
        blank=True,
        verbose_name='Temas Tratados'
    )
    problematicas_detectadas = models.TextField(
        blank=True,
        verbose_name='Problemáticas Detectadas'
    )
    alumnos_riesgo_ids = models.JSONField(
        default=list,
        blank=True,
        verbose_name='IDs Alumnos en Riesgo'
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    fecha_sesion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Sesión'
    )
    
    class Meta:
        verbose_name = 'Dato Reporte Grupal'
        verbose_name_plural = 'Datos Reportes Grupales'
    
    def __str__(self):
        return f"{self.reporte} - Grupal"
    
    @property
    def porcentaje_asistencia(self):
        if self.num_alumnos_grupo > 0:
            return (self.num_alumnos_atendidos / self.num_alumnos_grupo) * 100
        return 0
