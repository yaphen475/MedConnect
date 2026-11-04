from rest_framework import serializers

from .models import Consentement, DemandeDonnee, JournalAcces, RegleRetention


class ConsentementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consentement
        fields = [
            "id",
            "patient",
            "finalite",
            "accorde",
            "donne_le",
            "retire_le",
            "version_texte",
        ]
        read_only_fields = ["id", "donne_le", "retire_le"]


class DemandeDonneeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeDonnee
        fields = [
            "id",
            "patient",
            "type",
            "statut",
            "commentaire",
            "demande_le",
            "traite_le",
        ]
        read_only_fields = ["id", "statut", "demande_le", "traite_le"]


class JournalAccesSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.CharField(source="utilisateur.__str__", read_only=True)

    class Meta:
        model = JournalAcces
        fields = ["id", "utilisateur", "utilisateur_nom", "action", "chemin", "adresse_ip", "date"]


class RegleRetentionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegleRetention
        fields = ["id", "modele", "jours", "description"]
