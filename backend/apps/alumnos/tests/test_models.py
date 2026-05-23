import pytest
from apps.alumnos.models import Alumno
from apps.administracion.models import ProgramaEducativo, UnidadAcademica
from apps.usuarios.models import Usuario

@pytest.fixture
def unidad_academica(db):
    return UnidadAcademica.objects.create(
        clave="UNIDAD01",
        nombre="Unidad Centro"
    )

@pytest.fixture
def programa_educativo(db, unidad_academica):
    return ProgramaEducativo.objects.create(
        clave="PROG01",
        nombre="Ingeniería de Software",
        unidad=unidad_academica,
        duracion_semestres=9
    )

@pytest.fixture
def tutor(db):
    return Usuario.objects.create_user(
        username="tutor_test",
        password="password123",
        rol="tutor"
    )

@pytest.mark.django_db
class TestAlumnoModel:
    def test_creacion_alumno_basico(self, programa_educativo):
        """Prueba que un alumno se crea correctamente con campos obligatorios"""
        alumno = Alumno.objects.create(
            matricula="20260001",
            nombre="Juan",
            apellido_paterno="Pérez",
            email="juan.perez@uadeo.edu.mx",
            programa_educativo=programa_educativo,
            semestre=1
        )
        
        assert alumno.id is not None
        assert alumno.matricula == "20260001"
        assert alumno.activo is True
        assert alumno.requiere_tutoria_individual is False
        assert alumno.nombre_completo == "Juan Pérez "

    def test_creacion_alumno_completo(self, programa_educativo, tutor):
        """Prueba que un alumno se crea correctamente con todos los campos"""
        alumno = Alumno.objects.create(
            matricula="20260002",
            nombre="María",
            apellido_paterno="García",
            apellido_materno="López",
            email="maria.garcia@uadeo.edu.mx",
            telefono="5551234567",
            programa_educativo=programa_educativo,
            semestre=5,
            tutor=tutor,
            requiere_tutoria_individual=True,
            motivo_tutoria_individual="Bajo rendimiento en matemáticas"
        )
        
        assert alumno.nombre_completo == "María García López"
        assert alumno.tutor == tutor
        assert alumno.requiere_tutoria_individual is True