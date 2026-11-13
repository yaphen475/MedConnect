from django.db import models

from apps.accounts.models import User


class Patient(models.Model):
    """US-03: administrative fiche for a patient of the private practice."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient_profile",
        null=True,
        blank=True,
        limit_choices_to={"role": User.Role.PATIENT},
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    social_security_number = models.CharField(max_length=30, blank=True)

    # Administrative notes: doctor + secretary (RG-08 limited to useful data).
    administrative_notes = models.TextField(blank=True)
    # Medical notes: doctor only (RG-07, US-04, US-11).
    medical_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "patient"
        verbose_name_plural = "patients"

    def __str__(self):
        if self.last_name and self.first_name:
            return f"{self.last_name.upper()} {self.first_name}"
        return self.full_name

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        if name:
            return name
        if self.user_id:
            return self.user.username
        return f"Patient #{self.pk or '?'}"
