"""Point d'entree unique pour les taches planifiees.

Sans Redis : la tache s'execute EN SYNCHRONE (le projet reste demontrable).
Avec REDIS_URL : la tache part dans Celery.
PROPRIETAIRE : Ahmed (utilise par Leonardo pour les rappels/relances).
"""
from django.conf import settings


def run_task(task, *args, **kwargs):
    if getattr(settings, "CELERY_ENABLED", False):
        return task.delay(*args, **kwargs)
    return task(*args, **kwargs)
