from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsMedecinOuSecretariat

from .models import Patient
from .serializers import PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """CRUD des fiches patients - PROPRIETAIRE : Ahmed.

    US-05 a US-10 (voir docs/BACKLOG.md).
    """

    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsMedecinOuSecretariat]
    search_fields = ["first_name", "last_name", "email", "telephone"]
    ordering_fields = ["last_name", "cree_le"]

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        patient = getattr(request.user, "patient", None)
        if patient is None:
            return Response({"detail": "Aucune fiche patient associee a ce compte."}, status=404)
        return Response(PatientSerializer(patient).data)
