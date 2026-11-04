from django.db import models

from apps.accounts.models import User


class Patient(models.Model):
    user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="patient",
        verbose_name="compte patient",
    )
    first_name = models.CharField("prenom", max_length=100)
    last_name = models.CharField("nom", max_length=100)
    email = models.EmailField("email", blank=True)
    telephone = models.CharField("telephone", max_length=20, blank=True)
    date_naissance = models.DateField("date de naissance", null=True, blank=True)
    adresse = models.CharField("adresse", max_length=255, blank=True)
    notes = models.TextField("notes administratives", blank=True)
    cree_le = models.DateTimeField("cree le", auto_now_add=True)
    modifie_le = models.DateTimeField("modifie le", auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "patient"

    @property
    def nom_complet(self):
        return f"{self.last_name} {self.first_name}".strip()

    def __str__(self):
        return self.nom_complet
