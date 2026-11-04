from django.db import models

from apps.patients.models import Patient


class Segment(models.Model):
    """Groupe genere par le K-means - PROPRIETAIRE : Philippe (US-21 a US-25)."""

    nom = models.CharField("nom", max_length=100, unique=True)
    slug = models.SlugField("slug", unique=True)
    description = models.TextField("description", blank=True)
    centroid = models.JSONField("centroid", default=dict, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "segment"

    def __str__(self):
        return self.nom


class SegmentAssignment(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="affectations", verbose_name="patient"
    )
    segment = models.ForeignKey(
        Segment, on_delete=models.CASCADE, related_name="affectations", verbose_name="segment"
    )
    actif = models.BooleanField("actif", default=True)
    affecte_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-affecte_le"]
        verbose_name = "affectation de segment"

    def __str__(self):
        return f"{self.patient} -> {self.segment}"


class PatientScore(models.Model):
    """Score comportemental (0-100) recalcule par la tache de scoring."""

    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name="score", verbose_name="patient"
    )
    score = models.FloatField("score", default=0)
    facteurs = models.JSONField("facteurs", default=dict, blank=True)
    calcule_le = models.DateTimeField("calcule le", null=True, blank=True)

    class Meta:
        verbose_name = "score patient"

    def __str__(self):
        return f"{self.patient} : {self.score}"
