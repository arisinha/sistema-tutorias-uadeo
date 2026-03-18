"""
Modelos de usuarios y autenticación.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado con roles y unidad académica.
    """
    
    class Rol(models.TextChoices):
        TUTOR = 'tutor', 'Tutor'
        COORDINADOR = 'coordinador', 'Coordinador'
        JEFE_DEPARTAMENTO = 'jefe', 'Jefe de Departamento'
    
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.TUTOR,
        verbose_name='Rol'
    )
    unidad = models.ForeignKey(
        'administracion.UnidadAcademica',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
        verbose_name='Unidad Académica'
    )
    programa_educativo = models.ForeignKey(
        'administracion.ProgramaEducativo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
        verbose_name='Programa Educativo'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"
    
    @property
    def es_tutor(self):
        return self.rol == self.Rol.TUTOR
    
    @property
    def es_coordinador(self):
        return self.rol == self.Rol.COORDINADOR
    
    @property
    def es_jefe(self):
        return self.rol == self.Rol.JEFE_DEPARTAMENTO
