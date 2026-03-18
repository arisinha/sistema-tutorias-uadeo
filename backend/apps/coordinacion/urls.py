"""
URLs del dashboard de coordinación.
"""

from django.urls import path

from .views import (
    DashboardView,
    EstadisticasTutoresView,
    AlumnosRiesgoView,
    ResumenReportesView
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('estadisticas-tutores/', EstadisticasTutoresView.as_view(), name='estadisticas-tutores'),
    path('alumnos-riesgo/', AlumnosRiesgoView.as_view(), name='alumnos-riesgo'),
    path('resumen-reportes/', ResumenReportesView.as_view(), name='resumen-reportes'),
]
