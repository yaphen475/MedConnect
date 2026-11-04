from django.db import models

from apps.accounts.models import User
from apps.patients.models import Patient


class Thread(models.Model):
    """Fil de discussion entre utilisateurs - PROPRIETAIRE : Wissal (US-15 a US-17).

    RG-11 : seuls les participants (ManyToMany) voient le fil - ni l'admin
    technique, ni un tiers. `patient` est facultatif : simple contexte quand
    la conversation concerne un patient du cabinet.
    """

    participants = models.ManyToManyField(
        User, related_name="threads", verbose_name="participants"
    )
    patient = models.ForeignKey(
        Patient,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="conversations",
        verbose_name="patient (contexte)",
    )
    sujet = models.CharField("sujet", max_length=200, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-modifie_le"]
        verbose_name = "conversation"

    def __str__(self):
        return self.sujet or f"Conversation #{self.pk}"


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")
    emetteur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages_envoyes", verbose_name="emetteur"
    )
    corps = models.TextField("corps")
    piece_jointe = models.FileField("piece jointe", upload_to="messages/", blank=True, null=True)
    lu_le = models.DateTimeField("lu le", null=True, blank=True)
    cree_le = models.DateTimeField("envoye le", auto_now_add=True)

    class Meta:
        ordering = ["cree_le"]
        verbose_name = "message"

    def __str__(self):
        return f"Message de {self.emetteur} le {self.cree_le:%d/%m %H:%M}"
