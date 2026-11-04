from django.db import models

from apps.accounts.models import User
from apps.patients.models import Patient


class CompteRendu(models.Model):
    """US-11/US-12 - PROPRIETAIRE : Philippe.

    RG-07 : inaccessible a la secretaire. RG-09 : redige par le medecin seul.
    RG-10 : conserve dans l'historique du patient.
    """

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="comptes_rendus", verbose_name="patient"
    )
    medecin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="comptes_rendus_rediges",
        verbose_name="medecin",
    )
    date_consultation = models.DateField("date de consultation")
    titre = models.CharField("titre", max_length=200)
    contenu = models.TextField("contenu du compte rendu")
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_consultation"]
        verbose_name = "compte rendu medical"

    def __str__(self):
        return f"{self.titre} - {self.patient} ({self.date_consultation})"


class Ordonnance(models.Model):
    """US-13/US-14 - PROPRIETAIRE : Philippe.

    Document de DEMONSTRATION sans valeur medicale (voir docs/BACKLOG.md §1.3).
    RG-09 : redige par le medecin. RG-07 : contenu masque a la secretaire.
    """

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="ordonnances", verbose_name="patient"
    )
    medecin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="ordonnances_redigees",
        verbose_name="medecin",
    )
    date_ordonnance = models.DateField("date", auto_now_add=True)
    contenu = models.TextField("contenu (demonstration)")
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-cree_le"]
        verbose_name = "ordonnance"

    def __str__(self):
        return f"Ordonnance {self.patient} ({self.date_ordonnance})"
