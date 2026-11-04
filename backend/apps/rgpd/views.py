from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import Role
from apps.core.permissions import IsMedecin

from .models import Consentement, DemandeDonnee, JournalAcces, RegleRetention
from .serializers import (
    ConsentementSerializer,
    DemandeDonneeSerializer,
    JournalAccesSerializer,
    RegleRetentionSerializer,
)


class ConsentementViewSet(viewsets.ModelViewSet):
    """PROPRIETAIRE : Ahmed (US-02, US-38). Un patient ne voit que les siens."""

    queryset = Consentement.objects.all()
    serializer_class = ConsentementSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["finalite", "accorde"]

    def get_queryset(self):
        qs = Consentement.objects.select_related("patient")
        user = self.request.user
        if user.role == Role.PATIENT:
            patient = getattr(user, "patient", None)
            return qs.filter(patient=patient) if patient else qs.none()
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == Role.PATIENT:
            serializer.save(patient=getattr(user, "patient", None))
        else:
            serializer.save()


class DemandeDonneeViewSet(viewsets.ModelViewSet):
    """US-34 / US-37 : le patient demande un export ou un effacement."""

    queryset = DemandeDonnee.objects.all()
    serializer_class = DemandeDonneeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = DemandeDonnee.objects.select_related("patient")
        user = self.request.user
        if user.role == Role.PATIENT:
            patient = getattr(user, "patient", None)
            return qs.filter(patient=patient) if patient else qs.none()
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == Role.PATIENT:
            serializer.save(patient=getattr(user, "patient", None))
        else:
            serializer.save()


class JournalAccesViewSet(viewsets.ReadOnlyModelViewSet):
    """US-36 - consultation par le medecin uniquement."""

    queryset = JournalAcces.objects.select_related("utilisateur")
    serializer_class = JournalAccesSerializer
    permission_classes = [IsMedecin]


class RegleRetentionViewSet(viewsets.ModelViewSet):
    queryset = RegleRetention.objects.all()
    serializer_class = RegleRetentionSerializer
    permission_classes = [IsMedecin]
