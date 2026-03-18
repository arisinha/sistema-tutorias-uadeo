"""
Config package for Sistema de Tutorías.
"""
from .celery import app as celery_app

__all__ = ('celery_app',)
