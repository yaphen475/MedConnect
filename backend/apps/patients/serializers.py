from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    nom_complet = serializers.ReadOnlyField()

    class Meta:
        model = Patient
        fields = [
            "id",
            "user",
            "nom_complet",
            "first_name",
            "last_name",
            "email",
            "telephone",
            "date_naissance",
            "adresse",
            "notes",
            "cree_le",
            "modifie_le",
        ]
        read_only_fields = ["id", "cree_le", "modifie_le"]
