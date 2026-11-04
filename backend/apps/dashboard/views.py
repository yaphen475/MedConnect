"""US-21/US-22 - PROPRIETAIRE : Wissal (interface) + Philippe (calculs).

KPIs de base par profil (MedConnect §7) ; a enrichir avec les courbes et
l'entonnoir demande -> rendez-vous -> consultation.
"""
from datetime import date

from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Role
from apps.agenda.models import Appointment
from apps.core.permissions import IsMedecinOuSecretariat
from apps.dossiers.models import CompteRendu
from apps.messaging.models import Thread
from apps.patients.models import Patient
from apps.segments.models import Segment


class KpiView(APIView):
    permission_classes = [IsAuthenticated, IsMedecinOuSecretariat]

    def get(self, request):
        today = date.today()
        statuts_actifs = [Appointment.Statut.EN_ATTENTE, Appointment.Statut.CONFIRME]
        data = {
            "patients_total": Patient.objects.count(),
            "rendez_vous_jour": Appointment.objects.filter(
                debut__date=today, statut__in=statuts_actifs
            ).count(),
            "rendez_vous_a_venir": Appointment.objects.filter(
                debut__gt=timezone.now(), statut__in=statuts_actifs
            ).count(),
            # MedConnect US-22 : la secretaire voit surtout les demandes en attente
            "demandes_en_attente": Appointment.objects.filter(
                statut=Appointment.Statut.EN_ATTENTE
            ).count(),
            "conversations_total": Thread.objects.filter(participants=request.user).count(),
            "segments_total": Segment.objects.count(),
        }
        if request.user.role == Role.MEDECIN:
            data["comptes_rendus_total"] = CompteRendu.objects.count()
        return Response(data)
