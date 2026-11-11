from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrateur technique"
        DOCTOR = "DOCTOR", "Médecin"
        SECRETARY = "SECRETARY", "Secrétaire médicale"
        PATIENT = "PATIENT", "Patient"

    role = models.CharField(max_length=20, choices=Role.choices)

    REQUIRED_FIELDS = ["role"]

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    role__in=("ADMIN", "DOCTOR", "SECRETARY", "PATIENT")
                ),
                name="accounts_user_valid_role",
            )
        ]
