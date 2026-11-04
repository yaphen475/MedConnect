from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Administrateur"
    MEDECIN = "MEDECIN", "Medecin"
    SECRETARIAT = "SECRETARIAT", "Secretariat"
    PATIENT = "PATIENT", "Patient"


class User(AbstractUser):
    role = models.CharField("role", max_length=20, choices=Role.choices, default=Role.PATIENT)
    telephone = models.CharField("telephone", max_length=20, blank=True)

    class Meta:
        verbose_name = "utilisateur"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
