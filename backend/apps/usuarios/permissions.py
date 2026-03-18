"""
Permisos personalizados basados en roles.
"""

from rest_framework import permissions


class EsTutor(permissions.BasePermission):
    """Permite acceso solo a tutores."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.rol == 'tutor'
        )


class EsCoordinador(permissions.BasePermission):
    """Permite acceso solo a coordinadores."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.rol == 'coordinador'
        )


class EsJefeDepartamento(permissions.BasePermission):
    """Permite acceso solo a jefes de departamento."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.rol == 'jefe'
        )


class EsCoordinadorOJefe(permissions.BasePermission):
    """Permite acceso a coordinadores o jefes."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.rol in ['coordinador', 'jefe']
        )


class EsTutorOCoordinador(permissions.BasePermission):
    """Permite acceso a tutores o coordinadores."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.rol in ['tutor', 'coordinador']
        )
