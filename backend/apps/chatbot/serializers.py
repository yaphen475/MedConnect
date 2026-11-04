from rest_framework import serializers

from .models import Conversation, Document, MessageChat


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "titre", "contenu", "fichier", "indexe_le", "cree_le"]
        read_only_fields = ["id", "indexe_le", "cree_le"]


class MessageChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageChat
        fields = ["id", "conversation", "role", "contenu", "sources", "cree_le"]
        read_only_fields = ["id", "role", "sources", "cree_le"]


class AskSerializer(serializers.Serializer):
    question = serializers.CharField()
    conversation_id = serializers.IntegerField(required=False)
