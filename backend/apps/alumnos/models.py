"""
Modelos de gestión de alumnos.
"""

from django.db import models
from django.conf import settings


class Alumno(models.Model):
    """Modelo de alumno."""
    
    matricula = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Matrícula'
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre(s)'
    )
    apellido_paterno = models.CharField(
        max_length=100,
        verbose_name='Apellido Paterno'
    )
    apellido_materno = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Apellido Materno'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='Correo Electrónico'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    programa_educativo = models.ForeignKey(
        'administracion.ProgramaEducativo',
        on_delete=models.PROTECT,
        related_name='alumnos',
        verbose_name='Programa Educativo'
    )
    semestre = models.PositiveSmallIntegerField(
        verbose_name='Semestre'
    )
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alumnos_asignados',
        verbose_name='Tutor Asignado',
        limit_choices_to={'rol': 'tutor'}
    )
    requiere_tutoria_individual = models.BooleanField(
        default=False,
        verbose_name='Requiere Tutoría Individual'
    )
    motivo_tutoria_individual = models.TextField(
        blank=True,
        verbose_name='Motivo Tutoría Individual'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'
        ordering = ['apellido_paterno', 'apellido_materno', 'nombre']
        indexes = [
            models.Index(fields=['matricula']),
            models.Index(fields=['programa_educativo', 'semestre']),
            models.Index(fields=['tutor']),
        ]
    
    def __str__(self):
        return f"{self.matricula} - {self.nombre_completo}"
    
    @property
    def nombre_completo(self):
        nombres = [self.nombre, self.apellido_paterno]
        if self.apellido_materno:
            nombres.append(self.apellido_materno)
        return ' '.join(nombres)
    
    @property
    def apellidos(self):
        if self.apellido_materno:
            return f"{self.apellido_paterno} {self.apellido_materno}"
        return self.apellido_paterno
