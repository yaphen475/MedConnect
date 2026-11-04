try:
    from .celery import app as celery_app

    __all__ = ("celery_app",)
except Exception:
    # Celery/Redis optionnel : le projet tourne sans (voir settings.CELERY_ENABLED)
    pass
