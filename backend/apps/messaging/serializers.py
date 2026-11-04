from rest_framework import serializers

from apps.accounts.models import User

from .models import Message, Thread


class MessageSerializer(serializers.ModelSerializer):
    emetteur_nom = serializers.CharField(source="emetteur.get_full_name", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "thread",
            "emetteur",
            "emetteur_nom",
            "corps",
            "piece_jointe",
            "lu_le",
            "cree_le",
        ]
        read_only_fields = ["id", "emetteur", "lu_le", "cree_le"]


class ThreadSerializer(serializers.ModelSerializer):
    """US-15/US-16 - PROPRIETAIRE : Wissal."""

    messages = MessageSerializer(many=True, read_only=True)
    participants = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    participants_noms = serializers.SerializerMethodField()
    patient_nom = serializers.CharField(
        source="patient.nom_complet", read_only=True, default=None
    )

    class Meta:
        model = Thread
        fields = [
            "id",
            "participants",
            "participants_noms",
            "patient",
            "patient_nom",
            "sujet",
            "messages",
            "cree_le",
            "modifie_le",
        ]
        read_only_fields = ["id", "cree_le", "modifie_le"]

    def get_participants_noms(self, obj):
        return [u.get_full_name() or u.username for u in obj.participants.all()]
