"""
URL configuration for Sistema de Tutorías.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.usuarios.urls')),
    path('api/alumnos/', include('apps.alumnos.urls')),
    path('api/reportes/', include('apps.reportes.urls')),
    path('api/coordinacion/', include('apps.coordinacion.urls')),
    path('api/administracion/', include('apps.administracion.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
