import logging

logger = logging.getLogger('auditoria')

def get_client_ip(request):
    """Obtiene la IP del cliente desde el request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def registrar_accion(request, accion: str, detalle: str):
    """
    Registra una acción crítica en el modelo de auditoría y en los logs.
    """
    from .models import AuditoriaAccion
    
    usuario = request.user if request.user.is_authenticated else None
    ip = get_client_ip(request)
    
    # Registrar en DB
    AuditoriaAccion.objects.create(
        usuario=usuario,
        accion=accion,
        detalle=detalle,
        ip=ip
    )
    
    # Registrar en log file/console
    username = usuario.username if usuario else 'Anónimo'
    logger.info(f"AUDIT - [{username} @ {ip}] {accion}: {detalle}")
