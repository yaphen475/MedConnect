from rest_framework import serializers


class KpiSerializer(serializers.Serializer):
    patients_total = serializers.IntegerField()
    rendez_vous_jour = serializers.IntegerField()
    rendez_vous_a_venir = serializers.IntegerField()
    messages_non_lus = serializers.IntegerField()
    segments_total = serializers.IntegerField()
