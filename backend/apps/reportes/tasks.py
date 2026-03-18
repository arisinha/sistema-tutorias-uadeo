"""
Tareas asíncronas de Celery para procesamiento de reportes.
"""

from celery import shared_task
from django.utils import timezone


@shared_task(bind=True, max_retries=3)
def procesar_reporte_async(self, reporte_id: int):
    """
    Procesa un reporte de forma asíncrona.
    
    Args:
        reporte_id: ID del reporte a procesar
    """
    from .models import Reporte, DatoReporteIndividual, DatoReporteGrupal
    from .processors import procesar_reporte_individual, procesar_reporte_grupal
    
    try:
        reporte = Reporte.objects.get(id=reporte_id)
        reporte.estado = Reporte.Estado.PROCESANDO
        reporte.save(update_fields=['estado'])
        
        # Abrir archivo
        archivo = reporte.archivo_original.open('rb')
        
        if reporte.es_individual:
            # Procesar reporte individual
            datos, errores = procesar_reporte_individual(archivo, reporte)
            
            if errores and not datos:
                raise Exception('\n'.join(errores))
            
            # Crear registros de datos y recopilar alumnos que requieren seguimiento
            alumnos_seguimiento = []
            for dato in datos:
                reporte_ref = dato.pop('reporte')
                alumno_ref = dato.pop('alumno')
                
                DatoReporteIndividual.objects.update_or_create(
                    reporte=reporte_ref,
                    alumno=alumno_ref,
                    defaults=dato
                )
                
                # Marcar alumnos que requieren tutoría individual
                if dato.get('requiere_seguimiento'):
                    alumnos_seguimiento.append(alumno_ref.id)
            
            if alumnos_seguimiento:
                from apps.alumnos.models import Alumno
                Alumno.objects.filter(id__in=alumnos_seguimiento).update(
                    requiere_tutoria_individual=True
                )
        
        else:
            # Procesar reporte grupal
            datos, errores = procesar_reporte_grupal(archivo, reporte)
            
            if errores and not datos:
                raise Exception('\n'.join(errores))
            
            # Guardar referencia antes de pop
            reporte_ref = datos.pop('reporte')
            alumnos_riesgo_ids = datos.get('alumnos_riesgo_ids', [])
            
            # Crear registro de datos grupales
            DatoReporteGrupal.objects.update_or_create(
                reporte=reporte_ref,
                defaults=datos
            )
            
            # Marcar alumnos en riesgo
            if alumnos_riesgo_ids:
                from apps.alumnos.models import Alumno
                Alumno.objects.filter(id__in=alumnos_riesgo_ids).update(
                    requiere_tutoria_individual=True
                )
        
        archivo.close()
        
        # Actualizar estado
        reporte.estado = Reporte.Estado.PROCESADO
        reporte.fecha_procesado = timezone.now()
        reporte.mensaje_error = '\n'.join(errores) if errores else ''
        reporte.save(update_fields=['estado', 'fecha_procesado', 'mensaje_error'])
        
        return {
            'status': 'success',
            'reporte_id': reporte_id,
            'errores': errores
        }
        
    except Reporte.DoesNotExist:
        return {'status': 'error', 'message': 'Reporte no encontrado'}
    
    except Exception as e:
        # Reintentar o marcar como error
        try:
            reporte = Reporte.objects.get(id=reporte_id)
            reporte.estado = Reporte.Estado.ERROR
            reporte.mensaje_error = str(e)
            reporte.save(update_fields=['estado', 'mensaje_error'])
        except Exception:
            pass
        
        raise self.retry(exc=e, countdown=60)
