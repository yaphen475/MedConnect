from django import forms
from django.core.exceptions import ValidationError

from apps.agenda import services
from apps.agenda.models import Appointment
from apps.patients.models import Patient


class DirectAppointmentForm(forms.ModelForm):
    """US-08: secretary creates a confirmed appointment directly (RG-04)."""

    class Meta:
        model = Appointment
        fields = ["patient", "date", "start_time", "motif"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "start_time": forms.TimeInput(
                attrs={"type": "time"}, format="%H:%M"
            ),
            "motif": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["patient"].queryset = Patient.objects.all()
        self.fields["patient"].widget.attrs.setdefault("class", "form-select")
        self.fields["date"].widget.attrs.setdefault("class", "form-control")
        self.fields["start_time"].widget.attrs.setdefault(
            "class", "form-control"
        )

    def clean(self):
        cleaned = super().clean()
        day = cleaned.get("date")
        start_time = cleaned.get("start_time")
        if day and start_time:
            if start_time not in services.practice_slots(day):
                raise ValidationError(
                    "This time is outside the practice opening hours."
                )
            clash = Appointment.objects.filter(
                date=day,
                start_time=start_time,
                status=Appointment.Status.CONFIRMED,
            )
            if self.instance.pk:
                clash = clash.exclude(pk=self.instance.pk)
            if clash.exists():
                raise ValidationError(
                    "This slot already hosts a confirmed appointment."
                )
        return cleaned


class EditAppointmentForm(DirectAppointmentForm):
    """US-08: secretary modifies an appointment without breaking RG-04."""

    class Meta(DirectAppointmentForm.Meta):
        fields = ["patient", "date", "start_time", "motif"]
