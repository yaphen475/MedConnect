from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", _("Administrateur technique")
        DOCTOR = "DOCTOR", _("Médecin")
        SECRETARY = "SECRETARY", _("Secrétaire médicale")
        PATIENT = "PATIENT", _("Patient")

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
