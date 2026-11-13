from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """US-15 / US-16 / US-17: internal messaging between authorised users.

    The technical administrator never appears in a conversation (RG-11 /
    « Messagerie — Admin : sans accès au contenu »).
    """

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        names = ", ".join(
            self.participants.values_list("username", flat=True)
        )
        return f"Conversation ({names})"

    @classmethod
    def direct(cls, user_a, user_b):
        """Return (conversation, created) for a 1:1 conversation."""
        conversation = cls.objects.filter(participants=user_a).filter(
            participants=user_b
        ).first()
        if conversation is not None:
            return conversation, False
        conversation = cls.objects.create()
        conversation.participants.set([user_a, user_b])
        return conversation, True

    def is_participant(self, user):
        return self.participants.filter(pk=user.pk).exists()

    def other_participants(self, user):
        return self.participants.exclude(pk=user.pk)

    @property
    def last_message(self):
        return self.messages.order_by("-sent_at").first()


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["sent_at"]  # US-16: chronological history

    def __str__(self):
        return f"{self.sender} → {self.sent_at:%d/%m %H:%M}"
