from django.db import models

from apps.accounts.models import User
from apps.patients.models import Patient


class Consentement(models.Model):
    """US-02 / US-38 - PROPRIETAIRE : Ahmed."""

    class Finalite(models.TextChoices):
        RDV = "RDV", "Prise de rendez-vous"
        MESSAGERIE = "MESSAGERIE", "Messagerie"
        ANALYSE = "ANALYSE", "Segmentation et scoring"
        CHATBOT = "CHATBOT", "Assistant conversationnel"

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="consentements", verbose_name="patient"
    )
    finalite = models.CharField("finalite", max_length=20, choices=Finalite.choices)
    accorde = models.BooleanField("accorde", default=False)
    donne_le = models.DateTimeField("donne le", auto_now_add=True)
    retire_le = models.DateTimeField("retire le", null=True, blank=True)
    version_texte = models.CharField("version du texte", max_length=20, default="v1")

    class Meta:
        ordering = ["-donne_le"]
        verbose_name = "consentement"
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "finalite", "version_texte"], name="unique_consentement"
            )
        ]

    def __str__(self):
        return f"{self.patient} / {self.get_finalite_display()} : {'oui' if self.accorde else 'non'}"


class DemandeDonnee(models.Model):
    """US-34 / US-37 - droit a l'effacement et a la portabilite."""

    class Type(models.TextChoices):
        EXPORT = "EXPORT", "Export de mes donnees"
        EFFACEMENT = "EFFACEMENT", "Effacement de mes donnees"

    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        TRAITEE = "TRAITEE", "Traitee"
        REFUSEE = "REFUSEE", "Refusee"

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="demandes_donnees", verbose_name="patient"
    )
    type = models.CharField("type", max_length=20, choices=Type.choices)
    statut = models.CharField(
        "statut", max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE
    )
    commentaire = models.TextField("commentaire", blank=True)
    demande_le = models.DateTimeField("demande le", auto_now_add=True)
    traite_le = models.DateTimeField("traite le", null=True, blank=True)

    class Meta:
        ordering = ["-demande_le"]
        verbose_name = "demande sur les donnees"

    def __str__(self):
        return f"{self.patient} - {self.get_type_display()} ({self.get_statut_display()})"


class JournalAcces(models.Model):
    """US-36 - qui a vu quoi, quand (ecrit par AccessLogMiddleware)."""

    utilisateur = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="journal_acces"
    )
    action = models.CharField("action", max_length=255)
    chemin = models.CharField("chemin", max_length=255)
    adresse_ip = models.CharField("adresse IP", max_length=45, blank=True)
    date = models.DateTimeField("date", auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "journal d'acces"

    def __str__(self):
        return f"{self.date:%d/%m %H:%M} {self.action}"


class RegleRetention(models.Model):
    """US-35 - purge automatique, parametree par l'administrateur."""

    modele = models.CharField("modele concerne", max_length=100, unique=True)
    jours = models.PositiveIntegerField("duree de conservation (jours)")
    description = models.CharField("description", max_length=255, blank=True)

    class Meta:
        verbose_name = "regle de retention"

    def __str__(self):
        return f"{self.modele} : {self.jours} jours"
