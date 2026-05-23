import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.test import Client
from apps.usuarios.models import Usuario
from apps.administracion.models import UnidadAcademica, ProgramaEducativo
import json

c = Client(HTTP_HOST='localhost')

print("=== INICIANDO PRUEBAS DEL SISTEMA ===")
admin = Usuario.objects.get(username='admin')
c.force_login(admin)
resp = c.get('/api/auth/perfil/')
print(" Auth /perfil/ status:", resp.status_code)

resp = c.get('/api/reportes/')
print(" Reportes List status:", resp.status_code)

print("=== PRUEBAS FINALIZADAS ===")
