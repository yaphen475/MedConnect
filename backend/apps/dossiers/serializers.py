from rest_framework import serializers

from .models import CompteRendu, Ordonnance


class CompteRenduSerializer(serializers.ModelSerializer):
    patient_nom = serializers.CharField(source="patient.nom_complet", read_only=True)
    medecin_nom = serializers.CharField(source="medecin.get_full_name", read_only=True, default=None)

    class Meta:
        model = CompteRendu
        fields = [
            "id",
            "patient",
            "patient_nom",
            "medecin",
            "medecin_nom",
            "date_consultation",
            "titre",
            "contenu",
            "cree_le",
        ]
        read_only_fields = ["id", "medecin", "cree_le"]


class OrdonnanceSerializer(serializers.ModelSerializer):
    patient_nom = serializers.CharField(source="patient.nom_complet", read_only=True)
    medecin_nom = serializers.CharField(source="medecin.get_full_name", read_only=True, default=None)

    class Meta:
        model = Ordonnance
        fields = [
            "id",
            "patient",
            "patient_nom",
            "medecin",
            "medecin_nom",
            "date_ordonnance",
            "contenu",
            "cree_le",
        ]
        read_only_fields = ["id", "medecin", "cree_le"]
