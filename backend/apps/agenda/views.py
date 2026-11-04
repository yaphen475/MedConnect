from rest_framework import viewsets

from apps.accounts.models import Role
from apps.core.permissions import IsMedecinOuProprietaire, IsMedecinOuSecretariat

from .models import Appointment, AvailabilitySlot, Block
from .serializers import AppointmentSerializer, AvailabilitySlotSerializer, BlockSerializer


class AvailabilitySlotViewSet(viewsets.ModelViewSet):
    """PROPRIETAIRE : Leonardo (US-11)."""

    queryset = AvailabilitySlot.objects.all()
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [IsMedecinOuSecretariat]


class BlockViewSet(viewsets.ModelViewSet):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    permission_classes = [IsMedecinOuSecretariat]


class AppointmentViewSet(viewsets.ModelViewSet):
    """PROPRIETAIRE : Leonardo (US-12 a US-16).

    A FAIRE (Leonardo) :
    - filtrer les creneaux proposes selon AvailabilitySlot + Block
    - eviter les chevauchements a la creation
    - envoyer les rappels via apps.core.tasks.run_task
    """

    queryset = Appointment.objects.select_related("patient")
    serializer_class = AppointmentSerializer
    permission_classes = [IsMedecinOuProprietaire]
    filterset_fields = ["statut", "patient"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == Role.PATIENT:
            patient = getattr(user, "patient", None)
            return qs.filter(patient=patient) if patient else qs.none()
        return qs
