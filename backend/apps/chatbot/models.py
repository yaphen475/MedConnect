from django.db import models

from apps.patients.models import Patient


class Document(models.Model):
    """Documents du cabinet indexes pour le RAG - BONUS (US-26)."""

    titre = models.CharField("titre", max_length=200)
    contenu = models.TextField("contenu")
    fichier = models.FileField("fichier", upload_to="documents/", blank=True, null=True)
    indexe_le = models.DateTimeField("indexe le", null=True, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["titre"]
        verbose_name = "document du cabinet"

    def __str__(self):
        return self.titre


class Conversation(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="conversations_chatbot",
        null=True,
        blank=True,
        verbose_name="patient",
    )
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-cree_le"]
        verbose_name = "conversation avec l'assistant"

    def __str__(self):
        return f"Conversation #{self.pk}"


class MessageChat(models.Model):
    class Role(models.TextChoices):
        UTILISATEUR = "UTILISATEUR", "Utilisateur"
        ASSISTANT = "ASSISTANT", "Assistant"

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField("role", max_length=20, choices=Role.choices)
    contenu = models.TextField("contenu")
    sources = models.JSONField("sources", default=list, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["cree_le"]
        verbose_name = "message de l'assistant"

    def __str__(self):
        return f"{self.get_role_display()} : {self.contenu[:50]}"
