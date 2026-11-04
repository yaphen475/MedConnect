from rest_framework import serializers

from .models import PatientScore, Segment, SegmentAssignment


class SegmentSerializer(serializers.ModelSerializer):
    nb_patients = serializers.SerializerMethodField()

    class Meta:
        model = Segment
        fields = ["id", "nom", "slug", "description", "centroid", "nb_patients", "cree_le"]

    def get_nb_patients(self, obj):
        return obj.affectations.filter(actif=True).count()


class SegmentAssignmentSerializer(serializers.ModelSerializer):
    patient_nom = serializers.CharField(source="patient.nom_complet", read_only=True)
    segment_nom = serializers.CharField(source="segment.nom", read_only=True)

    class Meta:
        model = SegmentAssignment
        fields = ["id", "patient", "patient_nom", "segment", "segment_nom", "actif", "affecte_le"]


class PatientScoreSerializer(serializers.ModelSerializer):
    patient_nom = serializers.CharField(source="patient.nom_complet", read_only=True)

    class Meta:
        model = PatientScore
        fields = ["id", "patient", "patient_nom", "score", "facteurs", "calcule_le"]
