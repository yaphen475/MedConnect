"""US-35 : purge automatique des donnees expirees.

Lancer manuellement : python manage.py purge_donnees
(ou via Celery beat quand REDIS_URL est configure).
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from apps.rgpd.models import JournalAcces, RegleRetention


class Command(BaseCommand):
    help = "Applique la politique de retention (purge des donnees expirees)."

    def handle(self, *args, **options):
        regle = RegleRetention.objects.filter(modele="JournalAcces").first()
        jours = regle.jours if regle else settings.RGPD_JOURNAL_RETENTION_DAYS
        limite = timezone.now() - timedelta(days=jours)
        deleted, _ = JournalAcces.objects.filter(date__lt=limite).delete()
        self.stdout.write(
            self.style.SUCCESS(f"JournalAcces : {deleted} enregistrement(s) purge(s) (> {jours} jours).")
        )
