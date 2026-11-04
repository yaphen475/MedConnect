"""BONUS (US-26 a US-30) - PROPRIETAIRE : Philippe.

A FAIRE : embeddings locaux + sqlite-vec + LLM open-source auto-heberge
(AUCUN modele americain, AUCUNE donnee sortante - voir CONTRIBUTING.md).
"""
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsMedecinOuSecretariat

from .models import Conversation, Document, MessageChat
from .serializers import AskSerializer, DocumentSerializer, MessageChatSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsMedecinOuSecretariat]


class AskView(APIView):
    def post(self, request):
        serializer = AskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # TODO Philippe : retrieval sur Document, reponse generee en local
        # avec sources (US-27), puis tri de la demande (US-28).
        return Response(
            {
                "detail": "RAG non implemente (bonus) - modele local a brancher.",
                "question": serializer.validated_data["question"],
                "reponse": None,
                "sources": [],
            },
            status=501,
        )
