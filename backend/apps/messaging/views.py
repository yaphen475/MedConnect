from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Message, Thread
from .serializers import MessageSerializer, ThreadSerializer


class ThreadViewSet(viewsets.ModelViewSet):
    """US-15 a US-17 - PROPRIETAIRE : Wissal.

    RG-11 : chaque utilisateur ne voit QUE les conversations auxquelles il
    participe (le filtrage se fait ici, pas cote frontend).
    A FAIRE (Wissal) : marquer "lu_le" a la lecture, indicateur de non-lu.
    """

    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Thread.objects.filter(participants=self.request.user)
            .distinct()
            .select_related("patient")
            .prefetch_related("participants", "messages__emetteur")
        )

    def perform_create(self, serializer):
        thread = serializer.save()
        thread.participants.add(self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    """US-15/US-16 - un message ne peut etre envoye QUE dans un fil auquel
    on participe (sinon 403)."""

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Message.objects.filter(thread__participants=self.request.user)
            .distinct()
            .select_related("thread", "emetteur")
        )

    def perform_create(self, serializer):
        thread = serializer.validated_data["thread"]
        if self.request.user not in thread.participants.all():
            raise PermissionDenied("Vous ne faites pas partie de cette conversation.")
        serializer.save(emetteur=self.request.user)
        thread.save(update_fields=["modifie_le"])
