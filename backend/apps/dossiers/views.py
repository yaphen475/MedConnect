from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from apps.accounts.models import Role
from apps.core.permissions import IsMedecin, IsMedecinOuPatientProprietaire

from .models import CompteRendu, Ordonnance
from .serializers import CompteRenduSerializer, OrdonnanceSerializer


class CompteRenduViewSet(viewsets.ModelViewSet):
    """US-11/US-12 - PROPRIETAIRE : Philippe.

    RG-07/RG-09 : le medecin SEUL lit et redige. Secretaire, admin et
    autres patients n'ont aucun acces (IsMedecin).
    A FAIRE (Philippe) : tests de non-acces pour chaque role.
    """

    queryset = CompteRendu.objects.select_related("patient", "medecin")
    serializer_class = CompteRenduSerializer
    permission_classes = [IsMedecin]
    filterset_fields = ["patient", "date_consultation"]

    def perform_create(self, serializer):
        serializer.save(medecin=self.request.user)


class OrdonnanceViewSet(viewsets.ModelViewSet):
    """US-13/US-14 - PROPRIETAIRE : Philippe.

    Medecin : ecriture + lecture integrale.
    Patient : lecture de SES SEULES ordonnances (RG-06).
    Secretaire / admin : aucun acces (RG-07, RG-12).
    """

    queryset = Ordonnance.objects.all()
    serializer_class = OrdonnanceSerializer
    permission_classes = [IsMedecinOuPatientProprietaire]
    filterset_fields = ["patient"]

    def get_queryset(self):
        qs = super().get_queryset().select_related("patient", "medecin")
        user = self.request.user
        if user.role == Role.PATIENT:
            patient = getattr(user, "patient", None)
            return qs.filter(patient=patient) if patient else qs.none()
        if user.role == Role.MEDECIN:
            return qs
        return qs.none()

    def perform_create(self, serializer):
        if self.request.user.role != Role.MEDECIN:
            raise PermissionDenied("Seul le medecin peut rediger une ordonnance (RG-09).")
        serializer.save(medecin=self.request.user)
