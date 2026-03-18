"""
URLs de administración del sistema.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UnidadAcademicaViewSet,
    ProgramaEducativoViewSet,
    PeriodoAcademicoViewSet,
    ConfiguracionSistemaViewSet
)

router = DefaultRouter()
router.register(r'unidades', UnidadAcademicaViewSet, basename='unidades')
router.register(r'programas', ProgramaEducativoViewSet, basename='programas')
router.register(r'periodos', PeriodoAcademicoViewSet, basename='periodos')
router.register(r'configuracion', ConfiguracionSistemaViewSet, basename='configuracion')

urlpatterns = [
    path('', include(router.urls)),
]
