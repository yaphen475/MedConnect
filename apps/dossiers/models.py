from django.conf import settings
from django.db import models

from apps.patients.models import Patient


class MedicalReport(models.Model):
    """US-11 / US-12 / RG-09 / RG-10: compte rendu médical (doctor only)."""

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="medical_reports",
    )
    consultation_date = models.DateField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="authored_reports",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-consultation_date", "-created_at"]
        verbose_name = "medical report"
        verbose_name_plural = "medical reports"

    def __str__(self):
        return f"{self.title} — {self.patient} ({self.consultation_date})"


class Prescription(models.Model):
    """US-13 / US-14: démonstration ordonnance, sans valeur médicale."""

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="prescriptions",
    )
    issued_date = models.DateField()
    title = models.CharField(max_length=200, default="Ordonnance de démonstration")
    notes = models.TextField(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="authored_prescriptions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issued_date", "-created_at"]
        verbose_name = "prescription"
        verbose_name_plural = "prescriptions"

    def __str__(self):
        return f"Ordonnance {self.issued_date} — {self.patient}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="items",
    )
    medication = models.CharField(max_length=200)
    dosage = models.CharField(max_length=200, blank=True)
    instructions = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.medication
