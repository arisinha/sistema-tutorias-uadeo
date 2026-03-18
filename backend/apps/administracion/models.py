"""
Modelos de administración del sistema.
"""

from django.db import models


class UnidadAcademica(models.Model):
    """Unidad académica (campus, facultad, etc.)."""
    
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre'
    )
    clave = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Clave'
    )
    direccion = models.TextField(
        blank=True,
        verbose_name='Dirección'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    activa = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    class Meta:
        verbose_name = 'Unidad Académica'
        verbose_name_plural = 'Unidades Académicas'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.clave} - {self.nombre}"


class ProgramaEducativo(models.Model):
    """Programa educativo (carrera, licenciatura, etc.)."""
    
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre'
    )
    clave = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Clave'
    )
    unidad = models.ForeignKey(
        UnidadAcademica,
        on_delete=models.PROTECT,
        related_name='programas',
        verbose_name='Unidad Académica'
    )
    duracion_semestres = models.PositiveSmallIntegerField(
        default=9,
        verbose_name='Duración en Semestres'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        verbose_name = 'Programa Educativo'
        verbose_name_plural = 'Programas Educativos'
        ordering = ['unidad', 'nombre']
    
    def __str__(self):
        return f"{self.clave} - {self.nombre}"


class PeriodoAcademico(models.Model):
    """Período académico (semestre, cuatrimestre, etc.)."""
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    clave = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Clave'
    )
    fecha_inicio = models.DateField(
        verbose_name='Fecha de Inicio'
    )
    fecha_fin = models.DateField(
        verbose_name='Fecha de Fin'
    )
    activo = models.BooleanField(
        default=False,
        verbose_name='Activo'
    )
    
    class Meta:
        verbose_name = 'Período Académico'
        verbose_name_plural = 'Períodos Académicos'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        # Solo un período puede estar activo
        if self.activo:
            PeriodoAcademico.objects.filter(activo=True).exclude(pk=self.pk).update(activo=False)
        super().save(*args, **kwargs)


class ConfiguracionSistema(models.Model):
    """Configuración general del sistema."""
    
    clave = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Clave'
    )
    valor = models.TextField(
        verbose_name='Valor'
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
    
    def __str__(self):
        return self.clave
