from rest_framework import serializers

from apps.patients.serializers import PatientSerializer

from .models import Appointment, AvailabilitySlot, Block


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilitySlot
        fields = ["id", "jour", "debut", "fin", "duree_par_defaut", "actif"]


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ["id", "date_debut", "date_fin", "motif"]


class AppointmentSerializer(serializers.ModelSerializer):
    patient_nom = serializers.CharField(source="patient.nom_complet", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "patient_nom",
            "debut",
            "duree_minutes",
            "motif",
            "statut",
            "notes",
            "rappel_envoye",
            "cree_le",
        ]
        read_only_fields = ["id", "rappel_envoye", "cree_le"]
