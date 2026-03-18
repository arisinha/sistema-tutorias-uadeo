"""
URLs de autenticación y usuarios.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LoginView, LogoutView, PerfilView, UsuarioViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
    path('', include(router.urls)),
]
