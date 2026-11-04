from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsMedecinOuSecretariat

from .models import PatientScore, Segment, SegmentAssignment
from .serializers import PatientScoreSerializer, SegmentAssignmentSerializer, SegmentSerializer


class SegmentViewSet(viewsets.ReadOnlyModelViewSet):
    """PROPRIETAIRE : Philippe (US-21 a US-25).

    A FAIRE (Philippe) : scikit-learn (K-means) + score comportemental,
    a declencher via l'action "recalculer". scikit-learn n'est importe QUE
    dans l'action : le reste du projet tourne sans lui.
    """

    queryset = Segment.objects.all()
    serializer_class = SegmentSerializer
    permission_classes = [IsMedecinOuSecretariat]
    lookup_field = "slug"

    @action(detail=False, methods=["post"])
    def recalculer(self, request):
        from django.utils import timezone

        # TODO Philippe : extraire les features, entrainer KMeans, ecrire
        # Segment + SegmentAssignment + PatientScore (US-21, US-22).
        return Response(
            {
                "detail": "Non implemente (TODO Philippe - scikit-learn KMeans).",
                "segments": Segment.objects.count(),
                "scores": PatientScore.objects.count(),
                "calcule_le": timezone.now(),
            },
            status=501,
        )


class SegmentAssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SegmentAssignment.objects.select_related("patient", "segment")
    serializer_class = SegmentAssignmentSerializer
    permission_classes = [IsMedecinOuSecretariat]


class PatientScoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PatientScore.objects.select_related("patient")
    serializer_class = PatientScoreSerializer
    permission_classes = [IsMedecinOuSecretariat]
