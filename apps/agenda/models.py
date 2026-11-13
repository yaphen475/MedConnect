from django.conf import settings
from django.db import models

from apps.patients.models import Patient


class Appointment(models.Model):
    """A slot of the doctor's agenda (US-05 → US-10).

    Statuses follow the Product Backlog section 4:
    En attente / Confirmé / Refusé / Annulé.
    """

    class Status(models.TextChoices):
        PENDING = "EN_ATTENTE", "En attente"
        CONFIRMED = "CONFIRME", "Confirmé"
        REFUSED = "REFUSE", "Refusé"
        CANCELLED = "ANNULE", "Annulé"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    motif = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_appointments",
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_appointments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "start_time"]
        constraints = [
            # RG-04 / RG-05: a confirmed appointment locks its slot, and a slot
            # can never host two confirmed appointments.
            models.UniqueConstraint(
                fields=["date", "start_time"],
                condition=models.Q(status="CONFIRME"),
                name="agenda_confirmed_slot_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(duration_minutes__gt=0),
                name="agenda_positive_duration",
            ),
        ]

    def __str__(self):
        return f"{self.date} {self.start_time:%H:%M} — {self.patient}"

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING

    @property
    def is_confirmed(self):
        return self.status == self.Status.CONFIRMED
