import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.alumnos.models import Alumno
from apps.administracion.models import ProgramaEducativo, UnidadAcademica
from apps.usuarios.models import Usuario

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db):
    return Usuario.objects.create_user(
        username="admin_coordinador",
        password="password123",
        role="coordinador"
    )

@pytest.fixture
def setup_data(db):
    unidad = UnidadAcademica.objects.create(clave="UNI-X", nombre="Unidad Norte")
    programa = ProgramaEducativo.objects.create(
        clave="ING-SW", nombre="Ingeniería de Software", unidad=unidad
    )
    return {
        "unidad": unidad,
        "programa": programa
    }

@pytest.mark.django_db
class TestAlumnoAPI:
    def test_crear_alumno(self, api_client, admin_user, setup_data):
        """Prueba de integración: Crear Alumno vía API"""
        api_client.force_authenticate(user=admin_user)
        url = reverse('alumno-list') # asumiendo que router registra como 'alumno'
        
        payload = {
            "matricula": "12345678",
            "nombre": "Carlos",
            "apellido_paterno": "Serrano",
            "email": "carlos@test.com",
            "programa_educativo": setup_data["programa"].id,
            "semestre": 3
        }

        response = api_client.post(url, payload, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Alumno.objects.filter(matricula="12345678").exists()

    def test_listar_alumnos(self, api_client, admin_user, setup_data):
        """Prueba de integración: Listado y recuperación"""
        api_client.force_authenticate(user=admin_user)
        
        Alumno.objects.create(
            matricula="98765432",
            nombre="Ana",
            apellido_paterno="López",
            email="ana@test.com",
            programa_educativo=setup_data["programa"],
            semestre=5
        )
        
        url = reverse('alumno-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results'] if 'results' in response.data else response.data
        assert len(results) >= 1
        
        alumno_data = next((a for a in results if a['matricula'] == '98765432'), None)
        assert alumno_data is not None
        assert alumno_data['nombre'] == "Ana"