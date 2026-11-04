from django.db import models

from apps.patients.models import Patient


class AvailabilitySlot(models.Model):
    """Creneaux recurrents du medecin - PROPRIETAIRE : Leonardo (US-11)."""

    class Jour(models.TextChoices):
        LUNDI = "LUNDI", "Lundi"
        MARDI = "MARDI", "Mardi"
        MERCREDI = "MERCREDI", "Mercredi"
        JEUDI = "JEUDI", "Jeudi"
        VENDREDI = "VENDREDI", "Vendredi"
        SAMEDI = "SAMEDI", "Samedi"

    jour = models.CharField("jour", max_length=10, choices=Jour.choices)
    debut = models.TimeField("debut")
    fin = models.TimeField("fin")
    duree_par_defaut = models.PositiveIntegerField("duree par defaut (min)", default=30)
    actif = models.BooleanField("actif", default=True)

    class Meta:
        ordering = ["jour", "debut"]
        verbose_name = "creneau de disponibilite"

    def __str__(self):
        return f"{self.get_jour_display()} {self.debut}-{self.fin}"


class Block(models.Model):
    """Indisponibilites ponctuelles (conges, pauses)."""

    date_debut = models.DateField("du")
    date_fin = models.DateField("au")
    motif = models.CharField("motif", max_length=200, blank=True)

    class Meta:
        ordering = ["date_debut"]
        verbose_name = "indisponibilite"

    def __str__(self):
        return f"{self.date_debut} -> {self.date_fin} {self.motif}".strip()


class Appointment(models.Model):
    """Workflow des demandes (MedConnect RG-01 a RG-05) :

    EN_ATTENTE -> demande envoyee par le patient (RG-02, RG-03)
    CONFIRME   -> validee par la SECRETAIRE uniquement (RG-01, RG-04)
    REFUSE     -> demande rejetee par la secretaire
    ANNULE     -> rendez-vous confirme puis annule
    Plusieurs demandes peuvent viser le meme creneau, une seule est CONFIRME (RG-05).
    """

    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        CONFIRME = "CONFIRME", "Confirme"
        REFUSE = "REFUSE", "Refuse"
        ANNULE = "ANNULE", "Annule"
        TERMINE = "TERMINE", "Termine"
        ABSENTE = "ABSENTE", "Patient absent"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="rendez_vous",
        verbose_name="patient",
    )
    debut = models.DateTimeField("debut")
    duree_minutes = models.PositiveIntegerField("duree (min)", default=30)
    motif = models.CharField("motif", max_length=200)
    statut = models.CharField(
        "statut", max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE
    )
    notes = models.TextField("notes", blank=True)
    rappel_envoye = models.BooleanField("rappel envoye", default=False)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["debut"]
        verbose_name = "rendez-vous"

    def __str__(self):
        return f"{self.patient} - {self.debut:%d/%m/%Y %H:%M}"
